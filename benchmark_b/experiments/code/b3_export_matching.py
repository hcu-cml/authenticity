"""B3 prep -- score every Hamburg CityGML-OSM candidate pair so the M-set (manually verified
correspondence components) can be scored as soon as its labels arrive (score_b3.py).

Folds: the ENRICHED_BY bipartite graph is split into connected correspondence components (exactly the
1:1 / 1:n / n:1 / n:m units the M-set is stratified by); components are assigned to 5 folds at random
(seed 0). For fold k the learned encoders are trained exactly as in t3_matching.run_matching (train
positives = ENRICHED_BY edges of the other folds, k=5 hard negatives each, test edges removed from the
message-passing graph, dot-product decoder, BCE, 150 epochs) and then score the fold-k candidates:
  * every ENRICHED_BY edge of the fold-k components (is_edge=1), and
  * for each such edge, its building's 5 nearest non-matching OSM buildings (is_edge=0) -- the same
    hard negatives T3 uses, so pairs the overlap procedure did NOT link are also scored.
Scorers: spatial (negative centroid distance), attrsim (height vs. OSM levels), attr (no-graph learned),
sage (V0 agnostic GraphSAGE), aware (V1, Eq. 1). Writes results/b3_matching_scores.csv.gz.
--protocol disjoint (default, fixed) | legacy (paper protocol; graph encoders score below chance there,
see t3_matching.train_encoder). Output: results/b3_matching_scores_<protocol>.csv.gz.
"""
import os, sys, time

import numpy as np
import pandas as pd
import torch
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
BDIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BDIR)
import _setup_paths  # noqa: E402,F401  (adds shared/, t1_imputation/, ... to sys.path)
import s5_train as S        # noqa: E402
import t3_matching as T3    # noqa: E402

KINDS = ["attr", "sage", "aware"]
SEED, K_NEG, NFOLD = 0, 5, 5


def train_and_score(data, tr_cols, cand, kind, true_of_b, device, c, protocol):
    embed = T3.train_encoder(data, tr_cols, kind, SEED, K_NEG, true_of_b, device, c, protocol=protocol)
    with torch.no_grad():
        return T3._score(embed(), torch.tensor(cand, device=device)).cpu().numpy()


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", default="disjoint", choices=T3.PROTOCOLS)
    protocol = ap.parse_args().protocol
    device = S.pick_device()
    c = dict(S.CFG)
    data = torch.load(os.path.join(BDIR, "graph_hamburg.pt"), weights_only=False)
    tg = np.load(os.path.join(HERE, "..", "targets", "hamburg.npz"), allow_pickle=True)
    osm_id = np.load(os.path.join(HERE, "..", "targets", "hamburg_osm_ids.npz"), allow_pickle=True)["osm_id"]
    pos = data[T3.EDGE].edge_index.numpy()
    jac = data[T3.EDGE].edge_weight.numpy()
    nb, no = data["Building"].num_nodes, data["OsmBuilding"].num_nodes
    adj = coo_matrix((np.ones(pos.shape[1]), (pos[0], nb + pos[1])), shape=(nb + no, nb + no))
    _, comp_node = connected_components(adj, directed=False)
    comp = comp_node[pos[0]]
    ucomp = np.unique(comp)
    fold_of_comp = dict(zip(ucomp, np.random.default_rng(SEED).permutation(len(ucomp)) % NFOLD))
    efold = np.array([fold_of_comp[x] for x in comp])
    true_of_b = {}
    for b, o in pos.T:
        true_of_b.setdefault(int(b), set()).add(int(o))
    bpos, opos = data["Building"].pos.numpy(), data["OsmBuilding"].pos.numpy()

    frames = []
    for k in range(NFOLD):
        t0 = time.time()
        te_cols, tr_cols = np.where(efold == k)[0], np.where(efold != k)[0]
        te_pos = pos[:, te_cols]
        te_neg = T3._hard_negatives(bpos, opos, te_pos, K_NEG, SEED + 1, true_of_b)
        neg = np.unique(te_neg.T, axis=0).T                     # dedupe pairs
        cand = np.concatenate([te_pos, neg], 1)
        df = pd.DataFrame({"gml_id": tg["gml_id"][cand[0]], "osm_id": osm_id[cand[1]],
                           "b_idx": cand[0], "o_idx": cand[1],
                           "is_edge": np.r_[np.ones(te_pos.shape[1], int), np.zeros(neg.shape[1], int)],
                           "jaccard": np.r_[jac[te_cols], np.full(neg.shape[1], np.nan)],
                           "component": np.r_[comp[te_cols], np.full(neg.shape[1], -1)],
                           "building_osm_match_type": tg["osm_match_type"][cand[0]], "fold": k})
        for kind in ("spatial", "attrsim"):
            df[f"score_{kind}"] = T3._score_nonlearned(kind, data, cand)
        for kind in KINDS:
            df[f"score_{kind}"] = train_and_score(data, tr_cols, cand, kind, true_of_b, device, c, protocol)
        msg = " ".join(f"{s}={roc_auc_score(df.is_edge, df['score_' + s]):.3f}"
                       for s in ["spatial", "attrsim"] + KINDS)
        print(f"fold {k}: {len(te_cols)} edges + {neg.shape[1]} non-edges, AUC(edge vs non-edge) {msg} "
              f"({time.time()-t0:.0f}s)", flush=True)
        frames.append(df)
    out = os.path.join(HERE, "..", "results", f"b3_matching_scores_{protocol}.csv.gz")
    pd.concat(frames).to_csv(out, index=False)
    print("wrote", out)


if __name__ == "__main__":
    main()
