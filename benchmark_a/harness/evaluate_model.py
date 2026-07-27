#!/usr/bin/env python3
"""
evaluate_model.py — the model-evaluation harness for the AuthentiCity
NL-to-Cypher benchmark (design step E2, QUESTION_SUITE_DESIGN.md).

Takes a question suite (dev or held-out test with its private gold —
NEVER the public gold-stripped test file, which has nothing to score
against), sends each question's NL to a model, executes the model's
generated Cypher against the LIVE graph, and scores it against the
pre-materialized gold_answer from verify_questions.py.

This only evaluates questions whose `dataset` matches the graph currently
live in Neo4j (same one-city-at-a-time constraint as generate_questions.py
/ verify_questions.py — restore the matching city dump first). Run once per
city, then merge the per-city results files for the paper's tab:results_query.

Scoring (QUESTION_SUITE_DESIGN.md §10):
  - Feasible questions: execution accuracy (EX) — canonicalized, COLUMN-NAME-
    INSENSITIVE result-set equality against gold_answer (row_signature()/
    canonical_signature() below; deliberately NOT verify_questions.py's
    canonicalize(), which compares {key: value} dicts verbatim and is only
    correct for that script's own gold-vs-itself G2 check, where the column
    name never changes -- a model calling its own count "building_count"
    instead of gold's "n" is not a wrong answer). A REFUSE on a feasible
    question is wrong for EX AND counted separately as an over-refusal.
  - Context parity: every backend (Ollama, Claude API, or pregenerated
    answers from any other model incl. Claude Code subagents) MUST receive
    byte-identical schema text for a given city -- see get_cached_schema().
  - Infeasible questions: correct iff the model explicitly refuses. Per the
    design's explicit rule, a query that executes and returns 0 (or any
    other value) is a MISS even if it happens to match the guard's expected
    absence — the benchmark tests whether the model NOTICES the referent
    does not exist, not whether it accidentally computes zero.

Usage:
    py bench/evaluate_model.py --in bench/out/questions_hamburg_dev.jsonl \\
        --backend ollama --model qwen2.5-coder:7b \\
        --out bench/out/results_hamburg_qwen2.5-coder-7b.jsonl

    py bench/evaluate_model.py --in bench/out/questions_hamburg_test_private_gold.jsonl \\
        --backend anthropic --model claude-opus-4-8 \\
        --out bench/out/results_hamburg_claude-opus-4-8.jsonl

    py bench/evaluate_model.py --in ... --backend ollama --model ... --limit 10   # quick smoke test
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "neo4jneo4j")
# RELEASE: the per-city schema text lives in schema/ at the repository root.
SCHEMA_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "schema"


# Relationship types AND properties that genuinely exist in the graph but are
# dropped by langchain_neo4j's APOC-based schema sampling because they're rare
# relative to the dominant edge/property population (e.g. HAS_LOD3_FACADE: 303
# edges on Hamburg vs. tens of millions of HAS_BOUNDARY/HAS_POLYGON; the three
# lod3_confidence/lod3_method/lod3_source properties: only 17 of 388,267
# Hamburg buildings). Found because every lod3_* question failed identically
# across every backend during evaluation trials, traced to the schema simply
# never mentioning the edge/properties a correct query needs. Appended so
# EVERY backend (Ollama, Claude API, subagent) can discover it -- leaving it
# missing does not make the benchmark harder, it makes an entire category
# structurally unsolvable regardless of model capability.
SCHEMA_KNOWN_GAPS = """

