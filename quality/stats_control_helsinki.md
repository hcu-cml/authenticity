# Statistical + anomaly control: helsinki

Generated 20260716_165221 by `eval/stats_control.py`. Precheck: `stats_control_precheck_helsinki_20260716_164730.json`. Postcheck: `stats_control_postcheck_helsinki_20260716_165155.json`.

**4 anomalies** (1 critical, 1 low, 2 info); **1 need your decision.**

## Decisions needed

| # | Severity | Code | What | Recommended fix |
| --- | --- | --- | --- | --- |
| 1 | CRITICAL | DUPLICATE_GML_ID | 61 gml:id value(s) are shared by 122 buildings. MERGE (b:Building {id}) collapses each group into ONE node, losing 61 buildings. | Synthesize a unique id at ingest for these sources (e.g. source-file + gml:id + ordinal, or a geometry hash). |

## All anomalies

| Severity | Scope | Code | Count | Detail |
| --- | --- | --- | --- | --- |
| CRITICAL | input | DUPLICATE_GML_ID | 122 | 61 gml:id value(s) are shared by 122 buildings. MERGE (b:Building {id}) collapses each group into ONE node, losing 61 buildings. |
| LOW | graph | OSM_HIGH_ORPHAN_RATE | 51649 | 92.3% of OSM features are unmatched orphans (expected for city-wide extracts: roads, natural areas, POIs outside building footprints). Informational. |
| INFO | cross | ID_COLLISIONS_RESOLVED | 61 | 61 duplicate-id occurrence(s) in the source were resolved at ingest: 61 split onto synthesized ids (source_gml_id preserved), 0 deduplicated as identical content/geometry. |
| INFO | input | OGRINFO_FAILED | - | ogrinfo is on PATH but returned no feature counts for any layer (likely a GDAL/PROJ environment conflict, not an empty file). |

## Input statistics (CityGML)

| Metric | Value |
| --- | --- |
| Files | 1 |
| Building elements | 2980 |
| Distinct gml:ids | 2919 |
| Dominant CRS | urn:ogc:drf:crs:EPSG::3879 (EPSG:3879) |
| measuredHeight (n/min/med/max) | 2972/0.26/10.11/135.0 |
| Vertices/building (med/p99/max) | 116.0/2176.47/5663.0 |
| Roofmat coverage | 0 (0.0%) |

## Input statistics (OSM)

_ogrinfo returned no counts (GDAL/PROJ env conflict); see OGRINFO_FAILED. OSM completeness is gated by eval/osm_ingestion_census.py after fusion._

_Lossless per-feature OSM verification is eval/osm_ingestion_census.py (run it after fusion). This is a pre-ingest sanity count only._

## Graph statistics (Neo4j)

| Metric | Value |
| --- | --- |
| Dataset | helsinki_citygml2_lod2_2019.gml |
| Total nodes | 414459 |
| Total relationships | 619964 |
| Building nodes | 2980 |
| Boundaries/building (med/p99/max) | 10.0/83.63/245.0 |
| measured_height (n/min/med/max) | 2972/0.26/10.11/135.0 |

Nodes per building (CityGML subtree): min 15, avg 107.4, median 54.0, p90 251.0999999999999, p99 683.4700000000003, max 1697.

Geometry polygons per building: min 5, avg 43.2, median 20.0, p90 104.0, p99 311.6300000000001, max 817.

Thematic attributes per building: min 4, avg 37.1, median 43.0, p90 43.0, p99 43.0, max 43.

### Node labels

| Label | Count |
| --- | --- |
| Entity | 256292 |
| GeometryRing | 142094 |
| GeometryPolygon | 141076 |
| OsmFeature | 55930 |
| BoundarySurface | 50620 |
| OsmRoad | 20666 |
| GeometryLineString | 15180 |
| OsmFurniture | 10533 |
| GeometrySolid | 5585 |
| OsmPOI | 4942 |
| OsmBuilding | 3157 |
| Building | 2980 |
| OsmLandUse | 1958 |
| OsmVegetation | 1264 |
| OsmWater | 45 |
| Bridge | 31 |
| CityObject | 31 |
| GeometryMultiSurface | 31 |
| RoofType | 20 |
| BuildingFunction | 19 |
| SpatialLayer | 2 |
| City | 1 |
| Dataset | 1 |
| District | 1 |
| BuildingPart | 0 |
| TerrainIntersection | 0 |

### Relationship types

| Type | Count |
| --- | --- |
| HAS_EXTERIOR_RING | 141076 |
| HAS_SURFACE_MEMBER | 132691 |
| HAS_POLYGON | 79822 |
| PART_OF | 58942 |
| RTREE_REFERENCE | 58941 |
| LOCATED_IN | 58910 |
| HAS_BOUNDARY | 50620 |
| HAS_LOD_SURFACE | 15211 |
| HAS_FOOTPRINT | 8385 |
| HAS_LOD_SOLID | 5585 |
| ENRICHED_BY | 3011 |
| HAS_ROOF_TYPE | 2972 |
| HAS_POI | 1797 |
| HAS_INTERIOR_RING | 1018 |
| RTREE_CHILD | 884 |
| HAS_FUNCTION | 94 |
| RTREE_METADATA | 2 |
| RTREE_ROOT | 2 |
| COVERS | 1 |

### OSM enrichment

| Metric | Value |
| --- | --- |
| OsmFeature nodes | 55930 |
| By kind | road:20666, other:13365, furniture:10533, poi:4942, building:3157, landuse:1958, vegetation:1264, water:45 |
| Matched / orphan | 4281 / 51649 (92.3% orphan) |
| Enriched buildings | 2476 |
| POIs attached | 1797 |

## Paper-ready summary statistics

```json
{
  "city": "helsinki",
  "input_building_elements": 2980,
  "input_distinct_ids": 2919,
  "graph_building_nodes": 2980,
  "graph_total_nodes": 414459,
  "graph_total_relationships": 619964,
  "nodes_per_building": {
    "min": 15,
    "max": 1697,
    "avg": 107.43825503355684,
    "p50": 54.0,
    "p90": 251.0999999999999,
    "p99": 683.4700000000003,
    "buildings": 2980
  },
  "geoms_per_building": {
    "min": 5,
    "max": 817,
    "avg": 43.179530201342324,
    "p50": 20.0,
    "p90": 104.0,
    "p99": 311.6300000000001,
    "buildings": 2980,
    "unit": "GeometryPolygon nodes in the building's CityGML subtree"
  },
  "attrs_per_building": {
    "min": 4,
    "max": 43,
    "avg": 37.05973154362415,
    "p50": 43.0,
    "p90": 43.0,
    "p99": 43.0,
    "buildings": 2980,
    "unit": "thematic property keys on the Building node (identity/bbox/spatial-plugin/OSM/LoD3/ML keys excluded)"
  },
  "measured_height_m": {
    "n": 2972,
    "min": 0.26,
    "max": 135.0,
    "mean": 13.5935,
    "median": 10.11,
    "p90": 26.71,
    "p99": 46.358,
    "stdev": 11.5186
  },
  "osm_feature_nodes": 55930,
  "osm_orphan_rate": 0.9235,
  "roofmat_coverage": 0.0,
  "anomaly_counts_by_severity": {
    "critical": 1,
    "high": 0,
    "medium": 0,
    "low": 1,
    "info": 2
  }
}
```
