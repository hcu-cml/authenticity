"""Cross-city (leave-one-city-out) PAIRED tests, T1 height R^2 -- with the confidence-weighting
ablation so the paper's mechanistic contrast becomes a TEST, not an observation.

Run on the WORKSTATION (needs Neo4j for load_target, and 96 GB to hold NYC 1M / Tokyo 2M in one
combined graph). Reproduces the Table 5 setup (combine_cities, drop=[], measured_height, LOCO) and,
per held-out city and per seed, runs four arms:
    gnn         : agnostic GraphSAGE (neither source-typed nor confidence-weighted)
    aware_noconf: aware architecture, source-typed, confidence weights OFF (CONFIDENCE_RELS emptied)
    gnn_aware   : full aware (source-typed AND confidence-weighted)  [= Table 5 'aware']
    rgcn        : source-typed, different architecture (the reference the review cites)
Then, per city, paired t / Wilcoxon / Cohen's d_z / 95% CI for the two decompositions:
    typing  = aware_noconf - gnn          (does source typing help under shift?)
    conf    = gnn_aware   - aware_noconf   (does confidence weighting help BEYOND typing?  <-- key)
plus an across-city summary. Prediction if the story holds: `conf` ~ 0 in-distribution (see
paired_ablation_singlecity.py) but > 0 here, i.e. a double dissociation.

Usage:
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python3 -W ignore crosscity_paired.py
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

CITIES = ["hamburg", "helsinki", "nyc", "tokyo", "zurich"]
SEEDS = tuple(range(10))
EPOCHS = 150
OUT = "crosscity_paired.json"


@contextlib.contextmanager
def conf_off():
    saved = set(S.CONFIDENCE_RELS)
    S.CONFIDENCE_RELS = set()
    try:
        yield
    finally:
        S.CONFIDENCE_RELS = saved


def paired(a, b):
    """b - a  (a=baseline, b=treatment): >0 means the treatment arm is better."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    diff = b - a
    sd = diff.std(ddof=1) if len(diff) > 1 else 0.0
    dz = float(diff.mean() / sd) if sd > 0 else float("inf")
    try:
        tp = float(stats.ttest_rel(b, a).pvalue)
    except Exception:
        tp = float("nan")
    try:
        wp = float(stats.wilcoxon(b, a).pvalue)
    except Exception:
        wp = float("nan")
    tc = float(stats.t.ppf(0.975, len(diff) - 1)) if len(diff) > 1 else float("nan")
    se = sd / np.sqrt(len(diff)) if len(diff) else float("nan")
    return {"n": int(len(diff)), "baseline_mean": float(a.mean()), "treatment_mean": float(b.mean()),
            "delta_mean": float(diff.mean()), "ci95": [float(diff.mean() - tc * se), float(diff.mean() + tc * se)],
            "paired_t_p": tp, "wilcoxon_p": wp, "cohen_dz": dz}


graphs = {c: load_or_cache(f"graph_{c}.pt", database=c, city=c, verbose=False) for c in CITIES}
targets = [T1.load_target("measured_height", database=c) for c in CITIES]
dev = S.pick_device()
cfg = {**S.CFG, "epochs": EPOCHS}
print(f"device {dev} | cities {CITIES} | seeds {list(SEEDS)}", flush=True)

d = S8.combine_cities([graphs[c] for c in CITIES])
target = np.concatenate([np.asarray(t) for t in targets])
cid = d["Building"].city_id.numpy()
valid = ~np.isnan(target)
res = {}


def r2(pred, test):
    return T1.reg_metrics(target[test], pred[test])["R2"]


for i, held in enumerate(d.cities):
    test = (cid == i) & valid
    train = (cid != i) & valid
    if test.sum() == 0 or train.sum() == 0:
        print(f"skip {held}", flush=True)
        continue
    tr = torch.tensor(train)
    arms = {"gnn": [], "aware_noconf": [], "gnn_aware": [], "rgcn": []}
    t0 = time.time()
    for s in SEEDS:
        arms["gnn"].append(r2(T1._train_reg(d, target, tr, s, "gnn", [], False, dev, cfg), test))
        with conf_off():
            arms["aware_noconf"].append(r2(T1._train_reg(d, target, tr, s, "gnn_aware", [], True, dev, cfg), test))
        arms["gnn_aware"].append(r2(T1._train_reg(d, target, tr, s, "gnn_aware", [], True, dev, cfg), test))
        arms["rgcn"].append(r2(T1._train_reg(d, target, tr, s, "rgcn", [], False, dev, cfg), test))
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print(f"  {held} seed {s}: gnn={arms['gnn'][-1]:.3f} noconf={arms['aware_noconf'][-1]:.3f} "
              f"aware={arms['gnn_aware'][-1]:.3f} rgcn={arms['rgcn'][-1]:.3f} ({time.time()-t0:.0f}s)", flush=True)
    res[held] = {"arms_mean": {a: float(np.nanmean(v)) for a, v in arms.items()},
                 "typing__noconf_minus_gnn": paired(arms["gnn"], arms["aware_noconf"]),
                 "conf__aware_minus_noconf": paired(arms["aware_noconf"], arms["gnn_aware"]),
                 "aware_minus_gnn": paired(arms["gnn"], arms["gnn_aware"]),
                 "per_seed": arms}
    json.dump(res, open(OUT, "w"), indent=2)
    cf = res[held]["conf__aware_minus_noconf"]
    print(f"== {held}: conf(aware-noconf) delta={cf['delta_mean']:+.3f} CI{cf['ci95']} "
          f"p={cf['paired_t_p']:.4f} dz={cf['cohen_dz']:+.2f}", flush=True)

# ---- across-city: is the confidence-weighting effect positive under shift? ----
confs = np.array([res[c]["conf__aware_minus_noconf"]["delta_mean"] for c in res if c in graphs])
n_pos = int((confs > 0).sum())
res["_across_city_conf"] = {
    "cities": [c for c in res if c in graphs], "conf_deltas": confs.tolist(),
    "n_positive": n_pos, "mean_delta": float(confs.mean()) if len(confs) else float("nan"),
    "sign_test_p": float(stats.binomtest(n_pos, len(confs), 0.5).pvalue) if len(confs) else float("nan"),
    "onesample_t_p_over_cities": float(stats.ttest_1samp(confs, 0.0).pvalue) if len(confs) > 1 else float("nan")}
json.dump(res, open(OUT, "w"), indent=2)
print(f"\nACROSS CITIES conf effect: {n_pos}/{len(confs)} positive, mean={confs.mean():+.3f}, "
      f"sign p={res['_across_city_conf']['sign_test_p']:.3f}", flush=True)
print("DONE " + OUT, flush=True)
