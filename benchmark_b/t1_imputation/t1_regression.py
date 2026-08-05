"""
T1 — attribute regression (height, storeys) on Building.

Same rigour as T2: random (deceptive) + spatial K-fold CV (honest, pooled out-of-fold), mean±std over
seeds, all methods, agnostic vs aware. Metrics: MAE, RMSE, R^2 in ORIGINAL units.

LEAKAGE GUARD (§1 pt 3): the target attribute is removed from the Building feature matrix
(`building_features(..., drop=[target])`) — otherwise the model just reads the answer.
Note: height and storeys are physically correlated (height ≈ 3·storeys); predicting one with the other
present is legitimate (both are ground-truth attributes, neither derived from the other) but easy — the
`also_drop` knob lets you remove the correlated partner to make the graph earn its keep.

Coverage (S2, pilot): measured_height 81/81 (clean); storeys_above_ground 58/81 (0 = missing, masked).

CROSS-CITY HEIGHT (S1 city survey): NYC and Zurich carry no `measured_height` property on `Building`
at all (their LoD2 source has geometry but no authoritative height attribute). Height is instead
derived there as the bounding-box z-extent (`bbox_max_z - bbox_min_z`) of the building solid, which
every city's geometry provides. This is a per-city fallback in `load_target`, never a model input,
so it cannot leak into the graph features.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import _setup_paths  # noqa: F401

import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.nn import to_hetero

from splits import spatial_kfold, random_split
import s5_train as S

# target -> (property, also_drop-from-features). also_drop removes the correlated partner if desired.
TARGETS = {
    "height":  ("measured_height",      ["height"]),
    "storeys": ("storeys_above_ground", ["storeys"]),
}
REG_METHODS = ("mean", "probe", "gnn", "gat", "hgt", "han", "rgcn", "gnn_aware")


def _to_float(x, default=np.nan):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def load_target(prop, database=None):
    """Raw target per Building, ordered by elementId → aligned with the loader's node index.
    `database` selects a named city database (see neo4j_loader.load_from_neo4j)."""
    from neo4j import GraphDatabase
    drv = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                               auth=(os.environ.get("NEO4J_USER", "neo4j"), os.environ["NEO4J_PASSWORD"]))
    with drv.session(database=database) if database else drv.session() as s:
        rows = s.run(f"MATCH (b:Building) RETURN elementId(b) AS eid, b.`{prop}` AS v, "
                     f"b.bbox_min_z AS zmin, b.bbox_max_z AS zmax ORDER BY eid").data()
    drv.close()
    t = np.array([_to_float(r["v"]) for r in rows], dtype=np.float64)
    # 9999 / -9999 is a common GIS "no data" sentinel -- Tokyo uses it for both height and storeys
    # (storeys_above_ground=9999 for ~11% of buildings; measured_height=-9999 for ~1%). Left as-is,
    # these values are large enough to dominate any z-scored regression, silently wrecking every
    # city's training signal once cities are combined (see PROGRESS.md T1 cross-city note).
    t[np.abs(t) >= 9999] = np.nan
    if prop == "storeys_above_ground":
        t[t <= 0] = np.nan                 # 0 encodes missing (S2)
    if prop == "measured_height":
        # some cities (NYC, Zurich) have no authoritative height attribute at all -- fall back to
        # the LoD2 solid's bounding-box z-extent, which every city's geometry provides.
        missing = np.isnan(t)
        if missing.any():
            zmin = np.array([_to_float(r["zmin"]) for r in rows], dtype=np.float64)
            zmax = np.array([_to_float(r["zmax"]) for r in rows], dtype=np.float64)
            t[missing] = (zmax - zmin)[missing]
        t[t <= 0] = np.nan                 # guard against degenerate bbox-derived heights too
    return t


def reg_metrics(y_true, y_pred):
    err = y_pred - y_true
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    ss_res = float(np.sum(err ** 2))
    ss_tot = float(np.sum((y_true - y_true.mean()) ** 2)) + 1e-12
    return {"MAE": mae, "RMSE": rmse, "R2": 1.0 - ss_res / ss_tot}


def _train_reg(data, target, train_mask, seed, method, drop, use_prov, device, c):
    S.set_seed(seed)
    tm = train_mask.cpu().numpy()
    if method == "mean":
        return np.full(len(target), float(np.nanmean(target[tm])))     # baseline: predict train mean
    if method == "probe":
        from sklearn.linear_model import Ridge
        X = S.building_features(data, use_prov, drop=drop).cpu().numpy()
        return Ridge(alpha=1.0).fit(X[tm], target[tm]).predict(X)

    # GNN regressors (out=1, MSE on standardized target; predictions inverted to raw units)
    mu, sd = target[tm].mean(), target[tm].std() + 1e-6
    yb = torch.tensor((target - mu) / sd, dtype=torch.float)
    xd = {nt: data[nt].x.to(device) for nt in data.node_types}
    xd["Building"] = S.building_features(data, use_prov, drop=drop).to(device)
    ed = {et: data[et].edge_index.to(device) for et in data.edge_types}
    if method == "hgt":
        model = S.HGT(c["hidden"], 1, c["heads"], c["layers"], data.metadata()).to(device)
        fwd = lambda: model(xd, ed).squeeze(-1)
    elif method == "han":
        model = S.HAN(c["hidden"], 1, c["heads"], data.metadata(), c["dropout"]).to(device)
        fwd = lambda: model(xd, ed).squeeze(-1)
    elif method == "rgcn":
        order = list(data.node_types)
        hom_ei, edge_type, offset, _ = S._homogeneous_edge_index_typed(data)
        hom_ei, edge_type = hom_ei.to(device), edge_type.to(device)
        b0, nb = offset["Building"], data["Building"].num_nodes
        model = S.RGCN(c["hidden"], 1, len(data.edge_types), order, c["dropout"]).to(device)
        fwd = lambda: model(xd, order, hom_ei, edge_type)[b0:b0 + nb].squeeze(-1)
    elif method == "gnn_aware":
        ewd = S._norm_edge_weight_dict(data, device)
        model = to_hetero(S.ProvGNN(c["hidden"], 1, c["dropout"]), data.metadata(), aggr="sum").to(device)
        fwd = lambda: model(xd, ed, ewd)["Building"].squeeze(-1)
    else:
        conv = "gat" if method == "gat" else "sage"
        model = to_hetero(S.HeteroGNN(c["hidden"], 1, conv, c["heads"], c["dropout"]),
                          data.metadata(), aggr="sum").to(device)
        fwd = lambda: model(xd, ed)["Building"].squeeze(-1)
    with torch.no_grad():
        fwd()
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    ybd, tr = yb.to(device), train_mask.to(device)
    for _ in range(c["epochs"]):
        model.train(); opt.zero_grad()
        F.mse_loss(fwd()[tr], ybd[tr]).backward(); opt.step()
    model.eval()
    with torch.no_grad():
        pred_std = fwd().cpu().numpy()
    return pred_std * sd + mu


def _eval(data, target, method, seed, split, drop, use_prov, k, device, c):
    valid = ~np.isnan(target)
    if split == "random":
        tr, _, te = random_split(len(target), seed, labeled=valid)
        pred = _train_reg(data, target, tr, seed, method, drop, use_prov, device, c)
        m = te.numpy()
        return reg_metrics(target[m], pred[m])
    folds, _ = spatial_kfold(data["Building"].pos.numpy(), seed, k=k, labeled=valid)
    oof = np.full(len(target), np.nan)
    for tr, te in folds:
        pred = _train_reg(data, target, tr, seed, method, drop, use_prov, device, c)
        m = te.numpy(); oof[m] = pred[m]
    m = ~np.isnan(oof)
    return reg_metrics(target[m], oof[m])


def run_regression(data, target_name, methods=REG_METHODS, seeds=(0, 1, 2, 3, 4),
                   splits=("random", "spatial_cv"), also_drop=(), k=5, device=None,
                   database=None, **cfg):
    c = {**S.CFG, **cfg}
    device = device or S.pick_device()
    prop, drop = TARGETS[target_name]
    drop = list(drop) + list(also_drop)
    target = load_target(prop, database=database)
    out = {}
    for method in methods:
        use_prov = (method == "gnn_aware")
        out[method] = {}
        for split in splits:
            ms = [_eval(data, target, method, s, split, drop, use_prov, k, device, c) for s in seeds]
            out[method][split] = {k2: (float(np.mean([m[k2] for m in ms])),
                                       float(np.std([m[k2] for m in ms]))) for k2 in ms[0]}
    return out, int((~np.isnan(target)).sum())


def print_regression(target_name, res, n):
    print(f"\n=== T1 regression: {target_name}  (n={n} labeled) ===")
    print(f"  {'method':12s} {'split':11s} {'MAE':>14s} {'RMSE':>14s} {'R2':>12s}")
    for method, splits in res.items():
        for split, m in splits.items():
            print(f"  {method:12s} {split:11s} "
                  f"{m['MAE'][0]:7.3f}±{m['MAE'][1]:5.3f} {m['RMSE'][0]:7.3f}±{m['RMSE'][1]:5.3f} "
                  f"{m['R2'][0]:6.3f}±{m['R2'][1]:5.3f}")


if __name__ == "__main__":
    from neo4j_loader import load_from_neo4j
    data = load_from_neo4j(database="hamburg", city="hamburg", verbose=False)
    for tgt in ("height", "storeys"):
        res, n = run_regression(data, tgt, seeds=(0, 1, 2), epochs=120, database="hamburg")
        print_regression(tgt, res, n)
