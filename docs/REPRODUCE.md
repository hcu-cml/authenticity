# Reproducing AuthentiCity

Three levels of reproduction, from cheapest to most expensive. Pick the one that matches what you need to check.

| Level | What it verifies | Cost | Needs |
| --- | --- | --- | --- |
| **A. Verify the release** | that the published numbers describe the published graphs | minutes | a restored dump |
| **B. Reproduce the benchmarks** | the question suite and the baseline scores | hours | a restored dump; a model for new baselines |
| **C. Rebuild a graph from sources** | the whole construction pipeline | 2.5 min to 4 h per city | source data, the pykci repository |

---

## A. Verify the release

**A1. Check a restored graph against its manifest.**

```bash
python tools/verify_restore.py --city hamburg
```

Compares live node, relationship, building, OSM feature, `ENRICHED_BY`, and `HAS_POI` counts against [../dumps/counts/hamburg_counts.txt](../dumps/counts/), confirms the expected R-tree layers exist and answer a bounding-box query, and exits non-zero on any mismatch.

**A2. Re-verify every gold answer against the graph.** This is verification gate G5 and the strongest single check that the suite matches the data:

```bash
python benchmark_a/harness/verify_questions.py \
  --in  benchmark_a/questions/per_city/hamburg_dev.jsonl \
  --out /tmp/reverified_hamburg.jsonl \
  --report /tmp/reverified_hamburg.md
```

Every gold query is executed three times, canonicalized, and hashed; the hash must equal the `gold_answer_sha1` shipped with the question. Guard queries for infeasible questions must return zero. Compare the report with the shipped [../benchmark_a/verification/verification_report_hamburg.md](../benchmark_a/verification/).

**A3. Regenerate the reported result tables from the cached baseline outputs.** No model inference and no database needed:

```bash
python benchmark_a/harness/summarize_results.py --glob '*_dev.jsonl'    # development split
python benchmark_a/harness/summarize_results.py --glob '*_test.jsonl'   # held-out split
python benchmark_a/harness/summarize_results.py --glob '*_dev.jsonl' --latex
```

It reads `benchmark_a/baselines/results/` by default (override with `--results-dir`) and prints, per city and model, the execution-accuracy decomposition (EX, executed-but-wrong, errored, over-refusal), infeasibility precision, recall, and F1, and a breakdown of error kinds. These are the numbers reported in the paper.

**A4. Re-run the cross-source conflict measurement:**

```bash
python tools/osm_citygml_conflict_analysis.py --dataset hamburg_citygml2_lod2_2025.gml
```

Compare with [../quality/cross_source_conflict_hamburg.md](../quality/).

---

## B. Reproduce the benchmarks

### B1. Regenerate the question suite (development split)

The suite is machine-generated: slot values are read from the live graph, so the questions cannot reference data that does not exist, and gold answers are materialized against the graph rather than authored.

```bash
# 1. inspect the templates without touching a database
python benchmark_a/harness/generate_questions.py --dry-run

# 2. instantiate against the restored city graph
python benchmark_a/harness/generate_questions.py --out /tmp/questions_hamburg_raw.jsonl

# 3. run the verification gate (G1 to G4) and materialize gold answers
python benchmark_a/harness/verify_questions.py \
  --in  /tmp/questions_hamburg_raw.jsonl \
  --out /tmp/questions_hamburg_verified.jsonl \
  --report /tmp/verification_report_hamburg.md
```

Repeat per city (restore each dump in turn: generation and verification are one-city-at-a-time, since slot values come from the live graph), then split by template:

```bash
python benchmark_a/harness/split_dataset.py --dev-fraction 0.7
```

The released `templates.py` has the gold and guard queries of the 25 **held-out** templates withheld, so this reproduces the 1,024-question development split exactly and the 370 held-out questions as text only. Nothing else in the module is modified: the slot providers, the requirement gate, and the 59 development templates are intact. See [../benchmark_a/README.md](../benchmark_a/README.md) for how the held-out split is evaluated.

### B2. Re-score the cached baseline runs

The raw model answers are shipped as `{qid: output}` maps, which is exactly what the harness consumes, so a run can be re-scored with no inference at all (a restored graph is still needed, because scoring executes the generated Cypher):

```bash
python benchmark_a/harness/evaluate_model.py \
  --in benchmark_a/baselines/eval_subsets/hamburg_dev.jsonl \
  --backend claude_code_subagent --model claude-sonnet-5 \
  --pregenerated benchmark_a/baselines/model_outputs/hamburg_claude-sonnet-5_dev.json \
  --out /tmp/rescored_hamburg.jsonl
```

Each generated query is re-executed against the live graph and re-compared with gold, so this reproduces the execution-accuracy decomposition end to end. Numbers should match [../benchmark_a/baselines/reports/](../benchmark_a/baselines/reports/), except for queries whose runtime sits near the 20 s timeout on your hardware.

### B3. Evaluate a new model

