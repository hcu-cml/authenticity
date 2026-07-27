# OSM × CityGML conflict analysis — zurich

Dataset `zurich`. All figures computed by Cypher queries over the fused graph.

## 1. Footprint correspondence (geometric / topological)

- CityGML (pykci) buildings: **102,668**
- OSM buildings: **460,631**
- CityGML buildings enriched (≥1 OSM match): **93,958** (91.5 %)
- OSM buildings matched: **89,207** (19.4 %)

| Case | Components | CityGML bldgs | OSM bldgs | edges |
|------|-----------:|--------------:|----------:|------:|
| 1:1 | 75,541 | 75,430 | 75,430 | 75,430 |
| 1:n | 4,858 | 12,442 | 4,853 | 12,442 |
| n:1 | 2,003 | 1,999 | 4,325 | 4,325 |
| n:m | 787 | 3,812 | 3,744 | 5,621 |

## 2. Roof-material attribute duplication / conflict

- CityGML buildings with ML-predicted roof material: **0**
- OSM buildings carrying `roof:material`: **8,153**
- **Dual-sourced** buildings (ML prediction AND matched OSM `roof:material`): **0**

Raw OSM `roof:material` values on dual-sourced buildings:

_(none)_

## 2b. Height duplication / conflict (surveyed vs OSM)

- Dual-sourced (numeric `osm_height` AND surveyed `measured_height`): **770**
  - median |Δh| = **2.3 m**, mean 3.94 m
  - within 2 m: 357 (46.4 %) · off by >5 m: 174 (22.6 %)

- OSM roof material on buildings WITHOUT an ML prediction (net-new coverage): **822**

## 3. Other OSM contributions

- OSM features by kind: `{'vegetation': 13480, 'building': 460631, 'furniture': 424171, 'water': 4762, 'other': 253342, 'landuse': 43710, 'road': 502180, 'poi': 158125}`
- POIs attached to a containing building: **13,587**
- Net-new OSM orphans (no cadastral counterpart): **1,757,607** `{'no_pykci_type': 1241645, 'no_overlap': 372279, 'no_containing_building': 143683}`
