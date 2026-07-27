"""
build_review_sample.py -- draw the >=20% human-review sample for the AuthentiCity
question suite.

Reads the five per-city verified suites (bench/out/questions_<city>_verified.jsonl,
each carrying gold), pools them, and draws a deterministic, category-stratified
sample of at least 20% for independent human review of gold correctness and
natural phrasing (per the suite construction gate, Sec. 4.1 / app:questions).

Selection is deterministic (SHA1 of the qid, no RNG) so the sample is stable
across regenerations of the same suite: within each category the questions are
ordered by sha1(qid) and the first ceil(fraction * n) are taken. Category
stratification guarantees every category is represented at >= the target rate;
language variants (de/ja) are pooled in with the English questions, so the
sample covers the multilingual mechanism proportionally.

Outputs (bench/out/):
  human_review_sample.jsonl   one record per sampled question, full gold
  human_review_sample.csv     the same, flat, with empty reviewer_verdict /
                              reviewer_notes columns for a human to fill
                              (accept/reject only, no free editing -- see Sec. 7)

Usage:
  py bench/build_review_sample.py [--fraction 0.20] [--in-dir bench/out] [--out-dir bench/out]
"""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

CITIES = ["hamburg", "helsinki", "zurich", "nyc", "tokyo"]

# dataset name (as stored on each question) -> short city label
DATASET_CITY = {
    "hamburg_citygml2_lod2_2025.gml": "hamburg",
    "helsinki_citygml2_lod2_2019.gml": "helsinki",
    "zurich": "zurich",
    "nyc": "nyc",
    "tokyo": "tokyo",
}

REVIEW_COLUMNS = [
    "qid", "template_id", "category", "city", "lang", "difficulty",
    "feasible", "question", "gold_cypher", "guard", "gold_answer",
    "reviewer_verdict", "reviewer_notes",
]


def _city_of(rec):
    ds = rec.get("dataset", "")
    return DATASET_CITY.get(ds, ds)


def main():
    ap = argparse.ArgumentParser(description="Draw the human-review sample.")
    ap.add_argument("--fraction", type=float, default=0.20,
                    help="minimum sampling fraction per category (default 0.20)")
    ap.add_argument("--in-dir", default="bench/out")
    ap.add_argument("--out-dir", default="bench/out")
    args = ap.parse_args()

    in_dir, out_dir = Path(args.in_dir), Path(args.out_dir)

    by_cat = defaultdict(list)
    total = 0
    for city in CITIES:
        src = in_dir / f"questions_{city}_verified.jsonl"
        if not src.exists():
            print(f"  WARNING: {src} not found, skipping {city}")
            continue
        for line in src.open(encoding="utf-8"):
            rec = json.loads(line)
            by_cat[rec["category"]].append(rec)
            total += 1

    sample = []
    for cat in sorted(by_cat):
        recs = by_cat[cat]
        # deterministic order: sha1 of qid (stable across regenerations)
        recs_sorted = sorted(recs, key=lambda r: hashlib.sha1(r["qid"].encode("utf-8")).hexdigest())
        k = math.ceil(args.fraction * len(recs))
        sample.extend(recs_sorted[:k])

    # stable output order: category, then hash
    sample.sort(key=lambda r: (r["category"], hashlib.sha1(r["qid"].encode("utf-8")).hexdigest()))

    out_jsonl = out_dir / "human_review_sample.jsonl"
    with out_jsonl.open("w", encoding="utf-8") as f:
        for rec in sample:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    out_csv = out_dir / "human_review_sample.csv"
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for rec in sample:
            row = {c: rec.get(c, "") for c in REVIEW_COLUMNS}
            row["city"] = _city_of(rec)
            row["reviewer_verdict"] = ""
            row["reviewer_notes"] = ""
            w.writerow(row)

    n_nonen = sum(1 for r in sample if r.get("lang", "en") != "en")
    cats = defaultdict(int)
    for r in sample:
        cats[r["category"]] += 1
    print(f"Pooled {total} questions across {len([c for c in CITIES])} cities.")
    print(f"Sampled {len(sample)} ({100.0 * len(sample) / total:.1f}%), "
          f"{n_nonen} non-English ({sum(1 for r in sample if r.get('lang')=='de')} de / "
          f"{sum(1 for r in sample if r.get('lang')=='ja')} ja).")
    print("Per category (sampled / total):")
    for cat in sorted(by_cat):
        print(f"  {cat:13} {cats[cat]:3} / {len(by_cat[cat])}")
    print(f"Wrote {out_jsonl}")
    print(f"Wrote {out_csv}")


if __name__ == "__main__":
    main()
