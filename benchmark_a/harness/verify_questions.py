#!/usr/bin/env python3
"""
verify_questions.py — the verification gate for the AuthentiCity benchmark suite.

A question may enter the benchmark only if it passes every check:

  Feasible questions
    G1  gold Cypher executes without error
    G2  the result is deterministic: identical canonical form across
        --runs repeated executions (default 3)
    G3  the result is non-empty (unless the template sets allow_empty)

  Infeasible questions
    G4  the guard query proves absence: it must return exactly {n: 0},
        i.e. the information the question asks for truly does not exist
        in the released graph

Canonicalization (for G2 and for storing gold answers): rows are dicts
sorted by JSON serialization; floats rounded to 6 decimals; the canonical
answer is the sorted JSON dump. Numeric tolerance at evaluation time is the
job of the harness, not of this gate.

Output:
  --out          verified suite JSONL (records extended with gold_answer,
                 verified=true, and the canonical answer hash)
  --report       Markdown verification report (pass/fail by category+reason)

Usage:
    py bench/verify_questions.py --in bench/out/questions_raw.jsonl
    py bench/verify_questions.py --in ... --runs 5 --out ... --report ...
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "neo4jneo4j")


def canonicalize(rows):
    """Canonical, order-insensitive form of a query result."""
    def norm(v):
        if isinstance(v, float):
            return round(v, 6)
        if isinstance(v, dict):
            return {k: norm(x) for k, x in sorted(v.items())}
        if isinstance(v, (list, tuple)):
            return [norm(x) for x in v]
        return v

    normed = [json.dumps(norm(dict(r)), sort_keys=True, default=str) for r in rows]
    return json.dumps(sorted(normed), ensure_ascii=False)


def verify_feasible(sess, rec, runs):
    canon_forms = []
    for _ in range(runs):
        try:
            rows = list(sess.run(rec["gold_cypher"]))
        except Exception as exc:
            return False, f"G1_execution_error: {type(exc).__name__}: {exc}", None
        canon_forms.append(canonicalize(rows))
    if len(set(canon_forms)) != 1:
        return False, "G2_nondeterministic", None
    if canon_forms[0] == "[]" and not rec.get("allow_empty", False):
        return False, "G3_empty_result", None
    return True, None, canon_forms[0]


def verify_infeasible(sess, rec):
    guard = rec.get("guard")
    if not guard:
        return False, "G4_missing_guard", None
    try:
        row = sess.run(guard).single()
    except Exception as exc:
        return False, f"G4_guard_error: {type(exc).__name__}: {exc}", None
    if row is None or row.get("n") != 0:
        return False, f"G4_not_absent (guard n={None if row is None else row.get('n')})", None
    return True, None, "REFUSE"


def main():
    ap = argparse.ArgumentParser(description="Verify a generated AuthentiCity question suite.")
    ap.add_argument("--in", dest="infile", default="bench/out/questions_raw.jsonl")
    ap.add_argument("--out", default="bench/out/questions_verified.jsonl")
    ap.add_argument("--report", default="bench/out/verification_report.md")
    ap.add_argument("--runs", type=int, default=3, help="repeated executions for the stability check")
    args = ap.parse_args()

    records = [json.loads(line) for line in open(args.infile, encoding="utf-8")]
    print(f"Verifying {len(records)} questions ({args.runs} runs each) ...")

    driver = GraphDatabase.driver(
        NEO4J_URI, auth=NEO4J_AUTH,
        notifications_disabled_classifications={"DEPRECATION", "UNRECOGNIZED"})
    driver.verify_connectivity()

    passed, failed = [], []
    with driver.session(database="neo4j") as sess:
        for i, rec in enumerate(records, 1):
            t0 = time.perf_counter()
            if rec["feasible"]:
                ok, reason, gold_answer = verify_feasible(sess, rec, args.runs)
            else:
                ok, reason, gold_answer = verify_infeasible(sess, rec)
            elapsed = time.perf_counter() - t0
            status = "OK" if ok else f"FAIL ({reason})"
            print(f"  [{i}/{len(records)}] {rec['qid']}: {status}  ({elapsed:.2f}s)", flush=True)
            if ok:
                rec["gold_answer"] = gold_answer
                rec["gold_answer_sha1"] = hashlib.sha1(gold_answer.encode("utf-8")).hexdigest()
                rec["verified"] = True
                passed.append(rec)
            else:
                failed.append((rec, reason))
    driver.close()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        for r in passed:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ---- report ----
    by_cat = {}
    for r in passed:
        by_cat.setdefault(r["category"], [0, 0])[0] += 1
    for r, _ in failed:
        by_cat.setdefault(r["category"], [0, 0])[1] += 1

    lines = ["# AuthentiCity suite verification report", ""]
    lines.append(f"- Input: `{args.infile}` ({len(records)} questions)")
    lines.append(f"- Passed: **{len(passed)}**  Failed: **{len(failed)}**  (stability runs: {args.runs})")
    lines.append("")
    lines.append("| Category | Passed | Failed |")
    lines.append("| -------- | ------ | ------ |")
    for cat, (p, f) in sorted(by_cat.items()):
        lines.append(f"| {cat} | {p} | {f} |")
    if failed:
        lines.append("")
        lines.append("## Failures")
        lines.append("")
        for rec, reason in failed:
            lines.append(f"- `{rec['qid']}`: {reason}")
    lines.append("")
    lines.append("Human review (>=20% stratified sample) is still required before freezing "
                 "v1.0 — this gate checks executability, determinism, and absence proofs, "
                 "not phrasing quality. See KDD_PAPER_NOTES.md step B2.")
    Path(args.report).write_text("\n".join(lines), encoding="utf-8")

    print(f"\nPassed {len(passed)} / {len(records)}  ->  {out}")
    print(f"Report: {args.report}")
    if failed:
        print("Failures:")
        for rec, reason in failed[:15]:
            print(f"  {rec['qid']}: {reason}")


if __name__ == "__main__":
    main()
