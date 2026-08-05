"""
T3 / S7 — cross-source matching (entity resolution): does a CityGML Building correspond to an OSM
building? The positives are the ENRICHED_BY edges; we predict them from embeddings.

RIGOUR:
  * HARD negatives (§3 item 10): for each true (building, osm) pair, the negatives are the spatially
    NEAREST *other* OSM buildings — confusable, not trivially far away. Easy negatives measure nothing.
  * LEAKAGE guard: the TEST positive ENRICHED_BY edges (and their reverses) are REMOVED from the
    message-passing graph, so the encoder can't pass information along the very links it must predict.
  * Metrics: ROC-AUC, Average Precision, Hits@1 (is the true match ranked above all its hard negatives?).
  * Encoders compared: attribute-only (no graph), agnostic GraphSAGE, provenance-AWARE (Eq.1). Decoder
    is a dot product  score(a,b)=z_a·z_b, trained with binary cross-entropy.
  * Non-learned baselines (NONLEARNED_KINDS): "spatial" (closer footprints score higher) and
    "attrsim" (height vs. OSM levels similarity) -- no encoder, no training, same split/negatives.

Note the reflexive subtlety: here the provenance layer *is* the matching target, so the aware arm's
confidence weighting acts only on the TRAIN correspondence edges (test ones are held out) plus has_poi.
"""
import numpy as np
import torch
import torch.nn.functional as F
from scipy.spatial import cKDTree
from torch_geometric.nn import to_hetero, Linear
from sklearn.metrics import roc_auc_score, average_precision_score

import s5_train as S

EDGE = ("Building", "enriched_by", "OsmBuilding")
REV = ("OsmBuilding", "rev_enriched_by", "Building")


class AttrEncoder(torch.nn.Module):
    """No-graph baseline: per-type linear projection of node features to a shared space."""
    def __init__(self, hidden, node_types):
        super().__init__()
        self.proj = torch.nn.ModuleDict({nt: Linear(-1, hidden) for nt in node_types})

    def forward(self, xd, ed=None, ewd=None):
        return {nt: self.proj[nt](x) for nt, x in xd.items()}


def _mask_test_edges(data, keep_cols):
    """Clone the graph keeping only `keep_cols` of the ENRICHED_BY edges (train positives)."""
    d = data.clone()
    ei = data[EDGE].edge_index[:, keep_cols]
    ew = data[EDGE].edge_weight[keep_cols]
    d[EDGE].edge_index, d[EDGE].edge_weight = ei, ew
    d[REV].edge_index, d[REV].edge_weight = ei.flip(0), ew
    return d


def _hard_negatives(bpos, opos, pairs, k, seed, true_of_b):
    """k nearest non-matching OSM buildings per positive (aligned: k negs per positive, in order).

    Uses a k-d tree instead of a brute-force distance to every OSM building: at city scale (up to
    ~1M+ correspondences x ~1M+ OSM buildings) the naive O(n_pos * n_osm) pairwise distance is
    infeasible, while a tree query is O(n_pos log n_osm). Query a few extra neighbours beyond `k`
    since the true match itself is usually among the nearest and must be filtered out; widen the
    search only in the rare case that still isn't enough.
    """
    tree = cKDTree(opos)
    b_idx = pairs[0]
    query_k = min(k + 8, len(opos))
    _, nbrs = tree.query(bpos[b_idx], k=query_k)
    nbrs = np.atleast_2d(nbrs) if query_k > 1 else nbrs.reshape(-1, 1)
    negs = []
    for col, b in enumerate(b_idx.tolist()):
        cand = [j for j in nbrs[col].tolist() if j not in true_of_b[b]][:k]
        if len(cand) < k:                        # rare: too many of the nearest were true matches
            _, wide = tree.query(bpos[b], k=min(k + len(true_of_b[b]) + k, len(opos)))
            cand = [j for j in np.atleast_1d(wide).tolist() if j not in true_of_b[b]][:k]
        while len(cand) < k:                     # pad if too few OSM buildings exist at all
            cand.append(cand[-1] if cand else 0)
        negs += [(b, j) for j in cand]
    return np.array(negs, dtype=np.int64).T      # [2, n_pos*k], grouped k-per-positive


