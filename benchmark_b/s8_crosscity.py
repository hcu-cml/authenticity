"""
S8 — cross-city transfer. Train on a set of cities, test on a held-out city (leave-one-city-out).

Architecture (see the DB note): each city is loaded from its OWN Neo4j database into its own
HeteroData, then combined at the TENSOR level into one disconnected union graph with a per-node city
tag. There are no cross-city edges, so message passing stays within a city; holding a city out is just
a mask. Standardization is per-city (each city z-scored by the loader) — this removes per-city scale
shift and is the honest default for domain transfer (§3 item 11).

Robust to heterogeneity across cities:
  * feature columns aligned by NAME (union; a city missing a feature contributes zeros for it);
  * label spaces merged (union of roof-type codes → one global class set);
  * node/edge types unioned (a city lacking a type contributes 0 nodes/edges of it).

Only inductive methods make sense here (a GNN can embed an unseen city); transductive shallow
embeddings (node2vec/metapath2vec) cannot and are excluded.
"""
import numpy as np
import torch
from torch_geometric.data import HeteroData
from sklearn.metrics import f1_score

import s5_train as S


def _union(seqs):
    out, seen = [], set()
    for seq in seqs:
        for x in seq:
            if x not in seen:
                seen.add(x); out.append(x)
    return out


def _align(x, names, union):
    idx = {nm: i for i, nm in enumerate(names)}
    A = torch.zeros((x.size(0), len(union)), dtype=torch.float)
    for j, nm in enumerate(union):
        if nm in idx:
            A[:, j] = x[:, idx[nm]]
    return A


def combine_cities(graphs):
    """Union of per-city HeteroData into one disconnected graph. Tags data['Building'].city_id."""
    d = HeteroData()
    cities = [g.city for g in graphs]
    node_types = _union([list(g.node_types) for g in graphs])
    edge_types = _union([[tuple(et) for et in g.edge_types] for g in graphs])

    starts = {}                       # node type -> {city -> start index in the combined tensor}
    for nt in node_types:
        union = _union([g[nt].feat_names for g in graphs if nt in g.node_types])
        xs, cur, per_city = [], 0, {}
        for g in graphs:
            per_city[g.city] = cur
            if nt in g.node_types:
                xs.append(_align(g[nt].x, g[nt].feat_names, union))
                cur += g[nt].num_nodes
        starts[nt] = per_city
        d[nt].x = torch.cat(xs, 0) if xs else torch.zeros((0, len(union)))
        d[nt].feat_names = union

    # Building extras: global label, prov features, pos, city tag.
    # Not every city carries the roof-type label (NYC/Tokyo/Zurich don't -- see PROGRESS.md S1
    # city survey); those graphs simply contribute an all-unlabeled (-1) column below.
    has_roof = [g for g in graphs if "label_codes" in g["Building"]]
    allcodes = sorted(set().union(*[set(g["Building"].label_codes) for g in has_roof])) if has_roof else []
    code2y = {c: i for i, c in enumerate(allcodes)}
    name_of = {}
    for g in has_roof:
        for c, nm in zip(g["Building"].label_codes, g["Building"].label_names):
            name_of.setdefault(c, nm)
    ys, cids, provs, poss = [], [], [], []
    prov_union = _union([g["Building"].prov_names for g in graphs if "prov_names" in g["Building"]])
    for i, g in enumerate(graphs):
        if "label_codes" in g["Building"]:
            lc, yv = g["Building"].label_codes, g["Building"].y.numpy()
            ys.append(np.array([-1 if v < 0 else code2y[lc[v]] for v in yv], dtype=np.int64))
        else:
            ys.append(np.full(g["Building"].num_nodes, -1, dtype=np.int64))
        cids.append(np.full(g["Building"].num_nodes, i, dtype=np.int64))
        if prov_union and "x_prov" in g["Building"]:
            provs.append(_align(g["Building"].x_prov, g["Building"].prov_names, prov_union))
        if "pos" in g["Building"]:
            poss.append(g["Building"].pos)
    d["Building"].y = torch.tensor(np.concatenate(ys), dtype=torch.long)
    d["Building"].city_id = torch.tensor(np.concatenate(cids), dtype=torch.long)
    d["Building"].label_codes = allcodes
    d["Building"].label_names = [name_of[c] for c in allcodes]
    if provs:
        d["Building"].x_prov = torch.cat(provs, 0); d["Building"].prov_names = prov_union
    if poss:
        d["Building"].pos = torch.cat(poss, 0)

    for et in edge_types:
        s_, r_, t_ = et
        eis, ews = [], []
        for g in graphs:
            if et in set(tuple(e) for e in g.edge_types):
                ei = g[et].edge_index.clone()
                ei[0] += starts[s_][g.city]; ei[1] += starts[t_][g.city]
                eis.append(ei)
                if "edge_weight" in g[et]:
                    ews.append(g[et].edge_weight)
        d[et].edge_index = torch.cat(eis, 1) if eis else torch.empty((2, 0), dtype=torch.long)
        if ews:
            d[et].edge_weight = torch.cat(ews)
    d.cities = cities
    return d


