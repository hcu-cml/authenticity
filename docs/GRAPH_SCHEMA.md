# Graph schema reference

Read this before writing Cypher. The exact schema text per city, as given to the baseline models, is in [../schema/](../schema/); this document explains it.

The graph is a Neo4j labeled property graph. Three things distinguish it from a naive CityGML-to-graph mapping, and all three matter when querying:

1. **Coordinates are stored verbatim** as the source wrote them, never rounded or re-encoded. That is what makes the lossless round-trip possible, and it means coordinate strings are strings, while queryable numeric geometry lives in derived properties (`center_x`, `center_y`, `bbox_*`, `location`).
2. **Provenance is structural, not a comment.** Every node and edge has a `source`; derived scalars live in namespaces (`osm_*`, `predicted_*`, `lod3_*`); cross-source correspondence is an edge with confidence properties, not a merged value.
3. **Spatial queries go through Neo4j Spatial R-tree layers**, which store Cartesian coordinates in each city's metric CRS. There is one layer per source: `features` (CityGML objects), `osm_features` (OSM), and `lod3_features` (Hamburg's reconstructed layer).

---

## Node labels

### Semantic city objects

| Label | Meaning | Availability |
| --- | --- | --- |
| `Building` | one authoritative building | all cities |
| `BuildingPart` | a recursive `bldg:BuildingPart`, reached by `HAS_BUILDING_PART`; deliberately **not** labeled `Building`, so it stays out of building counts and the R-tree | Zurich only (12.0 k) |
| `CityObject` | umbrella label on every non-building module, alongside its module label | Helsinki (bridges), Tokyo |
| `Bridge`, `Road`, `WaterBody`, `CityFurniture`, `SolitaryVegetationObject`, `PlantCover`, `CityObjectGroup`, `LandUse`, `Tunnel` | module labels | per city; Tokyo has the widest set |
| `Room`, `BuildingInstallation`, `BuildingFurniture`, `Opening`, `NestedFeature` | interior and LoD3/LoD4 structure | Hamburg (openings), Tokyo (1 room) |
| `BuildingFunction`, `RoofType` | classifier hub nodes shared by many buildings | Hamburg (138 hubs), Helsinki (39); **absent in Zurich, New York, Tokyo** |
| `District`, `City`, `Dataset` | containers; `Dataset` holds the CRS, source CRS, and bounding box | all cities |

### Geometry

| Label | Meaning |
| --- | --- |
| `GeometrySolid` | `gml:Solid` behind a `lodNSolid` |
| `GeometryMultiSurface`, `GeometryCompositeSurface` | surface collections; a composite that is an xlink target becomes its own node |
| `BoundarySurface` | semantic surface (`RoofSurface`, `WallSurface`, `GroundSurface`, `ClosureSurface`, ...), distinguished by its `surface_type` |
| `GeometryPolygon` | one polygon |
| `GeometryRing` | exterior or interior ring; **holds `pos_list`, the verbatim coordinate string** |
| `GeometryLineString` | `lodN` MultiCurve geometry |
| `TerrainIntersection` | terrain intersection curves (Hamburg) |

### Fusion and index

| Label | Meaning |
| --- | --- |
| `OsmFeature` | one OpenStreetMap object, plus a dynamic sub-label (`OsmBuilding`, `OsmPOI`, `OsmRoad`, `OsmWater`, `OsmLandUse`, `OsmVegetation`, `OsmFurniture`); the canonical type key is `osm_kind` |
| `Lod3Facade` | marker on every node added by the LoD3 reconstruction, so the layer can be removed or trusted as a unit (Hamburg) |
| `Entity` | index plumbing only: carried by every node that can be the endpoint of an id-matched edge, backed by an `Entity(id)` index. **Ignore it in domain queries.** |
| `SpatialLayer`, R-tree nodes | Neo4j Spatial internals; excluded from any domain count |

---

## Relationship types