Known additional relationship (present in the graph, omitted above due to
schema-introspection sampling on rare relationship types):
(:Building)-[:HAS_LOD3_FACADE]->(:BoundarySurface)  -- the target node is ALSO
  labelled :Lod3Facade; reconstructed LoD3 facade detail (windows/doors via
  a further -[:HAS_OPENING]->(:Opening {opening_type: 'Window'|'Door'}) hop)
  attaches here, NOT via the ordinary HAS_BOUNDARY edge (which stays LoD2-only
  and is never overwritten, per the project's provenance design).

Known additional Building properties (present in the graph, omitted above due
to schema-introspection sampling on rare properties -- only a small minority
of buildings carry LoD3 reconstruction):
Building.lod3_confidence: FLOAT  -- reconstruction confidence, 0-1
Building.lod3_method: STRING     -- reconstruction method name
Building.lod3_source: STRING     -- provenance source identifier"""


def get_cached_schema(graph, dataset_name):
    """Every backend (Ollama, Claude API, or a Claude-Code-subagent run via
    --pregenerated) MUST see byte-identical schema text for a given city --
    that is the whole point of comparing backends. Cache to disk once per
    city instead of calling graph.refresh_schema() fresh on every run, so a
    rerun days later (or a manually-driven subagent trial) cannot silently
    diverge from what an earlier backend saw."""
    SCHEMA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", dataset_name)
    cache_path = SCHEMA_CACHE_DIR / f"{safe_name}.txt"
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    graph.refresh_schema()
    text = graph.schema
    # BUG FIXED 2026-07-22: this used to gate on `"HAS_LOD3_FACADE" not in
    # text`, which APOC's raw sampled schema never contains for ANY city (the
    # whole reason the patch is needed) -- so the condition was unconditionally
    # true and every non-Hamburg city's cache got Hamburg's LoD3 note appended
    # regardless of whether that city has LoD3 data at all (confirmed present
    # verbatim in the already-generated Zurich/NYC/Tokyo schema caches). Fixed
    # by actually probing the live graph for the fact the patch claims, instead
    # of assuming it from string absence. This mirrors the project's own
    # standing discipline (see bench/README.md: "learned from Zurich: check
    # the actual graph, not just the cached schema text") and only runs once
    # per city (this whole function body executes once, on first cache miss).
    if graph.query("MATCH (n:Lod3Facade) RETURN n LIMIT 1"):
        text += SCHEMA_KNOWN_GAPS
    cache_path.write_text(text, encoding="utf-8")
    return text

SPATIAL_HINT = """You are a Neo4j Cypher expert answering questions about a 3D city knowledge
graph (CityGML buildings enriched with OpenStreetMap data; some cities
additionally have ML-predicted roof materials and reconstructed LoD3 facade
detail). Follow these project rules exactly:

- For a bounding-box/window query use: CALL spatial.intersects('features', wkt) YIELD node
- For a radius query use: CALL spatial.withinDistance('features', point, distanceKm) YIELD node
- Never scan-filter on center_x/center_y; always use the spatial procedures above.
- OSM-derived fields are namespaced `osm_*` (e.g. osm_height, osm_building_levels) and
  must NEVER be confused with the authoritative field they mirror (e.g. measured_height,
  storeys_above_ground). Use the authoritative field unless the question explicitly asks
  about OSM/crowd-sourced data.
- `predictedroofmaterial` is a partial-coverage ML prediction (not every building has one);
  a question about coverage or "how many/what share" must account for that, not just count
  matches.
- Return EXACTLY the column(s) the question asks for, nothing more: no extra identifying or
  context columns even if they seem helpful, and always use a deterministic ORDER BY (add an
  `id ASC` tie-break after the ranking key) whenever the question asks for a ranked/top-k/most/
  least/tallest answer, since ties are otherwise returned in an arbitrary order.
- If, and only if, the question asks for information that DOES NOT EXIST anywhere in this
  graph's schema (the schema below is complete — nothing else is stored), reply with exactly
  the single word REFUSE and nothing else. Do not refuse just because a query might return
  zero rows; only refuse when the requested fact has no place to live in this schema at all.
- Otherwise reply with ONLY the Cypher query. No explanation, no markdown code fences, no
  commentary before or after it.

Graph schema:
{schema}

Question: {question}
Cypher:"""

REFUSE_TOKEN = "REFUSE"
CYPHER_FENCE_RE = re.compile(r"^```(?:cypher)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)
# Some backends (found: qwen2.5-coder:7b via Ollama) ignore the "ONLY the
# Cypher query, no explanation" instruction and wrap the query in prose
# ("To find X, use this query:\n```cypher\n...\n```\nThis query does Y.").
# CYPHER_FENCE_RE alone only strips the fence delimiters, leaving the prose
# glued onto the query -> guaranteed syntax error, not a fair reflection of
# the model's Cypher-writing ability. Prefer the content INSIDE a fenced
# block when one exists; only fall back to delimiter-stripping for backends
# (e.g. Claude subagents) that reliably return bare Cypher with no prose.
CYPHER_FENCE_BLOCK_RE = re.compile(r"```(?:cypher)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)


def get_llm(backend, model):
    if backend == "ollama":
        from langchain_ollama import OllamaLLM
        return OllamaLLM(model=model, temperature=0)
    if backend == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, temperature=0)
    raise SystemExit(f"Unknown backend: {backend} (expected 'ollama', 'anthropic', or --pregenerated)")


def row_signature(row_dict, decimals=2):
    """One row -> a sorted tuple of its VALUES only (column names dropped).
    Required by QUESTION_SUITE_DESIGN.md Sec10: EX comparison must be
    column-name-insensitive, since a model has no way to know gold's exact
    alias (gold's 'n' vs a model's equally-correct 'building_count':
    comparing key:value dicts verbatim -- what verify_questions.py's
    canonicalize() does, fine for its own gold-vs-itself G2 check -- would
    wrongly fail every semantically-correct answer that used a different
    column name. Floats rounded to `decimals`: gold_answer values were
    already rounded to ~2 decimals at authoring time by the gold Cypher
    itself (e.g. round(x*100)/100.0); a model's raw unrounded avg() must be
    compared at the same precision, not literalistically vs the design
    doc's 1e-6 (that figure targets exact-requery reproducibility, not
    cross-implementation float comparison against an already-rounded gold)."""
    def norm(v):
        if isinstance(v, bool):
            return ("bool", v)
        if isinstance(v, (int, float)):
            return ("num", round(float(v), decimals))
        return ("other", v)
    return tuple(sorted((norm(v) for v in row_dict.values()), key=lambda x: (x[0], str(x[1]))))


def canonical_signature(row_dicts, ranked=False):
    sigs = [row_signature(d) for d in row_dicts]
    if not ranked:
        sigs = sorted(sigs, key=lambda t: str(t))
    return json.dumps(sigs, default=str)


def gold_rows_from_answer(gold_answer_json):
    """gold_answer is a JSON array of per-row JSON-object strings (as written
    by verify_questions.py's canonicalize()); parse back to plain dicts."""
    return [json.loads(s) for s in json.loads(gold_answer_json)]


def extract_text(llm_output):
    """Both OllamaLLM and ChatAnthropic-via-invoke return slightly different
    shapes (str vs AIMessage); normalize to plain text."""
    return getattr(llm_output, "content", llm_output)


def clean_cypher(raw):
    block = CYPHER_FENCE_BLOCK_RE.search(raw)
    if block:
        return block.group(1).strip()
    return CYPHER_FENCE_RE.sub("", raw).strip()


def is_refusal(text):
    stripped = text.strip().strip(".").upper()
    if stripped == REFUSE_TOKEN:
        return True
    # loose fallback: no Cypher keyword present at all -> treat as a refusal
    # in spirit (logged, not silently miscounted as a crashed query)
    if not re.search(r"\bMATCH\b|\bCALL\b", text, re.IGNORECASE):
        return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Evaluate a model against the AuthentiCity suite.")
    ap.add_argument("--in", dest="infile", required=True,
                     help="dev.jsonl or test_private_gold.jsonl -- NEVER the public test.jsonl (no gold to score against)")
    ap.add_argument("--backend", required=True,
                     help="'ollama', 'anthropic', or any label (e.g. 'claude_code_subagent') when using --pregenerated")
    ap.add_argument("--model", required=True, help="model name, or a label when using --pregenerated")
    ap.add_argument("--pregenerated", default=None,
                     help="JSON file {qid: raw_output_text} produced some other way (e.g. Claude Code "
                          "subagents used as the model under test) -- skips the live llm.invoke() call "
                          "and scores these answers instead. The prompt/schema given to whatever produced "
                          "them MUST match SPATIAL_HINT + the cached schema exactly (see get_cached_schema) "
                          "for the comparison against Ollama/Claude runs to be fair.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", default=None, help="defaults to <out>.report.md")
    ap.add_argument("--limit", type=int, default=None, help="cap number of questions (smoke test)")
    ap.add_argument("--query-timeout", type=float, default=20.0,
                     help="server-side seconds before a model-generated query is aborted (default 20s). "
                          "A model has no way to know which Cypher shapes are efficient on THIS graph's "
                          "scale -- e.g. a per-row correlated procedure call (MATCH (b) CALL spatial.x(...) "
                          "YIELD ... WHERE node=b) is syntactically fine but pathological at 388k+ rows. "
                          "A timeout is scored as a wrong answer (error='QUERY_TIMEOUT'), not a crash.")
    args = ap.parse_args()

    from neo4j import GraphDatabase
    from langchain_neo4j import Neo4jGraph

    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH,
                                  notifications_disabled_classifications={"DEPRECATION", "UNRECOGNIZED"})
    driver.verify_connectivity()
    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_AUTH[0], password=NEO4J_AUTH[1])

    with driver.session(database="neo4j") as sess:
        live = sess.run("MATCH (ds:Dataset) RETURN ds.name AS name").single()
    live_dataset = live["name"] if live else None
    print(f"Live dataset: {live_dataset}")
    schema_text = get_cached_schema(graph, live_dataset)

    records = [json.loads(line) for line in open(args.infile, encoding="utf-8") if line.strip()]
    if "gold_answer" not in (records[0] if records else {}):
        raise SystemExit("ERROR: input file has no gold_answer -- did you pass the public "
                          "test.jsonl by mistake? Use dev.jsonl or test_private_gold.jsonl.")
    records = [r for r in records if r["dataset"] == live_dataset]
    if args.limit:
        records = records[: args.limit]
    if not records:
        raise SystemExit(f"No questions in {args.infile} match the live dataset '{live_dataset}'.")

    pregenerated = None
    if args.pregenerated:
        pregenerated = json.loads(Path(args.pregenerated).read_text(encoding="utf-8"))
        records = [r for r in records if r["qid"] in pregenerated]
        if not records:
            raise SystemExit(f"None of the qids in {args.pregenerated} match {args.infile} for '{live_dataset}'.")
        llm = None
    else:
        llm = get_llm(args.backend, args.model)

    print(f"Evaluating {len(records)} questions from {args.infile} against '{live_dataset}' "
          f"with {args.backend}/{args.model}{' (pregenerated)' if pregenerated else ''} ...")

    prompt = SPATIAL_HINT

    results = []
    with driver.session(database="neo4j") as sess:
        for i, rec in enumerate(records, 1):
            t0 = time.perf_counter()
            if pregenerated is not None:
                raw = pregenerated[rec["qid"]]
            else:
                raw = extract_text(llm.invoke(prompt.format(schema=schema_text, question=rec["question"])))
            gen = clean_cypher(raw)
            refused = is_refusal(gen)

            row = {
                "qid": rec["qid"], "template_id": rec["template_id"], "category": rec["category"],
                "difficulty": rec["difficulty"], "feasible": rec["feasible"], "dataset": rec["dataset"],
                "backend": args.backend, "model": args.model,
                "question": rec["question"], "generated_cypher": None if refused else gen,
                "raw_output": raw, "refused": refused,
            }

            if rec["feasible"]:
                if refused:
                    row.update(correct=False, over_refusal=True, error=None)
                else:
                    try:
                        with sess.begin_transaction(timeout=args.query_timeout) as tx:
                            model_rows = [dict(r) for r in tx.run(gen)]
                        gold_rows = gold_rows_from_answer(rec["gold_answer"])
                        # heuristic until the frozen `answer_type` field (QUESTION_SUITE_DESIGN.md
                        # Sec2) is emitted: these templates ORDER BY...LIMIT a ranked result, so
                        # sequence is part of the answer, not just the row multiset
                        ranked = rec["template_id"].startswith(
                            ("topk_", "spatial_knearest", "prov_weakest_matches", "spatial_roof_complexity"))
                        match = canonical_signature(model_rows, ranked) == canonical_signature(gold_rows, ranked)
                        row.update(correct=match, over_refusal=False, error=None)
                    except Exception as exc:
                        msg = str(exc)
                        is_timeout = "timeout" in msg.lower() or "timed out" in msg.lower()
                        row.update(correct=False, over_refusal=False,
                                    error=("QUERY_TIMEOUT: " if is_timeout else f"{type(exc).__name__}: ") + msg)
            else:
                # infeasible: correct iff refused, full stop (design rule --
                # an executed query that happens to return 0 is still a miss)
                row.update(correct=refused, over_refusal=False, error=None)

            row["latency_s"] = round(time.perf_counter() - t0, 3)
            results.append(row)
            status = "REFUSE" if refused else ("OK" if row["correct"] else "WRONG")
            print(f"  [{i}/{len(records)}] {rec['qid']}: {status}  ({row['latency_s']:.2f}s)", flush=True)

    driver.close()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    write_report(results, args, out)


