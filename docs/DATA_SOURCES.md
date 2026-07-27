# Data sources

Exactly where each city's data came from, what was in it, and what the pipeline did to it. Licensing and attribution obligations are in [../DATA_LICENSES.md](../DATA_LICENSES.md).

---

## Authoritative layer

| | Hamburg | Helsinki | Zurich | New York | Tokyo |
| --- | --- | --- | --- | --- | --- |
| Provider | LGV Hamburg | Helsinki Region Infoshare | swisstopo | NYC Office of Technology and Innovation | MLIT Project PLATEAU |
| Product | 3D-Stadtmodell LoD2 | Helsinki 3D city model | swissBUILDINGS3D 3.0 | 3D Building Model | 3D city model, 23 special wards |
| Vintage | 2025 | 2019 | 2019 | 2016 | 2025 (v5) |
| CityGML version | 2.0 | 2.0 | 2.0 | 1.0 and 2.0 mixed | 2.0 |
| Level of detail | LoD2 | LoD2 | LoD2.3 | LoD1 to LoD2 | LoD1 to LoD3, predominantly LoD1 |
| Source CRS | EPSG:25832 | EPSG:3879 | EPSG:2056 | EPSG:2263 (US survey feet) | EPSG:6697 (degrees) |
| Graph CRS | EPSG:25832 | EPSG:3879 | EPSG:2056 | **EPSG:32618** | **EPSG:6677** |
| Source files | 1 | 1 | 78 tiles | 20 district-area tiles | 2,335 files |
| Extent (bbox, km²) | 7,117 | 14 | 3,137 | 2,159 | 1,045 |
| Source building features | 388,267 | 2,980 | 102,673 | 1,083,437 | 2,980,839 |
| Distinct `gml:id`s | 388,267 | 2,919 | 102,628 | 1,083,437 | 2,005,294 |
| Building nodes in graph | 388,267 | 2,980 | 102,668 | 1,083,437 | 2,005,762 |
| Distinct source thematic keys | 19 | 49 | 22 | 5 | 20 |
| Median height (m) | 7.53 | 10.11 | 9.22 | not available | 7.9 |

Portals, licenses, and required attribution strings: [../DATA_LICENSES.md](../DATA_LICENSES.md) §2. Per-key attribute inventories per city: [../stats/](../stats/).

### Per-city notes that matter when querying

**Hamburg.** LGV publishes the LoD2 model as map tiles. The single file ingested here was produced by importing those tiles into 3DCityDB and re-exporting one merged CityGML, so ingest sees one file whose bounding box is the union of the tiles. Identifiers are clean: no duplicates, no splits. This is the only city with derived layers.

