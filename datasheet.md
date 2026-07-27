# Datasheet for AuthentiCity

Following *Datasheets for Datasets* (Gebru et al., 2021). This is the complete version; the paper's appendix carries a condensed form. Version 1.0.0, 2026-07-27.

Numbers in this document come from the released artifacts, not from re-derivation: per-city counts from [dumps/counts/](dumps/counts/) (written at dump time), storage from [quality/disk_footprint.md](quality/disk_footprint.md), verification outcomes from [quality/](quality/), and question-suite statistics from [benchmark_a/](benchmark_a/).

---

## Motivation

**For what purpose was the dataset created?**
To provide a multi-source, provenance-aware 3D city knowledge graph and a benchmark that evaluates reasoning over source origin, confidence, coverage, and cross-source agreement. Existing text-to-query benchmarks are built on single-source schemas where every fact is equally trustworthy, and existing urban graph benchmarks flatten heterogeneous sources into one canonical layer. Neither exercises the reasoning that real urban data integration demands: deciding which of two disagreeing sources to trust, recognizing that an aggregate over a half-covered attribute is only meaningful relative to the covered subset, or declining a question the data cannot answer.

**Who created the dataset?**
The authors of the accompanying paper, at the Computational Methods Lab, HafenCity University Hamburg: Huynh Duc An Son Nguyen, Lukas Arzoumanidis, and Youness Dehbi.

**Who funded the creation of the dataset?**
Academic research at HafenCity University Hamburg. Funding acknowledgements are in the paper.

---

## Composition

**What do the instances represent?**
Nodes are urban entities and their geometry: buildings, building parts, boundary surfaces (roof, wall, ground, closure), geometry primitives (solids, multi/composite surfaces, polygons, rings, line strings), and, per city, other CityGML modules (bridges, roads, vegetation, water bodies, city furniture, plant cover, city object groups). Alongside these sit fused OpenStreetMap features, and, for Hamburg, ML-predicted roof materials (as properties on building nodes) and reconstructed LoD3 facade geometry. Container and index nodes (`Dataset`, `City`, `District`, R-tree nodes) complete the graph.

**How many instances are there in total?**

| | Hamburg | Helsinki | Zurich | New York | Tokyo | Total |
| --- | --: | --: | --: | --: | --: | --: |
| Nodes | 17,440,924 | 414,459 | 41,508,371 | 45,797,985 | 74,409,400 | 179,571,139 |
| Relationships | 26,299,391 | 619,964 | 45,548,405 | 54,207,134 | 91,949,234 | 218,624,128 |
| Buildings | 388,267 | 2,980 | 102,668 | 1,083,437 | 2,005,762 | 3,583,114 |
| Other city objects | 0 | 31 | 0 | 0 | 659,006 | 659,037 |
| OSM features | 1,188,139 | 55,930 | 1,860,401 | 2,555,468 | 3,830,408 | 9,490,346 |
| `ENRICHED_BY` edges | 373,211 | 3,011 | 100,312 | 1,078,893 | 1,390,723 | 2,946,150 |
| `HAS_POI` edges | 22,219 | 1,797 | 13,587 | 52,449 | 91,487 | 181,539 |

Node property records total 998.88 M and relationship property records 185.01 M (1.18 B properties). Buildings per city range from 2,980 (Helsinki, an inner-city core release) to 2,005,762 (Tokyo, 23 special wards).

**Does the dataset contain all possible instances or is it a sample?**
It contains every building of each source's released extent, not a sample. What each source chooses to publish differs by more than an order of magnitude in area (Helsinki's 14 km² core against Hamburg's 7,117 km² federal-state bounding box), which is a property of the release boundaries, not of our selection. Tokyo is restricted to the PLATEAU B-core module set (`bldg`, `tran`, `brid`, `frn`, `veg`, `wtr`); land use, terrain, underground, and the PLATEAU ADE extensions are excluded by design as disproportionate in scale relative to their benchmark value.

**What data does each instance consist of?**
Raw features preserved from the source, plus derived structure. Buildings carry their source thematic attributes (per city 5 to 49 distinct keys, see [stats/](stats/)), their `gml:id` (or a synthesized id with the original preserved in `source_gml_id`), bounding boxes, and centroids. Geometry nodes carry coordinate strings **verbatim**, never rounded or reprojected after ingest, which is what makes the lossless round-trip possible. Non-metric sources are reprojected once, at ingest, to a per-city metric CRS; `Dataset.source_crs` records the original.

