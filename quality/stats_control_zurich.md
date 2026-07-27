# Statistical + anomaly control: zurich

Generated 20260716_175604 by `eval/stats_control.py`. Precheck: `stats_control_precheck_zurich_20260716_171020.json`. Postcheck: `stats_control_postcheck_zurich_20260716_175533.json`.

**8 anomalies** (3 critical, 1 high, 2 low, 2 info); **3 need your decision.**

## Decisions needed

| # | Severity | Code | What | Recommended fix |
| --- | --- | --- | --- | --- |
| 1 | CRITICAL | DUPLICATE_GML_ID | 17 gml:id value(s) are shared by 62 buildings. MERGE (b:Building {id}) collapses each group into ONE node, losing 45 buildings. | Synthesize a unique id at ingest for these sources (e.g. source-file + gml:id + ordinal, or a geometry hash). |
| 2 | CRITICAL | PLACEHOLDER_GML_ID | 1 placeholder gml:id value(s) (ID_) on 30 buildings. | Same fix as DUPLICATE_GML_ID; placeholder ids are the swissBUILDINGS3D failure mode. |
| 3 | CRITICAL | ID_COLLAPSE | 3 Building node(s) have anomalous fan-out (boundaries > 200 or > 20 building parts), the signature of many source buildings collapsed onto one gml:id. | Re-ingest the affected source with unique-id synthesis; these super-nodes distort every per-building statistic. |

## All anomalies

| Severity | Scope | Code | Count | Detail |
| --- | --- | --- | --- | --- |
| CRITICAL | input | DUPLICATE_GML_ID | 62 | 17 gml:id value(s) are shared by 62 buildings. MERGE (b:Building {id}) collapses each group into ONE node, losing 45 buildings. |
| CRITICAL | input | PLACEHOLDER_GML_ID | 30 | 1 placeholder gml:id value(s) (ID_) on 30 buildings. |
| CRITICAL | graph | ID_COLLAPSE | 3 | 3 Building node(s) have anomalous fan-out (boundaries > 200 or > 20 building parts), the signature of many source buildings collapsed onto one gml:id. |
| HIGH | input | NO_GEOMETRY | 5 | 5 building(s) carry no LinearRing geometry. |
| LOW | graph | OSM_HIGH_ORPHAN_RATE | 1757607 | 94.5% of OSM features are unmatched orphans (expected for city-wide extracts: roads, natural areas, POIs outside building footprints). Informational. |
| LOW | input | VERTEX_COUNT_OUTLIER | 15 | 15 building(s) exceed 20020 vertices (p99=4004.0). Possible merged multipart or a collapsed placeholder-id super-building. |
| INFO | cross | ID_COLLISIONS_RESOLVED | 45 | 45 duplicate-id occurrence(s) in the source were resolved at ingest: 40 split onto synthesized ids (source_gml_id preserved), 5 deduplicated as identical content/geometry. |
| INFO | input | OGRINFO_FAILED | - | ogrinfo is on PATH but returned no feature counts for any layer (likely a GDAL/PROJ environment conflict, not an empty file). |

## Input statistics (CityGML)

| Metric | Value |
| --- | --- |
| Files | 78 |
| Building elements | 102673 |
| Distinct gml:ids | 102628 |
| Dominant CRS | EPSG:2056 (EPSG:2056) |
| measuredHeight (n/min/med/max) | 100351/1.0/9.39/189.68 |
| Vertices/building (med/p99/max) | 496.0/4004.0/316924.0 |
| Roofmat coverage | 0 (0.0%) |

## Input statistics (OSM)

_ogrinfo returned no counts (GDAL/PROJ env conflict); see OGRINFO_FAILED. OSM completeness is gated by eval/osm_ingestion_census.py after fusion._

_Lossless per-feature OSM verification is eval/osm_ingestion_census.py (run it after fusion). This is a pre-ingest sanity count only._

## Graph statistics (Neo4j)

| Metric | Value |
| --- | --- |
| Dataset | zurich |
| Total nodes | 41508371 |
| Total relationships | 45548405 |
| Building nodes | 102668 |
| Boundaries/building (med/p99/max) | 3.0/13.0/916.0 |
| measured_height (n/min/med/max) | 95983/1.0/9.22/189.68 |

