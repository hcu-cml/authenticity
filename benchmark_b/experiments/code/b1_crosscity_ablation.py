"""B1 -- leave-one-city-out confidence-weighting ablation on T1 height.

Protocol = Table 7 (s8_crosscity.crosscity_eval_regression): the five cached city graphs combined
with s8_crosscity.combine_cities (order hamburg, helsinki, nyc, tokyo, zurich), train on four
cities' Buildings, test on the held-out city, hidden 64, 2 layers, dropout 0.3, Adam lr 0.01,
wd 5e-4, 150 epochs, full batch, seeds 0-9, S.set_seed(seed) before every run. Targets come from
targets/<city>.npz (extract_targets.py; identical to t1_regression.load_target, row order verified).

Variants (Eq. 1 terms):            source typing   confidence w_ce   coverage feats (x_prov)
  V0 agnostic   (Table 7 'gnn')    per-relation*   1                 no
  V1 aware      (Table 7 'gnn_aware') per-relation Jaccard           yes
  V2 no-conf                       per-relation    1                 yes
  V3 no-cov                        per-relation    Jaccard           no
  V4 conf-only                     shared W        Jaccard           no
  V5 agnostic-shared (paper's literal agnostic) shared W  1          no
* Table 7's agnostic arm is to_hetero(GraphSAGE), i.e. one SAGEConv per relation -- NOT a shared W.
  SAGEConv(mean) and GraphConv(add, per-target-normalised uniform weights) are the same function
  class (lin_l/lin_rel with bias on the neighbour mean + lin_r/lin_root without bias on self), so
  V0 is functionally "V1 with w=1 and no x_prov"; V0-vs-V2 isolates x_prov, V0-vs-V3 isolates w.

V0/V1/V3 call t1_regression._train_reg unchanged; V2 = the same call with s5_train.CONFIDENCE_RELS
emptied (uniform weights, still per-target normalised); V4/V5 are a homogeneous GraphConv on the
flattened graph (zero-padded inputs, no per-type parameters), weights normalised per (relation,
target) exactly like V1 and summed over relations, as to_hetero(aggr='sum') does.

Two feature protocols:
  t7      drop=[]          -- what Table 7 actually ran (crosscity_eval_regression passes drop=[]),
                              which leaves the per-city z-scored `height` input column in place.
  guarded drop=['height']  -- the leakage guard the paper states (§setup) and the single-city runs use.

Writes one JSON line per run to results/b1_runs.jsonl; re-running skips finished runs.
"""
import argparse, hashlib, json, os, sys, time

import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.nn import GraphConv, Linear
from torch_geometric.utils import scatter

HERE = os.path.dirname(os.path.abspath(__file__))
BDIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BDIR)
import _setup_paths  # noqa: E402,F401  (adds shared/, t1_imputation/, ... to sys.path)
import s5_train as S            # noqa: E402
import t1_regression as T1      # noqa: E402
import s8_crosscity as S8       # noqa: E402

CITIES = ["hamburg", "helsinki", "nyc", "tokyo", "zurich"]      # = run_full_experiments.CITIES
RES = os.path.join(HERE, "..", "results")
TGT = os.path.join(HERE, "..", "targets")
DROP = {"t7": [], "guarded": ["height"]}


def code_hash():
    h = hashlib.sha256()
    for f in ("shared/s5_train.py", "t1_imputation/t1_regression.py", "crosscity/s8_crosscity.py",
              "shared/neo4j_loader.py"):
        h.update(open(os.path.join(BDIR, f), "rb").read())
    h.update(open(os.path.abspath(__file__), "rb").read())
    return h.hexdigest()[:12]


def load_combined(cities=CITIES):
    graphs = [torch.load(os.path.join(BDIR, f"graph_{c}.pt"), weights_only=False) for c in cities]
    for g, c in zip(graphs, cities):
        g.city = c
    target = np.concatenate([np.load(os.path.join(TGT, f"{c}.npz"), allow_pickle=True)["height"]
                             for c in cities])
    d = S8.combine_cities(graphs)
    assert len(target) == d["Building"].num_nodes
    return d, target


# ------------------------------------------------------------- shared-W (homogeneous) variants
class SharedGNN(torch.nn.Module):
    def __init__(self, hidden, dropout):
        super().__init__()
        self.c1 = GraphConv(-1, hidden)
        self.c2 = GraphConv(hidden, hidden)
        self.lin = Linear(hidden, 1)
        self.drop = torch.nn.Dropout(dropout)

    def forward(self, x, ei, ew):
        x = self.c1(x, ei, ew).relu()
        x = self.drop(x)
        x = self.c2(x, ei, ew).relu()
        return self.lin(x)


def _shared_inputs(data, drop, use_conf, device):
    order = list(data.node_types)
    offset, cur = {}, 0
    for nt in order:
        offset[nt] = cur; cur += data[nt].num_nodes
    feats = {nt: data[nt].x for nt in order}
    feats["Building"] = S.building_features(data, use_prov=False, drop=drop)
    width = max(f.size(1) for f in feats.values())
    x = torch.zeros(cur, width)
    for nt in order:
        x[offset[nt]:offset[nt] + feats[nt].size(0), :feats[nt].size(1)] = feats[nt]
    eis, ews = [], []
    for et in data.edge_types:
        s_, rel, t_ = et
        ei = data[et].edge_index
        w = (data[et].edge_weight.clone().float()
             if use_conf and rel in S.CONFIDENCE_RELS and "edge_weight" in data[et]
             else torch.ones(ei.size(1)))
        den = scatter(w, ei[1], dim=0, dim_size=data[t_].num_nodes, reduce="sum")
        ews.append(w / (den[ei[1]] + 1e-16))
        eis.append(torch.stack([ei[0] + offset[s_], ei[1] + offset[t_]]))
    return (x.to(device), torch.cat(eis, 1).to(device), torch.cat(ews).to(device),
            offset["Building"], data["Building"].num_nodes)


