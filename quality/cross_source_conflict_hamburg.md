# OSM × CityGML conflict analysis — hamburg

Dataset `hamburg_citygml2_lod2_2025.gml`. All figures computed by Cypher queries over the fused graph.

## 1. Footprint correspondence (geometric / topological)

- CityGML (pykci) buildings: **388,267**
- OSM buildings: **354,162**
- CityGML buildings enriched (≥1 OSM match): **331,318** (85.3 %)
- OSM buildings matched: **334,488** (94.4 %)

| Case | Components | CityGML bldgs | OSM bldgs | edges |
|------|-----------:|--------------:|----------:|------:|
| 1:1 | 256,219 | 255,984 | 255,984 | 255,984 |
| 1:n | 19,167 | 47,936 | 19,096 | 47,936 |
| n:1 | 16,146 | 16,142 | 47,838 | 47,838 |
| n:m | 2,363 | 9,537 | 9,151 | 12,926 |

## 2. Roof-material attribute duplication / conflict

- CityGML buildings with ML-predicted roof material: **194,799**
- OSM buildings carrying `roof:material`: **11,890**
- **Dual-sourced** buildings (ML prediction AND matched OSM `roof:material`): **3,641**
  - agree (OSM vocab folded to the 5 ML classes): **2,637**
  - disagree: **870**
  - OSM value with no ML class: 134
  - agreement over mappable pairs: **75.2 %**

Raw OSM `roof:material` values on dual-sourced buildings:

| value | count |
|-------|------:|
| roof_tiles | 2,155 |
| tar_paper | 1,074 |
| gravel | 98 |
| concrete | 63 |
| slate | 44 |
| grass | 43 |
| metal | 43 |
| copper | 31 |
| thatch | 29 |
| glass | 24 |
| eternit | 17 |
| metal_sheet | 7 |
| steel | 7 |
| zinc | 4 |
| paving_stones | 1 |
| asphalt | 1 |

Confusion (rows = ML prediction, cols = OSM normalized):

| ML \ OSM | concrete | glass | metal | roof_tiles | tar_paper |
|---|---|---|---|---|---|
| concrete | 24 | 4 | 13 | 106 | 247 |
| glass | 0 | 6 | 7 | 20 | 14 |
| metal | 4 | 2 | 15 | 57 | 49 |
| roof_tiles | 7 | 1 | 23 | 1844 | 115 |
| tar_paper | 28 | 11 | 34 | 128 | 748 |

## 2b. Height duplication / conflict (surveyed vs OSM)

- Dual-sourced (numeric `osm_height` AND surveyed `measured_height`): **3,404**
  - median |Δh| = **0.27 m**, mean 1.72 m
  - within 2 m: 2,894 (85.0 %) · off by >5 m: 219 (6.4 %)

## 2c. Storeys duplication / conflict (ALKIS vs OSM levels)

- Dual-sourced (`osm_building_levels` AND `storeys_above_ground`): **144,364**
  - exact agreement: 125,930 (87.2 %) · within ±1: 142,401 (98.6 %)

- OSM roof material on buildings WITHOUT an ML prediction (net-new coverage): **5,059**

## 3. Other OSM contributions

- OSM features by kind: `{'water': 2939, 'vegetation': 7753, 'other': 140660, 'building': 354162, 'landuse': 20810, 'road': 281056, 'poi': 81353, 'furniture': 299406}`
- POIs attached to a containing building: **22,219**
- Net-new OSM orphans (no cadastral counterpart): **831,432** `{'no_pykci_type': 752624, 'no_overlap': 22093, 'no_containing_building': 56715}`
