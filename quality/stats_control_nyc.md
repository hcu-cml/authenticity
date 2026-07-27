# Statistical + anomaly control: nyc

Generated 20260716_201036 by `eval/stats_control.py`. Precheck: `stats_control_precheck_nyc_20260716_182921.json`. Postcheck: `stats_control_postcheck_nyc_20260716_201002.json`.

**2 anomalies** (1 critical, 1 info); **1 need your decision.**

## Decisions needed

| # | Severity | Code | What | Recommended fix |
| --- | --- | --- | --- | --- |
| 1 | CRITICAL | ID_COLLAPSE | 51 Building node(s) have anomalous fan-out (boundaries > 500 or > 20 building parts), the signature of many source buildings collapsed onto one gml:id. | Re-ingest the affected source with unique-id synthesis; these super-nodes distort every per-building statistic. |

## All anomalies

| Severity | Scope | Code | Count | Detail |
| --- | --- | --- | --- | --- |
| CRITICAL | graph | ID_COLLAPSE | 51 | 51 Building node(s) have anomalous fan-out (boundaries > 500 or > 20 building parts), the signature of many source buildings collapsed onto one gml:id. |
| INFO | input | OGRINFO_FAILED | - | ogrinfo is on PATH but returned no feature counts for any layer (likely a GDAL/PROJ environment conflict, not an empty file). |

## Input statistics (CityGML)

| Metric | Value |
| --- | --- |
| Files | 20 |
| Building elements | 1083437 |
| Distinct gml:ids | 1083437 |
| Dominant CRS | EPSG:2263 (EPSG:2263) |
| measuredHeight (n/min/med/max) | 0/None/None/None |
| Vertices/building (med/p99/max) | 52.0/338.0/18151.0 |
| Roofmat coverage | 0 (0.0%) |

## Input statistics (OSM)

_ogrinfo returned no counts (GDAL/PROJ env conflict); see OGRINFO_FAILED. OSM completeness is gated by eval/osm_ingestion_census.py after fusion._

_Lossless per-feature OSM verification is eval/osm_ingestion_census.py (run it after fusion). This is a pre-ingest sanity count only._

## Graph statistics (Neo4j)

| Metric | Value |
| --- | --- |
| Dataset | nyc |
| Total nodes | 45797985 |
| Total relationships | 54207134 |
| Building nodes | 1083437 |
| Boundaries/building (med/p99/max) | 10.0/53.0/3433.0 |
| measured_height (n/min/med/max) | 0/None/None/None |

Nodes per building (CityGML subtree): min 4, avg 36.9, median 31, p90 58.0, p99 160.0, max 9620.

Geometry polygons per building: min 1, avg 12.0, median 10, p90 19.0, p99 53.0, max 3093.

Thematic attributes per building: min 7, avg 7.0, median 7, p90 7.0, p99 7.0, max 7.

### Node labels

| Label | Count |
| --- | --- |
| Entity | 30946553 |
| GeometryRing | 14351004 |
| GeometryPolygon | 14341705 |
| BoundarySurface | 12965943 |
| OsmFeature | 2555468 |
| OsmBuilding | 1166948 |
| Building | 1083437 |
| OsmRoad | 659851 |
| GeometryLineString | 445957 |
| OsmFurniture | 209666 |
| OsmPOI | 201840 |
| OsmLandUse | 23488 |
| OsmVegetation | 7312 |
| OsmWater | 1471 |
| City | 20 |
| District | 20 |
| SpatialLayer | 2 |
| Dataset | 1 |
| BuildingFunction | 0 |
| BuildingPart | 0 |
| CityObject | 0 |
| GeometryMultiSurface | 0 |
| GeometrySolid | 0 |
| RoofType | 0 |
| TerrainIntersection | 0 |

### Relationship types

| Type | Count |
| --- | --- |
| HAS_EXTERIOR_RING | 14341705 |
| HAS_BOUNDARY | 12965943 |
| HAS_POLYGON | 12965603 |
| PART_OF | 3638925 |
| LOCATED_IN | 3638905 |
| RTREE_REFERENCE | 3638905 |
| HAS_FOOTPRINT | 1376102 |
| ENRICHED_BY | 1078893 |
| HAS_LOD_SURFACE | 445957 |
| RTREE_CHILD | 54424 |
| HAS_POI | 52449 |
| HAS_INTERIOR_RING | 9299 |
| COVERS | 20 |
| RTREE_METADATA | 2 |
| RTREE_ROOT | 2 |

### OSM enrichment

| Metric | Value |
| --- | --- |
| OsmFeature nodes | 2555468 |
| By kind | building:1166948, road:659851, other:284892, furniture:209666, poi:201840, landuse:23488, vegetation:7312, water:1471 |
| Matched / orphan | 1121901 / 1433567 (56.1% orphan) |
| Enriched buildings | 1070177 |
| POIs attached | 52449 |

## Paper-ready summary statistics

```json
{
  "city": "nyc",
  "input_building_elements": 1083437,
  "input_distinct_ids": 1083437,
  "graph_building_nodes": 1083437,
  "graph_total_nodes": 45797985,
  "graph_total_relationships": 54207134,
  "nodes_per_building": {
    "min": 4,
    "max": 9620,
    "avg": 36.9016297209719,
    "p50": 31,
    "p90": 58.0,
    "p99": 160.0,
    "buildings": 1083437
  },
  "geoms_per_building": {
    "min": 1,
    "max": 3093,
    "avg": 11.967103763301784,
    "p50": 10,
    "p90": 19.0,
    "p99": 53.0,
    "buildings": 1083437,
    "unit": "GeometryPolygon nodes in the building's CityGML subtree"
  },
  "attrs_per_building": {
    "min": 7,
    "max": 7,
    "avg": 7.0,
    "p50": 7,
    "p90": 7.0,
    "p99": 7.0,
    "buildings": 1083437,
    "unit": "thematic property keys on the Building node (identity/bbox/spatial-plugin/OSM/LoD3/ML keys excluded)"
  },
  "measured_height_m": {
    "n": 0
  },
  "osm_feature_nodes": 2555468,
  "osm_orphan_rate": 0.561,
  "roofmat_coverage": 0.0,
  "anomaly_counts_by_severity": {
    "critical": 1,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 1
  }
}
```
