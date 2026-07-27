# OSM × CityGML conflict analysis — helsinki

Dataset `helsinki_citygml2_lod2_2019.gml`. All figures computed by Cypher queries over the fused graph.

## 1. Footprint correspondence (geometric / topological)

- CityGML (pykci) buildings: **2,980**
- OSM buildings: **3,157**
- CityGML buildings enriched (≥1 OSM match): **2,476** (83.1 %)
- OSM buildings matched: **2,484** (78.7 %)

| Case | Components | CityGML bldgs | OSM bldgs | edges |
|------|-----------:|--------------:|----------:|------:|
| 1:1 | 1,692 | 1,686 | 1,686 | 1,686 |
| 1:n | 127 | 285 | 125 | 285 |
| n:1 | 129 | 127 | 281 | 281 |
| n:m | 62 | 318 | 302 | 460 |

## 2. Roof-material attribute duplication / conflict

- CityGML buildings with ML-predicted roof material: **0**
- OSM buildings carrying `roof:material`: **84**
- **Dual-sourced** buildings (ML prediction AND matched OSM `roof:material`): **0**

Raw OSM `roof:material` values on dual-sourced buildings:

_(none)_

## 2b. Height duplication / conflict (surveyed vs OSM)

- Dual-sourced (numeric `osm_height` AND surveyed `measured_height`): **76**
  - median |Δh| = **0.57 m**, mean 4.59 m
  - within 2 m: 47 (61.8 %) · off by >5 m: 22 (28.9 %)

## 2c. Storeys duplication / conflict (ALKIS vs OSM levels)

- Dual-sourced (`osm_building_levels` AND `storeys_above_ground`): **48**
  - exact agreement: 34 (70.8 %) · within ±1: 44 (91.7 %)

- OSM roof material on buildings WITHOUT an ML prediction (net-new coverage): **73**

## 3. Other OSM contributions

- OSM features by kind: `{'building': 3157, 'other': 13365, 'vegetation': 1264, 'water': 45, 'furniture': 10533, 'road': 20666, 'landuse': 1958, 'poi': 4942}`
- POIs attached to a containing building: **1,797**
- Net-new OSM orphans (no cadastral counterpart): **51,649** `{'no_overlap': 763, 'no_pykci_type': 47831, 'no_containing_building': 3055}`
