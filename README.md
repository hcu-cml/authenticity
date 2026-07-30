# AuthentiCity

**A multi-source, provenance-aware 3D city knowledge graph spanning five cities across three continents.**

AuthentiCity is **primarily a data contribution**: a unified, provenance-aware representation of heterogeneous urban data whose facts differ in reliability, coverage, and semantics. It fuses **authoritative** 3D city models (CityGML/ALKIS), **crowd-sourced** data (OpenStreetMap), **ML-predicted** attributes (roof materials), and **reconstructed** geometry (LoD3) into labeled property graphs that keep every fact traceable to its origin; derived information never replaces authoritative values. Confidence-weighted edges resolve many-to-many cross-source correspondences, constructing canonical urban entities while preserving traceable links to all contributing evidence.

To demonstrate the tasks the representation enables, we release two benchmark families, natural-language-to-query translation and graph representation learning, targeting capabilities that existing text-to-query and urban-reasoning benchmarks do not measure: provenance-aware filtering, cross-source (dis)agreement, coverage-aware aggregation, infeasible-query detection, 3D spatial reasoning, and provenance-aware embeddings.

The graph spans **five cities across three continents** (Hamburg, Helsinki, Zurich, New York, and Tokyo) and comprises roughly **180 GiB, 180 M nodes, 220 M edges, 1.2 B properties, and 3.6 M buildings**.

---

## The five city graphs

| City | Buildings | Nodes | Edges | Store (GiB) | Dump (GiB) | Extra layers |
|------|----------:|------:|------:|------------:|-----------:|--------------|
| Hamburg (flagship) | 388,267 | 17.44 M | 26.30 M | 14.8 | 3.1 | OSM · ML roof materials · LoD3 facades |
| Helsinki | 2,980 | 0.41 M | 0.62 M | 0.3 | 0.2 | OSM |
| Zurich | 102,668 | 41.51 M | 45.55 M | 30.2 | 5.6 | OSM |
| New York | 1,083,437 | 45.80 M | 54.21 M | 32.4 | 7.0 | OSM (97.5 % of heights are OSM-only; **0 % authoritative height**) |
| Tokyo | 2,005,762 | 74.41 M | 91.95 M | 99.2 | 11.3 | OSM (Japanese-keyed PLATEAU schema, mostly LoD1) |
| **Total** | **3,583,114** | **179.57 M** | **218.62 M** | **176.9** | **27.2** | |

Every city carries the authoritative CityGML layer plus OSM fusion; only Hamburg additionally carries the ML roof-material and reconstructed LoD3 layers.

---

## Provenance model

AuthentiCity is built on one binding principle: **every fact stays traceable to its source, and derived information never replaces authoritative data.** Four trust layers span the spectrum from surveyed to predicted:

| Layer | Source | Trust | Attached as |
|-------|--------|-------|-------------|
| Authoritative | CityGML / ALKIS (official 3D city models) | highest | native node properties |
| Crowd-sourced | OpenStreetMap | medium | `OsmFeature` nodes + `ENRICHED_BY` edges, `osm_*` scalars |
| ML-predicted | roof-material classifier (aerial orthophotos) | confidence-carrying | `predicted_roof_material_*` scalars (Hamburg) |
| Reconstructed | LoD3 facade reconstruction | derived | LoD3 geometry nodes (Hamburg) |

Cross-source correspondences are **not collapsed into hard matches.** OSM↔CityGML footprints are matched across the 1:1 / 1:n / n:1 / n:m cases and retained as confidence-weighted `ENRICHED_BY` edges (each edge carries its overlap coefficient, Jaccard index, intersection area, correspondence case, and a primary-match flag), so queries and learning methods can resolve correspondences as needed. Authoritative and derived values (e.g., `measured_height` vs. `osm_height`) sit side by side under distinct namespaces and can be compared directly.

---

## Graph schema (brief)

Labeled property graph in **Neo4j**. Core node labels: `Dataset`, `City`, `District`, `Building`, `BuildingPart`, `BoundarySurface`, `Geometry*` (polygon/ring/solid/multi-surface/…), `BuildingFunction`, `RoofType`, and the shared `CityObject` label for non-building modules (Bridge, Tunnel, Road, WaterBody, Vegetation, …). OSM adds `OsmFeature` (with a dynamic `Osm*` sub-label and `osm_kind`). Fusion edges: `ENRICHED_BY` (footprint correspondence) and `HAS_POI` (points of interest). Geometry coordinates are stored **verbatim**: the authoritative layer round-trips CityGML 2.0 losslessly (all LoD 0–4, all thematic modules). Spatial queries use per-layer R-tree indexes (`features` for CityGML, `osm_features` for OSM).

---

## Benchmarks

### Task Family A: Natural-language to Cypher

1,394 questions across 84 schema-grounded templates and nine categories, split by template into a public **development set** and a **held-out test set** (gold queries unpublished). Five categories are distinctive contributions: **spatial** (window / proximity / nearest-neighbor / 3D-structure / density), **cross-source** (authoritative vs. crowd-sourced agreement and OSM-only coverage), **provenance-filtered** (source/confidence constraints, including traps), **coverage-aware** (aggregates meaningful only over the covered subset), and **infeasible** (guard-verified questions with no valid answer). Feasibility is data-dependent, so the same template can flip category across cities.

We report **execution accuracy (EX)** decomposed into executed-and-correct, executed-but-wrong, errored, and over-refusal, plus infeasibility precision/recall/F1. Reference results:

