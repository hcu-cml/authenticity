"""T3 matching on the HARD n:m subset (Hamburg): can a learned encoder beat distance once the
negatives are distance-matched co-overlapping candidates?

Reuses t3_matching's encoder/training/leakage-guard verbatim and changes ONLY the evaluation:
  * Test buildings = those with >=2 ENRICHED_BY partners (co-overlapping OSM candidates).
  * Positive = the max-Jaccard partner (the "primary"); negatives = the other overlapping partners.
    These are distance-matched by construction, so raw proximity is uninformative (CPU check: distance
    AUC falls from ~0.99 on nearest-neighbor negatives to 0.74 here).
  * Leakage guard: ALL ENRICHED_BY edges of the test buildings are masked from the message-passing
    graph, so the encoder never sees their correspondences.
Metric: per building, is the primary ranked above its distractors (Hits@1) / mean rank-AUC -- the
SAME metric as the CPU distance check, so numbers are directly comparable to the 0.74 baseline.
Runs distance + attrsim (non-learned) and sage/aware encoders, each WITH and WITHOUT appended
position (the without-position arm probes non-geometric signal; note OSM still carries cx,cy).

October 2026: training now goes through t3_matching.train_encoder, so --protocol disjoint (default)
keeps the supervision edges out of the message-passing graph. The July version trained on edges that
were also in the graph (= --protocol legacy, kept only to reproduce the withdrawn numbers).
Usage: python t3_nm_matching.py [--protocol disjoint|legacy]   (run from the folder holding graph_hamburg.pt)
"""
import argparse
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import _setup_paths  # noqa: F401

import json
import numpy as np
import torch
from collections import defaultdict

from neo4j_loader import load_or_cache
import s5_train as S
import t3_matching as T3

EDGE = T3.EDGE
SEEDS = (0, 1, 2)
_ap = argparse.ArgumentParser()
_ap.add_argument("--protocol", default="disjoint", choices=("disjoint", "legacy"))
PROTOCOL = _ap.parse_args().protocol
OUT = f"t3_nm_matching_{PROTOCOL}.json"

data = load_or_cache("graph_hamburg.pt", verbose=False)
dev = S.pick_device()
cfg = dict(S.CFG)
pos = data[EDGE].edge_index.numpy()
w = data[EDGE].edge_weight.numpy().astype(float)
bpos, opos = data["Building"].pos.numpy(), data["OsmBuilding"].pos.numpy()
n_pos = pos.shape[1]

byb = defaultdict(list)
for col in range(n_pos):
    byb[int(pos[0, col])].append((col, int(pos[1, col]), float(w[col])))
nm = {b: cl for b, cl in byb.items() if len(cl) >= 2}
test_bs = list(nm.keys())

cand_of, mask_cols = {}, set()
for b in test_bs:
    cl = nm[b]
    k = int(np.argmax([x[2] for x in cl]))                 # primary = max jaccard
    cand_of[b] = [cl[k][1]] + [cl[i][1] for i in range(len(cl)) if i != k]   # primary first
    mask_cols |= {x[0] for x in cl}                        # mask ALL this building's edges
keep_cols = np.array([c for c in range(n_pos) if c not in mask_cols], dtype=np.int64)
allpairs = [(b, o) for b in test_bs for o in cand_of[b]]
true_of_b = {}
for b, o in pos.T:
    true_of_b.setdefault(int(b), set()).add(int(o))
print(f"device {dev} | n:m test buildings={len(test_bs)} | eval pairs={len(allpairs)} | "
      f"train edges kept={len(keep_cols)}/{n_pos}", flush=True)


def metrics(score_of):
    hits, aucs = [], []
    for b in test_bs:
        s = np.array([score_of[(b, o)] for o in cand_of[b]])   # index 0 is the primary
        order = np.argsort(-s); rank = int(np.where(order == 0)[0][0])
        hits.append(int(order[0] == 0)); aucs.append(1 - rank / (len(s) - 1))
    return {"Hits@1": float(np.mean(hits)), "meanAUC": float(np.mean(aucs))}


res = {"_meta": {"protocol": PROTOCOL, "n_test": len(test_bs), "chance_Hits@1":
                 float(np.mean([1 / len(cand_of[b]) for b in test_bs]))}}

# ---- non-learned baselines ----
res["distance"] = metrics({(b, o): -np.linalg.norm(bpos[b] - opos[o]) for (b, o) in allpairs})
hcol, lvcol = T3._feat_col(data, "Building", "height"), T3._feat_col(data, "OsmBuilding", "levels")
if hcol is not None and lvcol is not None:
    res["attrsim"] = metrics({(b, o): -abs(hcol[b] - lvcol[o]) for (b, o) in allpairs})
json.dump(res, open(OUT, "w"), indent=2)
print("non-learned:", {k: res[k] for k in ("distance", "attrsim") if k in res}, flush=True)


def run_learned(kind, use_pos):
    hh, aa = [], []
    for seed in SEEDS:
        S.set_seed(seed)
        saved = T3._shared_pos_norm
        if not use_pos:
            T3._shared_pos_norm = lambda d: {}                # drop appended shared-frame position
        try:
            # test buildings' edges are masked; training edges = keep_cols (split into message and
            # supervision edges under the disjoint protocol)
            embed = T3.train_encoder(data, keep_cols, kind, seed, 5, true_of_b, dev, cfg, protocol=PROTOCOL)
            with torch.no_grad():
                z = embed()
                sc = T3._score(z, torch.tensor(np.array(allpairs).T, device=dev)).cpu().numpy()
        finally:
            T3._shared_pos_norm = saved
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        m = metrics({p: sc[i] for i, p in enumerate(allpairs)})
        hh.append(m["Hits@1"]); aa.append(m["meanAUC"])
    return {"Hits@1": [float(np.mean(hh)), float(np.std(hh))],
            "meanAUC": [float(np.mean(aa)), float(np.std(aa))]}


for kind in ["sage", "aware"]:
    for use_pos in (True, False):
        tag = kind if use_pos else f"{kind}_nopos"
        try:
            res[tag] = run_learned(kind, use_pos)
        except Exception as e:
            print(f"{tag}: ERROR {type(e).__name__}: {e}", flush=True); res[tag] = None
        json.dump(res, open(OUT, "w"), indent=2)
        print(f"{tag}: {res[tag]}", flush=True)

print("DONE " + json.dumps({k: v for k, v in res.items() if k != "_meta"}), flush=True)