| Type | Pattern | Notes |
| --- | --- | --- |
| `HAS_BOUNDARY` | building or part to `BoundarySurface` | the authoritative semantic surface link |
| `HAS_LOD_SOLID`, `HAS_LOD_SURFACE`, `HAS_LOD_GEOMETRY`, `HAS_LOD_MULTICURVE` | feature to geometry, per level of detail | a feature carrying one solid per LoD keeps all of them |
| `HAS_POLYGON`, `HAS_SURFACE_MEMBER` | surface collections to polygons | an `xlink:href` member is a real edge carrying `via_xlink=true`, and `orientation` for an oriented surface |
| `HAS_EXTERIOR_RING`, `HAS_INTERIOR_RING` | polygon to ring | interior rings are the window and door openings |
| `HAS_FOOTPRINT`, `HAS_LINE`, `HAS_TERRAIN_INTERSECTION` | derived or auxiliary geometry | |
| `HAS_BUILDING_PART` | building to `BuildingPart`, ordered | Zurich |
| `HAS_FUNCTION`, `HAS_ROOF_TYPE` | building to classifier hub | Hamburg, Helsinki only |
| `HAS_INTERIOR_ROOM`, `HAS_ROOM_INSTALLATION`, `HAS_OUTER_INSTALLATION`, `HAS_INTERIOR_INSTALLATION`, `HAS_INTERIOR_FURNITURE`, `HAS_OPENING`, `HAS_NESTED` | interior and installation structure | |
| `HAS_GROUP_MEMBER` | `CityObjectGroup` membership, with `role` and `order` | |
| `PART_OF`, `LOCATED_IN`, `COVERS` | containment and topology: feature to dataset, building to district, district to city | |
| **`ENRICHED_BY`** | `(Building｜CityObject)` to `OsmFeature` | the cross-source correspondence edge; see below |
| **`HAS_POI`** | `Building` to a point `OsmFeature` | with `distance_m`; point-in-footprint containment |
| **`HAS_LOD3_FACADE`** | `Building` to reconstructed `BoundarySurface` | with `confidence`, `method`, `method_version`, `lod`, `source_type='reconstructed'` (Hamburg) |
| `HAS_OSM_MEMBER` | OSM relation to its members, with `role` and `order` | |
| `RTREE_*` | Neo4j Spatial internals | never traverse these in a domain query |

---

## Properties you will use most

### On `Building`

| Property | Meaning |
| --- | --- |
| `id` | node identity; equals the source `gml:id` unless it was split, in which case `source_gml_id` holds the original and `id_synthesized=true` |
| `source` | the source file or layer tag; the primary provenance handle |
| `measured_height`, `measured_height_uom` | authoritative height. **Guard with `> -999`**: Tokyo stores a `-9999` sentinel |
| `storeys_above_ground`, `storeys_below_ground` | authoritative storey counts; Tokyo uses a `9999` sentinel |
| `function_code`, `usage_code`, `class_code` (with their `_codespace`) | source classification codes |
| `roof_type_code` | source roof type where present |
| `center_x`, `center_y`, `location` | centroid; `location` is a point in the city's metric CRS and is what `point.distance` should use |
| `bbox_min_x`, `bbox_max_x`, `bbox_min_y`, `bbox_max_y`, `bbox_min_z`, `bbox_max_z`, `bbox_wkt` | bounding box; `bbox_wkt` is the R-tree geometry |
| `ground_z` | ground elevation |
| `address_xml` | the `bldg:address` xAL subtree, verbatim, as a JSON list |
| `_gen_attrs_map` | bookkeeping that lets export re-emit each generic attribute with its original name, type, and unit |
| source thematic keys | per city, from 5 (New York) to 49 (Helsinki) distinct keys, including non-Latin keys on Tokyo, queryable verbatim |

### Crowd-sourced, on an enriched authoritative node (`osm_` namespace)

`osm_name`, `osm_building`, `osm_amenity`, `osm_height`, `osm_building_levels`, `osm_roof_shape`, `osm_roof_material`, `osm_operator`, `osm_start_date`, `addr_street`, `addr_housenumber`, `addr_postcode`, `addr_city`, plus match metadata `osm_match_type` (`1:1`, `1:n`, `n:1`, `n:m`), `osm_match_count`, `osm_shared`, `osm_best_jaccard`.

These are copied from the **primary** match only. Values from secondary matches stay on their `OsmFeature` node, reachable through the non-primary `ENRICHED_BY` edges. An authoritative property is never overwritten: `measured_height` and `osm_height` coexist.

### On `OsmFeature`