**Is there a label or target associated with each instance?**
There is no single target. The representation-learning benchmark defines targets over existing attributes: building height (all five cities), cadastral building function (Hamburg), roof type (Hamburg, Helsinki), ML roof-material class (Hamburg, 50.2 % coverage), and `ENRICHED_BY` correspondence edges as link-prediction labels (all cities). Label coverage differs per task and city by construction; see [benchmark_b/README.md](benchmark_b/README.md).

**Is any information missing from individual instances?**
Yes, and the pattern is informative rather than accidental:

- New York's source model carries **no** `measuredHeight`. 97.5 % of its buildings have an OSM height and none an authoritative one.
- Zurich and New York carry no building-function or roof-type classification and no storey counts; their sources are geometry and cadastre only.
- Derived layers (ML roof materials, LoD3) exist for Hamburg only. Roof material covers 194,799 of 388,267 Hamburg buildings (50.2 %); 570 of those carry more than one predicted material. LoD3 reconstruction covers 17 buildings (303 `HAS_LOD3_FACADE` anchor edges, 3,404 facade surfaces).

Absence is never encoded as a negative observation. Coverage is explicit, so a consumer can distinguish "not covered" from "measured to be absent". The benchmark's infeasible category is built on exactly these gaps.

**Are relationships between instances made explicit?**
Yes; relationships are the dataset. Typed, directed edges connect each building to its parts, boundary surfaces, and geometry primitives, and to its district and city. Cross-source correspondence is an explicit edge carrying `overlap_ratio`, `jaccard`, `intersection_area`, `match_type` (the 1:1 / 1:n / n:1 / n:m case), and `is_primary`, rather than a silently merged scalar. Every node and edge records a `source`, so provenance is queryable at the relationship level.

**Are there recommended data splits?**
Yes, for both benchmarks, and they are released rather than described:

- Benchmark A: split **by template** into 1,024 development questions (59 templates, gold queries and materialized gold answers public) and 370 held-out test questions (25 unseen templates, gold withheld). Splitting by template, not by instance, means the test set contains unseen query patterns rather than unseen paraphrases of seen ones.
- Benchmark B: spatial-block 5-fold cross-validation within a city (out-of-fold predictions pooled so each entity is tested once) and leave-one-city-out for cross-city transfer.

**Are there errors, sources of noise, or redundancies?**
Yes, documented and preserved rather than silently repaired:

- **Non-unique source identifiers.** Helsinki (61 groups) and Zurich (45 occurrences) ship repeated `gml:id`s; Tokyo's ward packages repeat entire tiles. Identity resolution at ingest distinguishes genuine duplicates from distinct features sharing an id by full-content hash: Tokyo deduplicates 975,077 byte-identical replicas and splits 468 distinct same-id features; Zurich splits 40 and deduplicates 5; Helsinki splits 61. Split features get a synthesized id with the original kept in `source_gml_id`, so export re-emits the original. No city loses a building: distinct source ids equal graph building nodes everywhere ([quality/duplicate_ids_traceability.md](quality/duplicate_ids_traceability.md)).
- **Source sentinels.** Tokyo's PLATEAU export uses `-9999` for missing `measuredHeight` (36,071 buildings) and `9999` for storey counts (225,776 buildings, 11.3 %). Both are kept verbatim under the lossless-ingest principle and must be excluded from statistics; every gold query that aggregates height guards with `> -999`. This is documented as a data caveat, not repaired.
- **Upstream encoding damage.** The Helsinki export carries corrupted Finnish diacritics (1,490 Unicode replacement characters across 283 values), retained as-is while the integrity gates confirm faithful preservation.
- **Redundancy by design.** The same fact can appear twice on purpose: an authoritative value and its crowd-sourced counterpart under `osm_*`. That is the point of the dataset, not noise.

**Is the dataset self-contained?**
Yes. Each dump is a complete Neo4j database including its spatial R-tree layers; nothing is fetched at query time and no re-indexing is needed after a restore. The source files it was built from remain available at the portals listed in [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md), and the original coordinates, CRS, and `gml:id`s are retained in the graph so the mapping stays auditable.

**Does the dataset contain confidential or personal data?**
No. Instances are buildings, not people. All sources are already public open data. Address-level strings appear only where OpenStreetMap itself publishes them, copied under the `addr_*` namespace from the primary match. There are no human data subjects, so the datasheet questions on consent, ethical review, retention, and offensive content do not apply. See [ETHICS.md](ETHICS.md) for the reasoning and for the misuse that is nonetheless possible.

---

## Collection Process

