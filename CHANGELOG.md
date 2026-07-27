# Changelog

Two things are versioned here: the **graphs** (the Zenodo dumps) and the **question suite**. They are coupled, because gold answers are materialized against a specific graph. The coupling rule is verification gate G5: *any dataset rebuild re-materializes every gold answer, and any change to a gold answer bumps the suite version with an entry in this file.* Gold can therefore never silently drift from the released data.

Versioning is `MAJOR.MINOR.PATCH`:

- **MAJOR**: a category, task, or protocol changes; results across versions are not comparable.
- **MINOR**: new templates, new cities, or new source layers; existing results remain valid for the questions that did not change.
- **PATCH**: gold answers re-materialized after a graph rebuild, or a corrected gold query; the question text and split are unchanged.

Published Zenodo versions are immutable. A correction is always a new version, never an edit of an existing archive.

---

## 1.0.0 (2026-07-27)

First public release.

**Graphs.** Five city dumps written by Neo4j 2025.10.1, 26.9 GiB total, DOI [10.5281/zenodo.21547211](https://doi.org/10.5281/zenodo.21547211).

| City | Dump | Nodes | Relationships | Buildings |
| --- | --- | --: | --: | --: |
| Hamburg | `neo4j_hamburg_lod2_roofmats_lod3_osm_20260717.dump` | 17,440,924 | 26,299,391 | 388,267 |
| Helsinki | `neo4j_helsinki_lod2_osm_20260716.dump` | 414,459 | 619,964 | 2,980 |
| Zurich | `neo4j_zurich_lod2_osm_20260716.dump` | 41,508,371 | 45,548,405 | 102,668 |
| New York | `neo4j_nyc_lod2_osm_20260716.dump` | 45,797,985 | 54,207,134 | 1,083,437 |
| Tokyo | `neo4j_tokyo_bcore_osm_20260717.dump` | 74,409,400 | 91,949,234 | 2,005,762 |

All five passed the OSM ingestion completeness census with zero missing and zero extra features, and none lost a building (distinct source ids equal graph building nodes). Layer composition per city, including which derived layers exist, is in [README.md](README.md) and [datasheet.md](datasheet.md).

**Question suite v1.0.** 84 templates, 1,394 verified question instances out of 1,406 instantiated (99.1 %; every non-verified instance is a deliberate per-city feasibility flip). Split by template: 1,024 development questions over 59 templates (gold public) and 370 held-out test questions over 25 templates (gold withheld). 282 questions (20.2 %) additionally reviewed by the authors.

**Baseline results.** Claude Sonnet 5 (closed book, schema only) and qwen2.5-coder:7b (Ollama Q4_K_M) on all five cities, development and held-out test splits, with cached generated Cypher, per-question outcomes, exact prompts, and raw responses.

### Construction history that shaped this release

Recorded because it affects how the numbers should be read.

- **Identity resolution for non-unique source ids** (before this release). Helsinki and Zurich ship repeated `gml:id`s and Tokyo's ward packages repeat whole tiles. Earlier internal graphs collapsed such features into a single node, losing 61 buildings on Helsinki and 45 on Zurich. Ingest now distinguishes a genuine duplicate from two distinct features sharing an id by full-content hash, deduplicating the former and splitting the latter onto synthesized ids with `source_gml_id` preserved. All five released graphs are built with this resolution in place.
- **Metric CRS at ingest** (before this release). New York (US survey feet) and Tokyo (geographic degrees) are reprojected once at ingest, without which every distance, area, and proximity result on those cities would be wrong.
- **Spatial gold correction** (2026-07-23, before freeze). The authors' review of the spatial category found that `spatial.withinDistance` interprets its radius as kilometres against a geographic layer, while the R-tree stores Cartesian metres, so five proximity templates returned near-empty results. The machine gates had passed them (a `count` gold always returns one row, and ranked golds carried `allow_empty`). All five were rewritten to a metre-correct form (R-tree window plus exact `point.distance` recheck, or a true top-k over `point.distance`), two degenerate window providers were replaced, and the whole suite was regenerated and re-verified live against all five city graphs. Template and instance counts are unchanged. **The cached baseline results predate this correction**; see [benchmark_a/baselines/README.md](benchmark_a/baselines/README.md) for exactly which questions are affected and what that means for the reported numbers.

---

## Planned

Not commitments with dates, but the direction, so that consumers can judge stability:

- Further cities, prioritizing regions with different cadastral traditions.
- A sensed layer (street-level or LiDAR-derived) as inference data becomes available, following the same provenance contract: own node label, own R-tree layer, namespaced scalars, confidence on every derived fact.
- Additional registry and socio-economic layers, which would add real-valued targets to the representation-learning family and would flip some currently infeasible questions to feasible. Any such addition re-runs the guard queries (gate G6), because an infeasible question is only infeasible with respect to a specific graph version.
- Gold queries for a relational backend, which would let the same questions be posed over a table-based CityGML store. Out of scope in v1.0 by design: the benchmark's cross-source, provenance, and coverage categories read fusion structures that a relational CityGML schema has no column for.
