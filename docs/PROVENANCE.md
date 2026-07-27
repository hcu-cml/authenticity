# The provenance model

The design principle, the rules that implement it, and how to use it in queries and in learning.

---

## The principle

> **Every fact stays traceable to its origin, and derived information never replaces authoritative data.**

A city graph that fuses sources has to answer two questions that a single-source graph never faces: *where did this value come from*, and *what do I do when two sources disagree*. The common answer, picking a winner and writing one value, destroys exactly the information a consumer needs to make that decision differently. AuthentiCity keeps both values, records which is which, and attaches a confidence to the link between them.

Four consequences, binding on every mapping function in the pipeline:

1. **Set `source` on every node and every edge.** No fact is anonymous.
2. **Namespace derived scalars.** `osm_*` for crowd-sourced, `predicted_*` for ML output, `lod3_*` for reconstruction. An authoritative key can never be overwritten, not even accidentally: a generic source attribute whose slugged name would collide with a structural property is namespaced instead.
3. **Carry confidence.** On predictions (per-material pixel coverage) and on fusion edges (overlap ratio, Jaccard).
4. **Prefer a provenance node plus an explicit edge over a silent scalar.** The `OsmFeature` and `ENRICHED_BY` pattern is the template every new source follows.

---

## The four trust layers

| Layer | What it is | Trust | Representation | Coverage |
| --- | --- | --- | --- | --- |
| **Authoritative** | official CityGML and cadastral city models, surveyed or photogrammetrically derived, published by a public agency | highest | native node properties, the graph's backbone | all five cities, complete for their release extent |
| **Crowd-sourced** | OpenStreetMap | medium, variable by area and contributor | `OsmFeature` nodes plus `ENRICHED_BY` and `HAS_POI` edges, plus `osm_*` scalars mirrored onto the matched authoritative node | all five cities, whole city |
| **ML-predicted** | our roof-material classifier over aerial imagery | confidence-carrying, per-class | `predicted_roof_material_<i>` and `_coverage` properties plus a `_source` tag | Hamburg, 50.2 % of buildings |
| **Reconstructed** | our LoD3 facade reconstruction | derived | `HAS_LOD3_FACADE` edges with `confidence`, `method`, `method_version`, `lod`, into geometry marked `Lod3Facade` | Hamburg, 17 buildings |

The layers are deliberately *not* uniform in coverage. That is a feature: it produces the coverage-aware and infeasible reasoning that the benchmark measures, and it mirrors what any real integration effort faces.

---

## Cross-source correspondence, kept rather than collapsed

Matching OSM footprints to authoritative footprints is not a bijection. One authoritative building can overlap several OSM ways, one OSM way can span several buildings, and clusters can be entangled in both directions. The pipeline builds an overlap graph over footprint pairs whose overlap exceeds a threshold τ, takes its connected components, and labels each resulting correspondence with its case:

| Case | Meaning |
| --- | --- |
| `1:1` | one building, one OSM feature |
| `1:n` | one building overlapping several OSM features |
| `n:1` | several buildings under one OSM feature (a terrace under a single OSM way, for example) |
| `n:m` | an entangled cluster; the genuinely ambiguous case |

Every pair in a component becomes an `ENRICHED_BY` edge carrying `overlap_ratio`, `jaccard`, `intersection_area`, `match_type`, and `is_primary`. Nothing is thrown away and nothing is merged, so a consumer can rethreshold or reweight without redoing the alignment:

```cypher
// keep only high-confidence correspondences, without re-running the matcher
MATCH (b:Building)-[r:ENRICHED_BY]->(o:OsmFeature)
WHERE r.jaccard >= 0.7
RETURN count(*) AS strong_correspondences;
```

**Attribution rule.** Only the primary match propagates scalars onto the authoritative node, under `osm_*`. Secondary matches keep their values on their own `OsmFeature`. This avoids the ambiguity of writing two different OSM heights onto one building while still keeping both reachable.

**Threshold choice.** τ = 0.3, selected by sweeping τ over [0.1, 0.7] and tracking the mean Jaccard of primary matches (a precision proxy) against the number of enriched buildings (a recall proxy). The mean primary-match Jaccard stays flat at 0.775 across the sweep, which says τ only moves marginal edges: lower values admit low-Jaccard slivers that spuriously connect components and inflate the `n:m` case, higher values drop valid partial correspondences. τ = 0.3 gives near-maximal enrichment at unchanged correspondence quality. Because each edge stores its own Jaccard, this choice is revisable by any consumer.

**Unmatched OSM features are kept.** 6.67 M of 9.49 M OSM features (70.3 %) match no authoritative object, and they remain as spatially indexed standalone nodes with `matched=false` and an explicit `unmatched_reason`. Most are kinds the authoritative model has no counterpart for (roads, land use, water, street furniture); the rest are points inside no footprint or polygons overlapping no footprint. They are net-new knowledge, and treating them as failures would discard the majority of what the crowd layer contributes.