**How was the data acquired?**
Authoritative CityGML was downloaded from the open-government portals in [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md). OpenStreetMap was obtained as regional Geofabrik extracts (Hamburg 2026-06-29; New York and Kanto 2026-07-03; Finland and Switzerland 2026-07-04), clipped to each dataset's bounding box plus a 10 m buffer with `ogr2ogr`. The roof-material predictions come from our own imagery-based classifier; the LoD3 facades are reconstructed from our own facade imagery.

**What mechanisms or procedures were used?**
A scripted Python pipeline (pykci, MIT licensed, <https://github.com/hcu-cml/pykci>): streaming `lxml` CityGML parsing into Neo4j via idempotent `MERGE` batches, `pyproj` for reprojection, `shapely` for footprint overlap, and Neo4j Spatial R-trees for indexing. Every stage is a command in [docs/REPRODUCE.md](docs/REPRODUCE.md); no manual editing of graph content occurred at any point.

**Over what timeframe was the data collected?**
Source vintages span 2016 (New York) to 2025 (Hamburg, Tokyo) and are **not** harmonized: each city's graph reflects its own source date. The OSM extracts are from late June and early July 2026. Graph construction and fusion took place in June and July 2026; total build time across all five cities was 6.64 h wall clock on the reference machine ([docs/ENVIRONMENT.md](docs/ENVIRONMENT.md)).

**Was the data collected from third parties?**
Yes: five public agencies and the OpenStreetMap community. No data was collected from or about individuals.

---

## Preprocessing, Cleaning, and Labeling

**Was any preprocessing done?**

1. CityGML is mapped to a labeled property graph; coordinates are stored verbatim.
2. Non-metric sources are reprojected once at ingest: New York from EPSG:2263 (US survey feet) to EPSG:32618, Tokyo from EPSG:6697 (geographic degrees) to EPSG:6677. Without this, distances, areas, proximity queries, and footprint fusion would be wrong.
3. Fourteen of New York's twenty tiles are CityGML 1.0 and were namespace-upgraded to 2.0.
4. Non-unique identifiers are resolved by content hash (dedup) or split onto synthesized ids, as described above.
5. OSM footprints are matched to authoritative footprints through a confidence-weighted overlap graph (connected components over an overlap threshold of 0.3, selected by sensitivity analysis) and attached as `ENRICHED_BY` edges. Curated scalars from the **primary** match only are copied onto the authoritative node under `osm_*`; secondary matches stay on their OSM node.
6. Derived scalars are namespaced (`osm_*`, `predicted_*`, `lod3_*`) so they can never overwrite an authoritative value. A generic source attribute whose slugged key would collide with a structural property is namespaced instead.

**Was the raw data saved?**
Yes, and it is publicly re-obtainable from the portals and Geofabrik. Within the graph, `source`, `source_gml_id`, `source_crs`, and verbatim coordinate strings preserve the link back to it.

**Is the software available?**
Yes: pykci (MIT) builds the graphs; this repository holds the benchmark harness and release tooling.

**Was the data validated?**
Every released instance passes automated gates before it is dumped:

- **Lossless CityGML round-trip census.** Ingest to Neo4j and export back reproduces every element local name, attribute, leaf text, and coordinate token of the source (the appearance and material module is excluded by design). Proven on all LoD 0 to 4 and all ten thematic modules.
- **OSM ingestion completeness census.** For each city the fused graph is re-derived from the source `.osm.pbf` through the same extraction code path and checked at five levels: every admitted feature present exactly once (no missing, no extras), tags reconstructing losslessly by canonical hash, geometry verbatim, the attach-or-orphan partition exact, and every node R-tree registered with provenance. All five cities passed with zero missing and zero extra features ([quality/osm_census_*.md](quality/)).
- **Per-city statistical and anomaly control** before and after ingestion: duplicate and placeholder ids, degenerate geometry, coordinate ranges, height and vertex outliers, coverage, and fan-out ([quality/stats_control_*.md](quality/)).

Details, including what each gate does not cover, are in [docs/QUALITY_GATES.md](docs/QUALITY_GATES.md).

---

## Uses

**Has the dataset been used for any tasks already?**
Yes, the two benchmark families reported in the paper: natural-language-to-Cypher translation and graph representation learning. Baseline results, cached model outputs, prompts, and per-question outcomes are released with the benchmark. We are aware of no third-party uses at the time of release.

**What other tasks could the dataset be used for?**
Provenance- and confidence-aware data fusion and conflation; quality assurance and cross-source auditing of official city models; level-of-detail enrichment; attribute completion that respects source trust; cross-city transfer for data-scarce cities; spatial and 3D reasoning over indexed geometry; and multilingual schema grounding (the PLATEAU Japanese attribute keys are preserved verbatim as queryable keys).

**Is there anything about the composition or collection that might affect future uses?**
Yes, and consumers should read these before drawing conclusions:

- **Circularity for roof material.** The roof-material classifier was trained using OSM labels, so OSM-derived features leak information about that target. Report both protocol variants (with and without the OSM layer as input), and do not read the ML-vs-OSM agreement figure as independent validation. On the released Hamburg graph only 3.5 % of labeled buildings carry a matched OSM `roof:material` tag, which bounds the leakage but does not remove the concern.
- **Coverage is uneven by design.** Roof type spans two of five cities, building function one. A benchmark result reported on the best-covered city alone would misrepresent the dataset.
- **Source vintages differ** (2016 to 2025). Cross-city comparisons of, for example, building stock are comparisons of differently dated snapshots.
- **Proximity edges are deliberately absent.** Materialized building-to-building proximity edges explode edge counts at city scale, so they are opt-in in the pipeline and off in every release graph. Proximity is answered at query time through the R-tree and centroid distances, which is also what the benchmark's gold queries do.
- **Coordinate reference systems are per city.** There is no single global CRS; every metric computation must use the city's own.

**Are there tasks for which the dataset should not be used?**
The dataset describes the built environment, not individuals, and should not be repurposed to infer information about residents of specific buildings. Derived layers are explicitly marked as predicted or reconstructed so they can be excluded where authoritative-only evidence is required; they should not be presented as survey-grade. See [ETHICS.md](ETHICS.md).

---

## Distribution

**How is the dataset distributed?**
The five graphs are distributed as offline `neo4j-admin database dump` archives (26.9 GiB total, written by Neo4j 2025.10.1) from the Zenodo record, openly downloadable without a personal request. This repository distributes the loaders and verification tools, the complete question suite with gold queries and materialized answers for the development split, the held-out test questions, the evaluation harness, cached baseline outputs, the per-city verification reports, and this documentation. A backend-neutral node and edge table export is produced by [tools/export_tables.py](tools/export_tables.py) for consumers who do not want a Neo4j dependency.

**When will it be distributed and under what license?**
Version 1.0.0, 2026-07-27. The graph dumps are released under ODbL 1.0 because each embeds substantial OpenStreetMap content and ODbL's share-alike applies to a derived database; each source layer additionally retains its own license (Hamburg dl-de/by-2-0, Helsinki CC BY 4.0, Zurich swisstopo open government data terms, New York NYC OpenData terms, Tokyo PLATEAU Public Data License 1.0). Our annotations, question suite, and documentation are CC BY 4.0; the code is MIT. Attribution to OpenStreetMap and to the respective authoritative provider is required. Full terms and attribution strings: [DATA_LICENSES.md](DATA_LICENSES.md).

**Have any third parties imposed IP-based or other restrictions?**
No restrictions beyond the source licenses above. All five authoritative sources permit redistribution with attribution. No export controls or regulatory restrictions apply.

**Is there a DOI?**
Yes: [10.5281/zenodo.21547211](https://doi.org/10.5281/zenodo.21547211).

---

## Maintenance

**Who will support, host, and maintain the dataset?**
The authors, at HafenCity University Hamburg. Contact: Huynh Duc An Son Nguyen, <son.nguyen@hcu-hamburg.de>.

**How can the owner be contacted?**
By email as above, or by opening an issue on this repository.

**Is there an erratum?**
Corrections are recorded in [CHANGELOG.md](CHANGELOG.md). Any change to a released graph or to the question suite is a versioned release, never an in-place edit of a published archive: Zenodo records are immutable per version and a new version gets a new version DOI under the same concept DOI.

**Will the dataset be updated?**
Yes. Planned: further cities, and a sensed layer as inference imagery becomes available. The question suite is regenerated and re-verified against every new graph release; because gold answers are materialized against the data, a rebuild that changes any gold answer bumps the suite version and appends a changelog entry (verification gate G5), so gold can never silently drift from the released graph.

**If others want to extend or contribute, is there a mechanism?**
Yes: pull requests and issues on this repository. New source layers should follow the provenance contract in [docs/PROVENANCE.md](docs/PROVENANCE.md): own node label and R-tree layer, namespaced scalars, confidence-carrying explicit edges, and a completeness gate before release. Contributed benchmark results can be submitted as described in [benchmark_a/README.md](benchmark_a/README.md).

**Will older versions continue to be supported?**
Yes. Every published Zenodo version stays downloadable, and the suite version that a result was produced against is recorded in each results file, so past numbers remain interpretable.
