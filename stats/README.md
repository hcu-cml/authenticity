# Per-city content metrics

`<city>_content_metrics.json`, one per city: a machine-readable profile of the released graph, measured against the live graph at release time. These are the numbers behind the per-city tables in the paper and in [../docs/](../docs/), so a claim can be checked without restoring 27 GiB.

Each file records:

| Key | Content |
| --- | --- |
| `city`, `generated` | which graph, and when it was profiled |
| `total_nodes`, `total_rels` | graph size |
| `node_property_records`, `rel_property_records` | property counts, the basis of the 1.18 B figure for the corpus |
| `label_counts`, `rel_type_counts` | full label and relationship-type inventory with counts |
| `boundary_surface_split` | wall, roof, ground, and closure surface counts |
| `building_key_histogram` | every property key present on `Building`, with how many buildings carry it |
| `building_keys_by_class` | the same keys partitioned into `structural`, `thematic`, `osm`, `ml`, and `lod3`, which is the provenance partition made countable |
| `building_property_records_by_class` | property records per provenance class |
| `thematic_attrs_per_building` | distribution (min, median, max) of source thematic attributes per building |
| `nodes_per_building`, `polygons_per_building` | geometry-density distributions |
| `height_stats` | measured-height distribution, sentinels excluded |
| coverage blocks | OSM enrichment, roof-material prediction, and LoD3 coverage |

The `building_keys_by_class` partition is the most useful entry point for anyone building features for the representation-learning tasks: it says exactly which keys are authoritative, which are mirrored from OpenStreetMap, and which are model output, for that city.

Note that `uri` records the local Bolt address the profile was taken from. It is provenance about the measurement, not something to connect to.
