# Quality gates

What was verified before each graph was released, how, and what each gate does **not** cover. Machine-readable and human-readable reports for every city are in [../quality/](../quality/).

The philosophy is that a dataset paper should be able to state what it checked, not that its data is "clean". Four gates run on every city, each answering a different question.

---

## Gate 1: lossless CityGML round-trip

**Question: does the graph preserve the source document, or only a convenient projection of it?**

The source CityGML is ingested into Neo4j, exported back to CityGML from the graph alone, and the two documents are compared at four levels:

1. every element local name,
2. every `(attribute, value)` pair,
3. every leaf text node,
4. every coordinate token.

The gate passes only when the export covers everything in the source. The bar is semantic completeness, not byte identity: `gml:pos` against `gml:posList` encoding may differ, and element order within a feature is not significant, since the comparison is over multisets. The appearance and material module is excluded by design; the graphs carry geometry and semantics, not textures.

**Result.** Zero element, attribute, text, and coordinate loss on two independent axes: all levels of detail (LoD 0 to 4, using the FZK-Haus reference model) and all ten thematic modules (using the Railway Scene LoD3 reference model). The LoD4 case is the demanding one: 275,366 source instances, of which a naive mapping loses 270,887 and this mapping loses none. Numbers per axis: [../quality/roundtrip_census.md](../quality/roundtrip_census.md).

**What it does not cover.** It proves the mapping is information-preserving on reference models with full module and LoD coverage; it does not re-run the whole 6.4 GB Hamburg file through export on every release. It says nothing about whether the source itself is correct.

**Why it matters for a query benchmark.** It is the licence to store coordinates verbatim, which in turn is what makes geometric gold answers stable: nothing was rounded on the way in, so nothing shifts on the way out.

---

## Gate 2: OSM ingestion completeness census

**Question: did the fusion step keep everything, place everything, and invent nothing?**

For each city, the expected graph content is re-derived from the source `.osm.pbf` through the *same* extraction and classification code path as the fusion itself, then the fused graph is checked at five levels:

1. **Existence.** Every admitted feature appears exactly once: no missing, no extras, per OSM kind.
2. **Tag fidelity.** Tags reconstruct losslessly from the stored node, verified by canonical SHA1 over the tag set.
3. **Geometry fidelity.** Coordinate `pos_list` verbatim (order-independent digest) and exact bounding boxes.
4. **Placement partition.** The attach-or-orphan split is exact: `matched=true` if and only if an anchor edge exists; `matched=false` implies an `unmatched_reason`; the `osm_*` keys written onto an anchor are a subset of the permitted enrichment keys.
5. **Registration.** Every node is R-tree registered, has provenance, and has a `PART_OF` edge to its dataset.

A separate scope pass quantifies the admission boundary per layer (unfiltered against admitted), so what the fusion deliberately ignores is measured rather than assumed.

**Result: all five cities PASSED, zero missing and zero extra features.**

| City | Admitted features, source | In graph | Gate |
| --- | --: | --: | --- |
| Hamburg | 1,188,139 | 1,188,139 | PASSED |
| Helsinki | 55,930 | 55,930 | PASSED |
| Zurich | 1,860,401 | 1,860,401 | PASSED |
| New York | 2,555,468 | 2,555,468 | PASSED |
| Tokyo | 3,830,408 | 3,830,408 | PASSED |

Per-city reports, including the per-kind breakdown and every placement gate at zero violations: [../quality/osm_census_*.md](../quality/).

**What it does not cover.** It verifies that fusion is faithful to the source and internally consistent. It does not verify that a *match* is semantically correct: there is no city-scale ground truth for OSM-to-CityGML correspondence, which is precisely why the correspondence is released as a confidence-weighted edge instead of a decision, and why link prediction over those edges is one of the learning tasks.

---

## Gate 3: per-city statistical and anomaly control

**Question: what is wrong with the inputs, and did any of it damage the graph?**

Runs in two halves. *Precheck* profiles the source files with no database involved and flags input anomalies: duplicate, placeholder, and missing `gml:id` (the identity-collapse risk), degenerate or missing geometry, non-finite or out-of-CRS coordinates, mixed `srsName`, height, vertex, and spatial outliers, and derived-layer coverage. *Postcheck* profiles the ingested graph: label and edge inventory, nodes-per-building distribution, fan-out detection for identity collapse, missing-source and orphan nodes, OSM kind and orphan rates, and coverage of each derived layer. A cross-check fuses both, of which the important one is **building loss**: distinct source ids minus graph building nodes.