---

## Using provenance in queries

**Authoritative only, which is what a provenance-filtered question demands:**

```cypher
MATCH (b:Building) WHERE b.measured_height > -999
RETURN round(avg(b.measured_height) * 100) / 100.0 AS avg_height_m;   // never osm_height
```

**Compare the two sources directly, since both survive:**

```cypher
MATCH (b:Building)-[r:ENRICHED_BY {is_primary: true}]->(o:OsmFeature)
WHERE b.measured_height > -999 AND o.osm_height IS NOT NULL
WITH abs(toFloat(o.osm_height) - b.measured_height) AS delta
RETURN count(*) AS pairs,
       round(avg(delta) * 100) / 100.0 AS mean_abs_deviation_m,
       sum(CASE WHEN delta <= 1.0 THEN 1 ELSE 0 END) AS agree_within_1m;
```

**Ask what the crowd layer knows where the authoritative source is silent.** This is the only way to get a height for New York at all:

```cypher
MATCH (b:Building)-[:ENRICHED_BY {is_primary: true}]->(o:OsmFeature)
WHERE b.measured_height IS NULL AND o.osm_height IS NOT NULL
RETURN count(*) AS osm_only_heights,
       round(avg(toFloat(o.osm_height)) * 10) / 10.0 AS mean_osm_height_m;
```

**Filter by confidence, not just by existence:**

```cypher
MATCH (b:Building)-[r:ENRICHED_BY]->(o:OsmFeature)
WHERE r.match_type = 'n:m' AND r.jaccard < 0.3
RETURN b.id, o.osm_id, r.jaccard ORDER BY r.jaccard ASC, b.id ASC LIMIT 20;
```

**Respect coverage in aggregates.** A bare count over a partially covered attribute is the benchmark's flagship trap:

```cypher
MATCH (b:Building)
WITH count(b) AS total,
     count(CASE WHEN b.predictedroofmaterial IS NOT NULL THEN 1 END) AS covered
RETURN covered, total, round(100.0 * covered / total * 10) / 10.0 AS coverage_pct;
```

**Read a prediction with its confidence, not alone:**

```cypher
MATCH (b:Building) WHERE b.predicted_roof_material_count > 1
RETURN b.id, b.predicted_roof_material_0, b.predicted_roof_material_0_coverage,
       b.predicted_roof_material_1, b.predicted_roof_material_1_coverage
ORDER BY b.predicted_roof_material_1_coverage DESC, b.id ASC LIMIT 10;
```

**Discount reconstructed geometry independently of authoritative geometry.** `HAS_LOD3_FACADE` is a separate edge from `HAS_BOUNDARY` precisely so a query can trust one and not the other:

```cypher
MATCH (b:Building)-[e:HAS_LOD3_FACADE]->(:BoundarySurface)
WHERE e.confidence >= 0.8
RETURN b.id, e.method, e.confidence ORDER BY e.confidence DESC, b.id ASC;
```

---

## Using provenance in learning

Benchmark B's two protocols differ only in how much of this structure the encoder may see, so any gap is attributable to provenance awareness rather than to model capacity:

- **Provenance-agnostic**: flatten the multi-source graph into canonical entities, merge source-specific evidence, drop edge confidences, discard source labels. This is how existing urban graphs are consumed.
- **Provenance-aware**: keep source-typed nodes and relations, use the Jaccard on fusion edges as a normalized message-passing weight, and expose coverage and agreement features (source presence, source count, best-match confidence).

The measured outcome is reported honestly in [../benchmark_b/README.md](../benchmark_b/README.md): small but consistent gains in distribution, substantial gains under cross-city shift, and evidence that source *typing* rather than confidence *weighting* carries the in-distribution effect. Provenance-aware representation learning is posed as an open problem; this dataset is the substrate for it, not a solution to it.

---

## Adding a new source layer

Any contributed layer must decide and store provenance before writing anything. The contract, in the order the pipeline applies it:

1. **Own node label** (and own R-tree layer if it has geometry), so the layer can be identified, trusted, or removed as a unit.
2. **Namespaced scalars** on existing nodes; never an authoritative key.
3. **Explicit, confidence-carrying edges** for any correspondence, with the cardinality case recorded rather than resolved away.
4. **A `source` value on every node and edge** written.
5. **Coverage made explicit**, so absence reads as "not covered" and never as a negative observation.
6. **Idempotent ingest**, so a re-run replaces the layer rather than duplicating it.
7. **A completeness gate** before release, in the style of the OSM ingestion census: re-derive the expected content from the source and verify the graph against it.
8. **Guard queries re-run**, because an infeasible benchmark question is infeasible only with respect to a specific graph version, and a new layer can make it answerable.
