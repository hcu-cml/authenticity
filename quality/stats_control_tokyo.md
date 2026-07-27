# Statistical + anomaly control: tokyo

Generated 20260717_065423 by `eval/stats_control.py`. Precheck: `stats_control_precheck_tokyo_20260716_205933.json`. Postcheck: `stats_control_postcheck_tokyo_20260717_065415.json`.

**7 anomalies** (2 critical, 1 high, 1 low, 3 info); **3 need your decision.**

## Decisions needed

| # | Severity | Code | What | Recommended fix |
| --- | --- | --- | --- | --- |
| 1 | CRITICAL | DUPLICATE_GML_ID | 807091 gml:id value(s) are shared by 1782636 buildings. MERGE (b:Building {id}) collapses each group into ONE node, losing 975545 buildings. | Synthesize a unique id at ingest for these sources (e.g. source-file + gml:id + ordinal, or a geometry hash). |
| 2 | CRITICAL | ID_COLLAPSE | 273 Building node(s) have anomalous fan-out (boundaries > 248 or > 20 building parts), the signature of many source buildings collapsed onto one gml:id. | Re-ingest the affected source with unique-id synthesis; these super-nodes distort every per-building statistic. |
| 3 | HIGH | CRS_RANGE_MISMATCH | CRS EPSG:6697 is geographic but coords look projected (median 35.7, 139.7) | Verify srsName vs actual coordinates; pass the correct --source-crs/--target-crs at ingest. |

## All anomalies

| Severity | Scope | Code | Count | Detail |
| --- | --- | --- | --- | --- |
| CRITICAL | input | DUPLICATE_GML_ID | 1782636 | 807091 gml:id value(s) are shared by 1782636 buildings. MERGE (b:Building {id}) collapses each group into ONE node, losing 975545 buildings. |
| CRITICAL | graph | ID_COLLAPSE | 273 | 273 Building node(s) have anomalous fan-out (boundaries > 248 or > 20 building parts), the signature of many source buildings collapsed onto one gml:id. |
| HIGH | input | CRS_RANGE_MISMATCH | 1 | CRS EPSG:6697 is geographic but coords look projected (median 35.7, 139.7) |
| LOW | input | VERTEX_COUNT_OUTLIER | 72 | 72 building(s) exceed 20000 vertices (p99=411.0). Possible merged multipart or a collapsed placeholder-id super-building. |
| INFO | cross | ID_COLLISIONS_RESOLVED | 975545 | 975545 duplicate-id occurrence(s) in the source were resolved at ingest: 468 split onto synthesized ids (source_gml_id preserved), 975077 deduplicated as identical content/geometry. |
| INFO | input | HEIGHT_SENTINEL | 36071 | 36071 building(s) carry a missing-value sentinel measuredHeight (<= -999.0). Kept verbatim in the data, excluded from all height statistics. |
| INFO | input | OGRINFO_FAILED | - | ogrinfo is on PATH but returned no feature counts for any layer (likely a GDAL/PROJ environment conflict, not an empty file). |

## Input statistics (CityGML)

| Metric | Value |
| --- | --- |
| Files | 2335 |
| Building elements | 2980839 |
| Distinct gml:ids | 2005294 |
| Dominant CRS | http://www.opengis.net/def/crs/EPSG/0/6697 (EPSG:6697) |
| measuredHeight (n/min/med/max) | 2944768/0.1/8.0/355.5 |
| Vertices/building (med/p99/max) | 51.0/411.0/261763.0 |
| Roofmat coverage | 0 (0.0%) |

## Input statistics (OSM)

_ogrinfo returned no counts (GDAL/PROJ env conflict); see OGRINFO_FAILED. OSM completeness is gated by eval/osm_ingestion_census.py after fusion._

_Lossless per-feature OSM verification is eval/osm_ingestion_census.py (run it after fusion). This is a pre-ingest sanity count only._

## Graph statistics (Neo4j)

| Metric | Value |
| --- | --- |
| Dataset | tokyo |
| Total nodes | 74409400 |
| Total relationships | 91949234 |
| Building nodes | 2005762 |
| Boundaries/building (med/p99/max) | 0.0/31.0/6591.0 |
| measured_height (n/min/med/max) | 1981872/0.1/7.9/355.5 |

Nodes per building (CityGML subtree): min 15, avg 28.9, median 21.0, p90 37.0, p99 168.0, max 135567.

Geometry polygons per building: min 6, avg 12.1, median 9.0, p90 16.0, p99 66.0, max 64750.

Thematic attributes per building: min 13, avg 17.7, median 18.0, p90 19.0, p99 20.0, max 22.

### Node labels