```bash
# local open-weight model through Ollama
python benchmark_a/harness/evaluate_model.py \
  --in benchmark_a/questions/per_city/hamburg_dev.jsonl \
  --backend ollama --model qwen2.5-coder:7b \
  --out /tmp/results_hamburg_mymodel.jsonl

# commercial model through the Anthropic API (needs ANTHROPIC_API_KEY)
python benchmark_a/harness/evaluate_model.py \
  --in benchmark_a/questions/per_city/hamburg_dev.jsonl \
  --backend anthropic --model <model-id> \
  --out /tmp/results_hamburg_claude.jsonl
```

Context parity is enforced by the harness: every backend receives byte-identical schema text per city, taken from [../schema/](../schema/). Do not hand a model anything else if you intend to compare against the shipped baselines.

### B4. Benchmark B

Task definitions, protocols, splits, and the status of the training code: [../benchmark_b/README.md](../benchmark_b/README.md).

---

## C. Rebuild a graph from its sources

Needs the [pykci](https://github.com/hcu-cml/pykci) pipeline (MIT), the source CityGML for the city, and the matching OpenStreetMap extract; see [DATA_SOURCES.md](DATA_SOURCES.md) for every download location and the exact file names. Sizes are substantial (Hamburg 6.4 GB of CityGML, Tokyo 2,335 files) and the OSM step additionally needs the GDAL `ogr2ogr` CLI on `PATH`.

The pipeline stages, in the order they were run for every released city:

```bash
# 1. profile the source and flag input anomalies (no database involved)
python eval/stats_control.py precheck --city <CITY> --citygml <FILE-OR-DIR> [--osm <PBF>]

# 2. empty database, then ingest the authoritative layer
bash eval/reset_neo4j.sh
python ingest_citygml.py <FILE-OR-DIR ...> [--dataset-name <NAME>] \
       [--target-crs EPSG:N] [--writers 16] [--parse-workers 12]

# 3. fuse OpenStreetMap (clips and reprojects the .pbf itself)
python ingest_osm.py <PBF>

# 4. Hamburg only: ML roof materials, after OSM and before LoD3
python ingest_roof_materials.py input/geojson/<CITY>_roofmats*.geojson

# 5. Hamburg only: reconstructed LoD3 facades
python enrich_lod3_facades.py <LOD3.gml>

# 6. profile the resulting graph and produce the per-city report
python eval/stats_control.py postcheck --city <CITY> --deep --orphans
python eval/stats_control.py report --city <CITY>

# 7. the OSM completeness gate; must exit 0 with "CENSUS PASSED"
python eval/osm_ingestion_census.py --pbf <PBF>

# 8. cross-source conflict measurement
python bench/osm_citygml_conflict_analysis.py --dataset <DATASET>

# 9. record the on-disk footprint (must be captured at each stage,
#    because Neo4j never shrinks store files on delete)
python bench/measure_disk_footprint.py --city <CITY> --stage <STAGE>

# 10. dump the finished graph
docker compose exec neo4j neo4j-admin database dump neo4j --to-path=/backups
```

### Per-city parameters actually used

| City | CityGML input | `--dataset-name` | `--target-crs` | OSM extract | Extra stages |
| --- | --- | --- | --- | --- | --- |
| Hamburg | one merged `.gml` (6.4 GB) | (single file) | none | `hamburg-260629.osm.pbf` | roof materials, LoD3 |
| Helsinki | one `.gml` | (single file) | none | `finland-260704.osm.pbf` | none |
| Zurich | 78 tiles (13 GB) | `zurich` | none | `switzerland-260704.osm.pbf` | none |
| New York | 20 tiles (13 GB), 14 upgraded from CityGML 1.0 | `nyc` | `EPSG:32618` | `new-york-260703.osm.pbf` | none |
| Tokyo | 2,335 files under `*/udx/{bldg,tran,brid,frn,veg,wtr}` | `tokyo` | `EPSG:6677` | `kanto-260703.osm.pbf` | none |

`--dataset-name` merges tiled inputs into a single `Dataset` whose bounding box is the union of the tiles, while each feature keeps its own filename as `source`. `--target-crs` reprojects at ingest, which is mandatory for New York (US survey feet) and Tokyo (geographic degrees): without it every distance, area, and proximity result on those cities is wrong.

### Build times on the reference machine

| | Hamburg | Helsinki | Zurich | New York | Tokyo |
| --- | --- | --- | --- | --- | --- |
| CityGML ingest | 18.1 min | 28 s | 30.6 min | 75.5 min | 3.07 h |
| OSM fusion | 6.0 min | 2.0 min | 10.6 min | 15.9 min | 54.7 min |
| Roof materials | 13 s | | | | |
| LoD3 enrichment | 4 s | | | | |
| **Total** | **24.4 min** | **2.5 min** | **41.2 min** | **1.52 h** | **3.98 h** |

Total across all five cities: 6.64 h wall clock. Machine and configuration: [ENVIRONMENT.md](ENVIRONMENT.md).

### What will not be bit-identical

Ingest writes in parallel, so a rebuild can differ by a handful of nodes or relationships: rebuilds of the same Zurich input differed by 379 of 41.5 M nodes (0.0009 %) and of the same New York input by 200 of 45.8 M (0.0004 %). Building counts, OSM feature counts, correspondence-edge counts, and every gate outcome are stable; totals over geometry containers can move at that scale. If you need exact agreement with a published number, use the released dump rather than a rebuild.