def crosscity_eval(graphs, methods=("gnn", "gnn_aware"), seeds=(0, 1, 2), epochs=150, device=None):
    """Leave-one-city-out macro-F1 on roof type, agnostic vs aware. Returns {held_city: {method: (m,s)}}."""
    device = device or S.pick_device()
    d = combine_cities(graphs)
    y = d["Building"].y
    ncl = int(y[y >= 0].max()) + 1
    cid = d["Building"].city_id.numpy()
    labeled = y.numpy() >= 0
    out = {}
    for i, held in enumerate(d.cities):
        test = (cid == i) & labeled
        train = (cid != i) & labeled
        if test.sum() == 0 or train.sum() == 0:
            continue
        te = test
        out[held] = {}
        for m in methods:
            fs = []
            for s in seeds:
                pred = S.METHODS[m](d, y, torch.tensor(train), ncl, s,
                                    use_prov=(m == "gnn_aware"), device=device, epochs=epochs)
                fs.append(f1_score(y.numpy()[te], pred.numpy()[te],
                                   labels=list(range(ncl)), average="macro", zero_division=0))
            out[held][m] = (float(np.mean(fs)), float(np.std(fs)))
    return out, ncl


def crosscity_eval_regression(graphs, targets, methods=("probe", "gnn", "gnn_aware"),
                              seeds=(0, 1, 2), epochs=150, device=None):
    """Leave-one-city-out regression (height), agnostic vs aware -- same idea as `crosscity_eval`
    but for a continuous target, reusing t1_regression's training/metric code.

    `targets` are the raw per-Building target arrays from `t1_regression.load_target`, one per
    city, in the SAME order as `graphs` (combine_cities lays out each city's Buildings contiguously
    in that order, so concatenating the targets the same way keeps everything aligned)."""
    import t1_regression as T1
    device = device or S.pick_device()
    d = combine_cities(graphs)
    target = np.concatenate([np.asarray(t) for t in targets])
    cid = d["Building"].city_id.numpy()
    valid = ~np.isnan(target)
    c = {**S.CFG, "epochs": epochs}
    out = {}
    for i, held in enumerate(d.cities):
        test = (cid == i) & valid
        train = (cid != i) & valid
        if test.sum() == 0 or train.sum() == 0:
            continue
        out[held] = {}
        for m in methods:
            metrics = [T1.reg_metrics(target[test], T1._train_reg(
                d, target, torch.tensor(train), s, m, drop=[], use_prov=(m == "gnn_aware"),
                device=device, c=c)[test]) for s in seeds]
            out[held][m] = {k: (float(np.mean([r[k] for r in metrics])),
                                float(np.std([r[k] for r in metrics]))) for k in metrics[0]}
    return out


def print_crosscity_regression(res):
    print("\n=== S8 cross-city transfer (leave-one-city-out, height regression) ===")
    for city, methods in res.items():
        print(f"  held-out: {city}")
        for m, metrics in methods.items():
            print(f"    {m:10s} " + "  ".join(f"{k}={v[0]:.3f}±{v[1]:.3f}" for k, v in metrics.items()))


def print_crosscity(res, ncl):
    print(f"\n=== S8 cross-city transfer (leave-one-city-out, roof type, {ncl} classes) ===")
    print(f"  {'held-out city':16s} {'agnostic':>16s} {'prov-aware':>16s} {'Δ':>8s}")
    for city, m in res.items():
        a = m.get("gnn", (float('nan'), 0)); w = m.get("gnn_aware", (float('nan'), 0))
        print(f"  {city:16s} {a[0]:6.3f}±{a[1]:5.3f}   {w[0]:6.3f}±{w[1]:5.3f}   {w[0]-a[0]:+.3f}")


if __name__ == "__main__":
    # Mechanics check: simulate 3 "cities" from the Hamburg cache (one with a feature dropped) and
    # confirm combine + leave-one-city-out runs. Real transfer needs the real per-city databases
    # (see run_full_experiments.py for the actual 5-city run).
    import copy
    from neo4j_loader import load_or_cache
    base = load_or_cache("graph_hamburg.pt", database="hamburg", city="hamburg")
    gA = copy.deepcopy(base); gA.city = "cityA"
    gB = copy.deepcopy(base); gB.city = "cityB"
    gC = copy.deepcopy(base); gC.city = "cityC"
    # drop one Building feature from cityC to exercise name-based alignment
    keep = [j for j, nm in enumerate(gC["Building"].feat_names) if nm != "ground_z"]
    gC["Building"].x = gC["Building"].x[:, keep]
    gC["Building"].feat_names = [gC["Building"].feat_names[j] for j in keep]
    d = combine_cities([gA, gB, gC])
    print("combined:", {nt: d[nt].num_nodes for nt in d.node_types},
          "| Building feat_dim", d["Building"].x.size(1), "| cities", d.cities)
    res, ncl = crosscity_eval([gA, gB, gC], seeds=(0, 1), epochs=60)
    print_crosscity(res, ncl)
