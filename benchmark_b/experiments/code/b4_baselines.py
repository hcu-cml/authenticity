"""B4 -- extra baselines for Table 6 (Hamburg, single city, spatial 5-fold CV, seeds 0-2).

Tasks exactly as Table 6 (run_full_experiments.run_t1/run_t2_roof/run_t2_function):
  T2 roof type      splits.make_splits          spatial_cv, merged 3-class, pooled OOF macro-F1
  T2 building use   splits.make_splits_function spatial_cv, top-8 + Other, pooled OOF macro-F1
  T1 height         splits.spatial_kfold        pooled OOF R^2, `height` dropped, storeys KEPT
                                                (Table 6 keeps the collinear storey count)
New methods (same inputs as the probe = Building attributes, no provenance features):
  lgbm        LightGBM on the Building attributes
  lgbm_1hop   + 1-hop neighbour aggregates: for every relation into Building (OSM building via
              ENRICHED_BY, OSM POI via HAS_POI) the mean of the neighbours' features and the degree
  simplehgn   Simple-HGN (Lv et al., KDD 2021): GAT with learnable edge-type embeddings in the
              attention, residual node connections, residual attention (beta=0.05), L2-normalised
              output embedding; type-specific input projections; self-loops as their own edge type.
              Trained with the benchmark's shared budget (hidden 64, 2 layers, 4 heads, dropout 0.3,
              Adam lr 0.01, wd 5e-4, 150 epochs, full batch) -- no per-model tuning, as for every
              other Table 6 row. Since a 1-dim L2-normalised output is meaningless for regression,
              the L2 norm is applied to the 64-d embedding, followed by a linear head (both tasks).
Anchors (re-run in this harness to show it reproduces Table 6): probe, gnn, gnn_aware.
LightGBM uses fixed hyperparameters (500 trees, lr 0.05, 63 leaves, 0.8 row/col subsampling), no
early stopping, no tuning -- there is no validation split in the Table 6 protocol.

Writes results/b4_runs.jsonl (one line per task x method x seed, resumable).
"""
import argparse, json, os, sys, time

import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.nn import Linear
from torch_geometric.utils import softmax, scatter

HERE = os.path.dirname(os.path.abspath(__file__))
BDIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BDIR)
import _setup_paths  # noqa: E402,F401  (adds shared/, t1_imputation/, ... to sys.path)
sys.path.insert(0, HERE)
import s5_train as S            # noqa: E402
import t1_regression as T1      # noqa: E402
import splits as SP             # noqa: E402
from b1_crosscity_ablation import code_hash   # noqa: E402

RES = os.path.join(HERE, "..", "results")
LGB = dict(n_estimators=500, learning_rate=0.05, num_leaves=63, subsample=0.8, subsample_freq=1,
           colsample_bytree=0.8, n_jobs=8, verbose=-1)


# ------------------------------------------------------------------ LightGBM
def neighbour_features(data):
    """Per relation into Building: mean of source-node features + log1p(degree)."""
    nb = data["Building"].num_nodes
    blocks = []
    for et in data.edge_types:
        s_, rel, t_ = et
        if t_ != "Building" or s_ == "Building":
            continue
        ei = data[et].edge_index
        xs = data[s_].x
        mean = scatter(xs[ei[0]], ei[1], dim=0, dim_size=nb, reduce="mean")
        deg = scatter(torch.ones(ei.size(1)), ei[1], dim=0, dim_size=nb, reduce="sum")
        blocks += [mean, torch.log1p(deg).unsqueeze(1)]
    return torch.cat(blocks, 1)


_NB_CACHE = {}


def _lgbm_X(data, drop, hop):
    X = S.building_features(data, use_prov=False, drop=drop)
    if hop:
        key = id(data)
        if key not in _NB_CACHE:
            _NB_CACHE[key] = neighbour_features(data)
        X = torch.cat([X, _NB_CACHE[key]], 1)
    return X.numpy()


def lgbm_clf(data, y, train_mask, n_classes, seed, use_prov, hop=False, **_):
    import lightgbm as lgb
    X, tr = _lgbm_X(data, (), hop), train_mask.numpy()
    m = lgb.LGBMClassifier(random_state=seed, **LGB).fit(X[tr], y.numpy()[tr])
    return torch.tensor(m.predict(X), dtype=torch.long)


def lgbm_reg(data, target, train_mask, seed, drop, hop=False):
    import lightgbm as lgb
    X, tr = _lgbm_X(data, drop, hop), train_mask.numpy()
    return lgb.LGBMRegressor(random_state=seed, **LGB).fit(X[tr], target[tr]).predict(X)