**Result.** No city loses a building: distinct source ids equal graph building nodes everywhere. Findings that this gate produced and that changed the pipeline:

- **Identity collapse on non-unique ids.** Zurich (45) and Helsinki (61) buildings were collapsing into shared nodes because top-level features merge on `gml:id`. Fixed at ingest with content-hash identity resolution, which distinguishes a genuine duplicate (deduplicate) from two distinct features sharing an id (split onto a synthesized id, original kept in `source_gml_id`). Tokyo's ward tiling turned out to be the extreme case: 975,077 byte-identical replicas deduplicated, 468 distinct same-id features split. Traceability record: [../quality/duplicate_ids_traceability.md](../quality/duplicate_ids_traceability.md).
- **Height sentinels.** Tokyo's `-9999` heights (36,071 buildings) and `9999` storey counts (225,776) were found here and are preserved verbatim, excluded from statistics rather than repaired.
- **Known benign flags.** Each report lists flags that were investigated and found benign or false-positive, with the reason: identity-collapse fan-out on genuinely large single buildings (verified against the source), spatial outliers that are simply the city's full extent, high OSM orphan rates where the OSM extract covers more area than the authoritative release, and no-geometry placeholder features that are a source artifact. These are documented rather than silenced, because a reviewer should see what the gate flagged and why it was dismissed.

Per-city reports: [../quality/stats_control_*.md](../quality/).

---

## Gate 4: cross-source conflict analysis

**Question: where and how much do the sources actually disagree?**

Not a pass-or-fail gate but a measurement, run per city over the fused graph: how many buildings carry a value from more than one source for the same attribute, and how far apart those values are. It quantifies the phenomenon the benchmark's cross-source category asks models to reason about. Hamburg, for instance, has 3,641 buildings with a dual-sourced roof material (ML prediction and OSM tag), 3,404 with a dual-sourced height, and 144,364 with dual-sourced storey counts.

Per-city reports: [../quality/cross_source_conflict_*.md](../quality/). Reproduce with [../tools/osm_citygml_conflict_analysis.py](../tools/osm_citygml_conflict_analysis.py).

---

## Benchmark gates

The question suite has its own five gates, applied to every question before release:

| Gate | Check |
| --- | --- |
| **G1** | the gold query executes without error against the released graph |
| **G2** | its canonicalized answer hash is identical across three independent executions (determinism) |
| **G3** | the result is non-empty, unless the template explicitly permits emptiness |
| **G4** | for an infeasible question, a guard query proves the asked-for information is absent (it must return a count of zero on that city's graph) |
| **G5** | on every dataset rebuild all gold answers are re-materialized; any change bumps the suite version with a changelog entry, so gold cannot silently drift from the data |

**Result: 1,394 of 1,406 instantiated questions verified (99.1 %)**, where each of the twelve non-verified instances is a deliberate per-city feasibility flip rather than a failure: an infeasible template whose guard cannot prove absence on a city that happens to have the layer. Per-city verification reports: [../benchmark_a/verification/](../benchmark_a/verification/).

**Human review, and why the machine gates are not enough.** 282 questions (20.2 %), stratified by category, difficulty, city, and language, were reviewed by the authors. The review's material finding is a defect the executable gates had passed: five proximity templates used a radius argument that Neo4j Spatial interprets in kilometres against a geographic layer, while the R-tree stores Cartesian metres, so the effective radius collapsed to a few metres and those gold queries returned near-empty results. G1 to G4 accepted them because a `count` gold always returns one row and the ranked golds carried `allow_empty`. All five were rewritten and the suite was regenerated and re-verified on all five graphs. Two further notes were accepted without change (a harmless extra context column on two Helsinki aggregates, and the Tokyo storey sentinel appearing at the top of a ranked answer, which is correct with respect to the stored graph).

That episode is the honest answer to "who checked the gold?": the machine gate catches execution, determinism, and emptiness; only inspection of the returned *distributions* catches a query that runs cleanly and means the wrong thing. Both are needed, and the cached baseline results predate this particular fix, which is stated explicitly in [../benchmark_a/baselines/README.md](../benchmark_a/baselines/README.md).

---

## Reproducing the gates

All four data gates and the five benchmark gates are scripted. Commands, in the order they were run per city: [REPRODUCE.md](REPRODUCE.md).
