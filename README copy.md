# AuthentiCity

**A multi-source, provenance-aware 3D city knowledge graph spanning five cities across three continents, with two benchmark families built on it.**

[![Data DOI](https://img.shields.io/badge/data-10.5281%2Fzenodo.21547211-blue)](https://doi.org/10.5281/zenodo.21547211)
[![Docs license: CC BY 4.0](https://img.shields.io/badge/docs%20%26%20benchmark-CC%20BY%204.0-lightgrey)](LICENSE)
[![Code license: MIT](https://img.shields.io/badge/code-MIT-lightgrey)](LICENSE-CODE)
[![Graphs: ODbL 1.0](https://img.shields.io/badge/graph%20dumps-ODbL%201.0-lightgrey)](DATA_LICENSES.md)

This repository is the code-and-benchmark half of the AuthentiCity artifact. The five city graphs themselves are large binary databases and live in the Zenodo archive; everything needed to load them, verify them, query them, and reproduce both benchmarks is here.

AuthentiCity is **primarily a data contribution**: a unified representation of heterogeneous urban data whose facts differ in reliability, coverage, and semantics. It fuses **authoritative** 3D city models (CityGML, cadastral), **crowd-sourced** data (OpenStreetMap), **ML-predicted** attributes (roof materials), and **reconstructed** geometry (LoD3) into labeled property graphs in which every fact stays traceable to its origin and derived information never replaces authoritative values. Confidence-weighted edges retain many-to-many cross-source correspondences instead of collapsing them, so canonical urban entities can be constructed without discarding the contributing evidence.

Two benchmark families demonstrate what the representation enables: **natural-language-to-Cypher translation** and **graph representation learning**. Both target capabilities that existing text-to-query and urban-reasoning benchmarks do not measure: provenance-aware filtering, cross-source (dis)agreement, coverage-aware aggregation, infeasible-query detection, 3D spatial reasoning, and provenance-aware embeddings.

---

## Start here

| If you want to | Read |
| --- | --- |
| Download and restore a city graph, then run your first queries | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) |
| Understand the graph model before writing Cypher | [docs/GRAPH_SCHEMA.md](docs/GRAPH_SCHEMA.md) |
| Understand how provenance is represented and what the trust layers mean | [docs/PROVENANCE.md](docs/PROVENANCE.md) |
| Know exactly where every city's data came from and under which license | [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md), [DATA_LICENSES.md](DATA_LICENSES.md) |
| Evaluate a model on the NL-to-Cypher benchmark | [benchmark_a/README.md](benchmark_a/README.md) |
| Work on the representation-learning benchmark | [benchmark_b/README.md](benchmark_b/README.md) |
| Check how the released graphs were validated | [docs/QUALITY_GATES.md](docs/QUALITY_GATES.md), [quality/](quality/) |
| Reproduce a number from the paper | [docs/REPRODUCE.md](docs/REPRODUCE.md) |
| Read the dataset documentation in full (composition, collection, uses, distribution, maintenance) | [datasheet.md](datasheet.md) |
| Know what the dataset cannot do | [LIMITATIONS.md](LIMITATIONS.md), [ETHICS.md](ETHICS.md) |

---

## The five city graphs

| City | Buildings | Nodes | Edges | Store (GiB) | Dump (GiB) | Derived layers beyond CityGML + OSM |
| --- | --: | --: | --: | --: | --: | --- |
| Hamburg, DE (flagship) | 388,267 | 17.44 M | 26.30 M | 14.77 | 3.07 | ML roof materials, reconstructed LoD3 facades |
| Helsinki, FI | 2,980 | 0.41 M | 0.62 M | 0.28 | 0.15 | none |
| Zurich, CH | 102,668 | 41.51 M | 45.55 M | 30.21 | 5.57 | none |
| New York, US | 1,083,437 | 45.80 M | 54.21 M | 31.90 | 6.81 | none (97.5 % of heights are OSM-only; **no authoritative height at all**) |
| Tokyo, JP | 2,005,762 | 74.41 M | 91.95 M | 99.18 | 11.32 | none (Japanese-keyed PLATEAU schema, predominantly LoD1) |
| **Total** | **3,583,114** | **179.57 M** | **218.62 M** | **176.3** | **26.9** | |

Store sizes are the Neo4j data store with write-ahead logs excluded, as measured additively after each ingestion stage ([quality/disk_footprint.md](quality/disk_footprint.md)); dumps are the compressed archives actually released.

Every city carries the authoritative CityGML layer plus whole-city OpenStreetMap fusion (9,490,346 OSM features in total, 2.95 M confidence-weighted `ENRICHED_BY` correspondence edges, 181,539 `HAS_POI` attachments). Node and relationship property records total 1.18 B. Exact per-city counts, as written at dump time, are in [dumps/counts/](dumps/counts/); they are also what [tools/verify_restore.py](tools/verify_restore.py) checks a restore against.

The graphs are released as offline **Neo4j 2025.10.1** database dumps, one per city, on Zenodo: **[10.5281/zenodo.21547211](https://doi.org/10.5281/zenodo.21547211)**. A dump loads only into the same or a newer Neo4j version.

---

## Provenance model

One binding principle: **every fact stays traceable to its source, and derived information never replaces authoritative data.** Four layers span the spectrum from surveyed to predicted.

| Layer | Source | Trust | Attached as |
| --- | --- | --- | --- |
| Authoritative | CityGML / cadastral city models | highest | native node properties |
| Crowd-sourced | OpenStreetMap | medium | `OsmFeature` nodes, `ENRICHED_BY` / `HAS_POI` edges, `osm_*` scalars |
| ML-predicted | roof-material classifier over aerial imagery | confidence-carrying | `predicted_roof_material_*` scalars (Hamburg) |
| Reconstructed | LoD3 facade reconstruction | derived | LoD3 geometry nodes behind `HAS_LOD3_FACADE` (Hamburg) |

Cross-source correspondences are **not collapsed into hard matches**. OSM and CityGML footprints are matched across the 1:1, 1:n, n:1, and n:m cases and retained as confidence-weighted `ENRICHED_BY` edges, each carrying its overlap ratio, Jaccard index, intersection area, correspondence case, and a primary-match flag, so a consumer can rethreshold or reweight matches without redoing the alignment. Authoritative and derived values (for example `measured_height` against `osm_height`) sit side by side under distinct namespaces and can be compared directly. Full rules: [docs/PROVENANCE.md](docs/PROVENANCE.md).

---

## Graph schema in one paragraph

A labeled property graph in Neo4j. Core node labels: `Dataset`, `City`, `District`, `Building`, `BuildingPart`, `BoundarySurface`, the `Geometry*` family (polygon, ring, solid, multi-surface, composite surface, line string), `BuildingFunction`, `RoofType`, and the shared `CityObject` label for non-building modules (bridge, tunnel, road, water body, vegetation, city furniture, land use). OSM adds `OsmFeature` with a dynamic `Osm*` sub-label and a canonical `osm_kind`. Geometry coordinates are stored **verbatim**, never rounded, which is what makes the authoritative layer round-trip CityGML 2.0 losslessly across all LoD 0 to 4 and all thematic modules. Spatial queries use per-layer Neo4j Spatial R-tree indexes (`features` for CityGML, `osm_features` for OSM, `lod3_features` for the Hamburg LoD3 layer), which are contained in the dumps and need no rebuild after a restore. The exact schema text that models were given, per city, is in [schema/](schema/); the annotated reference is [docs/GRAPH_SCHEMA.md](docs/GRAPH_SCHEMA.md).

---

## Benchmarks

### Task Family A: natural-language to Cypher

**1,394 questions, 84 schema-grounded templates, nine categories, five cities, three languages.** Split by template into a public **development set** (1,024 questions, gold Cypher and materialized gold answers included) and a **held-out test set** (370 questions, 25 unseen templates, gold withheld). Five categories are distinctive contributions: **spatial** (window, proximity, nearest neighbor, 3D structure, density), **cross-source** (authoritative against crowd-sourced agreement, and what the crowd layer reports where the authoritative source is silent), **provenance-filtered** (source and confidence constraints, including traps), **coverage-aware** (aggregates meaningful only over the covered subset), and **infeasible** (guard-verified questions with no valid answer). Feasibility is a property of the data, so the same template can flip category across cities.

Every question passed a five-stage machine gate (executes, deterministic across three runs, non-empty unless permitted, guard-verified for infeasible, re-materialized on every rebuild), and 282 questions (20.2 %) were additionally reviewed by the authors. Reference results are cached in full: generated Cypher, per-question outcomes, exact prompts, and raw model responses.

- **Claude Sonnet 5** (commercial frontier model, closed-book, schema only): 54 to 69 % execution accuracy across the five cities. Nearly all remaining mass is *executed-but-wrong*, that is semantic rather than syntax failure.
- **qwen2.5-coder:7b** (local open-weight, Ollama Q4_K_M): 6 to 19 % execution accuracy, dominated by *errored* queries, largely hallucinated PostGIS `ST_*` functions in spatial tasks. It never abstains on an unanswerable question, so its infeasibility recall is 0 and its F1 undefined.

Even a strong commercial model leaves substantial headroom, concentrated in the provenance, coverage, and infeasibility categories. Details, file layout, scoring rules, and how to submit a run: [benchmark_a/README.md](benchmark_a/README.md).

### Task Family B: graph representation learning

Three tasks under fixed spatial-block (5-fold) and cross-city (leave-one-city-out) splits, each run in a **provenance-agnostic** protocol (source distinctions hidden, as existing urban graphs are consumed) and a **provenance-aware** protocol (source-typed relations, fusion-edge confidences as message-passing weights, coverage features):

- **Attribute imputation**: building height, and the ML roof-material class where the external model produced no label.
- **Node classification**: cadastral building-function and roof-type classes.
- **Link prediction**: held-out `ENRICHED_BY` correspondence edges, which casts OSM-to-CityGML footprint matching as a learning task.

The headline measurement is the difference between the two protocols. In distribution the aware encoder's advantage is statistically consistent but negligible (at most 0.010 absolute); under leave-one-city-out it becomes substantial (Hamburg height transfer R² 0.270 to 0.548). Learned encoders lose to non-learned baselines on matching, and collapse to chance on the ambiguous n:m subset where a trivial attribute rule still reaches 0.94 AUC. See [benchmark_b/README.md](benchmark_b/README.md) for the task definitions, protocols, reported numbers, and the code status.

---

## Repository layout

```text
authenticity/
├── README.md                  this file
├── datasheet.md               dataset documentation (Gebru et al. framework)
├── LIMITATIONS.md             what the dataset does not support
├── ETHICS.md                  privacy, bias, misuse, licensing ethics
├── DATA_LICENSES.md           per-source terms, attribution, redistribution
├── LICENSE / LICENSE-CODE     CC BY 4.0 (docs, annotations, benchmark) / MIT (code)
├── CITATION.cff               how to cite the dataset and the paper
├── CHANGELOG.md               dataset and question-suite versioning (gate G5)
├── croissant.json             machine-readable dataset metadata
├── requirements.txt           Python dependencies for the tools and harness
├── docs/                      getting started, schema, provenance, sources,
│                              quality gates, reproduction, environment
├── docker/                    Neo4j 2025.10.1 service matching the dumps
├── dumps/                     how to fetch the graphs + per-city count manifests
├── schema/                    per-city schema text given to the models
├── benchmark_a/               NL-to-Cypher: questions, splits, harness,
│                              verification reports, cached baselines
├── benchmark_b/               representation learning: tasks, protocols, splits
├── quality/                   per-city verification and anomaly reports
├── stats/                     per-city content metrics (machine-readable)
└── tools/                     restore verification, backend-neutral export,
                               cross-source conflict analysis
```

Files under `benchmark_a/`, `quality/`, `stats/`, `schema/`, and `dumps/counts/` are staged from the construction repository by a script, so the release can be rebuilt after any pipeline re-run rather than hand-curated. That script also enforces the two release invariants: no held-out gold and no credentials or local paths leave the source repo.

---

## Construction pipeline

The graphs are built by **pykci**, an open standalone Python pipeline (CityGML to Neo4j ingest, OSM fusion, ML and LoD3 enrichment, CityGML and 3D Tiles export, per-city statistical gates, lossless round-trip census): <https://github.com/hcu-cml/pykci>, MIT licensed. This repository does not duplicate it; [docs/REPRODUCE.md](docs/REPRODUCE.md) gives the exact commands, in order, that produced each released graph.

The question suite is machine-generated from schema-grounded templates whose slot values are read from the released graph and whose gold answers are re-materialized against it, so it cannot drift from the data. The generator, verifier, splitter, and evaluation harness all ship here.

---

## Licenses in short

- **Graph dumps (the data):** ODbL 1.0. Each dump embeds substantial OpenStreetMap-derived content, and ODbL's share-alike applies to a derived database. Attribution to OpenStreetMap **and** to the respective authoritative provider is required for any use or redistribution.
- **Source layers:** each retains its own license: Hamburg dl-de/by-2-0, Helsinki CC BY 4.0, Zurich swisstopo open government data terms, New York NYC OpenData terms, Tokyo PLATEAU Public Data License 1.0.
- **Our annotations, question suite, and documentation:** CC BY 4.0 ([LICENSE](LICENSE)).
- **Code in this repository:** MIT ([LICENSE-CODE](LICENSE-CODE)).

Full text, attribution strings, and per-source redistribution notes: [DATA_LICENSES.md](DATA_LICENSES.md).

---

## Citation

Please cite both the dataset and the paper.

```bibtex
@dataset{nguyen_authenticity_data_2026,
  author    = {Nguyen, Huynh Duc An Son and Arzoumanidis, Lukas and Dehbi, Youness},
  title     = {{AuthentiCity}: Five Multi-Source, Provenance-Aware 3D City
               Knowledge Graphs (Neo4j Database Dumps)},
  year      = {2026},
  publisher = {Zenodo},
  version   = {1.0.0},
  doi       = {10.5281/zenodo.21547211},
  url       = {https://doi.org/10.5281/zenodo.21547211}
}
```

The mapping pipeline is described in a companion system paper:

```bibtex
@misc{nguyen_pykci_2026,
  title         = {pykci: A Compact Urban Knowledge Graph for Semantic and
                   Spatial Queries using LLMs},
  author        = {Huynh Duc An Son Nguyen and Lukas Arzoumanidis and Youness Dehbi},
  year          = {2026},
  eprint        = {2607.01605},
  archivePrefix = {arXiv},
  primaryClass  = {cs.DB},
  url           = {https://arxiv.org/abs/2607.01605}
}
```

See [CITATION.cff](CITATION.cff) for the machine-readable form.

---

## Contact and maintenance

Corresponding author: Huynh Duc An Son Nguyen, <son.nguyen@hcu-hamburg.de>, Computational Methods Lab, HafenCity University Hamburg.

Issues and questions: please open a GitHub issue on this repository. Versioning policy, planned extensions, and what a new dataset release does to the question suite are documented in [CHANGELOG.md](CHANGELOG.md) and in the maintenance section of [datasheet.md](datasheet.md).
