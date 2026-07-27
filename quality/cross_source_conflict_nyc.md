# OSM × CityGML conflict analysis — nyc

Dataset `nyc`. All figures computed by Cypher queries over the fused graph.

## 1. Footprint correspondence (geometric / topological)

- CityGML (pykci) buildings: **1,083,437**
- OSM buildings: **1,166,948**
- CityGML buildings enriched (≥1 OSM match): **1,070,177** (98.8 %)
- OSM buildings matched: **1,069,452** (91.6 %)

| Case | Components | CityGML bldgs | OSM bldgs | edges |
|------|-----------:|--------------:|----------:|------:|
| 1:1 | 1,053,850 | 1,053,727 | 1,053,727 | 1,053,727 |
| 1:n | 3,046 | 8,448 | 3,015 | 8,448 |
| n:1 | 3,199 | 3,178 | 6,149 | 6,149 |
| n:m | 850 | 4,277 | 4,351 | 5,099 |

## 2. Roof-material attribute duplication / conflict

- CityGML buildings with ML-predicted roof material: **0**
- OSM buildings carrying `roof:material`: **2,166**
- **Dual-sourced** buildings (ML prediction AND matched OSM `roof:material`): **0**

Raw OSM `roof:material` values on dual-sourced buildings:

_(none)_

- OSM roof material on buildings WITHOUT an ML prediction (net-new coverage): **2,074**

## 3. Other OSM contributions

- OSM features by kind: `{'water': 1471, 'other': 284892, 'landuse': 23488, 'building': 1166948, 'vegetation': 7312, 'road': 659851, 'poi': 201840, 'furniture': 209666}`
- POIs attached to a containing building: **52,449**
- Net-new OSM orphans (no cadastral counterpart): **1,433,567** `{'no_pykci_type': 1186680, 'no_overlap': 99706, 'no_containing_building': 147181}`