**Helsinki.** The smallest and, by attribute count, the richest city in the corpus (49 distinct source thematic keys, including floor area, volume, construction year, native storey count, building material, lifecycle status, and the provider's own pre-existing record-linkage metadata). 61 duplicate-id groups in the source were split onto synthesized ids with `source_gml_id` preserved. Also carries 31 bridges. The export has upstream-corrupted Finnish diacritics, retained verbatim.

**Zurich.** Geometry and cadastre only: no building-function or roof-type classification, no storey counts, only roof-height bounds and a coarse category string. Highest geometric detail per building in the corpus (median 253 nodes and 124 geometry polygons per building, and the only city with `BuildingPart` nodes: 12.0 k). 78 tiles merged into one dataset. 45 duplicate-id occurrences resolved: 40 split, 5 deduplicated (no-geometry `ID_` placeholders, a source artifact).

**New York.** The most minimal source thematically: 5 distinct thematic keys, and **no `measuredHeight` at all**, plus no storeys, function, or roof type. This is what makes the OSM-only-height question category substantive here (97.5 % of buildings have an OSM height, 1,056,741 of 1,083,437, mean 8.3 m). Fourteen of the twenty tiles are CityGML 1.0 and were namespace-upgraded to 2.0 before ingest. Source coordinates are US survey feet and were reprojected to EPSG:32618 at ingest; without that, every distance, area, and height unit would be wrong.

**Tokyo.** Scoped to the PLATEAU B-core module set: `bldg`, `tran`, `brid`, `frn`, `veg`, `wtr`. Land use (`luse`, roughly 11.5 M parcels), terrain (`dem`, large TINs), underground (`uro`), and the PLATEAU ADE modules are excluded by design, being disproportionate in scale relative to their benchmark value. Non-building city objects: 605,293 roads, 38,231 city furniture, 10,883 vegetation objects, 2,895 water bodies, 968 bridges, 735 plant-cover areas, 1 city object group. Ward packages ship byte-identical replicas of bordering tiles, so 2,980,839 source building elements resolve to 2,005,762 distinct buildings: 975,077 exact replicas deduplicated by content hash and 468 distinct same-id features split. Source coordinates are geographic degrees, reprojected to EPSG:6677. `bldg:usage` is present but not `bldg:function` or `bldg:roofType`, so no function or roof-type hub nodes exist for Tokyo. Japanese attribute keys are preserved verbatim as queryable keys. Missing-value sentinels: `measuredHeight = -9999` on 36,071 buildings, `storeysAboveGround = 9999` on 225,776.

---

## Crowd-sourced layer: OpenStreetMap

Regional Geofabrik extracts, clipped with `ogr2ogr` to each dataset's bounding box plus a 10 m buffer and reprojected into the dataset CRS.

| City | Extract | Date | OSM features in graph |
| --- | --- | --- | --: |
| Hamburg | `hamburg-260629.osm.pbf` | 2026-06-29 | 1,188,139 |
| Helsinki | `finland-260704.osm.pbf` | 2026-07-04 | 55,930 |
| Zurich | `switzerland-260704.osm.pbf` | 2026-07-04 | 1,860,401 |
| New York | `new-york-260703.osm.pbf` | 2026-07-03 | 2,555,468 |
| Tokyo | `kanto-260703.osm.pbf` | 2026-07-03 | 3,830,408 |

Fusion outcome per city:

| | Hamburg | Helsinki | Zurich | New York | Tokyo | Corpus |
| --- | --: | --: | --: | --: | --: | --: |
| Matched to a city object | 356.7 k (30.0 %) | 4,281 (7.7 %) | 102.8 k (5.5 %) | 1.12 M (43.9 %) | 1.24 M (32.3 %) | 2.82 M (29.7 %) |
| Standalone, net-new | 831.4 k (70.0 %) | 51.6 k (92.3 %) | 1.76 M (94.5 %) | 1.43 M (56.1 %) | 2.60 M (67.7 %) | 6.67 M (70.3 %) |
| Buildings enriched | 331.3 k (85.3 %) | 2,476 (83.1 %) | 94.0 k (91.5 %) | 1.07 M (98.8 %) | 1.18 M (58.9 %) | 2.68 M (74.8 %) |
| `ENRICHED_BY` edges | 373,211 | 3,011 | 100,312 | 1,078,893 | 1,390,723 | 2,946,150 |
| `HAS_POI` edges | 22,219 | 1,797 | 13,587 | 52,449 | 91,487 | 181,539 |
| `osm_*` property records copied | 2.26 M | 15.4 k | 601.5 k | 6.98 M | 5.12 M | 14.97 M |

Standalone features are kept, not discarded: they are net-new knowledge outside the cadastral layer, each with an explicit `unmatched_reason` (`no_pykci_type` for kinds with no CityGML counterpart such as roads and land use, `no_containing_building` for points outside any footprint, `no_overlap` for polygons overlapping no authoritative footprint). The high standalone share on Zurich and Helsinki reflects release extent: their authoritative models cover a smaller area than the national OSM extract clipped to the same bounding box.

---

## Derived layers (Hamburg only)

| Layer | What it is | Coverage | How it is attached |
| --- | --- | --- | --- |
| ML-predicted roof material | Our own imagery-based classifier over aerial orthophotos; five classes (roof tiles, tar paper, concrete, metal, glass) | 194,799 of 388,267 buildings (50.2 %); 570 buildings carry more than one material | coverage-ranked properties `predicted_roof_material_<i>` and `_coverage` on the authoritative building node, matched by `gml:id` only, never spatially |
| Reconstructed LoD3 facades | Our own facade reconstruction from our own imagery | 17 buildings, 303 anchor edges, 3,404 facade surfaces | `HAS_LOD3_FACADE` edges carrying `confidence`, `method`, `method_version`, `lod`, separate from authoritative `HAS_BOUNDARY` |

Primary-material distribution over the covered Hamburg buildings: roof tiles 108,653, tar paper 51,325, concrete 22,905, metal 8,666, glass 3,250.

The classifier was trained using OpenStreetMap `roof:material` labels. That circularity is stated wherever the layer is used; see [../LIMITATIONS.md](../LIMITATIONS.md). The source aerial and facade imagery is not part of this release.

---

## What is not in the dataset

- No terrain or land-use layer for Tokyo, no PLATEAU ADE modules.
- No appearance or texture module for any city: the round-trip census excludes it by design, and the graphs carry geometry and semantics, not materials or textures.
- No street-level imagery, no point clouds, no sensor or IoT streams.
- No registry, census, energy, or transit layers. These are the obvious next sources, and adding any of them would flip some currently infeasible benchmark questions to feasible, which is why guard queries are re-run on every release.
- No materialized building-to-building proximity edges, by decision. See [../LIMITATIONS.md](../LIMITATIONS.md).
