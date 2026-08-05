"""Paired single-city significance tests (Hamburg): agnostic GraphSAGE vs aware (conf-weighted).

Bumps single-city seeds from 3 -> 10 and RETAINS per-seed metrics so we can run the rigorous
in-distribution NULL test the review asked for: paired t, Wilcoxon signed-rank, Cohen's d_z, and a
95% CI on the paired difference. Laptop-only (Hamburg fits 8 GB); the cross-city LOCO version
(NYC 1M / Tokyo 2M) needs the workstation -> crosscity_paired.py.

Each task compares, per seed, agnostic 'gnn' (GraphSAGE, use_prov=False) vs aware 'gnn_aware'
(use_prov=True). Pairing is valid because for a given seed s both methods use the SAME split
(splitter(data, s)) and the same seed, so the only thing that changes is the method.

  T1 height   : R^2, spatial 5-fold OOF, height dropped from inputs but storey KEPT (with-partner,
                as in Table 4). Target = z-scored 'height' feature; R^2 is invariant to an affine
                transform of a retrained target, so this reproduces the measured-height R^2 offline.
  T2 roof type: macro-F1, spatial 5-fold OOF (make_splits, merged 3-class path).
  T2 function : macro-F1, spatial 5-fold OOF (make_splits_function, top-8 + Other).
"""
import json, time
import numpy as np
import torch
from scipy import stats

from neo4j_loader import load_or_cache
import s5_train as S
import splits as SP
import t1_regression as T1

SEEDS = tuple(range(10))
OUT = "paired_singlecity.json"

g = load_or_cache("graph_hamburg.pt", verbose=False)
dev = S.pick_device()
c = dict(S.CFG)
print(f"device {dev} | Buildings {g['Building'].num_nodes} | seeds {list(SEEDS)}", flush=True)
res = {}


def clear():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def save():
    json.dump(res, open(OUT, "w"), indent=2)


def paired_stats(agn, aware):
    agn, aware = np.asarray(agn, float), np.asarray(aware, float)
    ok = np.isfinite(agn) & np.isfinite(aware)
    agn, aware = agn[ok], aware[ok]
    diff = aware - agn                                   # > 0  => aware better
    sd = diff.std(ddof=1) if len(diff) > 1 else 0.0
    dz = float(diff.mean() / sd) if sd > 0 else float("inf")
    try:
        tp = float(stats.ttest_rel(aware, agn).pvalue)
    except Exception:
        tp = float("nan")
    try:
        wp = float(stats.wilcoxon(aware, agn).pvalue)
    except Exception:
        wp = float("nan")
    tc = float(stats.t.ppf(0.975, len(diff) - 1)) if len(diff) > 1 else float("nan")
    se = sd / np.sqrt(len(diff)) if len(diff) > 0 else float("nan")
    return {
        "n": int(len(diff)),
        "agnostic_mean": float(agn.mean()), "agnostic_std": float(agn.std(ddof=1)),
        "aware_mean": float(aware.mean()), "aware_std": float(aware.std(ddof=1)),
        "delta_mean": float(diff.mean()),
        "ci95": [float(diff.mean() - tc * se), float(diff.mean() + tc * se)],
        "paired_t_p": tp, "wilcoxon_p": wp, "cohen_dz": dz,
        "per_seed_agnostic": agn.tolist(), "per_seed_aware": aware.tolist(),
    }


def run_task(name, fn):
    agn, aware = [], []
    t0 = time.time()
    for s in SEEDS:
        try:
            a, w = fn(s)
        except Exception as e:
            print(f"  {name} seed {s}: ERROR {type(e).__name__}: {e}", flush=True)
            a, w = float("nan"), float("nan")
        agn.append(a); aware.append(w); clear()
        print(f"  {name} seed {s}: agn={a:.4f} aware={w:.4f}  ({time.time()-t0:.0f}s)", flush=True)
    res[name] = paired_stats(agn, aware); save()
    r = res[name]
    print(f"== {name}: {r['agnostic_mean']:.3f} -> {r['aware_mean']:.3f}  "
          f"delta={r['delta_mean']:+.3f} CI{r['ci95']}  paired_t p={r['paired_t_p']:.4f} "
          f"wilcoxon p={r['wilcoxon_p']:.4f}  d_z={r['cohen_dz']:+.2f}", flush=True)


# ---- T1 height (regression, with-partner: drop height, keep storey) ----
fn = g["Building"].feat_names
target = g["Building"].x[:, fn.index("height")].numpy().astype(float)   # z-scored; R^2 affine-invariant


def _height(s):
    a = T1._eval(g, target, "gnn", s, "spatial_cv", ["height"], False, 5, dev, c)["R2"]
    w = T1._eval(g, target, "gnn_aware", s, "spatial_cv", ["height"], True, 5, dev, c)["R2"]
    return a, w


run_task("T1_height_R2", _height)

# ---- T2 roof type + T2 function (classification, macro-F1) ----
for nm, splitter in [("T2_rooftype_macroF1", SP.make_splits),
                     ("T2_function_macroF1", SP.make_splits_function)]:
    def _cls(s, splitter=splitter):
        a, _ = S._eval_one(g, "spatial_cv", "gnn", s, False, 5, c, dev, splitter)
        w, _ = S._eval_one(g, "spatial_cv", "gnn_aware", s, True, 5, c, dev, splitter)
        return a, w
    run_task(nm, _cls)

save()
print("DONE " + OUT, flush=True)
