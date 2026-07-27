# Statistical + anomaly control: hamburg

Generated 20260717_174439 by `eval/stats_control.py`. Precheck: `stats_control_precheck_hamburg_20260713_052553.json`. Postcheck: `stats_control_postcheck_hamburg_20260717_174439.json`.

**3 anomalies** (1 critical, 1 medium, 1 info); **1 need your decision.**

## Decisions needed

| # | Severity | Code | What | Recommended fix |
| --- | --- | --- | --- | --- |
| 1 | CRITICAL | ID_COLLAPSE | 4 Building node(s) have anomalous fan-out (boundaries > 456 or > 20 building parts), the signature of many source buildings collapsed onto one gml:id. | Re-ingest the affected source with unique-id synthesis; these super-nodes distort every per-building statistic. |

## All anomalies

| Severity | Scope | Code | Count | Detail |
| --- | --- | --- | --- | --- |
| CRITICAL | graph | ID_COLLAPSE | 4 | 4 Building node(s) have anomalous fan-out (boundaries > 456 or > 20 building parts), the signature of many source buildings collapsed onto one gml:id. |
| MEDIUM | input | SPATIAL_OUTLIER | 92 | 92 building(s) sit > 12 MAD from the dataset centroid (possible coordinate typo / wrong-tile contamination). |
| INFO | input | OGRINFO_FAILED | - | ogrinfo is on PATH but returned no feature counts for any layer (likely a GDAL/PROJ environment conflict, not an empty file). |

## Input statistics (CityGML)

| Metric | Value |
| --- | --- |
| Files | 1 |
| Building elements | 388267 |
| Distinct gml:ids | 388267 |
| Dominant CRS | urn:adv:crs:ETRS89_UTM32*DE_DHHN2016_NH (EPSG:25832) |
| measuredHeight (n/min/med/max) | 388267/0.737/7.528/158.47 |
| Vertices/building (med/p99/max) | 44.0/380.0/4071.0 |
| Roofmat coverage | 194799 (50.2%) |

Predicted roof-material classes: roof_tiles (108659), tar_paper (51435), concrete (22923), metal (8550), glass (3232)

## Input statistics (OSM)

_ogrinfo returned no counts (GDAL/PROJ env conflict); see OGRINFO_FAILED. OSM completeness is gated by eval/osm_ingestion_census.py after fusion._

_Lossless per-feature OSM verification is eval/osm_ingestion_census.py (run it after fusion). This is a pre-ingest sanity count only._

## Graph statistics (Neo4j)

| Metric | Value |
| --- | --- |
| Dataset | hamburg_citygml2_lod2_2025.gml |
| Total nodes | 17440924 |
| Total relationships | 26299391 |
| Building nodes | 388267 |
| Boundaries/building (med/p99/max) | 8.0/57.0/583.0 |
| measured_height (n/min/med/max) | 388267/0.737/7.528/158.47 |

Nodes per building (CityGML subtree): min 21, avg 41.0, median 30, p90 66.0, p99 177.0, max 1758.

Geometry polygons per building: min 5, avg 11.7, median 8, p90 20.0, p99 57.0, max 583.

Thematic attributes per building: min 18, avg 21.9, median 22, p90 24.0, p99 24.0, max 28.

### Node labels

| Label | Count |
| --- | --- |
| Entity | 11451598 |
| GeometryRing | 4957926 |
| GeometryPolygon | 4951956 |
| BoundarySurface | 4533833 |
| OsmFeature | 1188139 |
| GeometryLineString | 619363 |
| Building | 388267 |
| GeometrySolid | 388267 |
| TerrainIntersection | 388248 |
| OsmBuilding | 354162 |
| OsmFurniture | 299406 |
| OsmRoad | 281056 |
| OsmPOI | 81353 |
| OsmLandUse | 20810 |
| OsmVegetation | 7753 |
| Lod3Facade | 3404 |
| OsmWater | 2939 |
| GeometryMultiSurface | 499 |
| Opening | 499 |
| BuildingFunction | 131 |
| RoofType | 7 |
| SpatialLayer | 3 |
| City | 1 |
| Dataset | 1 |
| District | 1 |
| BuildingPart | 0 |
| CityObject | 0 |

### Relationship types

| Type | Count |
| --- | --- |
| HAS_EXTERIOR_RING | 4951956 |
| HAS_SURFACE_MEMBER | 4534029 |
| HAS_POLYGON | 4533833 |
| HAS_BOUNDARY | 4533530 |
| RTREE_REFERENCE | 1576709 |
| PART_OF | 1576407 |
| LOCATED_IN | 1576406 |
| HAS_FOOTPRINT | 417624 |
| HAS_LINE | 389197 |
| HAS_FUNCTION | 388267 |
| HAS_LOD_SOLID | 388267 |
| HAS_ROOF_TYPE | 388267 |
| HAS_TERRAIN_INTERSECTION | 388248 |
| ENRICHED_BY | 373211 |
| HAS_LOD_SURFACE | 230665 |
| RTREE_CHILD | 23777 |
| HAS_POI | 22219 |
| HAS_INTERIOR_RING | 5970 |
| HAS_OPENING | 499 |
| HAS_LOD3_FACADE | 303 |
| RTREE_METADATA | 3 |
| RTREE_ROOT | 3 |
| COVERS | 1 |

### OSM enrichment

| Metric | Value |
| --- | --- |
| OsmFeature nodes | 1188139 |
| By kind | building:354162, furniture:299406, road:281056, other:140660, poi:81353, landuse:20810, vegetation:7753, water:2939 |
| Matched / orphan | 356707 / 831432 (70.0% orphan) |
| Enriched buildings | 331318 |
| POIs attached | 22219 |

## Paper-ready summary statistics

```json
{
  "city": "hamburg",
  "input_building_elements": 388267,
  "input_distinct_ids": 388267,
  "graph_building_nodes": 388267,
  "graph_total_nodes": 17440924,
  "graph_total_relationships": 26299391,
  "nodes_per_building": {
    "min": 21,
    "max": 1758,
    "avg": 41.043907929337514,
    "p50": 30,
    "p90": 66.0,
    "p99": 177.0,
    "buildings": 388267
  },
  "geoms_per_building": {
    "min": 5,
    "max": 583,
    "avg": 11.678386265121858,
    "p50": 8,
    "p90": 20.0,
    "p99": 57.0,
    "buildings": 388267,
    "unit": "GeometryPolygon nodes in the building's CityGML subtree"
  },
  "attrs_per_building": {
    "min": 18,
    "max": 28,
    "avg": 21.949707289056022,
    "p50": 22,
    "p90": 24.0,
    "p99": 24.0,
    "buildings": 388267,
    "unit": "thematic property keys on the Building node (identity/bbox/spatial-plugin/OSM/LoD3/ML keys excluded)"
  },
  "measured_height_m": {
    "n": 388267,
    "min": 0.737,
    "max": 158.47,
    "mean": 7.7479,
    "median": 7.528,
    "p90": 13.8894,
    "p99": 24.4553,
    "stdev": 5.1083
  },
  "osm_feature_nodes": 1188139,
  "osm_orphan_rate": 0.6998,
  "roofmat_coverage": 0.5017,
  "anomaly_counts_by_severity": {
    "critical": 1,
    "high": 0,
    "medium": 1,
    "low": 0,
    "info": 1
  }
}
```