Nodes per building (CityGML subtree): min 6, avg 369.8, median 253.0, p90 738.0, p99 2019.0, max 160003.

Geometry polygons per building: min 2, avg 181.8, median 124.0, p90 365.0, p99 1001.0, max 79231.

Thematic attributes per building: min 3, avg 20.9, median 22.0, p90 22.0, p99 22.0, max 24.

### Node labels

| Label | Count |
| --- | --- |
| Entity | 21762846 |
| GeometryRing | 19259959 |
| GeometryPolygon | 19253759 |
| OsmFeature | 1860401 |
| OsmRoad | 502180 |
| OsmBuilding | 460631 |
| GeometryLineString | 455516 |
| BoundarySurface | 425263 |
| OsmFurniture | 424171 |
| OsmPOI | 158125 |
| GeometrySolid | 108725 |
| Building | 102668 |
| OsmLandUse | 43710 |
| OsmVegetation | 13480 |
| BuildingPart | 12030 |
| OsmWater | 4762 |
| City | 78 |
| District | 78 |
| SpatialLayer | 2 |
| Dataset | 1 |
| BuildingFunction | 0 |
| CityObject | 0 |
| GeometryMultiSurface | 0 |
| RoofType | 0 |
| TerrainIntersection | 0 |

### Relationship types

| Type | Count |
| --- | --- |
| HAS_EXTERIOR_RING | 19253759 |
| HAS_POLYGON | 9530119 |
| HAS_SURFACE_MEMBER | 9130806 |
| PART_OF | 1963147 |
| LOCATED_IN | 1963069 |
| RTREE_REFERENCE | 1963069 |
| HAS_FOOTPRINT | 592834 |
| HAS_LOD_SURFACE | 455516 |
| HAS_BOUNDARY | 425263 |
| HAS_LOD_SOLID | 108725 |
| ENRICHED_BY | 100312 |
| RTREE_CHILD | 29887 |
| HAS_POI | 13587 |
| HAS_BUILDING_PART | 12030 |
| HAS_INTERIOR_RING | 6200 |
| COVERS | 78 |
| RTREE_METADATA | 2 |
| RTREE_ROOT | 2 |

### OSM enrichment

| Metric | Value |
| --- | --- |
| OsmFeature nodes | 1860401 |
| By kind | road:502180, building:460631, furniture:424171, other:253342, poi:158125, landuse:43710, vegetation:13480, water:4762 |
| Matched / orphan | 102794 / 1757607 (94.5% orphan) |
| Enriched buildings | 93958 |
| POIs attached | 13587 |

## Paper-ready summary statistics

```json
{
  "city": "zurich",
  "input_building_elements": 102673,
  "input_distinct_ids": 102628,
  "graph_building_nodes": 102668,
  "graph_total_nodes": 41508371,
  "graph_total_relationships": 45548405,
  "nodes_per_building": {
    "min": 6,
    "max": 160003,
    "avg": 369.8380800249379,
    "p50": 253.0,
    "p90": 738.0,
    "p99": 2019.0,
    "buildings": 102668
  },
  "geoms_per_building": {
    "min": 2,
    "max": 79231,
    "avg": 181.75989597537733,
    "p50": 124.0,
    "p90": 365.0,
    "p99": 1001.0,
    "buildings": 102668,
    "unit": "GeometryPolygon nodes in the building's CityGML subtree"
  },
  "attrs_per_building": {
    "min": 3,
    "max": 24,
    "avg": 20.90915377722388,
    "p50": 22.0,
    "p90": 22.0,
    "p99": 22.0,
    "buildings": 102668,
    "unit": "thematic property keys on the Building node (identity/bbox/spatial-plugin/OSM/LoD3/ML keys excluded)"
  },
  "measured_height_m": {
    "n": 95983,
    "min": 1.0,
    "max": 189.68,
    "mean": 10.0303,
    "median": 9.22,
    "p90": 17.28,
    "p99": 25.82,
    "stdev": 5.5858
  },
  "osm_feature_nodes": 1860401,
  "osm_orphan_rate": 0.9447,
  "roofmat_coverage": 0.0,
  "anomaly_counts_by_severity": {
    "critical": 3,
    "high": 1,
    "medium": 0,
    "low": 2,
    "info": 2
  }
}
```
