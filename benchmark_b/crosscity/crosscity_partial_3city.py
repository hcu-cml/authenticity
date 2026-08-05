"""3-city LAPTOP partial of the cross-city confidence-weighting ablation (Hamburg/Helsinki/Zurich).

The full 5-city version (crosscity_paired.py) needs the workstation (NYC 1M + Tokyo 2M won't fit in
8 GB, and NYC has no height feature). This runs the SAME ablation on the three cities that fit and
have a height feature, for a DIRECTIONAL cross-city Delta_conf before the deadline.

CAVEATS: (a) drops the two strongest-shift cities (NYC, Tokyo); (b) offline target is the z-scored
height FEATURE per city (no Neo4j), with height dropped from inputs -- so absolute R^2 is NOT
comparable to Table 5, only Delta_conf is. Per held-out city, paired over seeds:
  gnn (agnostic) -> aware_noconf (source-typed, confidence OFF) -> gnn_aware (full)
  conf   = full - noconf   (confidence-weighting effect under shift -- the key number)
  typing = noconf - gnn
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import _setup_paths  # noqa: F401

import json, time, contextlib
import numpy as np
import torch
from scipy import stats

from neo4j_loader import load_or_cache
import s5_train as S
import s8_crosscity as S8
import t1_regression as T1

CITIES = ["hamburg", "helsinki", "zurich"]
SEEDS = tuple(range(10))
EPOCHS = 150
OUT = "crosscity_partial_3city.json"


@contextlib.contextmanager
def conf_off():
    saved = set(S.CONFIDENCE_RELS)
    S.CONFIDENCE_RELS = set()
    try:
        yield
    finally:
        S.CONFIDENCE_RELS = saved


def paired(a, b):                                    # returns stats on (b - a)
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b); a, b = a[ok], b[ok]
    diff = b - a
    sd = diff.std(ddof=1) if len(diff) > 1 else 0.0
    dz = float(diff.mean() / sd) if sd > 0 else float("inf")
    try:
        tp = float(stats.ttest_rel(b, a).pvalue)
    except Exception:
        tp = float("nan")
    tc = float(stats.t.ppf(0.975, len(diff) - 1)) if len(diff) > 1 else float("nan")
    se = sd / np.sqrt(len(diff)) if len(diff) else float("nan")
    return {"n": int(len(diff)), "baseline_mean": float(a.mean()), "treatment_mean": float(b.mean()),
            "delta_mean": float(diff.mean()), "ci95": [float(diff.mean() - tc * se), float(diff.mean() + tc * se)],
            "paired_t_p": tp, "cohen_dz": dz}


graphs = {}
targets = []
for c in CITIES:
    g = load_or_cache(f"graph_{c}.pt", verbose=False)
    g.city = c                                       # safeguard: combine_cities reads g.city
    graphs[c] = g
    fn = g["Building"].feat_names
    targets.append(g["Building"].x[:, fn.index("height")].numpy().astype(float))   # z-scored height

dev = S.pick_device()
cfg = {**S.CFG, "epochs": EPOCHS}
d = S8.combine_cities([graphs[c] for c in CITIES])
target = np.concatenate(targets)
cid = d["Building"].city_id.numpy()
valid = ~np.isnan(target)
print(f"device {dev} | combined Buildings={d['Building'].num_nodes} | cities={list(d.cities)}", flush=True)
res = {}

for i, held in enumerate(d.cities):
    test = (cid == i) & valid
    train = (cid != i) & valid
    if test.sum() == 0 or train.sum() == 0:
        print(f"skip {held}", flush=True); continue
    tr = torch.tensor(train)
    arms = {"gnn": [], "aware_noconf": [], "gnn_aware": []}
    t0 = time.time()
    for s in SEEDS:
        arms["gnn"].append(T1.reg_metrics(target[test],
            T1._train_reg(d, target, tr, s, "gnn", ["height"], False, dev, cfg)[test])["R2"])
        with conf_off():
            arms["aware_noconf"].append(T1.reg_metrics(target[test],
                T1._train_reg(d, target, tr, s, "gnn_aware", ["height"], True, dev, cfg)[test])["R2"])
        arms["gnn_aware"].append(T1.reg_metrics(target[test],
            T1._train_reg(d, target, tr, s, "gnn_aware", ["height"], True, dev, cfg)[test])["R2"])
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print(f"  {held} seed {s}: gnn={arms['gnn'][-1]:.3f} noconf={arms['aware_noconf'][-1]:.3f} "
              f"aware={arms['gnn_aware'][-1]:.3f} ({time.time()-t0:.0f}s)", flush=True)
    res[held] = {"arms_mean": {a: float(np.mean(v)) for a, v in arms.items()},
                 "conf__aware_minus_noconf": paired(arms["aware_noconf"], arms["gnn_aware"]),
                 "typing__noconf_minus_gnn": paired(arms["gnn"], arms["aware_noconf"]),
                 "per_seed": arms}
    json.dump(res, open(OUT, "w"), indent=2)
    cf = res[held]["conf__aware_minus_noconf"]
    print(f"== {held}: conf(full-noconf) delta={cf['delta_mean']:+.3f} CI{cf['ci95']} "
          f"p={cf['paired_t_p']:.3f} dz={cf['cohen_dz']:+.2f}", flush=True)

confs = np.array([res[c]["conf__aware_minus_noconf"]["delta_mean"] for c in res if c in graphs])
res["_across"] = {"cities": [c for c in res if c in graphs], "conf_deltas": confs.tolist(),
                  "n_positive": int((confs > 0).sum()), "mean_delta": float(confs.mean()) if len(confs) else float("nan")}
json.dump(res, open(OUT, "w"), indent=2)
print(f"\nACROSS 3 CITIES conf: {int((confs>0).sum())}/{len(confs)} positive, mean={confs.mean():+.3f}", flush=True)
print("DONE " + OUT, flush=True)