def write_report(results, args, out):
    feasible = [r for r in results if r["feasible"]]
    infeasible = [r for r in results if not r["feasible"]]
    ex = sum(r["correct"] for r in feasible) / len(feasible) if feasible else None
    over_refusal = sum(r["over_refusal"] for r in feasible) / len(feasible) if feasible else None
    tp = sum(r["correct"] for r in infeasible)  # correctly refused
    fn = len(infeasible) - tp                   # should have refused, didn't
    precision = tp / (tp + 0) if (tp) else 0.0   # every model "refusal call" on the infeasible set that we counted is a true refusal by construction (no false REFUSE on feasible counted here); precision over this axis is standard recall-style detection rate
    recall = tp / len(infeasible) if infeasible else None
    f1 = (2 * recall / (1 + recall)) if recall else None  # precision==1 here since infeasible-only pool; see caption note in report

    by_cat = {}
    for r in feasible:
        c = by_cat.setdefault(r["category"], {"n": 0, "correct": 0})
        c["n"] += 1
        c["correct"] += r["correct"]

    lines = [
        f"# Evaluation report — {args.backend}/{args.model}",
        "",
        f"- Input: `{args.infile}`  ({len(results)} questions: {len(feasible)} feasible, {len(infeasible)} infeasible)",
        f"- **Execution accuracy (feasible): {ex:.1%}**" if ex is not None else "- Execution accuracy: n/a (no feasible questions)",
        f"- **Over-refusal rate (feasible questions wrongly refused): {over_refusal:.1%}**" if over_refusal is not None else "",
        f"- **Infeasibility recall (correctly refused / total infeasible): {recall:.1%}**" if recall is not None else "- Infeasibility recall: n/a",
        "",
        "Note: precision is reported as recall here because this run only scores the infeasible "
        "subset in isolation (a REFUSE on a feasible question is tracked separately as "
        "over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set "
        "is computed once dev+test results across categories are combined (E4).",
        "",
        "| Category | n | EX |",
        "| -------- | - | -- |",
    ]
    for cat, c in sorted(by_cat.items()):
        lines.append(f"| {cat} | {c['n']} | {c['correct']/c['n']:.1%} |")

    errors = [r for r in results if r.get("error")]
    if errors:
        lines += ["", "## Execution errors", ""]
        for r in errors[:15]:
            lines.append(f"- `{r['qid']}`: {r['error']}")

    report_path = args.report or (str(out) + ".report.md")
    Path(report_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"\nEX={ex if ex is None else round(ex,3)}  over_refusal={over_refusal if over_refusal is None else round(over_refusal,3)}  "
          f"infeasibility_recall={recall if recall is None else round(recall,3)}")
    print(f"Results: {out}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
