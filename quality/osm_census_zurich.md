# OSM ingestion census — zurich

*Run 20260716_180836 · source `input\osm\switzerland-260704.osm.pbf` · CRS EPSG:2056 · buffer 10.0 m · gate **PASSED***

Completeness + placement gate for the OSM enrichment (`eval/osm_ingestion_census.py`): every OSM feature admitted from the source `.osm.pbf` must be stored losslessly as an `OsmFeature` node and placed either on a CityGML anchor (`ENRICHED_BY`/`HAS_POI`) or as a spatially indexed standalone node with an `unmatched_reason`.

## Source vs. graph

| Quantity | Source (expected) | Graph |
| -------- | ----------------- | ----- |
| OSM features (admitted, parseable) | 1860401 | 1860401 |
| kind `building` | 460631 | 460631 |
| kind `furniture` | 424171 | 424171 |
| kind `landuse` | 43710 | 43710 |
| kind `other` | 253342 | 253342 |
| kind `poi` | 158125 | 158125 |
| kind `road` | 502180 | 502180 |
| kind `vegetation` | 13480 | 13480 |
| kind `water` | 4762 | 4762 |

Placement split (graph): {'False': 1757607, 'True': 102794}. Source-side skips: 0 features with empty/unparseable geometry after the ogr2ogr clip; 0 duplicate stable ids.

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
| points | 813108 | 813108 |
| lines | 524034 | 455516 |
| multipolygons | 591777 | 591777 |
| multilinestrings | 5196 | — |
| other_relations | 6911 | — |