def _shared_pos_norm(data):
    """Normalize all node positions with ONE shared mean/std so Building & OsmBuilding coords stay in
    the same frame (essential: matching aligns locations across sources)."""
    allp = torch.cat([data[nt].pos for nt in data.node_types if "pos" in data[nt]], 0)
    mu, sd = allp.mean(0), allp.std(0) + 1e-6
    return {nt: (data[nt].pos - mu) / sd for nt in data.node_types if "pos" in data[nt]}


def _embed_fn(kind, data_m, device, c):
    """Return (model, embed()) where embed() -> {node_type: emb}. data_m is the masked graph.
    Position (shared frame) is appended to features so the decoder can align locations across sources."""
    use_prov = (kind == "aware")
    posn = _shared_pos_norm(data_m)
    xd = {}
    for nt in data_m.node_types:
        x = S.building_features(data_m, use_prov) if nt == "Building" else data_m[nt].x
        if nt in posn:
            x = torch.cat([x, posn[nt]], dim=1)
        xd[nt] = x.to(device)
    ed = {et: data_m[et].edge_index.to(device) for et in data_m.edge_types}
    meta = data_m.metadata()
    if kind == "attr":
        model = AttrEncoder(c["hidden"], meta[0]).to(device)
        return model, (lambda: model(xd, ed))
    if kind == "aware":
        ewd = S._norm_edge_weight_dict(data_m, device)
        model = to_hetero(S.ProvGNN(c["hidden"], c["hidden"], c["dropout"]), meta, aggr="sum").to(device)
        return model, (lambda: model(xd, ed, ewd))
    conv = "gat" if kind == "gat" else "sage"
    model = to_hetero(S.HeteroGNN(c["hidden"], c["hidden"], conv, c["heads"], c["dropout"]),
                      meta, aggr="sum").to(device)
    return model, (lambda: model(xd, ed))


def _score(z, ei):
    return (z["Building"][ei[0]] * z["OsmBuilding"][ei[1]]).sum(-1)


# Non-learned baselines: no encoder, no training loop, just a hand-written score per pair. These
# only need the raw split (which pairs are test positives/negatives); they never see train data.
NONLEARNED_KINDS = {"spatial", "attrsim"}


def _feat_col(data, node_type, name):
    """One named column of a node type's (already z-scored) feature matrix, or None if this city's
    schema doesn't have it (see neo4j_loader -- absent properties are dropped, not filled in)."""
    names = data[node_type].feat_names
    return data[node_type].x[:, names.index(name)].numpy() if name in names else None


def _score_nonlearned(kind, data, pairs):
    b, o = pairs
    if kind == "spatial":
        # Closer footprints score higher -- the non-learned analogue of the k-d tree used to mine
        # hard negatives, i.e. "does raw proximity alone already solve matching?"
        bpos, opos = data["Building"].pos.numpy(), data["OsmBuilding"].pos.numpy()
        return -np.linalg.norm(bpos[b] - opos[o], axis=1)
    if kind == "attrsim":
        # A taller building should be reported with more OSM storeys/levels -- score by how close
        # their (z-scored) values are. Falls back to an uninformative tie (all-zero score) where
        # either side of the pairing is absent for this city.
        h, lv = _feat_col(data, "Building", "height"), _feat_col(data, "OsmBuilding", "levels")
        if h is None or lv is None:
            return np.zeros(len(b))
        return -np.abs(h[b] - lv[o])
    raise ValueError(f"unknown non-learned kind {kind}")


