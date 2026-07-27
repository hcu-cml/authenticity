#!/usr/bin/env python3
"""
split_dataset.py — dev/test split for the AuthentiCity benchmark suite (B4,
QUESTION_SUITE_DESIGN.md §11).

Split unit is `template_id`, NOT question or city: every instantiation,
paraphrase, and language variant of a template lives on one side, so the
held-out test set contains unseen templates rather than unseen paraphrases
of seen ones. Stratified by `category` (category x difficulty was checked
and rejected — with 65 templates over 9 categories x 5 difficulties, most
(category, difficulty) cells hold 0-2 templates, too sparse to split
meaningfully; category alone has 4-12 templates per group, in a usable
range). Assignment is a stable hash of template_id (not a stored random
seed), so it is 100% reproducible from templates.py alone and stable across
reruns even as new templates are added (new templates get one deterministic
bucket without perturbing existing assignments).

Reads: bench/out/questions_<city>_verified.jsonl (one per city; a city
missing its file is skipped with a warning, not an error).
Writes:
  bench/out/split_assignment.json          template_id -> dev|test (+ counts)
  bench/out/questions_<city>_dev.jsonl      full records (incl. gold) for dev templates
  bench/out/questions_<city>_test.jsonl     PUBLIC test records, gold stripped
  bench/out/questions_<city>_test_private_gold.jsonl   full records for internal scoring only
  bench/out/questions_dev.jsonl             all 5 cities pooled, dev
  bench/out/questions_test.jsonl            all 5 cities pooled, public test
  bench/out/questions_test_private_gold.jsonl          all 5 cities pooled, private gold

The two "test_private_gold" outputs are NOT for release (Zenodo ships the
private gold under restricted access per the design doc, not in this repo's
plain-text form) — they exist only so this project's own evaluation harness
(evaluate_model.py) can score held-out performance without a human re-typing
answers.

Usage:
    py bench/split_dataset.py                    # 70/30, all 5 cities
    py bench/split_dataset.py --dev-fraction 0.7
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from templates import TEMPLATES  # noqa: E402

CITIES = ["hamburg", "helsinki", "zurich", "tokyo", "nyc"]
GOLD_FIELDS = ("gold_cypher", "gold_sql", "gold_answer", "gold_answer_sha1", "guard")


def template_bucket(template_id):
    """Deterministic pseudo-random rank in [0, 1) from a stable hash — no RNG,
    no stored seed, reproducible from template_id alone."""
    digest = hashlib.sha1(template_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def compute_split(dev_fraction):
    by_category = {}
    for t in TEMPLATES:
        by_category.setdefault(t["category"], []).append(t["id"])

    assignment = {}
    category_report = {}
    for category, ids in by_category.items():
        ranked = sorted(ids, key=template_bucket)
        n_dev = round(len(ranked) * dev_fraction)
        # guarantee at least one template on each side when the category has >=2
        if len(ranked) >= 2:
            n_dev = min(max(n_dev, 1), len(ranked) - 1)
        dev_ids = set(ranked[:n_dev])
        for tid in ranked:
            assignment[tid] = "dev" if tid in dev_ids else "test"
        category_report[category] = {
            "total": len(ranked),
            "dev": len(dev_ids),
            "test": len(ranked) - len(dev_ids),
        }
    return assignment, category_report


def strip_gold(record):
    return {k: v for k, v in record.items() if k not in GOLD_FIELDS}


def main():
    ap = argparse.ArgumentParser(description="Split the AuthentiCity suite into dev/test by template_id.")
    ap.add_argument("--dev-fraction", type=float, default=0.7)
    ap.add_argument("--in-dir", default="bench/out")
    ap.add_argument("--out-dir", default="bench/out")
    args = ap.parse_args()

    assignment, category_report = compute_split(args.dev_fraction)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    Path(out_dir / "split_assignment.json").write_text(
        json.dumps({"dev_fraction": args.dev_fraction, "assignment": assignment,
                     "by_category": category_report}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Split by category (dev/test/total):")
    for cat, rep in sorted(category_report.items()):
        print(f"  {cat:14s} {rep['dev']:3d} / {rep['test']:3d} / {rep['total']:3d}")

    pooled = {"dev": [], "test": [], "test_private_gold": []}
    in_dir = Path(args.in_dir)
    for city in CITIES:
        src = in_dir / f"questions_{city}_verified.jsonl"
        if not src.exists():
            print(f"  WARNING: {src} not found, skipping {city}")
            continue
        dev, test_public, test_private = [], [], []
        for line in src.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            side = assignment.get(rec["template_id"])
            if side is None:
                print(f"  WARNING: {rec['template_id']} not in split assignment (new template since split?) -> dev")
                side = "dev"
            if side == "dev":
                dev.append(rec)
            else:
                test_private.append(rec)
                test_public.append(strip_gold(rec))

        def write(name, records):
            p = out_dir / f"questions_{city}_{name}.jsonl"
            with open(p, "w", encoding="utf-8") as fh:
                for r in records:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            return p

        write("dev", dev)
        write("test", test_public)
        write("test_private_gold", test_private)
        pooled["dev"].extend(dev)
        pooled["test"].extend(test_public)
        pooled["test_private_gold"].extend(test_private)
        print(f"  {city:10s} dev={len(dev):3d}  test={len(test_public):3d}")

    for name, records in pooled.items():
        p = out_dir / f"questions_{name}.jsonl"
        with open(p, "w", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Pooled {name}: {len(records)} -> {p}")


if __name__ == "__main__":
    main()