def _train_shared(data, target, train_mask, seed, drop, use_conf, device, c):
    S.set_seed(seed)
    tm = train_mask.cpu().numpy()
    mu, sd = target[tm].mean(), target[tm].std() + 1e-6
    yb = torch.tensor((target - mu) / sd, dtype=torch.float).to(device)
    x, ei, ew, b0, nb = _shared_inputs(data, drop, use_conf, device)
    model = SharedGNN(c["hidden"], c["dropout"]).to(device)
    fwd = lambda: model(x, ei, ew)[b0:b0 + nb].squeeze(-1)
    with torch.no_grad():
        fwd()
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    tr = train_mask.to(device)
    for _ in range(c["epochs"]):
        model.train(); opt.zero_grad()
        F.mse_loss(fwd()[tr], yb[tr]).backward(); opt.step()
    model.eval()
    with torch.no_grad():
        return fwd().cpu().numpy() * sd + mu


# ------------------------------------------------------------- dispatch
def train_variant(v, data, target, train_mask, seed, drop, device, c):
    if v == "probe":                       # Table 7's no-graph Ridge column
        return T1._train_reg(data, target, train_mask, seed, "probe", drop, False, device, c)
    if v == "V0":
        return T1._train_reg(data, target, train_mask, seed, "gnn", drop, False, device, c)
    if v == "V1":
        return T1._train_reg(data, target, train_mask, seed, "gnn_aware", drop, True, device, c)
    if v == "V2":
        saved = S.CONFIDENCE_RELS
        S.CONFIDENCE_RELS = set()          # uniform w, still per-target normalised
        try:
            return T1._train_reg(data, target, train_mask, seed, "gnn_aware", drop, True, device, c)
        finally:
            S.CONFIDENCE_RELS = saved
    if v == "V3":
        return T1._train_reg(data, target, train_mask, seed, "gnn_aware", drop, False, device, c)
    if v == "V4":
        return _train_shared(data, target, train_mask, seed, drop, True, device, c)
    if v == "V5":
        return _train_shared(data, target, train_mask, seed, drop, False, device, c)
    raise ValueError(v)


def done_keys(path):
    keys = set()
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line)
            keys.add((r["protocol"], r["held_out"], r["variant"], r["seed"]))
    return keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", default="V2,V0,V1,V3")
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--held", default=",".join(CITIES))
    ap.add_argument("--protocols", default="guarded,t7")
    ap.add_argument("--out", default=os.path.join(RES, "b1_runs.jsonl"))
    ap.add_argument("--epochs", type=int, default=150)
    a = ap.parse_args()
    lo, hi = (a.seeds.split("-") + [None])[:2]
    seeds = list(range(int(lo), int(hi) + 1)) if hi else [int(x) for x in a.seeds.split(",")]
    variants, helds, protocols = a.variants.split(","), a.held.split(","), a.protocols.split(",")

    device = S.pick_device()
    c = {**S.CFG, "epochs": a.epochs}
    t0 = time.time()
    d, target = load_combined()
    cid = d["Building"].city_id.numpy()
    valid = ~np.isnan(target)
    print(f"combined graph loaded in {time.time()-t0:.0f}s; Buildings={len(target)}", flush=True)
    chash, done = code_hash(), done_keys(a.out)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)

    # seed-major order: a partial run still gives complete (city x variant) blocks for early seeds
    for seed in seeds:
        for proto in protocols:
            for held in helds:
                i = d.cities.index(held)
                test, train = (cid == i) & valid, (cid != i) & valid
                for v in variants:
                    if (proto, held, v, seed) in done:
                        continue
                    if device.type == "cuda":
                        torch.cuda.reset_peak_memory_stats()
                    t1 = time.time()
                    pred = train_variant(v, d, target, torch.tensor(train), seed, DROP[proto], device, c)
                    if device.type == "cuda":
                        torch.cuda.synchronize()
                    m = T1.reg_metrics(target[test], pred[test])
                    rec = {"task": "T1_height_crosscity", "protocol": proto, "held_out": held,
                           "variant": v, "seed": seed, **m, "n_test": int(test.sum()),
                           "n_train": int(train.sum()), "runtime_s": round(time.time() - t1, 2),
                           "peak_vram_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)
                           if device.type == "cuda" else None,
                           "epochs": c["epochs"], "code": chash}
                    with open(a.out, "a") as f:
                        f.write(json.dumps(rec) + "\n")
                    print(f"[{time.strftime('%H:%M:%S')}] {proto:7s} {held:8s} {v} s{seed} "
                          f"R2={m['R2']:.4f} ({rec['runtime_s']:.0f}s, {rec['peak_vram_gb']} GB)", flush=True)
                    del pred
                    if device.type == "cuda":
                        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