# ------------------------------------------------------------------ Simple-HGN
class SimpleHGNConv(torch.nn.Module):
    def __init__(self, in_dim, out_dim, heads, n_etypes, edge_dim, beta, dropout, concat=True):
        super().__init__()
        self.H, self.D, self.De, self.beta, self.concat = heads, out_dim, edge_dim, beta, concat
        self.W = Linear(in_dim, heads * out_dim, bias=False)
        self.emb = torch.nn.Embedding(n_etypes, edge_dim)
        self.We = Linear(edge_dim, heads * edge_dim, bias=False)
        self.a_l = torch.nn.Parameter(torch.empty(1, heads, out_dim))
        self.a_r = torch.nn.Parameter(torch.empty(1, heads, out_dim))
        self.a_e = torch.nn.Parameter(torch.empty(1, heads, edge_dim))
        for p in (self.a_l, self.a_r, self.a_e):
            torch.nn.init.xavier_normal_(p)
        self.res = Linear(in_dim, heads * out_dim, bias=False)
        self.drop = torch.nn.Dropout(dropout)

    def forward(self, x, ei, et, alpha_prev=None):
        src, dst = ei
        h = self.W(self.drop(x)).view(-1, self.H, self.D)
        e = self.We(self.emb(et)).view(-1, self.H, self.De)
        logit = ((h * self.a_l).sum(-1)[src] + (h * self.a_r).sum(-1)[dst] + (e * self.a_e).sum(-1))
        alpha = softmax(F.leaky_relu(logit, 0.2), dst, num_nodes=x.size(0))      # [E, H]
        if alpha_prev is not None:
            alpha = alpha * (1 - self.beta) + alpha_prev * self.beta
        out = scatter(h[src] * self.drop(alpha).unsqueeze(-1), dst, dim=0, dim_size=x.size(0), reduce="sum")
        out = out + self.res(x).view(-1, self.H, self.D)
        out = out.reshape(-1, self.H * self.D) if self.concat else out.mean(1)
        return out, alpha.detach()


class SimpleHGN(torch.nn.Module):
    def __init__(self, hidden, out, heads, n_etypes, node_types, dropout, edge_dim=64, beta=0.05):
        super().__init__()
        self.lin_in = torch.nn.ModuleDict({nt: Linear(-1, hidden) for nt in node_types})
        self.c1 = SimpleHGNConv(hidden, hidden, heads, n_etypes, edge_dim, beta, dropout, concat=True)
        self.c2 = SimpleHGNConv(hidden * heads, hidden, heads, n_etypes, edge_dim, beta, dropout, concat=False)
        self.head = Linear(hidden, out)

    def forward(self, xd, order, ei, et):
        h = torch.cat([self.lin_in[nt](xd[nt]) for nt in order], 0)
        h, a = self.c1(h, ei, et)
        h = F.elu(h)
        h, _ = self.c2(h, ei, et, a)
        return self.head(F.normalize(h, p=2, dim=-1))


def _simplehgn_setup(data, xb, n_out, device, c):
    order = list(data.node_types)
    ei, et, offset, total = S._homogeneous_edge_index_typed(data)
    R = len(data.edge_types)
    loops = torch.arange(total)
    ei = torch.cat([ei, torch.stack([loops, loops])], 1)
    et = torch.cat([et, torch.full((total,), R, dtype=torch.long)])
    xd = {nt: data[nt].x.to(device) for nt in order}
    xd["Building"] = xb.to(device)
    model = SimpleHGN(c["hidden"], n_out, c["heads"], R + 1, order, c["dropout"]).to(device)
    b0, nb = offset["Building"], data["Building"].num_nodes
    ei, et = ei.to(device), et.to(device)
    fwd = lambda: model(xd, order, ei, et)[b0:b0 + nb]
    with torch.no_grad():
        fwd()
    return model, fwd


def simplehgn_clf(data, y, train_mask, n_classes, seed, use_prov, device=None, **cfg):
    c = {**S.CFG, **cfg}; device = device or S.pick_device(); S.set_seed(seed)
    model, fwd = _simplehgn_setup(data, S.building_features(data, False), n_classes, device, c)
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    yb, tr = y.to(device), train_mask.to(device)
    for _ in range(c["epochs"]):
        model.train(); opt.zero_grad()
        F.cross_entropy(fwd()[tr], yb[tr]).backward(); opt.step()
    model.eval()
    with torch.no_grad():
        return fwd().argmax(1).cpu()


