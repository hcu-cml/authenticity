# Harness

The scripts that generate, verify, split, and score the question suite. They are the code that produced the released files, shipped as they ran, so the suite's construction and scoring are inspectable rather than described.

```text
templates.py            84 template definitions: phrasings, gold queries, slot
                        providers, and the per-template requirement gate
generate_questions.py   instantiate templates against a live city graph
verify_questions.py     the verification gate (G1 to G4) and gold materialization
split_dataset.py        split by template_id into dev and held-out test
evaluate_model.py       run a model, execute its Cypher, score it
summarize_results.py    the execution-accuracy decomposition and its LaTeX rows
build_review_sample.py  draw the stratified human-review sample
```

Pipeline, one city at a time (restore that city's dump first, since slot values are read from the live graph):

```bash
python generate_questions.py --out /tmp/raw.jsonl
python verify_questions.py --in /tmp/raw.jsonl --out /tmp/verified.jsonl --report /tmp/report.md
python split_dataset.py --dev-fraction 0.7          # after all five cities
python evaluate_model.py --in ../questions/per_city/hamburg_dev.jsonl \
       --backend ollama --model qwen2.5-coder:7b --out /tmp/results.jsonl
python summarize_results.py --glob '*_dev.jsonl'
```

Full commands with the release paths: [../../docs/REPRODUCE.md](../../docs/REPRODUCE.md).

## Two things that differ from the code as it ran

**`templates.py` has the held-out gold withheld.** The gold Cypher and guard queries of the 25 test-split templates are replaced by the string `<withheld: gold query of a held-out test template>`; the file header says so. Everything else, including all 59 development templates, every slot provider, and the requirement gate, is unchanged, so the development split regenerates end to end. The unredacted module stays with the authors, who score submitted test-split runs.

**Two path defaults were rewritten for this layout.** `summarize_results.py` now defaults to `../baselines/results` with a `--results-dir` override and a `*.jsonl` glob, and `evaluate_model.py` reads the per-city schema text from `schema/` at the repository root. Scoring, canonicalization, and gate logic are untouched. Verified after the rewrite: `summarize_results.py` reproduces the reported per-city numbers exactly from the cached results.

**Docstrings still reference the construction repository's layout** (`bench/out/...` for intermediate files, and the design notes that guided authoring). Those paths do not exist here; the release equivalents are:

| Docstring reference | Release location |
| --- | --- |
| `bench/out/questions_<city>_dev.jsonl` | `benchmark_a/questions/per_city/<city>_dev.jsonl` |
| `bench/out/questions_{dev,test}.jsonl` | `benchmark_a/questions/{dev,test}.jsonl` |
| `bench/out/questions_<city>_test_private_gold.jsonl` | withheld, not released |
| `bench/out/results_*.jsonl` | `benchmark_a/baselines/results/` |
| `bench/out/schema_cache/` | `schema/` |
| `bench/out/verification_report_<city>.md` | `benchmark_a/verification/` |
| `QUESTION_SUITE_DESIGN.md` sections | [../README.md](../README.md) and [../template_inventory.md](../template_inventory.md) |

## Requirements

`pip install -r ../../requirements.txt`. `evaluate_model.py` needs `langchain-neo4j` even when re-scoring cached outputs, because it reads the graph schema through it; the backend packages are needed only for a live model run.