`osm_id`, `osm_kind`, `osm_version`, `osm_timestamp`, promoted tags as above, `other_tags` (a JSON object with the complete remaining tag long tail, so nothing is lost), geometry properties in the dataset CRS, `matched` (boolean), `unmatched_reason` (`no_overlap`, `no_pykci_type`, `no_containing_building`; null when matched), and `source` (`osm:<filename>`).

### ML-predicted, on `Building` (Hamburg)

`predicted_roof_material_<i>` and `predicted_roof_material_<i>_coverage` for `i = 0 .. count-1`, ranked by coverage descending, plus `predicted_roof_material_count`, `predicted_roof_material_source` (the provenance tag), and `predictedroofmaterial`, a convenience key equal to the primary (highest-coverage) material.

### On `ENRICHED_BY`

| Property | Meaning |
| --- | --- |
| `overlap_ratio` | intersection area over the smaller footprint |
| `jaccard` | intersection over union; the confidence signal used as a message-passing weight in Benchmark B |
| `intersection_area` | absolute overlap in the city's CRS units |
| `match_type` | which correspondence case this edge belongs to: `1:1`, `1:n`, `n:1`, `n:m` |
| `is_primary` | true for the single largest-overlap match of that authoritative feature |

---

## Query rules that are easy to get wrong

**Filter to primary matches unless you mean otherwise.** `MATCH (b:Building)-[:ENRICHED_BY]->(o)` yields several rows for buildings in a 1:n or n:m case. Aggregating over edges overcounts such buildings (by 1.76 to 2.19 times on Tokyo). Either add `{is_primary: true}` or aggregate over the mirrored `osm_*` scalar on the building, which is already deduplicated.

**The R-tree layers are Cartesian metres.** `spatial.withinDistance(layer, point, d)` treats `d` as kilometres against a geographic layer, so on these layers it silently under-selects. Use a metre-sized window with `spatial.intersects` and then an exact `point.distance(...) <= r` recheck, or a plain top-k over `point.distance` for nearest-neighbor questions. Every proximity gold query in the benchmark uses one of those two idioms.

**One spatial procedure call per row does not scale.** A pattern of the shape `MATCH (b:Building) CALL spatial.withinDistance(...)` issues one call per building and does not finish at city scale, even where the driving set looks small. Bound the query to a window first, then compute exactly inside it.

**Guard the sentinels.** `measured_height > -999` rather than `IS NOT NULL` for any height aggregate or percentile. Maximum and "tallest" queries need no guard, since a negative floor is never the maximum, but storey maxima on Tokyo will return `9999`.

**Absence is not a negative.** `predictedroofmaterial IS NULL` means the layer does not cover that building, not that it has no roof material. Aggregates over partially covered attributes should report the covered subset and its size, which is exactly what the coverage-aware benchmark category tests.

**Ignore `Entity`, `SpatialLayer`, and `RTREE_*`.** They are index plumbing. `MATCH (n) RETURN count(n)` legitimately includes R-tree nodes (202.6 k across the corpus); domain counts should name a domain label.

**Rank deterministically.** Add a tie-break on `id` to any `ORDER BY ... LIMIT k`, otherwise the result is not reproducible. The benchmark's gold queries always do, and missing tie-breaks were the single most common baseline failure.

**`BuildingPart` is not a `Building`.** Zurich's 12.0 k parts are reached through `HAS_BUILDING_PART` and are excluded from building counts and from the R-tree on purpose.

---

## Sizes, for query planning

| | Hamburg | Helsinki | Zurich | New York | Tokyo |
| --- | --: | --: | --: | --: | --: |
| Nodes | 17.44 M | 414 k | 41.51 M | 45.80 M | 74.41 M |
| Relationships | 26.30 M | 620 k | 45.55 M | 54.21 M | 91.95 M |
| Geometry share of nodes | 90.8 % | 85.6 % | 95.2 % | 91.9 % | 91.1 % |
| Median nodes per building | 30 | 54 | 253 | 31 | 21 |
| Median geometry polygons per building | 8 | 20 | 124 | 10 | 9 |

Geometry dominates every graph, which is why a query that walks from buildings into rings without a bound is expensive: Zurich's median building alone has 124 polygons. Machine-readable per-city content metrics: [../stats/](../stats/).
