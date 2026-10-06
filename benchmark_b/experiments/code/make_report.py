"""Aggregate the per-run JSONL files into CSVs and the RESULTS template tables (paired statistics).

Paired comparison A-B: per-seed difference d_s = metric_A(seed s) - metric_B(seed s), same held-out
city and seed. Reported: mean d, 95% CI (t, n-1 df), paired t-test p, Wilcoxon signed-rank p
(two-sided, exact for small n), Cohen's d_z = mean(d)/sd(d). "Mean over cities": per seed, the
unweighted mean of the five cities' metrics, then the same paired statistics over seeds.
A comparison is called NULL when the CI contains 0 or |d_z| < 0.2 (negligible).
"""
import json, os, sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
N_CITY = {"hamburg": "388,267", "helsinki": "2,980", "nyc": "1,083,437", "tokyo": "2,005,762",
          "zurich": "102,668"}
CITY_ORDER = ["hamburg", "helsinki", "nyc", "tokyo", "zurich"]


def load(name):
    p = os.path.join(RES, name)
    return pd.DataFrame([json.loads(l) for l in open(p)]) if os.path.exists(p) else pd.DataFrame()


def paired(a, b):
    d = np.asarray(a) - np.asarray(b)
    n = len(d)
    if n < 2:
        return dict(n=n, diff=float(d.mean()) if n else np.nan, lo=np.nan, hi=np.nan, p_t=np.nan,
                    p_w=np.nan, dz=np.nan, null=None)
    m, sd = d.mean(), d.std(ddof=1)
    half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
    p_t = stats.ttest_rel(a, b).pvalue if sd > 0 else (1.0 if m == 0 else 0.0)
    try:
        p_w = stats.wilcoxon(d).pvalue if np.any(d != 0) else 1.0
    except ValueError:
        p_w = np.nan
    dz = m / sd if sd > 0 else np.nan
    null = bool((m - half <= 0 <= m + half) or (np.isfinite(dz) and abs(dz) < 0.2))
    return dict(n=n, diff=m, lo=m - half, hi=m + half, p_t=p_t, p_w=p_w, dz=dz, null=null)


def fmt_p(p):
    return "--" if not np.isfinite(p) else (f"{p:.1e}" if p < 1e-3 else f"{p:.3f}")


def ms(x):
    return f"{np.mean(x):.3f} ± {np.std(x, ddof=1):.3f}" if len(x) > 1 else (f"{x[0]:.3f}" if len(x) else "--")


def comparison_table(df, metric, variants, a, b, entity="held_out", order=CITY_ORDER, n_col=None,
                     with_mean=True):
    """Template table: per held-out city mean±std of each variant + paired stats for a-b."""
    lines = []
    head = ["Held-out", "n (bldgs)", "seeds"] + variants + [f"diff {a}-{b} [95% CI]", "p (t)",
                                                          "p (Wilcoxon)", "d_z", "verdict"]
    lines.append("| " + " | ".join(head) + " |")
    lines.append("|" + "---|" * len(head))
    rows = []
    wide_all = {}
    for city in order:
        sub = df[df[entity] == city]
        if sub.empty:
            continue
        wide = sub.pivot_table(index="seed", columns="variant", values=metric)
        wide_all[city] = wide
        cells = [ms(wide[v].dropna().values) if v in wide else "--" for v in variants]
        if a in wide and b in wide:
            pr = wide[[a, b]].dropna()
            st = paired(pr[a].values, pr[b].values)
        else:
            st = paired([], [])
        rows.append((city, st))
        verdict = "--" if st["null"] is None else ("null" if st["null"] else ("A>B" if st["diff"] > 0 else "A<B"))
        lines.append("| " + " | ".join([city.capitalize() if city != "nyc" else "NYC",
                                        (n_col or N_CITY).get(city, ""), str(st["n"])] + cells +
                                       [f"{st['diff']:+.3f} [{st['lo']:+.3f}, {st['hi']:+.3f}]",
                                        fmt_p(st["p_t"]), fmt_p(st["p_w"]),
                                        "--" if not np.isfinite(st["dz"]) else f"{st['dz']:+.2f}",
                                        verdict]) + " |")
    if with_mean and len(wide_all) == len(order):
        # per-seed mean over cities, seeds common to all cities and both variants
        common = None
        for w in wide_all.values():
            ok = w.dropna(subset=[c for c in (a, b) if c in w]).index
            common = ok if common is None else common.intersection(ok)
        mean_cells = []
        for v in variants:
            have = [w for w in wide_all.values() if v in w]
            if len(have) == len(order) and common is not None and len(common):
                mean_cells.append(ms(np.mean([w.loc[common, v].values for w in have], axis=0)))
            else:
                mean_cells.append("--")
        if common is not None and len(common) >= 2 and all(a in w and b in w for w in wide_all.values()):
            ma = np.mean([w.loc[common, a].values for w in wide_all.values()], axis=0)
            mb = np.mean([w.loc[common, b].values for w in wide_all.values()], axis=0)
            st = paired(ma, mb)
            verdict = "null" if st["null"] else ("A>B" if st["diff"] > 0 else "A<B")
            lines.append("| " + " | ".join(["**Mean over cities**", "", str(st["n"])] + mean_cells +
                                           [f"{st['diff']:+.3f} [{st['lo']:+.3f}, {st['hi']:+.3f}]",
                                            fmt_p(st["p_t"]), fmt_p(st["p_w"]), f"{st['dz']:+.2f}",
                                            verdict]) + " |")
    return "\n".join(lines)


