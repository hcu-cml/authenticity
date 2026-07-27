# OSM × CityGML conflict analysis — tokyo

Dataset `tokyo`. All figures computed by Cypher queries over the fused graph.

## 1. Footprint correspondence (geometric / topological)

- CityGML (pykci) buildings: **2,005,762**
- OSM buildings: **2,484,449**
- CityGML buildings enriched (≥1 OSM match): **1,181,049** (58.9 %)
- OSM buildings matched: **1,143,866** (46.0 %)

| Case | Components | CityGML bldgs | OSM bldgs | edges |
|------|-----------:|--------------:|----------:|------:|
| 1:1 | 823,560 | 821,655 | 821,655 | 821,655 |
| 1:n | 41,392 | 90,648 | 40,561 | 90,648 |
| n:1 | 22,288 | 22,273 | 46,975 | 46,975 |
| n:m | 71,562 | 224,653 | 224,226 | 389,725 |

## 2. Roof-material attribute duplication / conflict

- CityGML buildings with ML-predicted roof material: **0**
- OSM buildings carrying `roof:material`: **933**
- **Dual-sourced** buildings (ML prediction AND matched OSM `roof:material`): **0**

Raw OSM `roof:material` values on dual-sourced buildings:

_(none)_

## 2b. Height duplication / conflict (surveyed vs OSM)

- Dual-sourced (numeric `osm_height` AND surveyed `measured_height`): **61,373**
  - median |Δh| = **0.0 m**, mean 0.72 m
  - within 2 m: 57,938 (94.4 %) · off by >5 m: 1,533 (2.5 %)

## 2c. Storeys duplication / conflict (ALKIS vs OSM levels)

- Dual-sourced (`osm_building_levels` AND `storeys_above_ground`): **116,022**
  - exact agreement: 99,652 (85.9 %) · within ±1: 109,356 (94.3 %)

- OSM roof material on buildings WITHOUT an ML prediction (net-new coverage): **40**

## 3. Other OSM contributions

- OSM features by kind: `{'water': 3470, 'road': 836785, 'poi': 263523, 'vegetation': 26127, 'landuse': 49378, 'other': 100936, 'building': 2484449, 'furniture': 65740}`
- POIs attached to a containing building: **91,487**
- Net-new OSM orphans (no cadastral counterpart): **2,595,055** `{'no_pykci_type': 1082436, 'no_containing_building': 161587, 'no_overlap': 1351032}`
