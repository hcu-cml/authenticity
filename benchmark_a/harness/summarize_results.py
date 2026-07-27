#!/usr/bin/env python3
"""
summarize_results.py — aggregate the per-question results files written by
evaluate_model.py into the EX decomposition + infeasibility-detection metrics
used in the paper's tab:results_query (and KDD_PAPER_NOTES.md / bench/README.md).

Everything here is DERIVED from the existing `results_*.jsonl` files — no model
re-run and no DB access. The point is that EX alone hides *how* a model fails;
this script makes the decomposition (and the paper's promised
precision/recall/F1 + over-refusal) reproducible rather than hand-transcribed.

Feasible questions decompose into four mutually-exclusive outcomes that sum to
100 %:
  - EX            : executed and result-correct (the headline accuracy)
  - exec_wrong    : executed without error but result incorrect (semantic miss)
  - errored       : the generated query did not execute (syntax/type/timeout/…)
  - over_refusal  : wrongly declined a feasible question
Infeasibility detection (over the feasible+infeasible pool):
  - precision = correctly-refused / (correctly-refused + over-refusals)
  - recall    = correctly-refused / all-infeasible
  - F1        = harmonic mean (undefined when the model never refuses at all)
Errored queries are sub-classified (syntax / type / timeout / other) from the
stored `error` string.

Usage:
    py bench/summarize_results.py                       # all bench/out/results_*.jsonl
    py bench/summarize_results.py --glob 'results_hamburg_*.jsonl'
    py bench/summarize_results.py --latex               # also print LaTeX table rows
"""

import argparse
import glob
import json
import os
from collections import Counter

# RELEASE: default to the public layout benchmark_a/baselines/results
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           os.pardir, "baselines", "results")


def err_class(msg):
    if msg is None:
        return None
    if "QUERY_TIMEOUT" in msg:
        return "timeout"
    if "SyntaxError" in msg:
        return "syntax"
    if "TypeError" in msg:
        return "type"
    return "other"


def summarize(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    if not rows:
        return None
    feas = [r for r in rows if r["feasible"]]
    infe = [r for r in rows if not r["feasible"]]
    n = len(feas)

    correct = sum(1 for r in feas if r["correct"])
    over_ref = sum(1 for r in feas if r.get("over_refusal"))
    errored = [r for r in feas if r.get("error")]
    exec_wrong = sum(
        1 for r in feas
        if not r["correct"] and not r.get("over_refusal") and not r.get("error")
    )
    err_break = Counter(err_class(r["error"]) for r in errored)

    inf_ref = sum(1 for r in infe if r["correct"])  # correct == refused for infeasible
    denom_p = inf_ref + over_ref
    prec = (inf_ref / denom_p * 100) if denom_p else None
    rec = (inf_ref / len(infe) * 100) if infe else None
    f1 = (2 * prec * rec / (prec + rec)) if (prec and rec) else None

    pct = lambda x: x / n * 100 if n else 0.0
    return {
        "model": rows[0].get("model", "?"),
        "backend": rows[0].get("backend", "?"),
        "dataset": rows[0].get("dataset", "?"),
        "n_feasible": n,
        "n_infeasible": len(infe),
        "EX": pct(correct),
        "exec_wrong": pct(exec_wrong),
        "errored": pct(len(errored)),
        "over_refusal": pct(over_ref),
        "valid_exec_rate": pct(correct + exec_wrong),
        "infeas_precision": prec,
        "infeas_recall": rec,
        "infeas_f1": f1,
        "err_breakdown": dict(err_break),
    }


def fmt(x, latex=False):
    if x is None:
        return "\\textemdash" if latex else "n/a"
    return f"{x:.1f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results-dir", default=RESULTS_DIR,
                    help="directory holding the results JSONL files")
    ap.add_argument("--glob", default="*.jsonl",
                    help="glob under bench/out/ (default: results_*.jsonl; "
                         "report files ending .report.md are ignored automatically)")
    ap.add_argument("--latex", action="store_true",
                    help="also emit LaTeX rows for tab:results_query")
    args = ap.parse_args()

    paths = sorted(
        p for p in glob.glob(os.path.join(args.results_dir, args.glob))
        if p.endswith(".jsonl")
    )
    if not paths:
        raise SystemExit(f"No results files matched {args.glob} in {args.results_dir}")

    summaries = [s for s in (summarize(p) for p in paths) if s]

    hdr = ("dataset", "model", "EX", "exec_wrong", "errored", "over_refusal",
           "inf_P", "inf_R", "inf_F1", "err_breakdown")
    print(f"{'dataset':40} {'model':26} {'EX':>5} {'wrong':>6} {'err':>5} "
          f"{'oref':>5} {'infP':>5} {'infR':>5} {'infF1':>5}  err_breakdown")
    for s in summaries:
        print(f"{s['dataset'][:40]:40} {s['model'][:26]:26} "
              f"{s['EX']:5.1f} {s['exec_wrong']:6.1f} {s['errored']:5.1f} "
              f"{s['over_refusal']:5.1f} "
              f"{fmt(s['infeas_precision']):>5} {fmt(s['infeas_recall']):>5} "
              f"{fmt(s['infeas_f1']):>5}  {s['err_breakdown']}")

    if args.latex:
        print("\n% --- tab:results_query rows (feasible decomposition | infeasibility) ---")
        for s in summaries:
            print(f"    {s['model']} & {s['dataset']} & "
                  f"{s['EX']:.1f} & {s['exec_wrong']:.1f} & {s['errored']:.1f} & "
                  f"{s['over_refusal']:.1f} & & "
                  f"{fmt(s['infeas_precision'], latex=True)} & {fmt(s['infeas_recall'], latex=True)} & "
                  f"{fmt(s['infeas_f1'], latex=True)} \\\\")


if __name__ == "__main__":
    main()