def run_matching(data, kind="sage", seeds=(0, 1, 2, 3, 4), test_frac=0.3, k_neg=5, device=None,
                 return_scores=False, return_embeddings=False, **cfg):
    c = {**S.CFG, **cfg}
    device = device or S.pick_device()
    pos = data[EDGE].edge_index.numpy()                       # [2, n_pos]  (building, osm)
    n_pos = pos.shape[1]
    bpos, opos = data["Building"].pos.numpy(), data["OsmBuilding"].pos.numpy()
    true_of_b = {}
    for b, o in pos.T:
        true_of_b.setdefault(int(b), set()).add(int(o))

    aucs, aps, hits, curves = [], [], [], []
    for seed in seeds:
        S.set_seed(seed)
        rng = np.random.default_rng(seed)
        perm = rng.permutation(n_pos)
        n_te = max(1, int(round(test_frac * n_pos)))
        te_cols, tr_cols = perm[:n_te], perm[n_te:]

        te_pos = pos[:, te_cols]
        te_neg = _hard_negatives(bpos, opos, te_pos, k_neg, seed + 1, true_of_b)

        if kind in NONLEARNED_KINDS:
            sp = _score_nonlearned(kind, data, te_pos)
            sn = _score_nonlearned(kind, data, te_neg)
        else:
            data_m = _mask_test_edges(data, tr_cols)         # leakage guard
            tr_pos = pos[:, tr_cols]
            tr_neg = _hard_negatives(bpos, opos, tr_pos, k_neg, seed, true_of_b)

            model, embed = _embed_fn(kind, data_m, device, c)
            tp = torch.tensor(tr_pos, device=device); tn = torch.tensor(tr_neg, device=device)
            with torch.no_grad():
                embed()                                      # lazy init
            opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
            for _ in range(c["epochs"]):
                model.train(); opt.zero_grad()
                z = embed()
                logit = torch.cat([_score(z, tp), _score(z, tn)])
                label = torch.cat([torch.ones(tp.size(1), device=device),
                                   torch.zeros(tn.size(1), device=device)])
                F.binary_cross_entropy_with_logits(logit, label).backward(); opt.step()

            model.eval()
            with torch.no_grad():
                z = embed()
                sp = _score(z, torch.tensor(te_pos, device=device)).cpu().numpy()
                sn = _score(z, torch.tensor(te_neg, device=device)).cpu().numpy()
            if return_embeddings and seed == seeds[-1]:
                final_embeddings = {nt: t.detach().cpu().numpy() for nt, t in z.items()}

        y = np.r_[np.ones(len(sp)), np.zeros(len(sn))]
        s = np.r_[sp, sn]
        aucs.append(roc_auc_score(y, s)); aps.append(average_precision_score(y, s))
        if return_scores:
            curves.append((y, s))
        # Hits@1: per test positive, its score vs the max over its k hard negatives
        sn_grp = sn.reshape(len(sp), k_neg)
        hits.append(float(np.mean(sp > sn_grp.max(axis=1))))

    def ms(a):
        return float(np.mean(a)), float(np.std(a))
    out = {"AUC": ms(aucs), "AP": ms(aps), "Hits@1": ms(hits), "n_pos": n_pos, "n_test": n_te}
    if return_scores:
        out["curves"] = curves      # [(y_true, score), ...] one pair per seed, for PR curves
    if return_embeddings:
        out["embeddings"] = final_embeddings   # {'Building': [...], 'OsmBuilding': [...]}, last seed
    return out


def print_matching(res_by_kind):
    print(f"\n=== T3 matching (ENRICHED_BY, hard negatives)  n_pos={list(res_by_kind.values())[0]['n_pos']} ===")
    print(f"  {'encoder':16s} {'ROC-AUC':>14s} {'AP':>14s} {'Hits@1':>14s}")
    for kind, r in res_by_kind.items():
        print(f"  {kind:16s} {r['AUC'][0]:6.3f}±{r['AUC'][1]:5.3f} "
              f"{r['AP'][0]:6.3f}±{r['AP'][1]:5.3f} {r['Hits@1'][0]:6.3f}±{r['Hits@1'][1]:5.3f}")


if __name__ == "__main__":
    from neo4j_loader import load_from_neo4j
    data = load_from_neo4j(database="hamburg", city="hamburg", verbose=False)
    res = {}
    for kind in ("spatial", "attrsim", "attr", "sage", "aware"):
        res[kind] = run_matching(data, kind=kind, seeds=(0, 1, 2), epochs=120, k_neg=5)
    print_matching(res)