def main():
    out = []
    b1 = load("b1_runs.jsonl")
    if not b1.empty:
        b1.to_csv(os.path.join(RES, "b1_runs.csv"), index=False)
        variants = [v for v in ["V0", "V1", "V2", "V3", "V4", "V5"] if v in set(b1.variant)]
        for proto, title in [("guarded", "leakage-guarded protocol (target column `height` dropped, as the paper states)"),
                             ("t7", "Table-7-faithful protocol (drop=[], i.e. the per-city z-scored `height` input column is present)")]:
            sub = b1[b1.protocol == proto]
            if sub.empty:
                continue
            out.append(f"\n## B1 -- T1 height, leave-one-city-out R^2, {title}\n")
            for a, b, what in [("V1", "V2", "effect of confidence weighting (with typing + coverage feats)"),
                               ("V1", "V3", "effect of coverage/agreement features (with typing + confidence)"),
                               ("V2", "V0", "coverage features without confidence (V0 = to_hetero GraphSAGE, functionally V2 minus x_prov)"),
                               ("V3", "V0", "confidence without coverage features"),
                               ("V1", "V0", "full aware vs agnostic (Table 7's comparison)"),
                               ("V4", "V5", "confidence with a shared W (no source typing, no coverage)"),
                               ("V0", "V5", "source typing (per-relation W vs shared W; no conf, no coverage)")]:
                if a in variants and b in variants:
                    out.append(f"\n### {a} vs {b}: {what}\n")
                    out.append(comparison_table(sub, "R2", variants, a, b))
    b2 = load("b2_runs.jsonl")
    if not b2.empty:
        b2.to_csv(os.path.join(RES, "b2_runs.csv"), index=False)
        variants = [v for v in ["V0", "V1", "V2", "V3"] if v in set(b2.variant)]
        n2 = {}
        for h in ("hamburg", "helsinki"):
            r = b2[b2.held_out == h].iloc[0]
            n2[h] = f"{r['n_test']:,} test / {r['n_train']:,} train"
        out.append("\n## B2 -- T2 roof type, Hamburg <-> Helsinki transfer, macro-F1 (merged 3-class)\n")
        for h in ("hamburg", "helsinki"):
            r = b2[b2.held_out == h].iloc[0]
            cnt = np.array(r["test_class_counts"], float)
            p = cnt.max() / cnt.sum()
            floor = (2 * p / (1 + p)) / len(cnt)          # macro-F1 of "always predict the majority class"
            out.append(f"- held-out {h}: test class counts {dict(zip(r['class_names'], r['test_class_counts']))}; "
                       f"majority-class (constant) predictor: macro-F1 {floor:.3f}, accuracy {p:.3f}")
        for a, b in [("V1", "V2"), ("V1", "V3"), ("V2", "V0"), ("V1", "V0")]:
            if a in variants and b in variants:
                out.append(f"\n### {a} vs {b}\n")
                out.append(comparison_table(b2, "macro_f1", variants, a, b, order=["hamburg", "helsinki"],
                                            n_col=n2, with_mean=False))
        acc = b2.groupby(["held_out", "variant"]).accuracy.agg(["mean", "std"]).round(3)
        out.append("\nAccuracy (mean, std over seeds):\n\n" + acc.to_markdown())
    b4 = load("b4_runs.jsonl")
    if not b4.empty:
        b4.to_csv(os.path.join(RES, "b4_runs.csv"), index=False)
        out.append("\n## B4 -- extra baselines, Hamburg single city (Table 6 format, spatial 5-fold CV)\n")
        names = {"probe": "Probe (LogReg/Ridge; Table 6 'MLP') [anchor]", "gnn": "GraphSAGE (agnostic) [anchor]",
                 "gnn_aware": "Conf.-weighted GNN (aware) [anchor]", "lgbm": "LightGBM (attributes)",
                 "lgbm_1hop": "LightGBM (+1-hop neighbour aggregates)", "simplehgn": "Simple-HGN"}
        t6 = {"probe": (0.504, 0.329, 0.666), "gnn": (0.556, 0.462, 0.730), "gnn_aware": (0.559, 0.476, 0.733)}
        lines = ["| Model | Roof type macro-F1 | Building use macro-F1 | Height R^2 | seeds | Table 6 (roof/use/height) |",
                 "|---|---|---|---|---|---|"]
        for m in ["probe", "gnn", "gnn_aware", "lgbm", "lgbm_1hop", "simplehgn"]:
            sub = b4[b4.method == m]
            if sub.empty:
                continue
            cells = []
            for t in ["roof", "function", "height"]:
                v = sub[sub.task == t].value.values
                cells.append(ms(v) if len(v) else "--")
            ref = "/".join(f"{x:.3f}" for x in t6[m]) if m in t6 else "--"
            lines.append(f"| {names[m]} | " + " | ".join(cells) + f" | {sub.seed.nunique()} | {ref} |")
        out.append("\n".join(lines))
        rt = b4.groupby(["task", "method"]).agg(runtime_s=("runtime_s", "mean"),
                                                 peak_vram_gb=("peak_vram_gb", "max")).round(1)
        out.append("\nRuntime per seed (5 folds) and peak VRAM:\n\n" + rt.to_markdown())
    t3 = load("t3_runs.jsonl")
    if not t3.empty:
        t3.to_csv(os.path.join(RES, "t3_runs.csv"), index=False)
        out.append("\n## T3 matching rerun (tab:repL-match), legacy vs fixed (disjoint-supervision) protocol\n")
        for metric in ("AUC", "Hits@1"):
            lines = [f"| City | n pairs | seeds | spatial | attrsim | attr legacy | attr fixed | GraphSAGE legacy | "
                     f"GraphSAGE fixed | aware legacy | aware fixed | aware-GraphSAGE (fixed) [95% CI] |",
                     "|" + "---|" * 12]
            for city in ["hamburg", "helsinki", "nyc", "tokyo", "zurich"]:
                sub = t3[t3.city == city]
                if sub.empty:
                    continue
                cell = lambda k, p: ms(sub[(sub.kind == k) & (sub.protocol == p)][metric].values)
                w = sub[sub.protocol == "disjoint"].pivot_table(index="seed", columns="kind", values=metric)
                if {"aware", "sage"} <= set(w.columns):
                    pr = w[["aware", "sage"]].dropna()
                    st = paired(pr.aware.values, pr.sage.values)
                    dcell = f"{st['diff']:+.3f} [{st['lo']:+.3f}, {st['hi']:+.3f}] (n={st['n']})"
                else:
                    dcell = "--"
                lines.append(f"| {city} | {sub.n_pos.iloc[0]:,} | {sub.seed.nunique()} | {cell('spatial', 'n/a')} | "
                             f"{cell('attrsim', 'n/a')} | {cell('attr', 'legacy')} | {cell('attr', 'disjoint')} | "
                             f"{cell('sage', 'legacy')} | {cell('sage', 'disjoint')} | {cell('aware', 'legacy')} | "
                             f"{cell('aware', 'disjoint')} | {dcell} |")
            out.append(f"\n### {metric}\n\n" + "\n".join(lines))
    txt = "\n".join(out) + "\n"
    with open(os.path.join(RES, "TABLES.md"), "w") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
