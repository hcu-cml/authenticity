# OSM ingestion census — tokyo

*Run 20260717_071730 · source `input\osm\kanto-260703.osm.pbf` · CRS EPSG:6677 · buffer 10.0 m · gate **PASSED***

Completeness + placement gate for the OSM enrichment (`eval/osm_ingestion_census.py`): every OSM feature admitted from the source `.osm.pbf` must be stored losslessly as an `OsmFeature` node and placed either on a CityGML anchor (`ENRICHED_BY`/`HAS_POI`) or as a spatially indexed standalone node with an `unmatched_reason`.

## Source vs. graph

| Quantity | Source (expected) | Graph |
| -------- | ----------------- | ----- |
| OSM features (admitted, parseable) | 3830408 | 3830408 |
| kind `building` | 2484449 | 2484449 |
| kind `furniture` | 65740 | 65740 |
| kind `landuse` | 49378 | 49378 |
| kind `other` | 100936 | 100936 |
| kind `poi` | 263523 | 263523 |
| kind `road` | 836785 | 836785 |
| kind `vegetation` | 26127 | 26127 |
| kind `water` | 3470 | 3470 |

Placement split (graph): {'False': 2595055, 'True': 1235353}. Source-side skips: 0 features with empty/unparseable geometry after the ogr2ogr clip; 0 duplicate stable ids.

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
| points | 520560 | 520560 |
| lines | 713076 | 643074 |
| multipolygons | 2666774 | 2666774 |
| multilinestrings | 4141 | — |
| other_relations | 7823 | — |
