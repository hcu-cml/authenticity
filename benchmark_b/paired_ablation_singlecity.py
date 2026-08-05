"""Confidence-weighting ISOLATION ablation (Hamburg, in-distribution), paired over 10 seeds.

Turns the reviewer's contrast into a clean test: does confidence weighting add anything BEYOND source
typing? We compare the aware encoder with confidence weights ON vs OFF, holding architecture AND
source typing fixed. OFF = the SAME ProvGNN + to_hetero encoder but with CONFIDENCE_RELS emptied, so
the enriched_by correspondence edges aggregate with uniform (1/degree) weight instead of the jaccard
confidence -> source-typed but unweighted. R-GCN is a second, different-architecture source-typed
reference (the one the review cites).

  Delta_conf = aware_full - aware_noconf   isolates confidence weighting (same arch, same typing).
Prediction if the paper's story holds: Delta_conf ~ 0 here (in-distribution) and > 0 cross-city
(crosscity_paired.py). Pair the resulting aware_noconf against the agnostic column already produced
by paired_singlecity.py (same seeds -> same splits) to read off the source-typing effect too.
"""
import json, time, contextlib
import numpy as np
import torch
from scipy import stats

from neo4j_loader import load_or_cache
import s5_train as S
import splits as SP
import t1_regression as T1

SEEDS = tuple(range(10))
OUT = "paired_ablation_singlecity.json"
g = load_or_cache("graph_hamburg.pt", verbose=False)
dev = S.pick_device()
c = dict(S.CFG)
print(f"device {dev} | Buildings {g['Building'].num_nodes} | CONFIDENCE_RELS={S.CONFIDENCE_RELS}", flush=True)
res = {}


@contextlib.contextmanager
def conf_off():
    """Run the aware encoder source-typed but UNWEIGHTED (every relation gets uniform weight)."""
    saved = set(S.CONFIDENCE_RELS)
    S.CONFIDENCE_RELS = set()
    try:
        yield
    finally:
        S.CONFIDENCE_RELS = saved


def clear():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def paired(full, other):
    full, other = np.asarray(full, float), np.asarray(other, float)
    ok = np.isfinite(full) & np.isfinite(other)
    full, other = full[ok], other[ok]
    diff = full - other                                  # > 0 => confidence weighting helps
    sd = diff.std(ddof=1) if len(diff) > 1 else 0.0
    dz = float(diff.mean() / sd) if sd > 0 else float("inf")
    try:
        tp = float(stats.ttest_rel(full, other).pvalue)
    except Exception:
        tp = float("nan")
    try:
        wp = float(stats.wilcoxon(full, other).pvalue)
    except Exception:
        wp = float("nan")
    tc = float(stats.t.ppf(0.975, len(diff) - 1)) if len(diff) > 1 else float("nan")
    se = sd / np.sqrt(len(diff)) if len(diff) else float("nan")
    return {"n": int(len(diff)), "full_mean": float(full.mean()), "other_mean": float(other.mean()),
            "delta_mean": float(diff.mean()), "ci95": [float(diff.mean() - tc * se), float(diff.mean() + tc * se)],
            "paired_t_p": tp, "wilcoxon_p": wp, "cohen_dz": dz,
            "per_seed_full": full.tolist(), "per_seed_other": other.tolist()}


def run(name, arm_fn):
    arms = {"aware_full": [], "aware_noconf": [], "rgcn": []}
    t0 = time.time()
    for s in SEEDS:
        for arm in arms:
            try:
                v = arm_fn(s, arm)
            except Exception as e:
                print(f"  {name} seed {s} {arm}: ERROR {type(e).__name__}: {e}", flush=True)
                v = float("nan")
            arms[arm].append(v); clear()
        print(f"  {name} seed {s}: full={arms['aware_full'][-1]:.4f} noconf={arms['aware_noconf'][-1]:.4f} "
              f"rgcn={arms['rgcn'][-1]:.4f}  ({time.time()-t0:.0f}s)", flush=True)
    res[name] = {"arms_mean": {a: float(np.nanmean(v)) for a, v in arms.items()},
                 "delta_conf__full_minus_noconf": paired(arms["aware_full"], arms["aware_noconf"]),
                 "delta_vs_rgcn__full_minus_rgcn": paired(arms["aware_full"], arms["rgcn"]),
                 "per_seed": arms}
    json.dump(res, open(OUT, "w"), indent=2)
    dc = res[name]["delta_conf__full_minus_noconf"]
    print(f"== {name}: full={res[name]['arms_mean']['aware_full']:.3f} noconf={res[name]['arms_mean']['aware_noconf']:.3f} "
          f"rgcn={res[name]['arms_mean']['rgcn']:.3f} | Delta_conf={dc['delta_mean']:+.3f} CI{dc['ci95']} "
          f"p={dc['paired_t_p']:.4f} dz={dc['cohen_dz']:+.2f}", flush=True)


# ---- T1 height (regression, with-partner) ----
fn = g["Building"].feat_names
target = g["Building"].x[:, fn.index("height")].numpy().astype(float)


def _height(s, arm):
    if arm == "rgcn":
        return T1._eval(g, target, "rgcn", s, "spatial_cv", ["height"], False, 5, dev, c)["R2"]
    if arm == "aware_noconf":
        with conf_off():
            return T1._eval(g, target, "gnn_aware", s, "spatial_cv", ["height"], True, 5, dev, c)["R2"]
    return T1._eval(g, target, "gnn_aware", s, "spatial_cv", ["height"], True, 5, dev, c)["R2"]


run("T1_height_R2", _height)

# ---- T2 roof type + function (classification, macro-F1) ----
for nm, splitter in [("T2_rooftype_macroF1", SP.make_splits), ("T2_function_macroF1", SP.make_splits_function)]:
    def _cls(s, arm, splitter=splitter):
        if arm == "rgcn":
            m, _ = S._eval_one(g, "spatial_cv", "rgcn", s, False, 5, c, dev, splitter)
            return m
        if arm == "aware_noconf":
            with conf_off():
                m, _ = S._eval_one(g, "spatial_cv", "gnn_aware", s, True, 5, c, dev, splitter)
                return m
        m, _ = S._eval_one(g, "spatial_cv", "gnn_aware", s, True, 5, c, dev, splitter)
        return m
    run(nm, _cls)

json.dump(res, open(OUT, "w"), indent=2)
print("DONE " + OUT, flush=True)