def simplehgn_reg(data, target, train_mask, seed, drop, device, c):
    S.set_seed(seed)
    tm = train_mask.numpy()
    mu, sd = target[tm].mean(), target[tm].std() + 1e-6
    yb = torch.tensor((target - mu) / sd, dtype=torch.float).to(device)
    model, fwd = _simplehgn_setup(data, S.building_features(data, False, drop=drop), 1, device, c)
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    tr = train_mask.to(device)
    for _ in range(c["epochs"]):
        model.train(); opt.zero_grad()
        F.mse_loss(fwd().squeeze(-1)[tr], yb[tr]).backward(); opt.step()
    model.eval()
    with torch.no_grad():
        return fwd().squeeze(-1).cpu().numpy() * sd + mu


S.METHODS["lgbm"] = lambda *a, **k: lgbm_clf(*a, hop=False, **k)
S.METHODS["lgbm_1hop"] = lambda *a, **k: lgbm_clf(*a, hop=True, **k)
S.METHODS["simplehgn"] = simplehgn_clf


# ------------------------------------------------------------------ evaluation
def reg_once(data, target, method, seed, device, c, drop=("height",)):
    valid = ~np.isnan(target)
    folds, _ = SP.spatial_kfold(data["Building"].pos.numpy(), seed, k=5, labeled=valid)
    oof = np.full(len(target), np.nan)
    for tr, te in folds:
        if method == "lgbm":
            pred = lgbm_reg(data, target, tr, seed, list(drop), hop=False)
        elif method == "lgbm_1hop":
            pred = lgbm_reg(data, target, tr, seed, list(drop), hop=True)
        elif method == "simplehgn":
            pred = simplehgn_reg(data, target, tr, seed, list(drop), device, c)
        else:   # anchors: Table 6's exact code path
            pred = T1._train_reg(data, target, tr, seed, method, list(drop),
                                 method == "gnn_aware", device, c)
        m = te.numpy(); oof[m] = pred[m]
    m = ~np.isnan(oof)
    return T1.reg_metrics(target[m], oof[m])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--methods", default="lgbm,lgbm_1hop,simplehgn,probe,gnn,gnn_aware")
    ap.add_argument("--tasks", default="roof,function,height")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--epochs", type=int, default=150)
    ap.add_argument("--out", default=os.path.join(RES, "b4_runs.jsonl"))
    a = ap.parse_args()
    device = S.pick_device()
    c = {**S.CFG, "epochs": a.epochs}
    data = torch.load(os.path.join(BDIR, "graph_hamburg.pt"), weights_only=False)
    target = np.load(os.path.join(HERE, "..", "targets", "hamburg.npz"), allow_pickle=True)["height"]
    splitters = {"roof": SP.make_splits, "function": SP.make_splits_function}
    done = set()
    if os.path.exists(a.out):
        done = {(r["task"], r["method"], r["seed"]) for r in map(json.loads, open(a.out))}
    chash = code_hash()
    for seed in [int(s) for s in a.seeds.split(",")]:
        for task in a.tasks.split(","):
            for method in a.methods.split(","):
                if (task, method, seed) in done:
                    continue
                if device.type == "cuda":
                    torch.cuda.reset_peak_memory_stats()
                t1 = time.time()
                if task == "height":
                    m = reg_once(data, target, method, seed, device, c)
                    rec = {"metric": "R2", "value": m["R2"], "MAE": m["MAE"], "RMSE": m["RMSE"]}
                else:
                    use_prov = method == "gnn_aware"
                    macro, per = S._eval_one(data, "spatial_cv", method, seed, use_prov, 5,
                                             {"epochs": c["epochs"]}, device, splitters[task])
                    names = splitters[task](data, seed, k=5)["spatial_cv"]["names"]
                    rec = {"metric": "macro_f1", "value": float(macro),
                           "per_class_f1": dict(zip(names, np.round(per, 4).tolist()))}
                rec = {"task": task, "city": "hamburg", "method": method, "seed": seed, **rec,
                       "runtime_s": round(time.time() - t1, 2),
                       "peak_vram_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)
                       if device.type == "cuda" else None, "epochs": c["epochs"], "code": chash}
                with open(a.out, "a") as f:
                    f.write(json.dumps(rec) + "\n")
                print(f"[{time.strftime('%H:%M:%S')}] {task:8s} {method:10s} s{seed} "
                      f"{rec['metric']}={rec['value']:.4f} ({rec['runtime_s']:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
