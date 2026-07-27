# Benchmark A: natural-language to Cypher

**1,394 questions, 84 schema-grounded templates, nine categories, five cities, three languages, over graphs where facts differ in source, confidence, and coverage.**

Given a natural-language question and the graph schema, a model must either produce an executable Cypher query whose result matches the gold answer, or explicitly declare the question infeasible. The second option is not a formality: 153 of the questions have no valid answer, each paired with a guard query that proves on that city's graph that the information is absent.

Five of the nine categories are the contribution, because no existing text-to-query benchmark can express them on a single-source schema:

| Category | What a model has to get right | Templates | Instances |
| --- | --- | --: | --: |
| `spatial` | window, proximity, nearest neighbor, geometric multi-hop, 3D structure, density, over R-tree indexed geometry in a metric CRS | 12 | 462 |
| `cross_source` | compare authoritative against crowd-sourced values in both directions, and report what the crowd layer knows where the authoritative source is silent | 13 | 237 |
| `provenance` | constrain by source or by match confidence, including traps ("using only authoritative data ...") where reading the crowd-sourced value gives a plausible but wrong answer | 12 | 162 |
| `coverage` | recognize that an aggregate over a partially covered attribute is meaningful only relative to the covered subset | 6 | 24 |
| `infeasible` | decline instead of fabricating a query | 8 | 153 |
| `aggregate`, `filter_topk`, `multihop`, `lod3` | conventional grounding, retrieval, ranking, traversal, plus reconstructed-facade structure | 43 | 356 |

Two devices multiply what those categories measure. **Feasibility is a property of the data**, so the same template is coverage-aware on Hamburg and infeasible elsewhere, with the question text unchanged. And **ten templates are additionally posed in German and Japanese** (95 instances), including three Tokyo templates whose gold queries filter on Japanese property keys.

Full generated inventory, per template: [template_inventory.md](template_inventory.md) and [template_inventory.csv](template_inventory.csv).

**Where the specification lives.** The authoritative specification of the suite is executable, not prose: [harness/templates.py](harness/templates.py) holds all 84 template definitions with their natural-language phrasings, gold queries (except for the 25 held-out templates), slot providers, and the per-template requirement gate; [harness/verify_questions.py](harness/verify_questions.py) implements the gates; [harness/split_dataset.py](harness/split_dataset.py) implements the split policy; and [harness/evaluate_model.py](harness/evaluate_model.py) implements the scoring rules described below. The generated [template_inventory.md](template_inventory.md) is the readable index over all of it. Reading those four files tells you exactly what the benchmark is, with no risk of a prose document drifting from the shipped data.

---

## Files

```text
benchmark_a/
├── questions/
│   ├── dev.jsonl                 1,024 development questions, WITH gold Cypher and gold answers
│   ├── test.jsonl                  370 held-out questions, text only (gold withheld)
│   ├── per_city/<city>_{dev,test}.jsonl   the same, split by city
│   └── split_assignment.json     which template went to which split, and why
├── template_inventory.{md,csv}   generated; every template with its category, split, cities, gold state
├── harness/                      generator, verifier, splitter, evaluator, scorer, review sampler
├── verification/                 per-city G1-G4 reports for the released suite
├── baselines/                    cached model runs: results, reports, raw outputs, exact prompts
└── human_review/                 the stratified >=20 % review sample
```

**The primary key of a question is the pair `(dataset, qid)`, not `qid` alone.** A cross-city template instantiates once per city under the same `qid`, so joining results by `qid` across cities will collide. Within one city, `qid` is unique.

### Question record

| Field | Meaning |
| --- | --- |
| `qid` | question id, unique within a city; encodes the template and the phrasing (and the slot value where a template samples several) |
| `template_id` | the template it came from; **the split unit** |
| `category`, `tier`, `difficulty` | category as above; tier 2 marks the Hamburg-only deep-fusion categories; authored difficulty 1 to 5 |
| `feasible` | `false` for the infeasible category, where the expected behavior is a refusal |
| `lang` | `en`, `de`, or `ja` |
| `question` | the natural-language question given to the model |
| `gold_cypher` | the gold query (development split only) |
| `gold_answer`, `gold_answer_sha1` | the canonicalized materialized answer and its hash (development split only) |
| `guard` | for infeasible questions, the query that proves absence (development split only) |
| `slots` | the slot values read from the graph at generation time |
| `dataset` | which city graph this instance belongs to |
| `allow_empty` | whether an empty result is a legitimate gold answer |
| `verified` | passed gates G1 to G4 against the released graph |