| Label | Count |
| --- | --- |
| Entity | 44065533 |
| GeometryRing | 29600596 |
| GeometryPolygon | 29563224 |
| OsmFeature | 3830408 |
| BoundarySurface | 3087724 |
| GeometryMultiSurface | 2692170 |
| OsmBuilding | 2484449 |
| GeometrySolid | 2181009 |
| Building | 2005762 |
| OsmRoad | 836785 |
| CityObject | 659006 |
| GeometryLineString | 643074 |
| Road | 605293 |
| OsmPOI | 263523 |
| OsmFurniture | 65740 |
| OsmLandUse | 49378 |
| CityFurniture | 38231 |
| BuildingInstallation | 37053 |
| OsmVegetation | 26127 |
| SolitaryVegetationObject | 10883 |
| Opening | 6994 |
| OsmWater | 3470 |
| WaterBody | 2895 |
| NestedFeature | 2182 |
| City | 1600 |
| District | 1600 |
| Bridge | 968 |
| PlantCover | 735 |
| SpatialLayer | 2 |
| CityObjectGroup | 1 |
| Dataset | 1 |
| Room | 1 |
| BuildingFunction | 0 |
| BuildingPart | 0 |
| RoofType | 0 |
| TerrainIntersection | 0 |

### Relationship types

| Type | Count |
| --- | --- |
| HAS_EXTERIOR_RING | 29563224 |
| HAS_SURFACE_MEMBER | 26902860 |
| PART_OF | 6496776 |
| RTREE_REFERENCE | 6484630 |
| LOCATED_IN | 5836170 |
| HAS_POLYGON | 3727459 |
| HAS_LOD_SURFACE | 3296009 |
| HAS_BOUNDARY | 3087826 |
| HAS_FOOTPRINT | 2669627 |
| HAS_LOD_SOLID | 2181009 |
| ENRICHED_BY | 1390723 |
| RTREE_CHILD | 96990 |
| HAS_POI | 91487 |
| HAS_LOD_GEOMETRY | 39235 |
| HAS_INTERIOR_RING | 37372 |
| HAS_OUTER_INSTALLATION | 37046 |
| HAS_OPENING | 6994 |
| HAS_NESTED | 2185 |
| COVERS | 1600 |
| HAS_ROOM_INSTALLATION | 6 |
| RTREE_METADATA | 2 |
| RTREE_ROOT | 2 |
| HAS_INTERIOR_INSTALLATION | 1 |
| HAS_INTERIOR_ROOM | 1 |

### OSM enrichment

| Metric | Value |
| --- | --- |
| OsmFeature nodes | 3830408 |
| By kind | building:2484449, road:836785, poi:263523, other:100936, furniture:65740, landuse:49378, vegetation:26127, water:3470 |
| Matched / orphan | 1235353 / 2595055 (67.8% orphan) |
| Enriched buildings | 1181049 |
| POIs attached | 91487 |

## Paper-ready summary statistics

```json
{
  "city": "tokyo",
  "input_building_elements": 2980839,
  "input_distinct_ids": 2005294,
  "graph_building_nodes": 2005762,
  "graph_total_nodes": 74409400,
  "graph_total_relationships": 91949234,
  "nodes_per_building": {
    "min": 15,
    "max": 135567,
    "avg": 28.87079773173431,
    "p50": 21.0,
    "p90": 37.0,
    "p99": 168.0,
    "buildings": 2005762
  },
  "geoms_per_building": {
    "min": 6,
    "max": 64750,
    "avg": 12.101005503146098,
    "p50": 9.0,
    "p90": 16.0,
    "p99": 66.0,
    "buildings": 2005762,
    "unit": "GeometryPolygon nodes in the building's CityGML subtree"
  },
  "attrs_per_building": {
    "min": 13,
    "max": 22,
    "avg": 17.709120523772793,
    "p50": 18.0,
    "p90": 19.0,
    "p99": 20.0,
    "buildings": 2005762,
    "unit": "thematic property keys on the Building node (identity/bbox/spatial-plugin/OSM/LoD3/ML keys excluded)"
  },
  "measured_height_m": {
    "n": 1981872,
    "min": 0.1,
    "max": 355.5,
    "mean": 9.1162,
    "median": 7.9,
    "p90": 12.8,
    "p99": 35.6,
    "stdev": 6.0321
  },
  "osm_feature_nodes": 3830408,
  "osm_orphan_rate": 0.6775,
  "roofmat_coverage": 0.0,
  "anomaly_counts_by_severity": {
    "critical": 2,
    "high": 1,
    "medium": 0,
    "low": 1,
    "info": 3
  }
}
```
