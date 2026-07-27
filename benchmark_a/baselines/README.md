# Cached baseline runs

Everything from the two reference evaluations is here, so their scores can be recomputed, audited, and diagnosed per question without running any model.

```text
baselines/
├── results/        <city>_<model>_<split>.jsonl   per-question outcome, incl. the generated Cypher
├── reports/        <city>_<model>_<split>.md      the scored summary per run
├── model_outputs/  <city>_<model>_<split>.json    raw {qid: model output} maps, as the harness consumes them
├── eval_subsets/   <city>_<split>.jsonl           the exact question set each run was scored on
└── prompts/<city>/ batch_*_prompt.txt             the exact prompts, and the raw responses received
```

Recompute the reported tables with no database and no inference:

```bash
python ../harness/summarize_results.py --glob '*_dev.jsonl'
python ../harness/summarize_results.py --glob '*_test.jsonl'
```

Re-score from the raw model answers (needs a restored graph, since scoring executes each query):

```bash
python ../harness/evaluate_model.py \
  --in eval_subsets/hamburg_dev.jsonl \
  --backend claude_code_subagent --model claude-sonnet-5 \
  --pregenerated model_outputs/hamburg_claude-sonnet-5_dev.json \
  --out /tmp/rescored.jsonl
```

---

## The two models

| | Claude Sonnet 5 | qwen2.5-coder:7b |
| --- | --- | --- |
| Kind | commercial frontier model | local open-weight model |
| Serving | run closed book, schema-only context, no tool or database access | Ollama, `Q4_K_M` quantization |
| Context | byte-identical per-city schema text from [../../schema/](../../schema/) | the same bytes |
| Scoring timeout | 20 s per query | 20 s per query |

Latency is recorded but not comparable between them: the commercial run's timing covers Cypher execution only, the Ollama run's covers inference plus execution.

## What each run was scored on

The baselines were evaluated on **523 question instances per model** (392 development, 131 held-out test), one phrasing per template per city, not on all 1,394 released instances. Per split:

| City | Dev instances (feasible / infeasible) | Test instances (feasible / infeasible) |
| --- | --- | --- |
| Hamburg | 99 (89 / 10) | 31 (29 / 2) |
| Helsinki | 92 (82 / 10) | 32 (28 / 4) |
| Zurich | 75 (65 / 10) | 24 (20 / 4) |
| New York | 49 (39 / 10) | 18 (14 / 4) |
| Tokyo | 77 (67 / 10) | 26 (24 / 2) |

The evaluated sets are in `eval_subsets/` (gold withheld on held-out qids, as everywhere in this repository). 81 of the 84 templates are covered.

Two filters produced these sets, both stated so the numbers are not over-read:

1. **One phrasing per template per city.** The runs predate the paraphrase expansion that took every template to three accepted phrasings and added the German and Japanese variants. Adding paraphrases would multiply cost without adding a distinct capability probe, so this is a limit of the runs, not a sampling claim.
2. **Cross-city fairness exclusions.** A template whose gold reads a property that exists only on another city was excluded on the non-home city. The models are instructed to refuse when the information is absent from the schema they were given, which is exactly what they did on those questions; counting a compliant refusal as an over-refusal would be a scoring artifact. Those templates have since been brought under the declarative requirement gate, so on the released suite they simply do not instantiate off their home city.

## Important: these runs predate the spatial gold correction

The released suite carries corrected proximity and window gold (see [../../CHANGELOG.md](../../CHANGELOG.md)). The cached runs were scored before that fix, so:

- **457 of the 523 evaluated instances exist verbatim in the released suite** and their outcomes carry over unchanged.
- **66 do not**, because the fix changed either the gold query or the sampled window, so the question text or its `qid` differs. Affected templates and counts: `spatial_bbox_count` (20), `spatial_isolated` (10), `spatial_bbox_agg` (8), `spatial_bbox_tallest` (8), `prov_lod3_high_confidence_count` (6), `spatial_bbox_by_rooftype` (4), `multihop_building_parts` (3), `filter_has_basement` (2), `cov_share` (2), `cov_by_district` (1), `cov_material_distribution` (1), `cov_multi_material_count` (1).

What this means in practice: the reported numbers are correct for the question sets in `eval_subsets/`, which are shipped precisely so the claim is checkable, and the qualitative findings (semantic against syntactic failure, no refusal behavior in the small model, timeouts at the largest scale, failure concentration in the new categories) do not hinge on those 66 instances. A like-for-like comparison against the released suite needs a fresh run: cached model answers cannot be reused for a question whose text changed. If you evaluate a new model, run it on the released question files and say so; do not mix your numbers with these.

## Reading a results file

One JSON object per question:

| Field | Meaning |
| --- | --- |
| `qid`, `template_id`, `category`, `difficulty`, `feasible`, `dataset` | the question, as in the question file |
| `backend`, `model` | how the answer was produced |
| `question` | the exact natural-language input |
| `raw_output` | the model's unmodified reply |
| `generated_cypher` | the query extracted from it and executed |
| `refused` | the model explicitly declined |
| `correct` | execution accuracy for a feasible question; correct refusal for an infeasible one |
| `over_refusal` | declined a feasible question |
| `error` | why the query did not execute, when it did not |
| `latency_s` | see the caveat above |

No results file contains a gold query or a gold answer, so these files are safe to redistribute even for held-out questions.

## Per-question diagnosis

The `reports/*.md` files carry the scored summary per run, including the per-category breakdown. The recurring failure causes, established by diffing model against gold query by query rather than assumed, are listed in [../README.md](../README.md). Two of them are template-design findings rather than model errors and are recorded as such: an output-shape ambiguity on coverage-share questions, and a window-scoping ambiguity on isolation questions that recurs across cities.

## Adding a run

Community results are welcome. Open a pull request adding `baselines/community/<model>_<city>_<split>.jsonl` plus a short note on the serving setup and the context given to the model, or send the files by email for held-out test scoring. State clearly if the model received anything beyond the schema text: that is a different experiment, not a comparable number.