Difficulty distribution over the 1,394 instances: 47 at level 1, 272 at 2, 714 at 3, 247 at 4, 114 at 5. Per-city: Hamburg 346, Helsinki 319, Tokyo 291, Zurich 259, New York 179.

---

## Evaluating a model

Restore the city graph first ([../docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md)); scoring executes the model's query against the live graph.

```bash
python harness/evaluate_model.py \
  --in questions/per_city/hamburg_dev.jsonl \
  --backend ollama --model qwen2.5-coder:7b \
  --out /tmp/results_hamburg_mymodel.jsonl

python harness/summarize_results.py --results-dir /tmp --glob 'results_*.jsonl'
```

Backends: `ollama`, `anthropic`, or any label together with `--pregenerated <qid-to-output JSON>` for a model you ran elsewhere.

**Context parity is mandatory and enforced.** Every backend receives byte-identical, schema-only text per city, from [../schema/](../schema/). No database access, no tool use, no retrieval, no example gold queries. If you give a model more than that, say so, and do not compare the number against the shipped baselines.

### Scoring

**Feasible questions** are scored by execution accuracy: the result set must match the gold answer after canonicalization. Canonicalization is order-insensitive over rows, **column-name insensitive** (a model calling its count `building_count` where gold calls it `n` is not wrong), and rounds floats. Return exactly the requested columns: scoring compares full value tuples per row, so an extra column, even a correct one, changes the row signature and fails. Add a deterministic `ORDER BY ..., id ASC` tie-break to any ranked answer.

Every feasible question falls into exactly one of four outcomes, which sum to 100 %:

| Outcome | Meaning |
| --- | --- |
| **EX** | executed and result-correct |
| **executed-but-wrong** | valid Cypher, wrong result: a semantic failure |
| **errored** | the query did not execute (syntax, type, or timeout) |
| **over-refusal** | wrongly declined a feasible question |

This decomposition is the point. Aggregate accuracy hides the difference between a model that cannot emit valid Cypher and one that emits valid Cypher meaning the wrong thing, and the two baselines fail in exactly those two opposite ways.

**Infeasible questions** are correct only if the model explicitly refuses. A query that executes and happens to return zero is a miss: the benchmark tests whether the model notices that the referent does not exist, not whether it accidentally computes zero. Reported as infeasibility precision, recall, and F1, with over-refusals as the false positives. A model that never refuses has recall 0 and undefined precision and F1, which is a sharper statement than a low score.

### The held-out test split

`test.jsonl` ships questions only. Gold queries, guards, and materialized answers for its 25 templates are withheld, and the released `harness/templates.py` has those 25 gold and guard literals replaced by a placeholder while everything else in the module is intact, so the development split regenerates end to end.

To get a test-split score, send us your `results_*.jsonl` (the harness output, containing `qid`, `dataset`, and the generated Cypher per question) by email to <son.nguyen@hcu-hamburg.de> or as a pull request adding it under `baselines/community/`, and we will score it against the private gold and publish the numbers alongside a description of your setup. Report the development split as your primary number if you would rather not wait: it is 1,024 questions over 59 templates and is not a small evaluation.

Splitting by template rather than by instance means the test set contains **unseen query patterns**, not unseen paraphrases of seen ones. That is deliberate and makes the test split genuinely harder, which the baselines show.

---

## Reference results

Two model families, both closed book with schema-only context. Full tables, per-question outcomes, exact prompts, and raw responses: [baselines/](baselines/) (read [baselines/README.md](baselines/README.md) first, it states what the numbers do and do not cover).

| Model | Split | Hamburg | Helsinki | Zurich | New York | Tokyo |
| --- | --- | --: | --: | --: | --: | --: |
| Claude Sonnet 5 | dev | 60.7 | 56.1 | 61.5 | 69.2 | 53.7 |
| | test | 58.6 | 42.9 | 60.0 | 50.0 | 41.7 |
| qwen2.5-coder:7b | dev | 19.1 | 14.6 | 9.2 | 10.3 | 6.0 |
| | test | 20.7 | 10.7 | 15.0 | 14.3 | 12.5 |

Execution accuracy in percent on the feasible questions. What the decomposition shows:

