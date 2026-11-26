# Licenses, attribution, and redistribution

AuthentiCity combines six upstream data sources with different terms. This file states exactly what applies to what, and what a downstream user must do.

---

## 1. The released graph dumps: CC BY 4.0, with the OpenStreetMap-derived content under ODbL 1.0

**The five city dumps are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), the license of the Zenodo record. The OpenStreetMap-derived content inside them is not relicensed: it remains under the [Open Data Commons Open Database License v1.0 (ODbL-1.0)](https://opendatacommons.org/licenses/odbl/1-0/). Each authoritative source layer remains under its provider's license (§2).**

| Part of a dump | Terms |
| --- | --- |
| OpenStreetMap-derived content: the `OsmFeature` nodes with their tags and geometry (9,490,346 across the corpus) and the relationships among them, every `osm_*` property on other nodes, and the correspondence edges `ENRICHED_BY` and `HAS_POI` | ODbL 1.0, (c) OpenStreetMap contributors |
| The authoritative source layer of each city | The provider's license (§2) |
| What we added: the graph structure and identifiers, the provenance properties, the ML-predicted roof materials, the reconstructed LoD3 facades, and the selection and arrangement of the whole | CC BY 4.0 |

CC BY 4.0 covers our own contribution. It does not relicense OpenStreetMap data or provider data, and it does not remove any upstream obligation.

**How the two licenses fit together.** In every dump the OpenStreetMap-derived content stays identifiable and separable: each OSM object is its own node, OSM values copied onto other nodes sit in the `osm_*` namespace, no authoritative value is overwritten, and no feature of either source is dropped because of the other. We therefore treat a dump as a collection of which the OpenStreetMap-derived content is one part. ODbL does not require such a collection to be under ODbL as a whole, and it continues to apply to the OpenStreetMap-derived part (ODbL 1.0, section 4.5 a).

What this means in practice for a user of the dumps:

- **Attribute.** Credit AuthentiCity, OpenStreetMap, and the city's authoritative provider (strings in §2).
- **Share alike, for the OpenStreetMap-derived content.** If you publicly use an adapted database that is based on this content, offer that adapted database under ODbL 1.0.
- **Keep it open.** Do not use technical measures that restrict others from using the OpenStreetMap-derived content.
- Results, models, and analyses computed *from* the database (a "Produced Work" in ODbL terms) are not themselves forced under ODbL. They still require attribution, including a notice that they contain information from OpenStreetMap, which is made available under ODbL 1.0.

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

Use the line for the city you are working with, together with the OSM line and the dataset line.

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
Dataset    AuthentiCity v1.0.0, DOI 10.5281/zenodo.21547211, CC BY 4.0;
           OpenStreetMap-derived content under ODbL 1.0.
```

### Derived layers we produced

| Layer | Cities | Terms |
| --- | --- | --- |
| ML-predicted roof materials | Hamburg | Our own model output, CC BY 4.0, citable via the model reference given in the paper. The classifier was trained using OpenStreetMap `roof:material` labels, so credit OpenStreetMap (ODbL 1.0) when you use this layer. |
| Reconstructed LoD3 facades | Hamburg | Our own reconstruction from our own facade imagery, CC BY 4.0. The source imagery is **not** released. |
| Cross-source correspondence edges (`ENRICHED_BY`, `HAS_POI`) and all `osm_*` scalars | all | Our own computation over OSM and authoritative footprints. They are derived from OpenStreetMap data, so they belong to the OpenStreetMap-derived content under ODbL 1.0. |

---

## 3. This repository

| Content | License | File |
| --- | --- | --- |
| Question suite (questions, gold Cypher, materialized gold answers, splits), verification reports, cached baseline outputs, documentation, datasheet | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | [LICENSE](LICENSE) |
| Code: harness, loaders, export and verification tools, Docker configuration | [MIT](https://opensource.org/licenses/MIT) | [LICENSE-CODE](LICENSE-CODE) |
| Construction pipeline (separate repository, pykci) | MIT | <https://github.com/hcu-cml/pykci> |

The per-city schema text under [schema/](schema/) describes the graph structure and is CC BY 4.0. Note that the question files quote *values* read from the released graphs (district ids, street names, materials, thresholds, and materialized answer rows). Those quoted values are database content. Where they come from the OpenStreetMap-derived content of a graph and a redistribution amounts to a substantial extract of it, treat that extract as ODbL content and attribute accordingly. Redistributing the suite as a benchmark, with attribution, is exactly the intended use.

---

## 4. Redistribution checklist

If you republish a dump, a derived graph, or a substantial extract:

1. Keep or reproduce this file and the attribution strings in §2.
2. State which AuthentiCity version and DOI you started from.
3. Keep the OpenStreetMap-derived content under ODbL 1.0. If your adapted database is based on that content, release it under ODbL 1.0; that always satisfies the OpenStreetMap terms.
4. If you removed the OSM layer entirely and can show that no OSM-derived content remains (no `OsmFeature` nodes, no `osm_*` scalars, no `ENRICHED_BY` or `HAS_POI` edges), then ODbL no longer applies to what is left: it is under CC BY 4.0 together with the authoritative source's own license (for Hamburg, keep the OpenStreetMap credit for the roof-material layer). The burden of demonstrating that is yours.
5. Do not add restrictions on downstream use of the OpenStreetMap-derived content, and do not remove provenance properties: they are what makes the licensing auditable.