- **Claude (commercial frontier model, closed-book):** 54–69 % EX across the five cities; the remaining mass is mostly *executed-but-wrong* (semantic, not syntax, failures).
- **qwen2.5-coder:7b (local open-weight):** 6–19 % EX, dominated by *errored* queries, largely hallucinated PostGIS `ST_*` functions in spatial tasks; it **never abstains** on an unanswerable question, generating a query for every infeasible case (infeasibility recall 0).

Even a strong commercial model leaves substantial headroom, concentrated in the novel provenance-, coverage-, and infeasibility categories.

### Task Family B: Graph representation learning

Three tasks under fixed random / spatial-block / cross-city splits, each run in two protocols:

- **Attribute imputation:** predict roof-material class (labels cover ~50 % of buildings).
- **Node classification:** predict ALKIS building-function and roof-type classes.
- **Link prediction:** predict held-out `ENRICHED_BY` correspondence edges (casts OSM↔CityGML footprint matching as a learning task).

Each task is evaluated under a **provenance-agnostic** protocol (source distinctions hidden, as in existing urban graphs) and a **provenance-weighted** protocol (trust classes and fusion-edge confidences exposed, e.g. Jaccard-weighted message passing). The Δ between them is the headline measurement: the first such comparison on a real city-scale multi-source graph.

---

## Getting started

The graphs are released as offline **Neo4j 2025.10.1** database dumps (one per city). A version mismatch will fail to load.

```bash
# Restore one city into a fresh/empty Neo4j 2025.10.1 instance
neo4j-admin database load neo4j --from-path=/path/to/dumps --overwrite-destination
neo4j start
```

```cypher
// Sanity-check the restore
MATCH (n)                        RETURN count(n);   // total nodes
MATCH (b:Building)               RETURN count(b);   // buildings
MATCH ()-[r:ENRICHED_BY]->()     RETURN count(r);   // OSM correspondences

// Example: buildings where OSM and authoritative height disagree by > 3 m
MATCH (b:Building)-[:ENRICHED_BY {is_primary:true}]->(o:OsmFeature)
WHERE o.osm_height IS NOT NULL AND b.measured_height IS NOT NULL
  AND abs(toFloat(o.osm_height) - b.measured_height) > 3.0
RETURN b.id, b.measured_height, o.osm_height;
```

**Memory sizing:** the reference configuration (`heap=16g`, `pagecache=32g`) targets a ~62 GiB machine. Keep `heap + pagecache` under ~80 % of available RAM. Plan around store sizes above: Tokyo (~99 GiB) is the largest; start with Hamburg (smallest full-stack city) if resources are tight.

---

## Repository layout

```text
authenticity/
├── README.md                ← this file
├── dumps/                    ← the five enriched property graphs (Neo4j 2025.10.1 dumps)
├── loaders/                  ← graph loaders / export utilities
├── benchmark_a/              ← question suite with gold Cypher + materialized gold answers, task splits, evaluation harness, cached model outputs
├── benchmark_b/              ← representation-learning task splits, loaders, baseline configs
├── schema/                   ← graph schema reference, ALKIS code lists, Cypher cheat-sheet
└── datasheet.md              ← dataset datasheet (motivation, composition, collection, uses, distribution)
```

> The public **development split** ships complete: questions, **gold Cypher queries, and materialized gold answers**, for offline scoring against the released graphs. The **test split** is released as a genuine held-out benchmark (see the datasheet for its gold-answer policy).

---

## Reproducibility

Graphs are constructed by an open, standalone Python pipeline (CityGML → Neo4j ingest, OSM fusion, ML/LoD3 enrichment, export) with per-city before/after statistical gates and lossless round-trip census checks. The benchmark question suite is machine-generated from schema-grounded templates and re-materialized against the released graphs, so it cannot drift from the data. See the datasheet and the accompanying paper for the full protocol.

---

## License

- **Data:** released under an open license compatible with its sources (CityGML/ALKIS per each provider's terms; OpenStreetMap under ODbL). See `LICENSE` and per-source attribution in the datasheet. *(Finalize before release.)*
- **Code / benchmark harness:** open-source license. *(Finalize before release.)*

---

## Citation

AuthentiCity paper:

```bibtex
@misc{nguyen_authenticity_2026,
      title={{AuthentiCity: A Multi-Source Provenance-Aware Knowledge Graph and Benchmark for 3D City Models}}, 
      author={Huynh Duc An Son Nguyen and Lukas Arzoumanidis and Youness Dehbi},
      year={2026},
      eprint={2607.25243},
      archivePrefix={arXiv},
      primaryClass={cs.DB},
      url={https://arxiv.org/abs/2607.25243}, 
}
```

AuthentiCity was built using our tool pykci - Python Knowledge Graph for Cities:

```bibtex
@misc{nguyen_pykci_2026,
      title={pykci: A Compact Urban Knowledge Graph for Semantic and Spatial Queries using LLMs},
      author={Huynh Duc An Son Nguyen and Lukas Arzoumanidis and Youness Dehbi},
      year={2026},
      eprint={2607.01605},
      archivePrefix={arXiv},
      primaryClass={cs.DB},
      url={https://arxiv.org/abs/2607.01605},
}
```

An archival DOI will accompany the camera-ready release.

---

## Contact

Corresponding author:
Huynh Duc An Son Nguyen · `son.nguyen@hcu-hamburg.de` · HafenCity University Hamburg