- **Claude's misses are semantic, not syntactic.** Its valid-execution rate is 93 to 100 %, so almost all of the remaining mass is executed-but-wrong. Infeasibility F1 is 72 to 95 on the development split: it declines appropriately most of the time.
- **qwen fails at producing runnable Cypher at all** 40 to 54 % of the time, overwhelmingly Cypher syntax errors concentrated in the spatial category, where it hallucinates PostGIS `ST_*` functions that have no Cypher equivalent, despite the `spatial.*` procedures being given explicitly in its context.
- **qwen never refuses.** Zero of the infeasible questions on any city, on either split. It always fabricates a plausible query instead, for example mapping "owner" to `osm_operator`, a real property with the wrong meaning.
- **Errors on New York and Tokyo test splits are timeouts, not confusion**: correct-shaped spatial queries that do not finish over 1 M and 2 M buildings.
- **Failures concentrate in the new categories.** On Hamburg, Claude scores 100 % on LoD3 and 83 % on aggregates but 40 % on cross-source and 31 % on provenance.

The recurring, cross-city failure causes, diagnosed per question rather than assumed, are: a missing deterministic tie-break on ranked answers; reading a mirrored `osm_*` scalar instead of traversing the `ENRICHED_BY` edge (or the reverse, where gold deliberately uses the mirror because edge-level aggregation overcounts multi-edge buildings by 1.76 to 2.19 times on Tokyo); missing rounding to the gold's precision; an unbounded cross-join where the gold pre-filters spatially; window-scoping ambiguity on isolation questions; and returning extra columns.

---

## Construction and verification

The suite is generated, not authored by hand, and every question is verified against the released graph.

**Grounded slots.** Every slot value (district ids, function names, materials, height thresholds from the city's own percentiles, buildings that actually host a POI, bounding-box windows drawn from the building-coordinate percentile box) is read from the live graph, so no question can reference data that does not exist. A provider that returns nothing disables its template with a warning rather than emitting a broken question.

**Declarative requirement gate.** Each feasible template declares the graph tokens its gold query reads (a property, a `CamelCase` label, or an `UPPER_SNAKE` edge type). The generator probes the live graph and instantiates the template only where those tokens exist. This is data-driven on measured presence, not a hardcoded per-city allowlist, so instantiation is deterministic on every rerun. It is also what makes the feasibility flip principled: the mirror-image infeasible templates check citywide *absence*, so refusal is tested exactly where a layer is missing.

**Five gates.** G1 the gold executes; G2 its canonicalized answer hash is identical across three runs; G3 the result is non-empty unless the template permits emptiness; G4 an infeasible question's guard proves absence (count zero) on that city; G5 every rebuild re-materializes all gold answers and any change bumps the suite version with a changelog entry. Result: **1,394 of 1,406 instantiated questions verified (99.1 %)**, each of the twelve non-verified being a deliberate feasibility flip. Per-city reports: [verification/](verification/).

**Human review.** 282 questions (20.2 %), stratified by category, difficulty, city, and language, reviewed by the authors. It found a defect the machine gates had passed, in five proximity templates, and that defect was fixed before release. Details and the sample: [human_review/](human_review/) and [../docs/QUALITY_GATES.md](../docs/QUALITY_GATES.md).

Reproduce any of this: [../docs/REPRODUCE.md](../docs/REPRODUCE.md).

---

## Design choices worth knowing before you interpret a score

**Inlined literals.** Gold queries inline every value rather than using query parameters, so any query in this repository is copy-pasteable into the Neo4j Browser.

**Metric CRS and R-tree semantics.** All five graphs are in a projected metric CRS. The R-tree layers store Cartesian metres, while `spatial.withinDistance` interprets its radius in kilometres against a geographic layer. Proximity gold therefore uses an R-tree window in metres plus an exact `point.distance` recheck, or a plain top-k over `point.distance`. A model that reaches for `withinDistance` with a metre radius will silently get almost nothing, which is a fair test: the schema text states the procedures available, and the correct idiom follows from the CRS.

**No precomputed proximity edges.** Deliberately. The suite tests live spatial procedures rather than a materialized shortcut, uniformly across city sizes.

**Height sentinels.** Gold queries that aggregate height guard with `> -999`, because Tokyo stores `-9999` for missing heights. Storey templates deliberately do not filter the `9999` storey sentinel: the gold is correct with respect to the stored graph, and the sentinel is documented as a data property rather than repaired.

**One defensible answer shape per question.** Some questions admit more than one reasonable shape (a bare fraction against a count-plus-coverage triple). Gold fixes one. Where that cost a baseline a point it is stated per question in the baseline reports rather than quietly absorbed.

---

## License and citation

Questions, gold queries, gold answers, and reports are CC BY 4.0; the harness is MIT; question content quotes values from the released graphs, which are ODbL 1.0. See [../DATA_LICENSES.md](../DATA_LICENSES.md). Cite as in [../CITATION.cff](../CITATION.cff).
