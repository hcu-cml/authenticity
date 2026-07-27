#!/usr/bin/env python3
"""
generate_questions.py — instantiate AuthentiCity benchmark questions from the
schema-grounded templates in templates.py against the live pykci graph.

For every template, slot values are read from the graph via the PROVIDERS
queries (so all questions reference data that actually exists), gold Cypher
is materialized with inlined literals, and every NL paraphrase becomes its
own question record sharing the same gold query.

Output: JSONL, one record per question:
  {qid, template_id, category, tier, difficulty, feasible, lang, question,
   gold_cypher, gold_sql, guard, slots, dataset, allow_empty}

`lang` is "en" for the standard accepted paraphrases, plus "de"/"ja" for the
LANG_VARIANTS translations (QUESTION_SUITE_DESIGN.md §4.10): German on every
city, Japanese on Tokyo only (10 designated cross-city templates + the 3
Tokyo schema-bridging templates, which are ja-only since their "nl" list is
already English-only by design).

Usage:
    py bench/generate_questions.py                          # all templates
    py bench/generate_questions.py --out bench/out/questions_raw.jsonl
    py bench/generate_questions.py --max-per-slot 2         # cap slot expansion
    py bench/generate_questions.py --dry-run                # list templates, no DB

The suite then passes through verify_questions.py (the verification gate)
before it may be called a benchmark. See bench/README.md.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from templates import (  # noqa: E402
    PROVIDERS, TEMPLATES, REQUIRES, LANG_VARIANTS, graph_presence, satisfies_requirements,
)

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "neo4jneo4j")


def fetch_slot_values(sess, max_per_slot):
    """Run every provider once; return {provider_name: [values]}."""
    values = {}
    for name, query in PROVIDERS.items():
        try:
            rows = [r["value"] for r in sess.run(query) if r["value"] is not None]
        except Exception as exc:
            print(f"  WARNING: provider '{name}' failed: {exc}")
            rows = []
        if not rows:
            print(f"  WARNING: provider '{name}' returned no values; dependent templates will be skipped.")
        values[name] = rows[:max_per_slot]
    return values


def _record(template, qid, question, gold, guard, combo, dataset_name, lang):
    return {
        "qid": qid.replace(" ", "_"),
        "template_id": template["id"],
        "category": template["category"],
        "tier": template["tier"],
        "difficulty": template["difficulty"],
        "feasible": template["feasible"],
        "lang": lang,
        "question": question,
        "gold_cypher": gold,
        "gold_sql": template.get("gold_sql"),  # TODO: 3DCityDB backend (B2)
        "guard": guard,
        "slots": combo,
        "dataset": dataset_name,
        "allow_empty": template.get("allow_empty", False),
    }


def expand(template, slot_values, dataset_name):
    """Yield one question record per (slot combination x paraphrase), plus
    one per language variant declared in LANG_VARIANTS (lang != "en"):
    translations of a template, not extra paraphrases (QUESTION_SUITE_DESIGN.md
    §4.10/§7) -- same gold query, same slots, only the NL differs. Japanese
    variants are Tokyo-only by design (the project's non-Latin-schema city);
    German variants instantiate on every city."""
    slots = template.get("slots", {})
    # build the list of slot combinations (cartesian product, provider-capped)
    combos = [{}]
    for slot_name, provider in slots.items():
        vals = slot_values.get(provider, [])
        if not vals:
            return  # provider empty -> skip template entirely
        combos = [dict(c, **{slot_name: v}) for c in combos for v in vals]

    is_tokyo = "tokyo" in dataset_name.lower()
    variants = LANG_VARIANTS.get(template["id"], {})

    for combo in combos:
        fmt = {k: v for k, v in combo.items()}
        gold = template["gold_cypher"]
        if gold is not None:
            gold = gold.format(**fmt)
        guard = template.get("guard")
        if guard is not None:
            guard = guard.format(**fmt)
        slot_suffix = "_".join(str(v)[:24] for v in combo.values())
        base_id = template["id"] + (f"__{slot_suffix}" if slot_suffix else "")

        for p_idx, phrasing in enumerate(template["nl"]):
            question = phrasing.format(**fmt)
            qid = base_id + f"__p{p_idx}"
            yield _record(template, qid, question, gold, guard, combo, dataset_name, "en")

        for lang, phrasing in variants.items():
            if lang == "ja" and not is_tokyo:
                continue
            question = phrasing.format(**fmt)
            qid = base_id + f"__{lang}"
            yield _record(template, qid, question, gold, guard, combo, dataset_name, lang)


def main():
    ap = argparse.ArgumentParser(description="Generate AuthentiCity benchmark questions from templates.")
    ap.add_argument("--out", default="bench/out/questions_raw.jsonl")
    ap.add_argument("--max-per-slot", type=int, default=2,
                    help="max slot values sampled per provider (default 2)")
    ap.add_argument("--dry-run", action="store_true", help="list templates without touching the DB")
    args = ap.parse_args()

    if args.dry_run:
        by_cat = {}
        for t in TEMPLATES:
            by_cat.setdefault(t["category"], []).append(t["id"])
        for cat, ids in by_cat.items():
            print(f"{cat:14s} ({len(ids)}): {', '.join(ids)}")
        print(f"\nTotal templates: {len(TEMPLATES)}")
        return

    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        NEO4J_URI, auth=NEO4J_AUTH,
        notifications_disabled_classifications={"DEPRECATION", "UNRECOGNIZED"})
    driver.verify_connectivity()

    with driver.session(database="neo4j") as sess:
        ds = sess.run("MATCH (d:Dataset) RETURN d.name AS name LIMIT 1").single()
        dataset_name = ds["name"] if ds else "unknown"
        n_buildings = sess.run("MATCH (b:Building) RETURN count(b) AS n").single()["n"]
        if n_buildings == 0:
            raise SystemExit("ERROR: graph contains no buildings — ingest a dataset first "
                             "(py ingest_citygml.py input/citygml/<file>.gml).")
        print(f"Dataset: {dataset_name}  ({n_buildings} buildings)")
        print("Probing the graph for per-city requirement tokens ...")
        present = graph_presence(sess)  # (props, labels, edges)
        print("Fetching slot values from the graph ...")
        slot_values = fetch_slot_values(sess, args.max_per_slot)

    driver.close()

    records = []
    skipped = []
    for t in TEMPLATES:
        if not satisfies_requirements(t["id"], *present):
            missing = [tok for tok in REQUIRES.get(t["id"], [])
                       if tok not in present[0] | present[1] | present[2]]
            skipped.append((t["id"], missing))
            continue
        records.extend(expand(t, slot_values, dataset_name))

    if skipped:
        print(f"\nRequirement gate: skipped {len(skipped)} template(s) not answerable on "
              f"'{dataset_name}' (missing tokens absent from this graph):")
        for tid, missing in sorted(skipped):
            print(f"  - {tid:40s} needs: {', '.join(missing)}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    by_cat = {}
    for r in records:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    print(f"\nWrote {len(records)} questions to {out}")
    for cat, n in sorted(by_cat.items()):
        print(f"  {cat:14s} {n}")
    print("\nNext: py bench/verify_questions.py --in " + str(out))


if __name__ == "__main__":
    main()
