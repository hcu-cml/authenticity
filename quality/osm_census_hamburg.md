# OSM ingestion census — hamburg_citygml2_lod2_2025.gml

*Run 20260717_175025 · source `input\osm\hamburg-260629.osm.pbf` · CRS EPSG:25832 · buffer 10.0 m · gate **PASSED***

Completeness + placement gate for the OSM enrichment (`eval/osm_ingestion_census.py`): every OSM feature admitted from the source `.osm.pbf` must be stored losslessly as an `OsmFeature` node and placed either on a CityGML anchor (`ENRICHED_BY`/`HAS_POI`) or as a spatially indexed standalone node with an `unmatched_reason`.

## Source vs. graph

| Quantity | Source (expected) | Graph |
| -------- | ----------------- | ----- |
| OSM features (admitted, parseable) | 1188139 | 1188139 |
| kind `building` | 354162 | 354162 |
| kind `furniture` | 299406 | 299406 |
| kind `landuse` | 20810 | 20810 |
| kind `other` | 140660 | 140660 |
| kind `poi` | 81353 | 81353 |
| kind `road` | 281056 | 281056 |
| kind `vegetation` | 7753 | 7753 |
| kind `water` | 2939 | 2939 |

Placement split (graph): {'False': 831432, 'True': 356707}. Source-side skips: 0 features with empty/unparseable geometry after the ogr2ogr clip; 0 duplicate stable ids.

## Per-feature fidelity findings

None — feature existence, tag reconstruction (canonical SHA1), verbatim geometry `pos_list` digests, bboxes, labels, and point locations all match the source.

## Placement / indexing / provenance gates

| Gate | Violations |
| ---- | ---------- |
| flag_null | 0 |
| matched_without_anchor | 0 |
| orphan_with_anchor | 0 |
| orphan_without_reason | 0 |
| missing_provenance | 0 |
| missing_part_of | 0 |
| missing_rtree | 0 |
| missing_bbox_wkt | 0 |
| enriched_by_bad_props | 0 |
| has_poi_bad_props | 0 |
| bad_anchor_labels | 0 |
| anchor_namespace_violations | 0 |

## Scope: thematic tag filter admission (informational)

Unfiltered feature counts per GDAL/OSM canonical layer inside the same city bounding box. The ingestion reads the three geometry-bearing layers: `points` and `multipolygons` unfiltered, `lines` restricted by the `LAYER_WHERE` filter (transport/water network). `multilinestrings` (route relations) and `other_relations` are views over member ways/nodes already present in the base layers.

| Layer | Unfiltered in bbox | Admitted |
| ----- | -------------------- | -------- |
| points | 540664 | 540664 |
| lines | 274507 | 230166 |
| multipolygons | 417309 | 417309 |
| multilinestrings | 1425 | — |
| other_relations | 8613 | — |
