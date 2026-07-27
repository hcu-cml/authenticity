# Licenses, attribution, and redistribution

AuthentiCity is a derived database built from six upstream data sources with different terms. This file states exactly what applies to what, and what a downstream user must do.

---

## 1. The released graph dumps: ODbL 1.0

**Every one of the five city dumps is released under the [Open Data Commons Open Database License v1.0 (ODbL-1.0)](https://opendatacommons.org/licenses/odbl/1-0/).**

Reason: each dump contains substantial OpenStreetMap-derived content (9,490,346 `OsmFeature` nodes with their tags and geometry across the corpus). OpenStreetMap is ODbL-1.0, whose share-alike provision extends to a *derived database*. A permissive license on the fused graphs would conflict with the OSM terms, so ODbL is not a preference here but a consequence.

What this means in practice for a user of the dumps:

- **Attribute.** Credit both OpenStreetMap and the city's authoritative provider (strings in §2).
- **Share alike.** If you publicly use an adapted version of a dump, offer that adapted database under ODbL as well.
- **Keep it open.** Do not use technical measures that restrict others from using the database.
- Results, models, and analyses computed *from* the database (a "Produced Work" in ODbL terms) are not themselves forced under ODbL; only the database and adaptations of it are. Produced works still require attribution.

Each authoritative source layer additionally remains under its own license (§2). ODbL on the compilation does not relicense the upstream data, and it does not remove any upstream obligation.

---

## 2. Source data and required attribution

| City | Provider and product | Vintage | License | Portal |
| --- | --- | --- | --- | --- |
| Hamburg, DE | Landesbetrieb Geoinformation und Vermessung (LGV) Hamburg, 3D-Stadtmodell LoD2 | 2025 | [dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0) | <https://www.geoportal-hamburg.de/> |
| Helsinki, FI | Helsinki Region Infoshare, Helsinki 3D city model (CityGML LoD2) | 2019 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | <https://hri.fi/data/en_GB/dataset/helsingin-3d-kaupunkimalli> |
| Zurich, CH | swisstopo, swissBUILDINGS3D 3.0 (LoD2.3) | 2019 | [swisstopo open government data terms](https://www.swisstopo.admin.ch/en/terms-of-use-free-geodata-and-geoservices) | <https://www.swisstopo.admin.ch/en/landscape-model-swissbuildings3d-3-0> |
| New York, US | NYC Office of Technology and Innovation, 3D Building Model | 2016 | [NYC OpenData terms of use](https://www.nyc.gov/home/terms-of-use.page) | <https://www.nyc.gov/content/planning/pages/resources/datasets/3-d-building> |
| Tokyo, JP | MLIT Project PLATEAU, 3D city model (2025 release, v5), 23 special wards | 2025 | [PLATEAU Public Data License 1.0](https://www.mlit.go.jp/plateau/site-policy/) | <https://www.mlit.go.jp/plateau/> |
| All cities | OpenStreetMap (Geofabrik regional extracts, 2026-06-29 / 2026-07-03 / 2026-07-04) | 2026 | [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) | <https://www.openstreetmap.org/copyright> |

All five authoritative sources permit redistribution with attribution, which is what this release does.

### Attribution strings

Use the line for the city you are working with, together with the OSM line.

```text
Hamburg    Contains data from Landesbetrieb Geoinformation und Vermessung (LGV)
           Hamburg, 3D-Stadtmodell LoD2 (2025), licensed under dl-de/by-2-0.
Helsinki   Contains data from Helsinki Region Infoshare, Helsinki 3D city model
           (2019), licensed under CC BY 4.0.
Zurich     Contains data from swisstopo, swissBUILDINGS3D 3.0, used under the
           swisstopo terms for free geodata and geoservices.
New York   Contains data from the New York City Office of Technology and
           Innovation, 3D Building Model (2016), via NYC OpenData.
Tokyo      Contains data from MLIT Project PLATEAU, 3D city model (2025), used
           under the PLATEAU Public Data License 1.0.

All cities (c) OpenStreetMap contributors, available under the Open Database
           License (ODbL 1.0). See https://www.openstreetmap.org/copyright
Dataset    AuthentiCity v1.0.0, DOI 10.5281/zenodo.21547211, released under
           ODbL 1.0 (graph dumps).
```

### Derived layers we produced

| Layer | Cities | Terms |
| --- | --- | --- |
| ML-predicted roof materials | Hamburg | Our own model output; released as part of the graph under ODbL 1.0, and citable via the model reference given in the paper. |
| Reconstructed LoD3 facades | Hamburg | Our own reconstruction from our own facade imagery; released as part of the graph under ODbL 1.0. The source imagery is **not** released. |
| Cross-source correspondence edges (`ENRICHED_BY`, `HAS_POI`) and all `osm_*` scalars | all | Our own computation over OSM and authoritative footprints; part of the database, so ODbL 1.0. |

---

## 3. This repository

| Content | License | File |
| --- | --- | --- |
| Question suite (questions, gold Cypher, materialized gold answers, splits), verification reports, cached baseline outputs, documentation, datasheet | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | [LICENSE](LICENSE) |
| Code: harness, loaders, export and verification tools, Docker configuration | [MIT](https://opensource.org/licenses/MIT) | [LICENSE-CODE](LICENSE-CODE) |
| Construction pipeline (separate repository, pykci) | MIT | <https://github.com/hcu-cml/pykci> |

The per-city schema text under [schema/](schema/) describes the graph structure and is CC BY 4.0. Note that the question files quote *values* read from the released graphs (district ids, street names, materials, thresholds, and materialized answer rows). Those quoted values are database content, so if you redistribute the question suite as a substantial extract of the graphs, treat that extract as ODbL content and attribute accordingly. Redistributing the suite as a benchmark, with attribution, is exactly the intended use.

---

## 4. Redistribution checklist

If you republish a dump, a derived graph, or a substantial extract:

1. Keep or reproduce this file and the attribution strings in §2.
2. State which AuthentiCity version and DOI you started from.
3. Release your adapted database under ODbL 1.0.
4. If you removed the OSM layer entirely and can show that no OSM-derived content remains (no `OsmFeature` nodes, no `osm_*` scalars, no `ENRICHED_BY` or `HAS_POI` edges), then only the authoritative source's own license applies to what is left; the burden of demonstrating that is yours.
5. Do not add restrictions on downstream use, and do not remove provenance properties: they are what makes the licensing auditable.
