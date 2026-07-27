# OSM ingestion census — helsinki_citygml2_lod2_2019.gml

*Run 20260716_165805 · source `input\osm\finland-260704.osm.pbf` · CRS EPSG:3879 · buffer 10.0 m · gate **PASSED***

Completeness + placement gate for the OSM enrichment (`eval/osm_ingestion_census.py`): every OSM feature admitted from the source `.osm.pbf` must be stored losslessly as an `OsmFeature` node and placed either on a CityGML anchor (`ENRICHED_BY`/`HAS_POI`) or as a spatially indexed standalone node with an `unmatched_reason`.

## Source vs. graph

| Quantity | Source (expected) | Graph |
| -------- | ----------------- | ----- |
| OSM features (admitted, parseable) | 55930 | 55930 |
| kind `building` | 3157 | 3157 |
| kind `furniture` | 10533 | 10533 |
| kind `landuse` | 1958 | 1958 |
| kind `other` | 13365 | 13365 |
| kind `poi` | 4942 | 4942 |
| kind `road` | 20666 | 20666 |
| kind `vegetation` | 1264 | 1264 |
| kind `water` | 45 | 45 |

Placement split (graph): {'True': 4281, 'False': 51649}. Source-side skips: 0 features with empty/unparseable geometry after the ogr2ogr clip; 0 duplicate stable ids.

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
| points | 32406 | 32406 |
| lines | 20961 | 15180 |
| multipolygons | 8344 | 8344 |
| multilinestrings | 235 | — |
| other_relations | 381 | — |
