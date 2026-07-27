# Duplicate / non-unique `gml:id` buildings — traceability record

This document lists every source building affected by a non-unique `gml:id` in the Helsinki, Zürich and Tokyo CityGML datasets, with enough provenance (source file, line range, CRS, bounding box, centroid, footprint) for the data provider to locate and, if desired, correct each one. The graph loader never edits the source; it resolves each collision at ingest and records the outcome (see the *disposition* / *resulting node id* columns). Coordinates are in each dataset's native CRS.

## Helsinki

- CRS: `EPSG:3879` · files scanned: 1 · building elements: 2,980 · distinct gml:ids: 2,919
- **Duplicate-id groups: 61 (122 buildings involved).**

### `BID_0338b8c4-838e-4453-a6a5-231e6f6b0bdb` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 31179–31822 | [25497886.841, 6675507.367, 25497918.787, 6675521.029] | [25497902.814, 6675514.198] | 1224 | kept (first occurrence) | `BID_0338b8c4-838e-4453-a6a5-231e6f6b0bdb` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 58951–61965 | [25497886.841, 6675507.367, 25497918.787, 6675521.029] | [25497902.814, 6675514.198] | 1371 | split (distinct content, synthesized id) | `BID_0338b8c4-838e-4453-a6a5-231e6f6b0bdb__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54979177849E7 6675510.3237 16.94 2.54979167128E7 6675510.269 16.94 2.54979137817E7 6675509.3215 16.94 2.54979134161E7 6675510.453 16.94 2.54979123517E7 6675510.109199999 16.94 2.54979120187E7 6675510.0926 16.94 2.54979120324E7 6675509.8316 16.94 2.54979110303E7 6675509.7808 16.94 2.54979080992E7 6675508.8334 16.94 2.54979077336E7 6675509.9648 16.94 2.54979066692E7 6675509.6201 16.94 2.5497906336 …`

### `BID_04b55dd6-c136-49a6-b142-723c0eb5ee89` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 85879–86034 | [25499054.17, 6674555.691, 25499071.122, 6674607.256] | [25499062.646, 6674581.474] | 90 | kept (first occurrence) | `BID_04b55dd6-c136-49a6-b142-723c0eb5ee89` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 91380–91739 | [25499054.17, 6674555.691, 25499071.122, 6674607.256] | [25499062.646, 6674581.474] | 90 | split (distinct content, synthesized id) | `BID_04b55dd6-c136-49a6-b142-723c0eb5ee89__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54990541699E7 6674605.9733 3.1805 2.54990659855E7 6674607.2558 3.1805 2.54990711217E7 6674559.9382 3.1805 2.54990596279E7 6674555.691 3.1805 2.54990541699E7 6674605.9733 3.1805`

### `BID_0514e7b4-0e87-43ef-b651-eee63840f97f` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 56724–56933 | [25498767.731, 6674390.712, 25498816.87, 6674420.03] | [25498792.3, 6674405.371] | 216 | kept (first occurrence) | `BID_0514e7b4-0e87-43ef-b651-eee63840f97f` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 79466–80083 | [25498767.731, 6674390.712, 25498816.87, 6674420.03] | [25498792.3, 6674405.371] | 216 | split (distinct content, synthesized id) | `BID_0514e7b4-0e87-43ef-b651-eee63840f97f__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54987824392E7 6674405.7392 0.756 2.54987790676E7 6674390.7115 0.756 2.5498767730699997E7 6674393.2551 0.756 2.54987710962E7 6674408.2551 0.756 2.5498769032E7 6674408.7204 0.756 2.54987698941E7 6674412.5337 0.756 2.54987719398E7 6674412.0775 0.756 2.54987736635E7 6674420.03 0.756 2.54988168695E7 6674410.2615 0.756 2.54988142289E7 6674398.582099999 0.756 2.54987824392E7 6674405.7392 0.756`

### `BID_099c2f64-8d58-4823-bfa9-b8a7630c04a6` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 17136–17293 | [25497718.737, 6674376.464, 25497766.218, 6674421.958] | [25497742.477, 6674399.211] | 90 | kept (first occurrence) | `BID_099c2f64-8d58-4823-bfa9-b8a7630c04a6` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 20711–21298 | [25497718.737, 6674376.464, 25497766.218, 6674421.958] | [25497742.477, 6674399.211] | 288 | split (distinct content, synthesized id) | `BID_099c2f64-8d58-4823-bfa9-b8a7630c04a6__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54977611279E7 6674405.8896 -0.117 2.54977335831E7 6674380.6364 -0.117 2.5497729032E7 6674376.464 -0.117 2.54977258982E7 6674379.8772 -0.117 2.54977217477E7 6674384.3978 -0.117 2.5497718736999996E7 6674387.677 -0.117 2.54977187971E7 6674387.7321 -0.117 2.54977234896E7 6674392.035 -0.117 2.5497751032E7 6674417.2909 -0.117 2.5497756122E7 6674421.9583 -0.117 2.54977590737E7 6674418.625 -0.117 2.5497 …`

### `BID_0d2d4f78-8d7e-43fd-aa44-ed3a5145c8ff` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 50086–50279 | [25498936.051, 6674480.883, 25498945.407, 6674494.997] | [25498940.729, 6674487.94] | 174 | kept (first occurrence) | `BID_0d2d4f78-8d7e-43fd-aa44-ed3a5145c8ff` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 63205–64051 | [25498936.051, 6674480.883, 25498945.407, 6674494.997] | [25498940.729, 6674487.94] | 321 | split (distinct content, synthesized id) | `BID_0d2d4f78-8d7e-43fd-aa44-ed3a5145c8ff__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54989423701E7 6674480.8825 3.52 2.54989360513E7 6674482.4066 3.52 2.54989390879E7 6674494.9965 3.52 2.54989430884E7 6674494.031699999 3.52 2.54989428486E7 6674493.0392 3.52 2.54989448834E7 6674492.5598 3.52 2.54989451202E7 6674493.541699999 3.52 2.54989454067E7 6674493.4725 3.52 2.54989423701E7 6674480.8825 3.52`

### `BID_0f7bfad2-a770-470d-96ae-4a965f68429d` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 44087–44442 | [25498851.927, 6674459.234, 25498877.009, 6674513.731] | [25498864.468, 6674486.482] | 552 | kept (first occurrence) | `BID_0f7bfad2-a770-470d-96ae-4a965f68429d` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 77753–79465 | [25498851.927, 6674459.234, 25498877.009, 6674513.731] | [25498864.468, 6674486.482] | 735 | split (distinct content, synthesized id) | `BID_0f7bfad2-a770-470d-96ae-4a965f68429d__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54988702485E7 6674478.7025 2.71 2.54988683951E7 6674479.121 2.71 2.54988679547E7 6674477.1701 2.71 2.5498869808E7 6674476.7516 2.71 2.54988664144E7 6674461.7196 2.71 2.54988644635E7 6674462.16 2.71 2.54988638028E7 6674459.2337 2.71 2.5498855062799998E7 6674461.2069 2.71 2.54988557234E7 6674464.1332 2.71 2.54988537725E7 6674464.5736 2.71 2.5498855469099995E7 6674472.0885 2.71 2.54988535611E7 6674 …`

### `BID_1414245b-1796-4bac-a3af-a4bc9046773e` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 43149–43736 | [25498756.745, 6674464.944, 25498846.241, 6674499.205] | [25498801.493, 6674482.075] | 1098 | kept (first occurrence) | `BID_1414245b-1796-4bac-a3af-a4bc9046773e` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 82545–85373 | [25498756.745, 6674464.944, 25498846.241, 6674499.205] | [25498801.493, 6674482.075] | 1269 | split (distinct content, synthesized id) | `BID_1414245b-1796-4bac-a3af-a4bc9046773e__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54987638231E7 6674499.2047 1.8379999999999999 2.54987703616E7 6674494.946299999 1.8379999999999999 2.54988462407E7 6674476.6443 1.8379999999999999 2.54988437718E7 6674466.4083 1.8379999999999999 2.54988400383E7 6674467.3344 1.8379999999999999 2.54988394374E7 6674464.9435 1.8379999999999999 2.54988351885E7 6674465.9683 1.8379999999999999 2.54988357618E7 6674468.3633 1.8379999999999999 2.549883263 …`

### `BID_1b431d54-c7e5-4ed8-aa6a-fab0dfc9dd54` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 8909–9535 | [25497972.355, 6672817.091, 25498013.045, 6672864.23] | [25497992.7, 6672840.661] | 1167 | kept (first occurrence) | `BID_1b431d54-c7e5-4ed8-aa6a-fab0dfc9dd54` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 50280–55108 | [25497972.355, 6672817.091, 25498013.045, 6672864.23] | [25497992.7, 6672840.661] | 2337 | split (distinct content, synthesized id) | `BID_1b431d54-c7e5-4ed8-aa6a-fab0dfc9dd54__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54980068168E7 6672817.091099999 2.5384 2.54979933746E7 6672826.244 2.5384 2.54979911191E7 6672827.779799999 2.5384 2.54979880176E7 6672829.891699999 2.5384 2.54979824495E7 6672833.683 2.5384 2.54979804557E7 6672835.0406 2.5384 2.54979774131E7 6672837.112399999 2.5384 2.54979723553E7 6672840.5563 2.5384 2.54979731659E7 6672841.769 2.5384 2.54979752826E7 6672844.9358 2.5384 2.54979751277E7 6672846 …`

### `BID_1ff0fc11-a905-4a99-8de6-5f7747ff9f26` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 13038–13619 | [25497287.787, 6672830.726, 25497339.25, 6672900.453] | [25497313.519, 6672865.589] | 1062 | kept (first occurrence) | `BID_1ff0fc11-a905-4a99-8de6-5f7747ff9f26` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 65550–73021 | [25497287.787, 6672830.726, 25497339.25, 6672900.453] | [25497313.519, 6672865.589] | 3537 | split (distinct content, synthesized id) | `BID_1ff0fc11-a905-4a99-8de6-5f7747ff9f26__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54973392356E7 6672842.9059999995 3.75 2.5497339204E7 6672842.715699999 3.75 2.54973391552E7 6672842.5289 3.75 2.54973390895E7 6672842.3475 3.75 2.54973390075E7 6672842.1728 3.75 2.54973389099E7 6672842.0063 3.75 2.54973388969E7 6672841.7648 3.75 2.5497338241799995E7 6672841.671 3.75 2.54973385979E7 6672835.4119 3.75 2.54973380891E7 6672835.2839 3.75 2.54973383134E7 6672831.9959 3.75 2.5497335490 …`

### `BID_2120ac24-96f9-4457-bef2-85176c9e8e1b` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 33765–34003 | [25498147.488, 6672600.878, 25498173.215, 6672635.297] | [25498160.352, 6672618.088] | 279 | kept (first occurrence) | `BID_2120ac24-96f9-4457-bef2-85176c9e8e1b` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 64052–65549 | [25498147.488, 6672600.878, 25498173.215, 6672635.297] | [25498160.352, 6672618.088] | 585 | split (distinct content, synthesized id) | `BID_2120ac24-96f9-4457-bef2-85176c9e8e1b__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54981482215E7 6672602.0205 2.88 2.54981474876E7 6672635.1154 2.88 2.54981556606E7 6672635.2966 2.88 2.54981575331E7 6672627.5362 2.88 2.54981560065E7 6672619.6975 2.88 2.54981560963E7 6672615.6485 2.88 2.54981651475E7 6672618.9876 2.88 2.54981726813E7 6672617.5553 2.88 2.5498172688E7 6672617.2553 2.88 2.5498172887999997E7 6672617.2598 2.88 2.5498173215E7 6672602.5995 2.88 2.54981655511E7 6672600 …`

### `BID_25d4f21c-7975-4acb-8e32-45af0e46783e` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 16978–17135 | [25497931.162, 6674371.825, 25497941.089, 6674377.994] | [25497936.126, 6674374.91] | 90 | kept (first occurrence) | `BID_25d4f21c-7975-4acb-8e32-45af0e46783e` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 20349–20710 | [25497931.162, 6674371.825, 25497941.089, 6674377.994] | [25497936.126, 6674374.91] | 90 | split (distinct content, synthesized id) | `BID_25d4f21c-7975-4acb-8e32-45af0e46783e__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5497931162E7 6674371.85 1.7118 2.5497931182E7 6674377.994 1.7118 2.5497941088999998E7 6674377.969 1.7118 2.5497941069E7 6674371.825 1.7118 2.5497931162E7 6674371.85 1.7118`

### `BID_27c83168-ae3b-4a24-be52-89d624145acf` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 43929–44086 | [25498922.928, 6674483.93, 25498932.769, 6674498.162] | [25498927.848, 6674491.046] | 90 | kept (first occurrence) | `BID_27c83168-ae3b-4a24-be52-89d624145acf` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 57466–57827 | [25498922.928, 6674483.93, 25498932.769, 6674498.162] | [25498927.848, 6674491.046] | 90 | split (distinct content, synthesized id) | `BID_27c83168-ae3b-4a24-be52-89d624145acf__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54989229278E7 6674485.5718 3.7199999999999998 2.54989259645E7 6674498.1618 3.7199999999999998 2.54989327692E7 6674496.5206 3.7199999999999998 2.54989297326E7 6674483.9305 3.7199999999999998 2.54989229278E7 6674485.5718 3.7199999999999998`

### `BID_292aa677-7d39-4b0c-85f8-8969ecf706d1` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 43737–43928 | [25498318.62, 6674782.212, 25498341.285, 6674812.228] | [25498329.953, 6674797.22] | 174 | kept (first occurrence) | `BID_292aa677-7d39-4b0c-85f8-8969ecf706d1` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 56934–57465 | [25498318.62, 6674782.212, 25498341.285, 6674812.228] | [25498329.953, 6674797.22] | 174 | split (distinct content, synthesized id) | `BID_292aa677-7d39-4b0c-85f8-8969ecf706d1__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5498332438E7 6674812.228 2.6856 2.5498341285E7 6674807.193 2.6856 2.5498327068999995E7 6674782.212 2.6856 2.549831862E7 6674787.949 2.6856 2.54983198101E7 6674790.0401 2.6856 2.54983203316E7 6674789.7433 2.6856 2.54983218897E7 6674792.4809 2.6856 2.5498321368199997E7 6674792.7777 2.6856 2.5498332438E7 6674812.228 2.6856`

### `BID_29d5c8c9-a6e1-439b-ad4e-cceab20d9f9e` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 11617–12350 | [25497346.362, 6672790.689, 25497420.423, 6672868.705] | [25497383.392, 6672829.697] | 1434 | kept (first occurrence) | `BID_29d5c8c9-a6e1-439b-ad4e-cceab20d9f9e` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 36496–43148 | [25497346.362, 6672790.689, 25497420.423, 6672868.705] | [25497383.392, 6672829.697] | 2823 | split (distinct content, synthesized id) | `BID_29d5c8c9-a6e1-439b-ad4e-cceab20d9f9e__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54974044112E7 6672794.3126 1.9 2.54974044079E7 6672794.0986 1.9 2.54974013708E7 6672793.9563 1.9 2.5497401347E7 6672794.152299999 1.9 2.54973929317E7 6672793.744 1.9 2.54973929806E7 6672792.9254 1.9 2.54973917505E7 6672792.8489 1.9 2.54973917265E7 6672793.2781 1.9 2.54973899382E7 6672793.1702 1.9 2.54973899824E7 6672792.74 1.9 2.54973887644E7 6672792.6735 1.9 2.54973887403E7 6672793.1027 1.9 2.5 …`

### `BID_3224c543-6e8e-4e0d-a828-ca0742564036` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 76821–77122 | [25498872.616, 6674985.952, 25498974.973, 6675042.373] | [25498923.795, 6675014.162] | 426 | kept (first occurrence) | `BID_3224c543-6e8e-4e0d-a828-ca0742564036` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 86193–88405 | [25498872.616, 6674985.952, 25498974.973, 6675042.373] | [25498923.795, 6675014.162] | 963 | split (distinct content, synthesized id) | `BID_3224c543-6e8e-4e0d-a828-ca0742564036__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54989670435E7 6674985.9523 2.2079999999999997 2.54989183276E7 6674996.9507 2.2079999999999997 2.54989180221E7 6674995.5977 2.2079999999999997 2.54989078579E7 6674997.8924 2.2079999999999997 2.54989081634E7 6674999.2454 2.2079999999999997 2.54989038888E7 6675000.2104 2.2079999999999997 2.54988846746E7 6675004.5483 2.2079999999999997 2.54988843691E7 6675003.1954 2.2079999999999997 2.54988756681E7  …`

### `BID_36219417-7791-4bee-b6ad-c73cf558f365` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 12351–12626 | [25497225.905, 6672784.465, 25497248.267, 6672827.712] | [25497237.086, 6672806.089] | 348 | kept (first occurrence) | `BID_36219417-7791-4bee-b6ad-c73cf558f365` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 22740–24849 | [25497225.905, 6672784.465, 25497248.267, 6672827.712] | [25497237.086, 6672806.089] | 1020 | split (distinct content, synthesized id) | `BID_36219417-7791-4bee-b6ad-c73cf558f365__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54972279627E7 6672784.465099999 3.2259 2.54972276568E7 6672790.7042 3.2259 2.54972274051E7 6672795.837799999 3.2259 2.54972273126E7 6672797.7235 3.2259 2.549722623E7 6672819.802 3.2259 2.5497226226499997E7 6672819.8744 3.2259 2.54972262195E7 6672820.0161 3.2259 2.54972259048E7 6672826.434899999 3.2259 2.54972288391E7 6672826.6196 3.2259 2.54972461991E7 6672827.7124 3.2259 2.54972463198E7 6672825 …`

### `BID_37f515ba-6d88-4c20-a4b0-3e02a9587d4d` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 76429–76820 | [25498345.167, 6675252.861, 25498522.531, 6675374.812] | [25498433.849, 6675313.837] | 636 | kept (first occurrence) | `BID_37f515ba-6d88-4c20-a4b0-3e02a9587d4d` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 192414–199107 | [25498345.167, 6675252.861, 25498522.531, 6675374.812] | [25498433.849, 6675313.837] | 3111 | split (distinct content, synthesized id) | `BID_37f515ba-6d88-4c20-a4b0-3e02a9587d4d__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54984093864E7 6675339.0591 2.0 2.549841025E7 6675338.6207 2.0 2.5498396551299997E7 6675311.016899999 2.0 2.54984086217E7 6675304.957199999 2.0 2.54984081828E7 6675304.072 2.0 2.54984097491E7 6675303.2752 2.0 2.54984064613E7 6675296.9107 2.0 2.54984048028E7 6675297.7541 2.0 2.54983994995E7 6675287.3742 2.0 2.5498398335E7 6675285.1196 2.0 2.54983581012E7 6675305.4659 2.0 2.5498357397999994E7 66753 …`

### `BID_3af25639-51b0-48e1-bbb6-6d9b72777748` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 20015–20190 | [25497301.345, 6673995.485, 25497337.251, 6674089.238] | [25497319.298, 6674042.362] | 132 | kept (first occurrence) | `BID_3af25639-51b0-48e1-bbb6-6d9b72777748` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 26131–26578 | [25497301.345, 6673995.485, 25497337.251, 6674089.238] | [25497319.298, 6674042.362] | 132 | split (distinct content, synthesized id) | `BID_3af25639-51b0-48e1-bbb6-6d9b72777748__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5497337251299996E7 6674074.3542 2.6003 2.54973250565E7 6674074.0009 2.6003 2.54973273122E7 6673996.1595 2.6003 2.5497304032E7 6673995.4849 2.6003 2.5497301345E7 6674088.21 2.6003 2.549733682E7 6674089.238 2.6003 2.5497337251299996E7 6674074.3542 2.6003`

### `BID_3c01cc21-8dd9-4fbf-8821-e49ac474abcd` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 34004–34197 | [25498159.923, 6672635.563, 25498169.957, 6672642.95] | [25498164.94, 6672639.257] | 174 | kept (first occurrence) | `BID_3c01cc21-8dd9-4fbf-8821-e49ac474abcd` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 56319–56723 | [25498159.923, 6672635.563, 25498169.957, 6672642.95] | [25498164.94, 6672639.257] | 129 | split (distinct content, synthesized id) | `BID_3c01cc21-8dd9-4fbf-8821-e49ac474abcd__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54981699569E7 6672636.7815 3.6679999999999997 2.549816561E7 6672635.5633 3.6679999999999997 2.54981649174E7 6672635.665 3.6679999999999997 2.54981620482E7 6672636.086299999 3.6679999999999997 2.54981601106E7 6672636.3708 3.6679999999999997 2.54981599234E7 6672642.5374 3.6679999999999997 2.54981698198E7 6672642.9501 3.6679999999999997 2.54981698296E7 6672642.506299999 3.6679999999999997 2.5498169 …`

### `BID_3eb2b5dc-7420-426e-8462-0c6db92e0823` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 3451–3608 | [25498384.778, 6676319.22, 25498426.029, 6676344.058] | [25498405.403, 6676331.639] | 90 | kept (first occurrence) | `BID_3eb2b5dc-7420-426e-8462-0c6db92e0823` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 90271–90632 | [25498384.778, 6676319.22, 25498426.029, 6676344.058] | [25498405.403, 6676331.639] | 90 | split (distinct content, synthesized id) | `BID_3eb2b5dc-7420-426e-8462-0c6db92e0823__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54983847779E7 6676333.9829 1.576 2.5498422032899998E7 6676344.0581 1.576 2.54984260293E7 6676329.2878 1.576 2.54983887961E7 6676319.2203 1.576 2.54983847779E7 6676333.9829 1.576`

### `BID_4004a9f3-f091-47c6-b045-a85d95eaee26` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 419415–419570 | [25500191.055, 6674495.239, 25500209.757, 6674513.472] | [25500200.406, 6674504.355] | 90 | kept (first occurrence) | `BID_4004a9f3-f091-47c6-b045-a85d95eaee26` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 423893–424435 | [25500191.055, 6674495.239, 25500209.757, 6674513.472] | [25500200.406, 6674504.355] | 207 | split (distinct content, synthesized id) | `BID_4004a9f3-f091-47c6-b045-a85d95eaee26__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.55002068536E7 6674499.1548 10.299999999999999 2.5500206112399995E7 6674498.3379 10.299999999999999 2.5500203301E7 6674495.239 10.299999999999999 2.5500191054999996E7 6674506.352 10.299999999999999 2.55001938624E7 6674509.4517 10.299999999999999 2.55001946029E7 6674510.2693 10.299999999999999 2.55001975035E7 6674513.472 10.299999999999999 2.5500209757E7 6674502.355 10.299999999999999 2.5500206853 …`

### `BID_44a7f916-3b44-434b-8676-50058ffc8329` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 82369–82544 | [25499049.105, 6674605.973, 25499093.202, 6674652.636] | [25499071.153, 6674629.305] | 132 | kept (first occurrence) | `BID_44a7f916-3b44-434b-8676-50058ffc8329` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 96122–96845 | [25499049.105, 6674605.973, 25499093.202, 6674652.636] | [25499071.153, 6674629.305] | 246 | split (distinct content, synthesized id) | `BID_44a7f916-3b44-434b-8676-50058ffc8329__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54990660004E7 6674607.2575 3.2599999999999993 2.54990541699E7 6674605.9733 3.2599999999999993 2.54990491047E7 6674652.6362 3.2599999999999993 2.54990932016E7 6674627.5494 3.2599999999999993 2.54990882509E7 6674618.8471 3.2599999999999993 2.5499063195099995E7 6674633.1014 3.2599999999999993 2.54990660004E7 6674607.2575 3.2599999999999993`

### `BID_4cc6f55f-3f10-41b0-8bf4-d2820c873a2b` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 19857–20014 | [25497923.008, 6674368.935, 25497929.187, 6674373.956] | [25497926.098, 6674371.445] | 90 | kept (first occurrence) | `BID_4cc6f55f-3f10-41b0-8bf4-d2820c873a2b` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 25769–26130 | [25497923.008, 6674368.935, 25497929.187, 6674373.956] | [25497926.098, 6674371.445] | 90 | split (distinct content, synthesized id) | `BID_4cc6f55f-3f10-41b0-8bf4-d2820c873a2b__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5497923007999998E7 6674368.969 1.6628 2.5497923033999998E7 6674373.955999999 1.6628 2.5497929187E7 6674373.922 1.6628 2.5497929161E7 6674368.935 1.6628 2.5497923007999998E7 6674368.969 1.6628`

### `BID_4e333fb8-4e25-41b4-a9ff-ff34d8c10dd3` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 49892–50085 | [25498942.37, 6674479.358, 25498951.725, 6674493.473] | [25498947.047, 6674486.416] | 174 | kept (first occurrence) | `BID_4e333fb8-4e25-41b4-a9ff-ff34d8c10dd3` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 57828–58588 | [25498942.37, 6674479.358, 25498951.725, 6674493.473] | [25498947.047, 6674486.416] | 279 | split (distinct content, synthesized id) | `BID_4e333fb8-4e25-41b4-a9ff-ff34d8c10dd3__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54989486888E7 6674479.3584 3.5099999999999993 2.54989423701E7 6674480.8825 3.5099999999999993 2.54989454067E7 6674493.4725 3.5099999999999993 2.54989494251E7 6674492.498399999 3.5099999999999993 2.54989491907E7 6674491.5263 3.5099999999999993 2.54989512186E7 6674491.0205 3.5099999999999993 2.54989514569E7 6674492.008399999 3.5099999999999993 2.54989517254E7 6674491.9484 3.5099999999999993 2.5498 …`

### `BID_508bfef0-6aaf-476b-8daa-1669665405c0` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 13620–14760 | [25497344.758, 6672790.689, 25497420.423, 6672905.578] | [25497382.591, 6672848.134] | 2349 | kept (first occurrence) | `BID_508bfef0-6aaf-476b-8daa-1669665405c0` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 123488–132146 | [25497344.758, 6672790.689, 25497420.423, 6672905.578] | [25497382.591, 6672848.134] | 4731 | split (distinct content, synthesized id) | `BID_508bfef0-6aaf-476b-8daa-1669665405c0__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54974182268E7 6672794.5626 -12.074 2.5497418240999997E7 6672794.313 -12.074 2.5497415192799997E7 6672794.1397 -12.074 2.54974151661E7 6672794.3817 -12.074 2.5497413091E7 6672794.2602 -12.074 2.54974130456E7 6672794.7793 -12.074 2.54974096206E7 6672794.5942 -12.074 2.54974088015E7 6672794.549899999 -12.074 2.54974044112E7 6672794.3126 -12.074 2.54974044079E7 6672794.0986 -12.074 2.54974013708E7 6 …`

### `BID_55519a0d-b032-47aa-8138-bf13d53a5e8f` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 55109–55266 | [25498948.689, 6674477.717, 25498958.529, 6674491.948] | [25498953.609, 6674484.832] | 90 | kept (first occurrence) | `BID_55519a0d-b032-47aa-8138-bf13d53a5e8f` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 58589–58950 | [25498948.689, 6674477.717, 25498958.529, 6674491.948] | [25498953.609, 6674484.832] | 90 | split (distinct content, synthesized id) | `BID_55519a0d-b032-47aa-8138-bf13d53a5e8f__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54989486888E7 6674479.3584 3.5223 2.54989517254E7 6674491.9484 3.5223 2.54989585291E7 6674490.3026 3.5223 2.54989554935E7 6674477.7171 3.5223 2.54989486888E7 6674479.3584 3.5223`

### `BID_5e10e2e5-9b57-4911-aed5-a9e9c998c485` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 10736–10936 | [25497657.06, 6672655.264, 25497686.869, 6672726.054] | [25497671.964, 6672690.659] | 195 | kept (first occurrence) | `BID_5e10e2e5-9b57-4911-aed5-a9e9c998c485` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 17609–18508 | [25497657.06, 6672655.264, 25497686.869, 6672726.054] | [25497671.964, 6672690.659] | 342 | split (distinct content, synthesized id) | `BID_5e10e2e5-9b57-4911-aed5-a9e9c998c485__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54976607235E7 6672656.7222 2.8 2.54976570605E7 6672671.9529 2.8 2.54976691702E7 6672674.865299999 2.8 2.5497657271699995E7 6672724.339599999 2.8 2.5497663885E7 6672726.0543 2.8 2.5497671892E7 6672720.662 2.8 2.5497686869E7 6672658.387 2.8 2.54976738842E7 6672655.2642 2.8 2.54976728332E7 6672659.6346 2.8 2.54976607235E7 6672656.7222 2.8`

### `BID_5f1bf6a1-8d26-4cac-b0b6-7411f93da6f1` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 419571–419728 | [25500168.93, 6674860.992, 25500183.922, 6674876.307] | [25500176.426, 6674868.649] | 90 | kept (first occurrence) | `BID_5f1bf6a1-8d26-4cac-b0b6-7411f93da6f1` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 425744–426105 | [25500168.93, 6674860.992, 25500183.922, 6674876.307] | [25500176.426, 6674868.649] | 90 | split (distinct content, synthesized id) | `BID_5f1bf6a1-8d26-4cac-b0b6-7411f93da6f1__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.550016893E7 6674866.101 7.2638 2.55001784559E7 6674876.306999999 7.2638 2.5500183922E7 6674871.21 7.2638 2.5500174394E7 6674860.992 7.2638 2.550016893E7 6674866.101 7.2638`

### `BID_61fc6e9a-3347-4a73-bd26-3d4a06362e45` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 8753–8908 | [25497682.086, 6672667.169, 25497739.984, 6672710.314] | [25497711.035, 6672688.741] | 90 | kept (first occurrence) | `BID_61fc6e9a-3347-4a73-bd26-3d4a06362e45` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 15583–15942 | [25497682.086, 6672667.169, 25497739.984, 6672710.314] | [25497711.035, 6672688.741] | 90 | split (distinct content, synthesized id) | `BID_61fc6e9a-3347-4a73-bd26-3d4a06362e45__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54976820859E7 6672702.7037 1.8599999999999999 2.54976872551E7 6672710.3137 1.8599999999999999 2.54977399837E7 6672674.7995 1.8599999999999999 2.54977348443E7 6672667.1689 1.8599999999999999 2.54976820859E7 6672702.7037 1.8599999999999999`

### `BID_66ca5a62-2bc2-4489-a81b-c01160b1cc0f` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 76199–76428 | [25497970.041, 6675537.02, 25498022.244, 6675569.376] | [25497996.142, 6675553.198] | 258 | kept (first occurrence) | `BID_66ca5a62-2bc2-4489-a81b-c01160b1cc0f` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 114955–116803 | [25497970.041, 6675537.02, 25498022.244, 6675569.376] | [25497996.142, 6675553.198] | 1029 | split (distinct content, synthesized id) | `BID_66ca5a62-2bc2-4489-a81b-c01160b1cc0f__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54980222342E7 6675568.347 21.332 2.5498022052699998E7 6675558.4952 21.332 2.54980218429E7 6675547.1152 21.332 2.54980216594E7 6675537.1593 21.332 2.54980216568E7 6675537.0195 21.332 2.54980162268E7 6675537.2226 21.332 2.54980113407E7 6675537.4053 21.332 2.54980065918E7 6675537.5829 21.332 2.54980009203E7 6675537.795 21.332 2.5498000574E7 6675537.808 21.332 2.5498000595999997E7 6675538.389 21.332 …`

### `BID_6f4243bf-e3a7-4ea7-92c0-c5b53e42fe08` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 76041–76198 | [25498515.651, 6675258.415, 25498555.682, 6675291.732] | [25498535.667, 6675275.073] | 90 | kept (first occurrence) | `BID_6f4243bf-e3a7-4ea7-92c0-c5b53e42fe08` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 80802–81212 | [25498515.651, 6675258.415, 25498555.682, 6675291.732] | [25498535.667, 6675275.073] | 111 | split (distinct content, synthesized id) | `BID_6f4243bf-e3a7-4ea7-92c0-c5b53e42fe08__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5498515651E7 6675274.199 3.484 2.5498524464E7 6675291.732 3.484 2.54985556818E7 6675275.9173 3.484 2.54985468153E7 6675258.4151 3.484 2.5498515651E7 6675274.199 3.484`

### `BID_74e134e0-d8be-4a2a-b747-190143386f41` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 81213–81406 | [25499674.674, 6674714.96, 25499692.148, 6674731.801] | [25499683.411, 6674723.38] | 174 | kept (first occurrence) | `BID_74e134e0-d8be-4a2a-b747-190143386f41` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 92754–93440 | [25499674.674, 6674714.96, 25499692.148, 6674731.801] | [25499683.411, 6674723.38] | 237 | split (distinct content, synthesized id) | `BID_74e134e0-d8be-4a2a-b747-190143386f41__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5499685988E7 6674714.96 7.3999999999999995 2.54996746737E7 6674723.7278 7.3999999999999995 2.54996765243E7 6674726.0635 7.3999999999999995 2.54996754034E7 6674726.9516 7.3999999999999995 2.54996781018E7 6674730.3252 7.3999999999999995 2.5499679207E7 6674729.4496 7.3999999999999995 2.549968107E7 6674731.801 7.3999999999999995 2.5499692148E7 6674723.024 7.3999999999999995 2.5499685988E7 6674714.96 …`

### `BID_77133ab7-da2e-4a72-bb94-69fcac556917` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 56055–56318 | [25498302.878, 6674793.117, 25498324.468, 6674821.611] | [25498313.673, 6674807.364] | 342 | kept (first occurrence) | `BID_77133ab7-da2e-4a72-bb94-69fcac556917` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 81407–82368 | [25498302.812, 6674793.045, 25498324.536, 6674821.679] | [25498313.674, 6674807.362] | 324 | split (distinct content, synthesized id) | `BID_77133ab7-da2e-4a72-bb94-69fcac556917__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54983159089E7 6674802.6437 2.69 2.54983191557E7 6674808.3493 2.69 2.54983195749E7 6674808.0646 2.694 2.54983163478E7 6674802.3939 2.694 2.54983159089E7 6674802.6437 2.69`

### `BID_7b481eea-a20a-4b3d-bf1d-c7a31503812d` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 10937–11616 | [25497290.67, 6672788.346, 25497341.127, 6672832.022] | [25497315.899, 6672810.184] | 1308 | kept (first occurrence) | `BID_7b481eea-a20a-4b3d-bf1d-c7a31503812d` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 27428–31178 | [25497290.67, 6672788.346, 25497341.127, 6672832.022] | [25497315.899, 6672810.184] | 1671 | split (distinct content, synthesized id) | `BID_7b481eea-a20a-4b3d-bf1d-c7a31503812d__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54972925923E7 6672800.9986 1.92 2.54972915774E7 6672800.922299999 1.92 2.54972914893E7 6672801.596 1.92 2.54972917433E7 6672801.582999999 1.92 2.54972916065E7 6672803.998 1.92 2.54972913525E7 6672803.998299999 1.92 2.54972913281E7 6672804.8118 1.92 2.54972915185E7 6672804.748 1.92 2.54972915344E7 6672807.455099999 1.92 2.54972912168E7 6672807.3792 1.92 2.5497291205E7 6672808.1291 1.92 2.54972914 …`

### `BID_7c1ce529-f780-46c3-9aa8-440af70ddc7a` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 16558–16977 | [25497686.814, 6674235.173, 25497793.435, 6674338.971] | [25497740.124, 6674287.072] | 684 | kept (first occurrence) | `BID_7c1ce529-f780-46c3-9aa8-440af70ddc7a` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 99455–106372 | [25497686.814, 6674235.173, 25497793.435, 6674338.971] | [25497740.124, 6674287.072] | 3303 | split (distinct content, synthesized id) | `BID_7c1ce529-f780-46c3-9aa8-440af70ddc7a__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54977879572E7 6674300.2417 -7.59 2.54977875727E7 6674299.640199999 -7.59 2.54977854588E7 6674296.3326 -7.59 2.54977853864E7 6674296.2193 -7.59 2.54977851497E7 6674295.8491 -7.59 2.54977834825E7 6674293.2405 -7.59 2.5497780369799998E7 6674288.3702 -7.59 2.5497779872E7 6674287.5914 -7.59 2.54977736902E7 6674277.9193 -7.59 2.54977724432E7 6674275.9683 -7.59 2.5497772281099997E7 6674275.7146 -7.59 2 …`

### `BID_835109fc-63a7-493e-b691-7f4011d0678d` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 73022–73179 | [25498755.928, 6675187.08, 25498788.068, 6675247.954] | [25498771.998, 6675217.517] | 90 | kept (first occurrence) | `BID_835109fc-63a7-493e-b691-7f4011d0678d` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 88406–89123 | [25498755.928, 6675187.08, 25498788.068, 6675247.954] | [25498771.998, 6675217.517] | 252 | split (distinct content, synthesized id) | `BID_835109fc-63a7-493e-b691-7f4011d0678d__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54987762566E7 6675187.0801 0.2 2.54987559284E7 6675197.3379 0.2 2.54987665356E7 6675247.9544 0.2 2.54987880681E7 6675243.441999999 0.2 2.54987762566E7 6675187.0801 0.2`

### `BID_84d96d04-e1d4-4a42-a2a7-b9a9397c86b7` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 16391–16557 | [25497444.995, 6674884.395, 25497481.903, 6674906.915] | [25497463.449, 6674895.655] | 111 | kept (first occurrence) | `BID_84d96d04-e1d4-4a42-a2a7-b9a9397c86b7` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 21299–22739 | [25497444.995, 6674884.395, 25497481.903, 6674906.915] | [25497463.449, 6674895.655] | 501 | split (distinct content, synthesized id) | `BID_84d96d04-e1d4-4a42-a2a7-b9a9397c86b7__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54974468476E7 6674884.3953 17.91 2.54974449945E7 6674900.856 17.91 2.54974799584E7 6674906.9146 17.91 2.54974819026E7 6674889.7185 17.91 2.54974521022E7 6674884.5797 17.91 2.54974468476E7 6674884.3953 17.91`

### `BID_87552cc2-eb82-4e36-aa52-9e478985d931` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 55441–55596 | [25498790.884, 6674505.296, 25498844.874, 6674528.449] | [25498817.879, 6674516.873] | 90 | kept (first occurrence) | `BID_87552cc2-eb82-4e36-aa52-9e478985d931` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 62845–63204 | [25498790.884, 6674505.296, 25498844.874, 6674528.449] | [25498817.879, 6674516.873] | 90 | split (distinct content, synthesized id) | `BID_87552cc2-eb82-4e36-aa52-9e478985d931__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54987908836E7 6674517.6927 2.566 2.5498793478E7 6674528.4493 2.566 2.54988448741E7 6674516.0528 2.566 2.54988422797E7 6674505.2963 2.566 2.54987908836E7 6674517.6927 2.566`

### `BID_99ea274e-73c7-41ab-8d71-62c0883fee01` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 19663–19856 | [25497479.958, 6674889.719, 25497516.863, 6674912.965] | [25497498.411, 6674901.342] | 174 | kept (first occurrence) | `BID_99ea274e-73c7-41ab-8d71-62c0883fee01` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 34198–36000 | [25497479.958, 6674889.719, 25497516.863, 6674912.965] | [25497498.411, 6674901.342] | 639 | split (distinct content, synthesized id) | `BID_99ea274e-73c7-41ab-8d71-62c0883fee01__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5497501764E7 6674892.996 17.886 2.549749901E7 6674892.503 17.886 2.54974989437E7 6674892.6571 17.886 2.54974819026E7 6674889.7185 17.886 2.54974799584E7 6674906.9146 17.886 2.54975149532E7 6674912.9648 17.886 2.54975168629E7 6674895.7471 17.886 2.54975017706E7 6674893.1446 17.886 2.5497501764E7 6674892.996 17.886`

### `BID_a8385f58-4d43-4a5f-b8a4-821573950f81` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 5136–5383 | [25497309.141, 6672803.752, 25497330.64, 6672819.31] | [25497319.891, 6672811.531] | 300 | kept (first occurrence) | `BID_a8385f58-4d43-4a5f-b8a4-821573950f81` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 18509–19662 | [25497309.141, 6672803.752, 25497330.64, 6672819.31] | [25497319.891, 6672811.531] | 456 | split (distinct content, synthesized id) | `BID_a8385f58-4d43-4a5f-b8a4-821573950f81__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54973096867E7 6672803.7524 3.4 2.54973096456E7 6672805.244199999 3.4 2.54973092061E7 6672805.2407 3.4 2.54973091414E7 6672808.138 3.4 2.5497315234E7 6672808.4973 3.4 2.54973152618E7 6672808.1628 3.4 2.54973161233E7 6672808.2094 3.4 2.5497316136E7 6672810.1303 3.4 2.54973125532E7 6672809.9118 3.4 2.54973123319E7 6672819.160099999 3.4 2.54973158343E7 6672819.31 3.4 2.54973159001E7 6672817.2623 3.4 …`

### `BID_acfafbdb-93ac-4fc8-85bc-2d398af24144` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 17294–17450 | [25497268.319, 6674054.993, 25497283.415, 6674074.944] | [25497275.867, 6674064.968] | 90 | kept (first occurrence) | `BID_acfafbdb-93ac-4fc8-85bc-2d398af24144` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 24850–25406 | [25497268.319, 6674054.993, 25497283.415, 6674074.944] | [25497275.867, 6674064.968] | 150 | split (distinct content, synthesized id) | `BID_acfafbdb-93ac-4fc8-85bc-2d398af24144__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5497269329399996E7 6674054.993 2.54 2.5497268319E7 6674074.203 2.54 2.5497282407E7 6674074.944 2.54 2.5497283415E7 6674055.733 2.54 2.5497269329399996E7 6674054.993 2.54`

### `BID_ae9c4527-3e45-4ab4-9307-32093ad6fa37` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 55597–55790 | [25498929.733, 6674482.407, 25498939.088, 6674496.521] | [25498934.41, 6674489.464] | 174 | kept (first occurrence) | `BID_ae9c4527-3e45-4ab4-9307-32093ad6fa37` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 80084–80801 | [25498929.733, 6674482.407, 25498939.088, 6674496.521] | [25498934.41, 6674489.464] | 258 | split (distinct content, synthesized id) | `BID_ae9c4527-3e45-4ab4-9307-32093ad6fa37__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54989360513E7 6674482.4066 3.56 2.54989297326E7 6674483.9305 3.56 2.54989327692E7 6674496.5206 3.56 2.54989367696E7 6674495.555699999 3.56 2.54989365301E7 6674494.5632 3.56 2.5498938562E7 6674494.0731 3.56 2.5498938801399995E7 6674495.065699999 3.56 2.54989390879E7 6674494.9965 3.56 2.54989360513E7 6674482.4066 3.56`

### `BID_af955f0d-d963-41e3-a563-9dee154dfddf` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 9536–9711 | [25497673.317, 6672723.238, 25497707.798, 6672750.518] | [25497690.558, 6672736.878] | 132 | kept (first occurrence) | `BID_af955f0d-d963-41e3-a563-9dee154dfddf` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 15943–16390 | [25497673.317, 6672723.238, 25497707.798, 6672750.518] | [25497690.558, 6672736.878] | 132 | split (distinct content, synthesized id) | `BID_af955f0d-d963-41e3-a563-9dee154dfddf__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54976733174E7 6672743.6361 2.2769 2.54976778751E7 6672750.5181 2.2769 2.54977077977E7 6672730.796 2.2769 2.54977027897E7 6672723.2377 2.2769 2.5497685848999996E7 6672734.4382 2.2769 2.5497686266E7 6672735.0821 2.2769 2.54976733174E7 6672743.6361 2.2769`

### `BID_c268d168-ddd0-44dd-a19b-b327940454b9` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 3135–3292 | [25498575.383, 6676007.814, 25498611.247, 6676042.094] | [25498593.315, 6676024.954] | 90 | kept (first occurrence) | `BID_c268d168-ddd0-44dd-a19b-b327940454b9` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 12627–13037 | [25498575.383, 6676007.814, 25498611.247, 6676042.094] | [25498593.315, 6676024.954] | 111 | split (distinct content, synthesized id) | `BID_c268d168-ddd0-44dd-a19b-b327940454b9__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54986010301E7 6676042.094 1.8637 2.5498611247E7 6676030.561 1.8637 2.5498585569999997E7 6676007.814 1.8637 2.5498575383E7 6676019.252 1.8637 2.54986010301E7 6676042.094 1.8637`

### `BID_c4874819-3333-4829-a178-11b0d33f7900` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 3293–3450 | [25498426.483, 6676330.484, 25498479.583, 6676358.507] | [25498453.033, 6676344.496] | 90 | kept (first occurrence) | `BID_c4874819-3333-4829-a178-11b0d33f7900` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 9712–10073 | [25498426.483, 6676330.484, 25498479.583, 6676358.507] | [25498453.033, 6676344.496] | 90 | split (distinct content, synthesized id) | `BID_c4874819-3333-4829-a178-11b0d33f7900__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54984264831E7 6676345.2351 1.5291999999999997 2.54984756014E7 6676358.5074 1.5291999999999997 2.5498479582599998E7 6676343.758799999 1.5291999999999997 2.54984304712E7 6676330.4837 1.5291999999999997 2.54984264831E7 6676345.2351 1.5291999999999997`

### `BID_c6c36d17-6fc8-4d7b-a0c9-182adc969178` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 85374–85666 | [25499078.717, 6674565.486, 25499103.824, 6674627.549] | [25499091.271, 6674596.518] | 405 | kept (first occurrence) | `BID_c6c36d17-6fc8-4d7b-a0c9-182adc969178` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 108632–109638 | [25499078.717, 6674565.486, 25499103.824, 6674627.549] | [25499091.271, 6674596.518] | 405 | split (distinct content, synthesized id) | `BID_c6c36d17-6fc8-4d7b-a0c9-182adc969178__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5499100008499995E7 6674615.9348 3.167 2.5499098303399995E7 6674608.3732 3.167 2.54991007303E7 6674607.8215 3.167 2.54990992755E7 6674601.3866 3.167 2.54990968443E7 6674601.9233 3.167 2.54990940968E7 6674589.8249 3.167 2.54990965386E7 6674589.2811 3.167 2.5499095579E7 6674585.037099999 3.167 2.54990931526E7 6674585.5771 3.167 2.54990919281E7 6674580.1591 3.167 2.54990943546E7 6674579.6211 3.167 2 …`

### `BID_cc9e190f-eb2a-4d7b-8f4d-e46176111183` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 55267–55440 | [25498860.69, 6674943.749, 25498895.264, 6674984.491] | [25498877.977, 6674964.12] | 132 | kept (first occurrence) | `BID_cc9e190f-eb2a-4d7b-8f4d-e46176111183` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 77123–77752 | [25498860.69, 6674943.749, 25498895.264, 6674984.491] | [25498877.977, 6674964.12] | 216 | split (distinct content, synthesized id) | `BID_cc9e190f-eb2a-4d7b-8f4d-e46176111183__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.549886069E7 6674953.3177 2.57 2.54988677279E7 6674984.4911 2.57 2.54988901608E7 6674981.849 2.57 2.54988894552E7 6674975.725 2.57 2.54988952644E7 6674973.3813 2.57 2.5498885652499996E7 6674943.7495 2.57 2.549886069E7 6674953.3177 2.57`

### `BID_ce1bcfa8-a9e4-43e3-b27b-e772975077ac` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 2977–3134 | [25498392.191, 6676277.72, 25498437.209, 6676316.704] | [25498414.7, 6676297.212] | 90 | kept (first occurrence) | `BID_ce1bcfa8-a9e4-43e3-b27b-e772975077ac` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 15172–15582 | [25498392.191, 6676277.72, 25498437.209, 6676316.704] | [25498414.7, 6676297.212] | 111 | split (distinct content, synthesized id) | `BID_ce1bcfa8-a9e4-43e3-b27b-e772975077ac__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54984293963E7 6676316.7039 1.567 2.54984372095E7 6676287.7783 1.567 2.5498399995099995E7 6676277.7203 1.567 2.5498392191E7 6676306.6603 1.567 2.54984293963E7 6676316.7039 1.567`

### `BID_d08cae1d-607a-483a-962e-18d97ae35fcd` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 85667–85878 | [25499939.706, 6674905.946, 25499953.21, 6674918.694] | [25499946.458, 6674912.32] | 216 | kept (first occurrence) | `BID_d08cae1d-607a-483a-962e-18d97ae35fcd` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 94056–94975 | [25499939.706, 6674905.946, 25499953.21, 6674918.694] | [25499946.458, 6674912.32] | 312 | split (distinct content, synthesized id) | `BID_d08cae1d-607a-483a-962e-18d97ae35fcd__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5499950152E7 6674910.291 6.62 2.5499950516E7 6674909.793 6.62 2.5499947567E7 6674907.646 6.62 2.5499947208E7 6674908.1391 6.62 2.5499944175E7 6674905.946 6.62 2.54999397062E7 6674912.0562 6.62 2.54999432538E7 6674914.7083 6.62 2.54999452825E7 6674916.1694 6.62 2.5499948788E7 6674918.693999999 6.62 2.549995321E7 6674912.554 6.62 2.5499950152E7 6674910.291 6.62`

### `BID_d1809b6a-4f25-4ac2-a94e-1a6f11ea5c20` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 32621–32794 | [25497722.172, 6676442.006, 25497727.789, 6676450.561] | [25497724.98, 6676446.283] | 132 | kept (first occurrence) | `BID_d1809b6a-4f25-4ac2-a94e-1a6f11ea5c20` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 36001–36495 | [25497722.172, 6676442.006, 25497727.789, 6676450.561] | [25497724.98, 6676446.283] | 153 | split (distinct content, synthesized id) | `BID_d1809b6a-4f25-4ac2-a94e-1a6f11ea5c20__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54977264058E7 6676442.0062 2.6433999999999997 2.54977221717E7 6676442.851799999 2.6433999999999997 2.54977228431E7 6676446.7757 2.6433999999999997 2.54977224081E7 6676446.8216 2.6433999999999997 2.54977231034E7 6676450.561 2.6433999999999997 2.54977277888E7 6676449.8567 2.6433999999999997 2.54977264058E7 6676442.0062 2.6433999999999997`

### `BID_d1e8b6e7-9ec7-4742-8ebf-73374f5b31f0` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 421013–421168 | [25500064.676, 6675991.873, 25500071.734, 6675998.231] | [25500068.205, 6675995.052] | 90 | kept (first occurrence) | `BID_d1e8b6e7-9ec7-4742-8ebf-73374f5b31f0` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 426841–427249 | [25500064.676, 6675991.873, 25500071.734, 6675998.231] | [25500068.205, 6675995.052] | 111 | split (distinct content, synthesized id) | `BID_d1e8b6e7-9ec7-4742-8ebf-73374f5b31f0__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.55000697278E7 6675998.2306 9.65 2.5500071734E7 6675995.6248 9.65 2.55000666491E7 6675991.8728 9.65 2.5500064676E7 6675994.4111 9.65 2.55000697278E7 6675998.2306 9.65`

### `BID_d3a96da0-69a8-432d-b550-2d98ba9fa1df` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 86035–86192 | [25499701.35, 6674703.554, 25499711.584, 6674713.368] | [25499706.467, 6674708.461] | 90 | kept (first occurrence) | `BID_d3a96da0-69a8-432d-b550-2d98ba9fa1df` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 89860–90270 | [25499701.35, 6674703.554, 25499711.584, 6674713.368] | [25499706.467, 6674708.461] | 111 | split (distinct content, synthesized id) | `BID_d3a96da0-69a8-432d-b550-2d98ba9fa1df__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5499708158E7 6674713.368 6.1007 2.5499711584E7 6674709.228 6.1007 2.54997047273E7 6674703.5539 6.1007 2.54997013502E7 6674707.7019 6.1007 2.5499708158E7 6674713.368 6.1007`

### `BID_d5ccde5c-bd5f-4bf1-9c36-4e27a48d9919` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 20191–20348 | [25497945.989, 6674363.635, 25497955.648, 6674373.118] | [25497950.818, 6674368.376] | 90 | kept (first occurrence) | `BID_d5ccde5c-bd5f-4bf1-9c36-4e27a48d9919` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 26845–27206 | [25497945.989, 6674363.635, 25497955.648, 6674373.118] | [25497950.818, 6674368.376] | 90 | split (distinct content, synthesized id) | `BID_d5ccde5c-bd5f-4bf1-9c36-4e27a48d9919__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5497945989E7 6674368.387 1.5939999999999999 2.5497949918E7 6674373.117999999 1.5939999999999999 2.5497955648E7 6674368.366 1.5939999999999999 2.5497951719E7 6674363.635 1.5939999999999999 2.5497945989E7 6674368.387 1.5939999999999999`

### `BID_d8fdc007-ef5f-405e-b462-1e95be5d310f` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 27207–27427 | [25497774.741, 6675259.376, 25497849.529, 6675316.093] | [25497812.135, 6675287.735] | 237 | kept (first occurrence) | `BID_d8fdc007-ef5f-405e-b462-1e95be5d310f` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 31823–32620 | [25497774.741, 6675259.376, 25497849.529, 6675316.093] | [25497812.135, 6675287.735] | 300 | split (distinct content, synthesized id) | `BID_d8fdc007-ef5f-405e-b462-1e95be5d310f__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54978421395E7 6675269.9631 10.246 2.54978048789E7 6675299.6355 10.246 2.54978016281E7 6675288.1819 10.246 2.54978130334E7 6675292.9784 10.246 2.54978190643E7 6675259.3763 10.246 2.54977747406E7 6675271.9563 10.246 2.54977801208E7 6675290.912499999 10.246 2.54977879832E7 6675288.681 10.246 2.54977957633E7 6675316.0933 10.246 2.5497820659E7 6675309.0278 10.246 2.54978495291E7 6675302.4636 10.246 2 …`

### `BID_dd9e21c0-f3bc-43b8-8d2b-6a69918e535f` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 89124–89405 | [25499624.263, 6674869.156, 25499639.95, 6674892.682] | [25499632.106, 6674880.919] | 384 | kept (first occurrence) | `BID_dd9e21c0-f3bc-43b8-8d2b-6a69918e535f` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 98358–99454 | [25499624.263, 6674869.156, 25499639.95, 6674892.682] | [25499632.106, 6674880.919] | 447 | split (distinct content, synthesized id) | `BID_dd9e21c0-f3bc-43b8-8d2b-6a69918e535f__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54996258874E7 6674881.8435 2.87 2.5499626002E7 6674884.099 2.87 2.5499625015E7 6674884.137999999 2.87 2.5499625461E7 6674892.682 2.87 2.54996321944E7 6674892.3424 2.87 2.54996319449E7 6674887.5489 2.87 2.5499639235E7 6674887.1695 2.87 2.54996390189E7 6674883.0175 2.87 2.549963995E7 6674882.969 2.87 2.5499639726E7 6674878.739999999 2.87 2.54996388095E7 6674878.7885 2.87 2.5499638610999998E7 66748 …`

### `BID_dfe55944-74c6-44b2-82ff-1820eeee2713` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 2192–2349 | [25498433.863, 6676288.975, 25498490.813, 6676331.196] | [25498462.338, 6676310.086] | 90 | kept (first occurrence) | `BID_dfe55944-74c6-44b2-82ff-1820eeee2713` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 14761–15171 | [25498433.863, 6676288.975, 25498490.813, 6676331.196] | [25498462.338, 6676310.086] | 111 | split (distinct content, synthesized id) | `BID_dfe55944-74c6-44b2-82ff-1820eeee2713__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5498482982499998E7 6676331.1959 1.5474 2.54984908126E7 6676302.2408 1.5474 2.54984416861E7 6676288.975199999 1.5474 2.54984338634E7 6676317.9103 1.5474 2.5498482982499998E7 6676331.1959 1.5474`

### `BID_e2465660-54cf-4fae-adc2-d64d5bb43c5e` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 17451–17608 | [25497951.577, 6674354.11, 25497960.746, 6674363.686] | [25497956.161, 6674358.898] | 90 | kept (first occurrence) | `BID_e2465660-54cf-4fae-adc2-d64d5bb43c5e` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 25407–25768 | [25497951.577, 6674354.11, 25497960.746, 6674363.686] | [25497956.161, 6674358.898] | 90 | split (distinct content, synthesized id) | `BID_e2465660-54cf-4fae-adc2-d64d5bb43c5e__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5497951577E7 6674360.412 1.643 2.5497956789E7 6674363.686 1.643 2.5497960746E7 6674357.384 1.643 2.5497955533999998E7 6674354.11 1.643 2.5497951577E7 6674360.412 1.643`

### `BID_ef92ed39-1569-4773-834a-f916dd4dfa6a` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 55791–56054 | [25498729.123, 6674493.787, 25498779.546, 6674548.722] | [25498754.334, 6674521.254] | 342 | kept (first occurrence) | `BID_ef92ed39-1569-4773-834a-f916dd4dfa6a` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 110146–112125 | [25498729.123, 6674493.787, 25498779.546, 6674548.722] | [25498754.334, 6674521.254] | 912 | split (distinct content, synthesized id) | `BID_ef92ed39-1569-4773-834a-f916dd4dfa6a__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54987732621E7 6674525.2036 2.44 2.54987650698E7 6674529.8681 2.44 2.54987625515E7 6674531.302 2.44 2.54987478373E7 6674509.4864 2.44 2.5498750006E7 6674508.0236 2.44 2.5498755214E7 6674504.511 2.44 2.5498747996999998E7 6674493.787 2.44 2.54987406415E7 6674498.7282 2.44 2.54987323429E7 6674504.303 2.44 2.5498729123E7 6674506.466 2.44 2.54987362428E7 6674517.022 2.44 2.5498738524399996E7 6674515.4 …`

### `BID_f180b9d7-2ea9-4471-bee9-904407794f47` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 26579–26844 | [25497342.297, 6674997.719, 25497376.354, 6675043.305] | [25497359.325, 6675020.512] | 342 | kept (first occurrence) | `BID_f180b9d7-2ea9-4471-bee9-904407794f47` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 32795–33764 | [25497342.297, 6674997.719, 25497376.354, 6675043.305] | [25497359.325, 6675020.512] | 384 | split (distinct content, synthesized id) | `BID_f180b9d7-2ea9-4471-bee9-904407794f47__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.5497342702E7 6674997.719 22.319499999999998 2.5497342297E7 6675006.345 22.319499999999998 2.5497354735999998E7 6675006.912 22.319499999999998 2.549735459E7 6675010.16 22.319499999999998 2.5497360623E7 6675010.44 22.319499999999998 2.54973607729E7 6675007.2097 22.319499999999998 2.5497367611E7 6675007.527 22.319499999999998 2.5497366351E7 6675034.368 22.319499999999998 2.5497344049E7 6675033.301  …`

### `BID_f2b6e1f2-9a20-45ee-8e84-ac1a457470ed` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 10074–10735 | [25497344.758, 6672850.738, 25497418.323, 6672905.578] | [25497381.541, 6672878.158] | 1266 | kept (first occurrence) | `BID_f2b6e1f2-9a20-45ee-8e84-ac1a457470ed` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 44443–49891 | [25497344.758, 6672850.738, 25497418.323, 6672905.578] | [25497381.541, 6672878.158] | 2319 | split (distinct content, synthesized id) | `BID_f2b6e1f2-9a20-45ee-8e84-ac1a457470ed__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54974108535E7 6672850.737999999 -11.3928 2.54974106476E7 6672855.8706 -11.3928 2.549740743E7 6672855.5986 -11.3928 2.54974074215E7 6672855.7611 -11.3928 2.54974066216E7 6672855.6595 -11.3928 2.54974060418E7 6672874.1918 -11.3928 2.54974075904E7 6672875.7033 -11.3928 2.54974071261E7 6672891.3903 -11.3928 2.54973940467E7 6672891.1112 -11.3928 2.54973946762E7 6672874.916099999 -11.3928 2.5497393469 …`

### `BID_ffbea37b-15be-4b3c-8360-6a86870afa01` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `helsinki_citygml2_lod2_2019.gml` | 75883–76040 | [25498524.464, 6675275.917, 25498564.339, 6675308.866] | [25498544.402, 6675292.391] | 90 | kept (first occurrence) | `BID_ffbea37b-15be-4b3c-8360-6a86870afa01` |
| 2 | `helsinki_citygml2_lod2_2019.gml` | 89406–89859 | [25498524.464, 6675275.917, 25498564.339, 6675308.866] | [25498544.402, 6675292.391] | 132 | split (distinct content, synthesized id) | `BID_ffbea37b-15be-4b3c-8360-6a86870afa01__helsinki_citygml2_lod2_2019_gml__1` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 2: `2.54985556818E7 6675275.9173 3.0482 2.5498524464E7 6675291.732 3.0482 2.5498533033E7 6675308.866 3.0482 2.5498564339E7 6675293.01 3.0482 2.54985556818E7 6675275.9173 3.0482`

## Zürich

- CRS: `EPSG:2056` · files scanned: 78 · building elements: 102,673 · distinct gml:ids: 102,628
- **Duplicate-id groups: 17 (62 buildings involved).**

### `ID_` — 30× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1031-44.gml` | 115127 | [2686731.68, 1280214.578, 2687836.281, 1280849.555] | [2687283.981, 1280532.066] | 14160 | kept (first occurrence) | `ID_` |
| 2 | `swissBUILDINGS3D_3-0_1032-31.gml` | 3160992–3190126 | [2690123.797, 1282120.648, 2692429.355, 1283343.336] | [2691276.576, 1282731.992] | 36108 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1032_31_gml__1` |
| 3 | `swissBUILDINGS3D_3-0_1032-33.gml` | 526–3446 | [2693471.81, 1279111.668, 2693480.702, 1279120.56] | [2693476.256, 1279116.114] | 3696 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1032_33_gml__2` |
| 4 | `swissBUILDINGS3D_3-0_1032-43.gml` | 603574–613459 | [2699597.723, 1278288.939, 2701055.318, 1278917.346] | [2700326.521, 1278603.143] | 12396 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1032_43_gml__3` |
| 5 | `swissBUILDINGS3D_3-0_1032-44.gml` | 2133–27366 | [2705850.781, 1278720.006, 2706809.203, 1279656.969] | [2706329.992, 1279188.488] | 30864 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1032_44_gml__4` |
| 6 | `swissBUILDINGS3D_3-0_1032-44.gml` | 3817057–3817059 | — | None | 0 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1032_44_gml__5` |
| 7 | `swissBUILDINGS3D_3-0_1051-41.gml` | 1374017–1377884 | [2682447.069, 1269893.754, 2683117.105, 1270610.672] | [2682782.087, 1270252.213] | 4632 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1051_41_gml__6` |
| 8 | `swissBUILDINGS3D_3-0_1052-23.gml` | 1444–3144 | [2701783.811, 1273300.113, 2702192.357, 1273371.919] | [2701988.084, 1273336.016] | 2016 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1052_23_gml__7` |
| 9 | `swissBUILDINGS3D_3-0_1052-23.gml` | 758636–759754 | [2701785.01, 1273339.471, 2701836.778, 1273370.721] | [2701810.894, 1273355.096] | 1416 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1052_23_gml__8` |
| 10 | `swissBUILDINGS3D_3-0_1052-42.gml` | 1056551–1063153 | [2705210.854, 1269215.637, 2705395.25, 1269502.737] | [2705303.052, 1269359.187] | 8544 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1052_42_gml__9` |
| 11 | `swissBUILDINGS3D_3-0_1052-44.gml` | 1494101–1496798 | [2704834.819, 1267197.973, 2704919.925, 1267500.771] | [2704877.372, 1267349.372] | 3204 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1052_44_gml__10` |
| 12 | `swissBUILDINGS3D_3-0_1070-22.gml` | 900651–921650 | [2668295.261, 1263025.74, 2670919.027, 1265518.773] | [2669607.144, 1264272.257] | 25788 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1070_22_gml__11` |
| 13 | `swissBUILDINGS3D_3-0_1070-24.gml` | 1306313–2079235 | [2668116.769, 1260039.073, 2670525.441, 1263015.109] | [2669321.105, 1261527.091] | 950772 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1070_24_gml__12` |
| 14 | `swissBUILDINGS3D_3-0_1070-42.gml` | 123739–270526 | [2668118.07, 1257068.286, 2669990.691, 1259430.085] | [2669054.38, 1258249.186] | 183612 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1070_42_gml__13` |
| 15 | `swissBUILDINGS3D_3-0_1070-44.gml` | 4530–633924 | [2668200.944, 1253990.883, 2670946.598, 1257004.692] | [2669573.771, 1255497.788] | 772164 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1070_44_gml__14` |
| 16 | `swissBUILDINGS3D_3-0_1070-44.gml` | 3580974–3580976 | — | None | 0 | deduped (identical content) | `ID___swissbuildings3d_3_0_1032_44_gml__5` |
| 17 | `swissBUILDINGS3D_3-0_1073-13.gml` | 2684923–2690756 | [2709735.867, 1262497.033, 2709856.728, 1262589.709] | [2709796.298, 1262543.371] | 7320 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1073_13_gml__15` |
| 18 | `swissBUILDINGS3D_3-0_1090-22.gml` | 2103352–2106471 | [2671371.706, 1252163.17, 2671503.888, 1252264.436] | [2671437.797, 1252213.803] | 3900 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1090_22_gml__16` |
| 19 | `swissBUILDINGS3D_3-0_1090-42.gml` | 4541000–4543687 | [2672469.426, 1247582.549, 2672517.273, 1247630.143] | [2672493.35, 1247606.346] | 3324 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1090_42_gml__17` |
| 20 | `swissBUILDINGS3D_3-0_1091-14.gml` | 10–57796 | [2677359.832, 1249342.645, 2678027.16, 1250408.467] | [2677693.496, 1249875.556] | 76092 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1091_14_gml__18` |
| 21 | `swissBUILDINGS3D_3-0_1091-14.gml` | 11942536–11942538 | — | None | 0 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1091_14_gml__19` |
| 22 | `swissBUILDINGS3D_3-0_1091-21.gml` | 21676–90436 | [2684224.444, 1252280.922, 2684894.563, 1253907.229] | [2684559.504, 1253094.076] | 89532 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1091_21_gml__20` |
| 23 | `swissBUILDINGS3D_3-0_1091-21.gml` | 11848272–11848274 | — | None | 0 | deduped (identical content) | `ID___swissbuildings3d_3_0_1091_14_gml__19` |
| 24 | `swissBUILDINGS3D_3-0_1091-22.gml` | 873370–881795 | [2685642.418, 1251155.402, 2687459.82, 1251953.44] | [2686551.119, 1251554.421] | 10908 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1091_22_gml__21` |
| 25 | `swissBUILDINGS3D_3-0_1091-24.gml` | 1594812–1606460 | [2686739.894, 1248585.333, 2687080.363, 1249894.218] | [2686910.128, 1249239.775] | 14160 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1091_24_gml__22` |
| 26 | `swissBUILDINGS3D_3-0_1091-43.gml` | 5151473–5209156 | [2682951.0, 1242704.664, 2685512.15, 1244695.61] | [2684231.575, 1243700.137] | 72420 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1091_43_gml__23` |
| 27 | `swissBUILDINGS3D_3-0_1091-44.gml` | 9912–17653 | [2685630.719, 1244625.768, 2685912.875, 1244763.034] | [2685771.797, 1244694.401] | 9996 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1091_44_gml__24` |
| 28 | `swissBUILDINGS3D_3-0_1093-11.gml` | 47693 | [2711119.498, 1251051.664, 2711189.514, 1253840.829] | [2711154.506, 1252446.246] | 5724 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1093_11_gml__25` |
| 29 | `swissBUILDINGS3D_3-0_1111-13.gml` | 90946–93165 | [2673776.617, 1238478.213, 2673810.5, 1238508.627] | [2673793.559, 1238493.42] | 2700 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1111_13_gml__26` |
| 30 | `swissBUILDINGS3D_3-0_1111-21.gml` | 10–1716 | [2681611.617, 1241961.429, 2681622.68, 1241973.753] | [2681617.149, 1241967.591] | 2016 | split (distinct content, synthesized id) | `ID___swissbuildings3d_3_0_1111_21_gml__27` |

Footprint exterior ring(s) (`gml:posList`, native CRS):

- occ. 1: `2687822.1953000017 1280831.0390999988 380.6889999999985 2687817.468800001 1280835.1640999988 380.6889999999985 2687817.3125 1280834.7655999996 380.6889999999985 2687822.1953000017 1280831.0390999988 380.6889999999985`
- occ. 2: `2692424.6171999983 1282125.8515999988 415.7149999999965 2692425.4219000004 1282120.6484000012 415.7149999999965 2692427.3905999996 1282124.4063000008 415.7149999999965 2692424.6171999983 1282125.8515999988 415.7149999999965`
- occ. 3: `2693480.7021999992 1279117.3940000013 546.2029999999941 2693474.9761000015 1279120.5601000004 546.2029999999941 2693472.206099998 1279118.3520999998 546.2029999999941 2693480.7021999992 1279117.3940000013 546.2029999999941`
- occ. 4: `2700950.0771999992 1278814.1440999992 418.58000000000175 2700947.0190000013 1278818.1521000005 418.58000000000175 2700934.3110000007 1278808.481899999 418.58000000000175 2700950.0771999992 1278814.1440999992 418.58000000000175`
- occ. 5: `2706064.6875 1279358.8046999983 407.84500000000116 2706062.0155999996 1279362.9296999983 407.84500000000116 2706056.7030999996 1279361.5546999983 407.84500000000116 2706064.6875 1279358.8046999983 407.84500000000116`
- occ. 7: `2682474.525899999 1270596.486299999 461.44899999999325 2682466.178199999 1270601.128899999 461.44899999999325 2682464.746100001 1270598.5546999983 461.44899999999325 2682474.525899999 1270596.486299999 461.44899999999325`
- occ. 8: `2701825.7820000015 1273350.2490000017 497.29899999999907 2701816.8779000007 1273355.9648000002 497.29899999999907 2701814.1799000017 1273344.2314000018 497.29899999999907 2701825.7820000015 1273350.2490000017 497.29899999999907`
- occ. 10: `2705382.835999999 1269272.0234000012 377.4279999999999 2705340.289999999 1269271.3574 377.4279999999999 2705367.7699999996 1269256.7509999983 377.4279999999999 2705382.835999999 1269272.0234000012 377.4279999999999`
- occ. 11: `2704909.8110000007 1267207.5478999987 423.57300000000396 2704908.8310000002 1267210.450199999 423.57300000000396 2704906.1510000005 1267206.4521999992 423.57300000000396 2704909.8110000007 1267207.5478999987 423.57300000000396`
- occ. 12: `2668311.7655999996 1264713.2529999986 556.0638000000035 2668312.0507999994 1264708.6070000008 556.0638000000035 2668316.4921999983 1264709.9990000017 556.0638000000035 2668311.7655999996 1264713.2529999986 556.0638000000035`
- occ. 13: `2668463.156300001 1261554.9309 439.55740000000515 2668458.601599999 1261559.6909000017 439.55740000000515 2668455.4023 1261550.7870999984 439.55740000000515 2668463.156300001 1261554.9309 439.55740000000515`
- occ. 14: `2668243.253899999 1257865.0190000013 427.4180000000051 2668242.960900001 1257867.2949 427.4180000000051 2668236.7655999996 1257864.5029000007 427.4180000000051 2668243.253899999 1257865.0190000013 427.4180000000051`
- occ. 15: `2668955.3867000006 1254361.7188000008 388.99520000000484 2668955.3594000004 1254364.1992000006 388.99520000000484 2668951.5625 1254363.8427999988 388.99520000000484 2668955.3867000006 1254361.7188000008 388.99520000000484`
- occ. 17: `2709826.4375 1262580.1094000004 498.3231999999989 2709826.0898 1262581.1532999985 498.3231999999989 2709817.539099999 1262578.3007999994 498.3231999999989 2709826.4375 1262580.1094000004 498.3231999999989`
- occ. 18: `2671374.7969000004 1252249.5683999993 386.1113000000041 2671404.5117000006 1252229.0898000002 386.1113000000041 2671414.683600001 1252233.0439000018 386.1113000000041 2671374.7969000004 1252249.5683999993 386.1113000000041`
- occ. 19: `2672496.9453000017 1247615.1563000008 439.320000000007 2672486.5742000006 1247619.246100001 439.320000000007 2672486.4257999994 1247619.0742000006 439.320000000007 2672496.9453000017 1247615.1563000008 439.320000000007`
- occ. 20: `2677777.7305000015 1249827.9037999995 396.4149999999936 2677771.218800001 1249831.9761000015 396.4149999999936 2677768.8671999983 1249830.7041000016 396.4149999999936 2677777.7305000015 1249827.9037999995 396.4149999999936`
- occ. 22: `2684330.8828000017 1253617.9433999993 433.99899999999616 2684323.8867000006 1253624.5009999983 433.99899999999616 2684323.4296999983 1253623.9345999993 433.99899999999616 2684330.8828000017 1253617.9433999993 433.99899999999616`
- occ. 24: `2685647.6444999985 1251882.4023000002 422.72299999999814 2685648.378899999 1251881.1816000007 422.72299999999814 2685651.8944999985 1251889.7694999985 422.72299999999814 2685647.6444999985 1251882.4023000002 422.72299999999814`
- occ. 25: `2687071.0780999996 1248592.8861999996 596.0460000000021 2687067.2069999985 1248596.945799999 596.0460000000021 2687064.281300001 1248594.1601999998 596.0460000000021 2687071.0780999996 1248592.8861999996 596.0460000000021`
- occ. 26: `2685461.023400001 1244693.6350000016 459.74099999999453 2685460.2617000006 1244694.9090999998 459.74099999999453 2685459.0898 1244694.2069999985 459.74099999999453 2685461.023400001 1244693.6350000016 459.74099999999453`
- occ. 27: `2685670.1444999985 1244663.4019999988 457.4799999999959 2685674.7969000004 1244639.886 457.4799999999959 2685681.7421999983 1244643.0020000003 457.4799999999959 2685670.1444999985 1244663.4019999988 457.4799999999959`
- occ. 28: `2711139.158 1251068.7080000006 664.6790000000037 2711143.0480000004 1251061.3900000006 664.6790000000037 2711147.403999999 1251069.539999999 664.6790000000037 2711139.158 1251068.7080000006 664.6790000000037`
- occ. 29: `2673802.7773 1238495.298799999 457.93619999999646 2673804.7344000004 1238492.128899999 457.93610000000626 2673809.8125 1238495.2655999996 457.93619999999646 2673802.7773 1238495.298799999 457.93619999999646`
- occ. 30: `2681619.0977 1241962.927000001 437.14890000000014 2681616.333999999 1241964.511 437.14890000000014 2681615.5176 1241961.4310000017 437.14890000000014 2681619.0977 1241962.927000001 437.14890000000014`

### `ID_10C4883F-6AA1-46A2-B57E-A3606C4D35C1` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-23.gml` | 2989–3280 | [2681967.012, 1248434.659, 2681986.09, 1248440.76] | [2681976.551, 1248437.709] | 204 | kept (first occurrence) | `ID_10C4883F-6AA1-46A2-B57E-A3606C4D35C1` |
| 2 | `swissBUILDINGS3D_3-0_1091-23.gml` | 7530489–7530714 | [2681967.01, 1248434.659, 2681986.091, 1248440.76] | [2681976.55, 1248437.709] | 216 | split (distinct content, synthesized id) | `ID_10C4883F-6AA1-46A2-B57E-A3606C4D35C1__swissbuildings3d_3_0_1091_23_gml__1` |

### `ID_20ED8585-33A8-480E-9D89-D50D877AC2CC` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-32.gml` | 10–256 | [2681196.883, 1247162.382, 2681210.438, 1247167.613] | [2681203.661, 1247164.998] | 144 | kept (first occurrence) | `ID_20ED8585-33A8-480E-9D89-D50D877AC2CC` |
| 2 | `swissBUILDINGS3D_3-0_1091-32.gml` | 636443–636614 | [2681196.881, 1247162.382, 2681210.438, 1247167.613] | [2681203.66, 1247164.998] | 144 | split (distinct content, synthesized id) | `ID_20ED8585-33A8-480E-9D89-D50D877AC2CC__swissbuildings3d_3_0_1091_32_gml__1` |

### `ID_31D38AE0-05D9-4EC6-B4AD-2C1098BAD104` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-42.gml` | 10–256 | [2685799.467, 1245440.581, 2685825.746, 1245464.946] | [2685812.606, 1245452.763] | 144 | kept (first occurrence) | `ID_31D38AE0-05D9-4EC6-B4AD-2C1098BAD104` |
| 2 | `swissBUILDINGS3D_3-0_1091-42.gml` | 707949–708120 | [2685799.467, 1245440.581, 2685825.746, 1245464.946] | [2685812.606, 1245452.763] | 144 | split (distinct content, synthesized id) | `ID_31D38AE0-05D9-4EC6-B4AD-2C1098BAD104__swissbuildings3d_3_0_1091_42_gml__1` |

### `ID_3D611D32-10B0-499D-8D16-72410663C77E` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-21.gml` | 520–5853 | [2683473.758, 1252581.985, 2683486.449, 1252594.676] | [2683480.104, 1252588.331] | 6864 | kept (first occurrence) | `ID_3D611D32-10B0-499D-8D16-72410663C77E` |
| 2 | `swissBUILDINGS3D_3-0_1091-21.gml` | 2002772–2008541 | [2683474.654, 1252582.786, 2683485.681, 1252593.808] | [2683480.167, 1252588.297] | 7608 | split (distinct content, synthesized id) | `ID_3D611D32-10B0-499D-8D16-72410663C77E__swissbuildings3d_3_0_1091_21_gml__1` |

### `ID_40C30522-294B-4CA2-A969-C75EFBCB5FF8` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-43.gml` | 666–1366 | [2684823.289, 1244950.676, 2684857.617, 1244998.633] | [2684840.453, 1244974.654] | 624 | kept (first occurrence) | `ID_40C30522-294B-4CA2-A969-C75EFBCB5FF8` |
| 2 | `swissBUILDINGS3D_3-0_1091-43.gml` | 278738–279269 | [2684823.291, 1244950.676, 2684857.616, 1244998.633] | [2684840.453, 1244974.654] | 624 | split (distinct content, synthesized id) | `ID_40C30522-294B-4CA2-A969-C75EFBCB5FF8__swissbuildings3d_3_0_1091_43_gml__1` |

### `ID_41A37A14-98BA-44F0-8EBA-32827920A2AC` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1113-32.gml` | 2408–2654 | [2715099.338, 1235903.92, 2715110.368, 1235912.966] | [2715104.853, 1235908.443] | 144 | kept (first occurrence) | `ID_41A37A14-98BA-44F0-8EBA-32827920A2AC` |
| 2 | `swissBUILDINGS3D_3-0_1113-32.gml` | 117923–118094 | [2715099.338, 1235903.92, 2715110.368, 1235912.966] | [2715104.853, 1235908.443] | 144 | split (distinct content, synthesized id) | `ID_41A37A14-98BA-44F0-8EBA-32827920A2AC__swissbuildings3d_3_0_1113_32_gml__1` |

### `ID_439025FC-01EF-41E1-8CBA-146AE90776EF` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-41.gml` | 10–292 | [2681824.734, 1247278.958, 2681844.785, 1247299.1] | [2681834.76, 1247289.029] | 192 | kept (first occurrence) | `ID_439025FC-01EF-41E1-8CBA-146AE90776EF` |
| 2 | `swissBUILDINGS3D_3-0_1091-41.gml` | 8354897–8355104 | [2681824.735, 1247278.958, 2681844.786, 1247299.1] | [2681834.76, 1247289.029] | 192 | split (distinct content, synthesized id) | `ID_439025FC-01EF-41E1-8CBA-146AE90776EF__swissbuildings3d_3_0_1091_41_gml__1` |

### `ID_47EBD6FB-4383-489E-B91A-8E686DBA3D72` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-43.gml` | 10–418 | [2681638.734, 1243046.938, 2681660.809, 1243073.892] | [2681649.771, 1243060.415] | 360 | kept (first occurrence) | `ID_47EBD6FB-4383-489E-B91A-8E686DBA3D72` |
| 2 | `swissBUILDINGS3D_3-0_1091-43.gml` | 477476–477791 | [2681638.733, 1243046.938, 2681660.81, 1243073.892] | [2681649.771, 1243060.415] | 336 | split (distinct content, synthesized id) | `ID_47EBD6FB-4383-489E-B91A-8E686DBA3D72__swissbuildings3d_3_0_1091_43_gml__1` |

### `ID_5CC367CE-DD0D-4058-B71C-49CF9481050B` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-23.gml` | 10–1410 | [2681337.934, 1248789.579, 2681440.797, 1248869.66] | [2681389.365, 1248829.62] | 1152 | kept (first occurrence) | `ID_5CC367CE-DD0D-4058-B71C-49CF9481050B` |
| 2 | `swissBUILDINGS3D_3-0_1091-23.gml` | 24466089–24466095 | — | None | 0 | split (distinct content, synthesized id) | `ID_5CC367CE-DD0D-4058-B71C-49CF9481050B__swissbuildings3d_3_0_1091_23_gml__1` |

### `ID_63FD7DE4-9F2D-4DF0-BD87-86760470B43D` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-23.gml` | 1411–2988 | [2681415.277, 1248771.639, 2681545.312, 1248834.184] | [2681480.294, 1248802.911] | 1668 | kept (first occurrence) | `ID_63FD7DE4-9F2D-4DF0-BD87-86760470B43D` |
| 2 | `swissBUILDINGS3D_3-0_1091-23.gml` | 10038627–10039698 | [2681415.276, 1248771.639, 2681545.311, 1248834.184] | [2681480.294, 1248802.911] | 1344 | split (distinct content, synthesized id) | `ID_63FD7DE4-9F2D-4DF0-BD87-86760470B43D__swissbuildings3d_3_0_1091_23_gml__1` |

### `ID_6C000625-236B-4567-B69F-AFF202B85F5A` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-12.gml` | 10–814 | [2680066.68, 1252659.306, 2680076.887, 1252668.306] | [2680071.783, 1252663.806] | 888 | kept (first occurrence) | `ID_6C000625-236B-4567-B69F-AFF202B85F5A` |
| 2 | `swissBUILDINGS3D_3-0_1091-12.gml` | 3615632–3616361 | [2680066.681, 1252659.306, 2680076.885, 1252668.306] | [2680071.783, 1252663.806] | 888 | split (distinct content, synthesized id) | `ID_6C000625-236B-4567-B69F-AFF202B85F5A__swissbuildings3d_3_0_1091_12_gml__1` |

### `ID_7004B7EE-A83E-4353-B52C-6852D8532D50` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-21.gml` | 10–519 | [2683311.246, 1251780.999, 2683553.762, 1251920.924] | [2683432.504, 1251850.962] | 432 | kept (first occurrence) | `ID_7004B7EE-A83E-4353-B52C-6852D8532D50` |
| 2 | `swissBUILDINGS3D_3-0_1091-21.gml` | 8049712–8049883 | [2683311.245, 1251793.264, 2683368.593, 1251830.317] | [2683339.919, 1251811.791] | 144 | split (distinct content, synthesized id) | `ID_7004B7EE-A83E-4353-B52C-6852D8532D50__swissbuildings3d_3_0_1091_21_gml__1` |

### `ID_841EC70E-E57C-4EBE-BBEB-9A60DAC84280` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1112-44.gml` | 13070–14164 | [2704071.012, 1231634.155, 2704131.937, 1231668.541] | [2704101.475, 1231651.348] | 1212 | kept (first occurrence) | `ID_841EC70E-E57C-4EBE-BBEB-9A60DAC84280` |
| 2 | `swissBUILDINGS3D_3-0_1112-44.gml` | 2079075–2080002 | [2704071.012, 1231634.789, 2704131.295, 1231668.541] | [2704101.154, 1231651.665] | 1152 | split (distinct content, synthesized id) | `ID_841EC70E-E57C-4EBE-BBEB-9A60DAC84280__swissbuildings3d_3_0_1112_44_gml__1` |

### `ID_B1582C1E-97E7-4E23-B46C-F989926EE5BF` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-43.gml` | 1367–1613 | [2684907.75, 1244801.565, 2684935.445, 1244831.885] | [2684921.598, 1244816.725] | 144 | kept (first occurrence) | `ID_B1582C1E-97E7-4E23-B46C-F989926EE5BF` |
| 2 | `swissBUILDINGS3D_3-0_1091-43.gml` | 3004170–3004341 | [2684907.751, 1244801.565, 2684935.445, 1244831.885] | [2684921.598, 1244816.725] | 144 | split (distinct content, synthesized id) | `ID_B1582C1E-97E7-4E23-B46C-F989926EE5BF__swissbuildings3d_3_0_1091_43_gml__1` |

### `ID_C92E0E5F-9FE8-4F8E-90BF-82E117071CDD` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-43.gml` | 419–665 | [2683294.844, 1243297.579, 2683310.688, 1243313.596] | [2683302.766, 1243305.587] | 144 | kept (first occurrence) | `ID_C92E0E5F-9FE8-4F8E-90BF-82E117071CDD` |
| 2 | `swissBUILDINGS3D_3-0_1091-43.gml` | 3961518–3961689 | [2683294.844, 1243297.579, 2683310.686, 1243313.596] | [2683302.765, 1243305.587] | 144 | split (distinct content, synthesized id) | `ID_C92E0E5F-9FE8-4F8E-90BF-82E117071CDD__swissbuildings3d_3_0_1091_43_gml__1` |

### `ID_DF116B92-BDEC-40BA-95A0-15ADFFDEC6D3` — 2× — distinct geometry -> split

| # | source file | lines | bbox (native CRS) | centroid | verts | disposition | resulting node id |
|---|---|---|---|---|---|---|---|
| 1 | `swissBUILDINGS3D_3-0_1091-41.gml` | 293–539 | [2681612.594, 1247145.713, 2681628.656, 1247154.272] | [2681620.625, 1247149.993] | 144 | kept (first occurrence) | `ID_DF116B92-BDEC-40BA-95A0-15ADFFDEC6D3` |
| 2 | `swissBUILDINGS3D_3-0_1091-41.gml` | 18853465–18853636 | [2681612.949, 1247145.726, 2681628.584, 1247154.045] | [2681620.766, 1247149.885] | 144 | split (distinct content, synthesized id) | `ID_DF116B92-BDEC-40BA-95A0-15ADFFDEC6D3__swissbuildings3d_3_0_1091_41_gml__1` |

## Tokyo (PLATEAU)

- CRS: `EPSG:6697` · building tile files: 980 · unique mesh-tile files: 692 · **redundant (duplicate) files: 288**.

Tokyo's duplication is not per-building but per-file: PLATEAU packages each ward
separately, so a mesh tile straddling a ward boundary is shipped as a copy in every
adjacent ward's package. Of the 240 shared mesh tiles, **177 are byte-identical**
across their wards and **63 differ** — but in the differing case the difference is
confined to the PLATEAU `uro:*` ADE data-quality metadata
(`uro:thematicSrcDesc`, `uro:geometrySrcDescLod3`, etc.), which is ward-specific;
the building **geometry is identical** across ward copies (verified: 100 % of shared
buildings in the sampled differing tiles have an identical `gml:posList` geometry
hash). The two-tier resolution therefore collapses both: byte-identical copies
deduplicate on the content hash, and geometry-identical-but-metadata-differing copies
deduplicate on the geometry signature (coordinate-identical geometry), so each real
building becomes exactly one node with no phantom split. Ward-span distribution (mesh tiles appearing in N wards): {2: 196,
3: 40, 4: 4}. The table below marks which mesh tiles are byte-identical (`True`) and
which differ only in ADE metadata (`False`).

| mesh-tile file | appears in wards | #wards | byte-identical | md5 | lines |
|---|---|---|---|---|---|
| `53393508_bldg_6697_op.gml` | ota, shinagawa | 2 | True | `f3ed1f78a12aed19…` | 1,035,284 |
| `53393509_bldg_6697_op.gml` | ota, shinagawa | 2 | True | `7a6272cb40bfaa7d…` | 65,878 |
| `53393512_bldg_6697_op.gml` | ota, setagaya | 2 | True | `e7b31cc0e741aec6…` | 678,412 |
| `53393513_bldg_6697_op.gml` | ota, setagaya | 2 | True | `99d03afc830d825f…` | 816,679 |
| `53393514_bldg_6697_op.gml` | ota, setagaya | 2 | True | `7f7e89125daa282a…` | 1,027,617 |
| `53393517_bldg_6697_op.gml` | ota, shinagawa | 2 | True | `81e017ea0dc1272f…` | 1,299,389 |
| `53393518_bldg_6697_op.gml` | ota, shinagawa | 2 | True | `603c10e77cdd9d84…` | 1,106,437 |
| `53393523_bldg_6697_op.gml` | meguro, setagaya | 2 | True | `6e7a2384cfa2450f…` | 1,023,592 |
| `53393524_bldg_6697_op.gml` | meguro, ota, setagaya | 3 | True | `c8a2f3820e2dabd8…` | 975,789 |
| `53393525_bldg_6697_op.gml` | meguro, ota, shinagawa | 3 | True | `53ec8c2919aedc5b…` | 972,582 |
| `53393526_bldg_6697_op.gml` | ota, shinagawa | 2 | True | `c0f75b0ac2dc4fc4…` | 1,296,103 |
| `53393527_bldg_6697_op.gml` | ota, shinagawa | 2 | True | `3d8d772a0f71e27e…` | 1,339,564 |
| `53393533_bldg_6697_op.gml` | meguro, setagaya | 2 | True | `6bda5a595dea3a72…` | 973,574 |
| `53393534_bldg_6697_op.gml` | meguro, ota, setagaya | 3 | True | `fb696afffd73f272…` | 1,136,423 |
| `53393535_bldg_6697_op.gml` | meguro, ota, shinagawa | 3 | True | `4bbadbe412083378…` | 1,157,543 |
| `53393543_bldg_6697_op.gml` | meguro, setagaya | 2 | True | `6b03b8418c08859b…` | 795,715 |
| `53393545_bldg_6697_op.gml` | meguro, shinagawa | 2 | True | `9a6dd441acc7ec9b…` | 1,240,397 |
| `53393546_bldg_6697_op.gml` | meguro, shinagawa | 2 | True | `cc7b0a9509c033b6…` | 1,266,780 |
| `53393548_bldg_6697_op.gml` | minato, shinagawa | 2 | False | `DIFFERS: 211e167…` | 1,259,023 |
| `53393549_bldg_6697_op.gml` | minato, shinagawa | 2 | False | `DIFFERS: a01ea48…` | 733,642 |
| `53393552_bldg_6697_op.gml` | meguro, setagaya | 2 | True | `d8b0d56fd1d91592…` | 729,103 |
| `53393553_bldg_6697_op.gml` | meguro, setagaya | 2 | True | `19c153742ccd42c3…` | 868,628 |
| `53393554_bldg_6697_op.gml` | meguro, setagaya | 2 | True | `caf3725d8f74de87…` | 1,010,820 |
| `53393555_bldg_6697_op.gml` | meguro, shinagawa | 2 | True | `2773b006c1c2faf3…` | 1,019,497 |
| `53393556_bldg_6697_op.gml` | meguro, shinagawa | 2 | True | `ca61b7b153978e43…` | 966,916 |
| `53393557_bldg_6697_op.gml` | meguro, shinagawa | 2 | True | `fdd6bd3d87b92a1e…` | 682,751 |
| `53393558_bldg_6697_op.gml` | minato, shinagawa | 2 | False | `DIFFERS: 135dd31…` | 1,186,616 |
| `53393564_bldg_6697_op.gml` | meguro, setagaya | 2 | True | `51feb08c1dfafdb3…` | 1,099,346 |
| `53393567_bldg_6697_op.gml` | meguro, minato, shibuya, shinagawa | 4 | False | `DIFFERS: 06041df…` | 560,062 |
| `53393568_bldg_6697_op.gml` | minato, shinagawa | 2 | False | `DIFFERS: c838817…` | 1,395,360 |
| `53393574_bldg_6697_op.gml` | meguro, setagaya | 2 | True | `247347ee89f7fd37…` | 564,977 |
| `53393575_bldg_6697_op.gml` | meguro, shibuya | 2 | True | `e57b682c6776a26d…` | 1,037,110 |
| `53393576_bldg_6697_op.gml` | meguro, shibuya | 2 | True | `b55939787cc12a22…` | 761,077 |
| `53393577_bldg_6697_op.gml` | meguro, minato, shibuya | 3 | False | `DIFFERS: c6cf3b8…` | 979,203 |
| `53393584_bldg_6697_op.gml` | meguro, setagaya | 2 | True | `93ac3e4708516953…` | 748,887 |
| `53393585_bldg_6697_op.gml` | meguro, shibuya | 2 | True | `facfa13dd6f24996…` | 1,616,226 |
| `53393587_bldg_6697_op.gml` | minato, shibuya | 2 | False | `DIFFERS: 357e339…` | 579,636 |
| `53393590_bldg_6697_op.gml` | setagaya, suginami | 2 | True | `8887a11ea48f32a8…` | 874,269 |
| `53393591_bldg_6697_op.gml` | setagaya, suginami | 2 | True | `4c2070319daf8120…` | 1,230,453 |
| `53393593_bldg_6697_op.gml` | setagaya, shibuya | 2 | True | `f495e2cce313b0c6…` | 1,323,014 |
| `53393594_bldg_6697_op.gml` | meguro, setagaya, shibuya | 3 | True | `151c89fff481cef6…` | 609,805 |
| `53393595_bldg_6697_op.gml` | meguro, shibuya | 2 | True | `416215eeea3c080c…` | 1,503,528 |
| `53393596_bldg_6697_op.gml` | minato, shibuya | 2 | False | `DIFFERS: 05f947e…` | 1,760,123 |
| `53393597_bldg_6697_op.gml` | minato, shibuya | 2 | False | `DIFFERS: 7846be9…` | 535,644 |
| `53393600_bldg_6697_op.gml` | ota, shinagawa | 2 | True | `205c714edf8b64bc…` | 36,886 |
| `53393601_bldg_6697_op.gml` | ota, shinagawa | 2 | True | `05807da21787ad63…` | 44,314 |
| `53393611_bldg_6697_op.gml` | ota, shinagawa | 2 | True | `4baba5b1f9a95354…` | 40,371 |
| `53393613_bldg_6697_op.gml` | koto, ota | 2 | True | `d6169449a0de2f79…` | 14,845 |
| `53393614_bldg_6697_op.gml` | koto, ota | 2 | True | `d2039a4bc76e2f17…` | 10,314 |
| `53393640_bldg_6697_op.gml` | minato, shinagawa | 2 | False | `DIFFERS: 4a0dc5b…` | 91,521 |
| `53393641_bldg_6697_op.gml` | koto, minato, shinagawa | 3 | False | `DIFFERS: a4b18a8…` | 160,536 |
| `53393650_bldg_6697_op.gml` | minato, shinagawa | 2 | False | `DIFFERS: 783644d…` | 99,281 |
| `53393651_bldg_6697_op.gml` | minato, shinagawa | 2 | False | `DIFFERS: 4bab7a1…` | 367,689 |
| `53393652_bldg_6697_op.gml` | koto, minato | 2 | False | `DIFFERS: 21f7ad6…` | 552,740 |
| `53393662_bldg_6697_op.gml` | koto, minato | 2 | False | `DIFFERS: b9d4769…` | 186,656 |
| `53393672_bldg_6697_op.gml` | chuo, koto | 2 | False | `DIFFERS: 8485c23…` | 286,226 |
| `53393680_bldg_6697_op.gml` | chuo, minato | 2 | True | `74d6b993ef4c8fd9…` | 1,523,009 |
| `53393681_bldg_6697_op.gml` | chuo, minato | 2 | True | `0ac20012110becef…` | 464,540 |
| `53393683_bldg_6697_op.gml` | chuo, koto | 2 | False | `DIFFERS: 6aa7d03…` | 683,529 |
| `53393690_bldg_6697_op.gml` | chuo, minato | 2 | True | `e38d4de3b02f073c…` | 3,495,002 |
| `53393691_bldg_6697_op.gml` | chuo, minato | 2 | True | `3c7369aa94110275…` | 1,190,516 |
| `53393693_bldg_6697_op.gml` | chuo, koto | 2 | False | `DIFFERS: 4c7815a…` | 253,903 |
| `53394408_bldg_6697_op.gml` | setagaya, suginami | 2 | True | `70651e48bbd86b3f…` | 986,528 |
| `53394409_bldg_6697_op.gml` | setagaya, suginami | 2 | True | `fd47e2ce6670be50…` | 798,519 |
| `53394417_bldg_6697_op.gml` | setagaya, suginami | 2 | True | `da2a61626da2b44c…` | 687,047 |
| `53394418_bldg_6697_op.gml` | setagaya, suginami | 2 | True | `fc2a11fe2d3e58b0…` | 782,125 |
| `53394419_bldg_6697_op.gml` | setagaya, suginami | 2 | True | `a96ebc9d302d3065…` | 775,208 |
| `53394456_bldg_6697_op.gml` | nerima, suginami | 2 | True | `5697995230cc384e…` | 1,063,222 |
| `53394466_bldg_6697_op.gml` | nerima, suginami | 2 | True | `8a5cdb9f250288df…` | 949,358 |
| `53394467_bldg_6697_op.gml` | nerima, suginami | 2 | True | `7a2910470db8b894…` | 919,357 |
| `53394478_bldg_6697_op.gml` | nerima, suginami | 2 | True | `8c647f4f530110b3…` | 971,555 |
| `53394479_bldg_6697_op.gml` | nakano, nerima, suginami | 3 | True | `279f579a159f76fd…` | 862,680 |
| `53394500_bldg_6697_op.gml` | setagaya, suginami | 2 | True | `5384c20d73254ea6…` | 997,032 |
| `53394501_bldg_6697_op.gml` | setagaya, suginami | 2 | True | `ffefb055b210ffac…` | 860,213 |
| `53394502_bldg_6697_op.gml` | setagaya, shibuya, suginami | 3 | True | `aeb233469ea3f412…` | 1,161,547 |
| `53394503_bldg_6697_op.gml` | setagaya, shibuya | 2 | True | `ba0c30199900af60…` | 1,093,430 |
| `53394506_bldg_6697_op.gml` | minato, shibuya | 2 | False | `DIFFERS: 7bd9d6e…` | 572,637 |
| `53394507_bldg_6697_op.gml` | minato, shibuya, shinjuku | 3 | False | `DIFFERS: a115b8b…` | 643,934 |
| `53394509_bldg_6697_op.gml` | chiyoda, minato | 2 | True | `a2af5a4676713d57…` | 2,062,268 |
| `53394512_bldg_6697_op.gml` | nakano, shibuya, suginami | 3 | True | `3d827728207eacc9…` | 1,238,313 |
| `53394513_bldg_6697_op.gml` | nakano, shibuya, suginami | 3 | True | `8494b2de6fb1c61f…` | 1,267,882 |
| `53394515_bldg_6697_op.gml` | shibuya, shinjuku | 2 | True | `d26eefc768aa8419…` | 570,385 |
| `53394517_bldg_6697_op.gml` | minato, shibuya, shinjuku | 3 | False | `DIFFERS: 65ecc3f…` | 395,779 |
| `53394518_bldg_6697_op.gml` | chiyoda, minato, shinjuku | 3 | False | `DIFFERS: 70f877c…` | 527,930 |
| `53394519_bldg_6697_op.gml` | chiyoda, minato | 2 | True | `ac43b6660879a857…` | 196,573 |
| `53394522_bldg_6697_op.gml` | nakano, suginami | 2 | True | `bc3a1544099bfe6d…` | 911,973 |
| `53394523_bldg_6697_op.gml` | nakano, shibuya, suginami | 3 | True | `b69e970d699fccc2…` | 967,711 |
| `53394524_bldg_6697_op.gml` | nakano, shibuya, shinjuku | 3 | True | `d0d3b4e6a36d540b…` | 1,338,649 |
| `53394525_bldg_6697_op.gml` | shibuya, shinjuku | 2 | True | `a79998f7aa4a7b62…` | 1,622,317 |
| `53394526_bldg_6697_op.gml` | shibuya, shinjuku | 2 | True | `d1528a150e20c677…` | 1,077,882 |
| `53394528_bldg_6697_op.gml` | chiyoda, shinjuku | 2 | False | `DIFFERS: 302c118…` | 807,613 |
| `53394532_bldg_6697_op.gml` | nakano, suginami | 2 | True | `c9c2ed0d971a92b5…` | 1,051,741 |
| `53394533_bldg_6697_op.gml` | nakano, suginami | 2 | True | `a3c1fec41548046c…` | 1,215,038 |
| `53394534_bldg_6697_op.gml` | nakano, shibuya, shinjuku | 3 | True | `f58f17abf258aee8…` | 1,103,138 |
| `53394535_bldg_6697_op.gml` | nakano, shinjuku | 2 | True | `b8cad9e6f9765365…` | 2,151,087 |
| `53394538_bldg_6697_op.gml` | chiyoda, shinjuku | 2 | False | `DIFFERS: 8a8fdbb…` | 511,211 |
| `53394539_bldg_6697_op.gml` | chiyoda, shinjuku | 2 | False | `DIFFERS: 3e16cd0…` | 527,696 |
| `53394542_bldg_6697_op.gml` | nakano, suginami | 2 | True | `a5d33e8297213667…` | 1,155,368 |
| `53394545_bldg_6697_op.gml` | nakano, shinjuku | 2 | True | `539968d1354e557c…` | 969,784 |
| `53394548_bldg_6697_op.gml` | bunkyo, shinjuku | 2 | True | `bf79c64787502ebf…` | 1,179,236 |
| `53394549_bldg_6697_op.gml` | bunkyo, chiyoda, shinjuku | 3 | False | `DIFFERS: 605e599…` | 1,034,630 |
| `53394550_bldg_6697_op.gml` | nakano, suginami | 2 | True | `b52eeb6c9cb63e71…` | 1,344,300 |
| `53394551_bldg_6697_op.gml` | nakano, suginami | 2 | True | `ca447babf4850e1d…` | 1,377,230 |
| `53394552_bldg_6697_op.gml` | nakano, suginami | 2 | True | `6448a6d0f6b8467e…` | 1,281,735 |
| `53394554_bldg_6697_op.gml` | nakano, shinjuku | 2 | True | `8e8e31fc6b778917…` | 1,138,639 |
| `53394555_bldg_6697_op.gml` | nakano, shinjuku | 2 | True | `e1a342f893a8de91…` | 927,674 |
| `53394556_bldg_6697_op.gml` | shinjuku, toshima | 2 | True | `f1ee43c289dfa58d…` | 976,318 |
| `53394557_bldg_6697_op.gml` | bunkyo, shinjuku, toshima | 3 | True | `9bf55c832eb1ff97…` | 784,788 |
| `53394558_bldg_6697_op.gml` | bunkyo, shinjuku | 2 | True | `331726da6bb42ebd…` | 789,212 |
| `53394559_bldg_6697_op.gml` | bunkyo, shinjuku | 2 | True | `7cac5347789f09cf…` | 789,234 |
| `53394560_bldg_6697_op.gml` | nakano, suginami | 2 | True | `1c6b5cdc7e1f277b…` | 1,046,840 |
| `53394563_bldg_6697_op.gml` | nakano, shinjuku | 2 | True | `e01ba3698a9640e0…` | 1,110,760 |
| `53394564_bldg_6697_op.gml` | nakano, shinjuku, toshima | 3 | True | `06bcf00916485769…` | 1,000,892 |
| `53394565_bldg_6697_op.gml` | shinjuku, toshima | 2 | True | `58bf4e893c5be41a…` | 1,070,675 |
| `53394566_bldg_6697_op.gml` | shinjuku, toshima | 2 | True | `8eb959e2f8a9eb4c…` | 749,979 |
| `53394567_bldg_6697_op.gml` | bunkyo, toshima | 2 | True | `f70f6156a9103daf…` | 1,036,405 |
| `53394568_bldg_6697_op.gml` | bunkyo, toshima | 2 | True | `6fa1762d9dcaab93…` | 609,704 |
| `53394570_bldg_6697_op.gml` | nakano, nerima, suginami | 3 | True | `0c6050c536f11940…` | 1,042,546 |
| `53394571_bldg_6697_op.gml` | nakano, nerima | 2 | True | `2f00ad488624cd90…` | 898,737 |
| `53394572_bldg_6697_op.gml` | nakano, nerima | 2 | True | `8c0b72a1b8860066…` | 912,180 |
| `53394573_bldg_6697_op.gml` | nakano, nerima | 2 | True | `06ee81440e8b3e49…` | 905,856 |
| `53394574_bldg_6697_op.gml` | nakano, nerima, shinjuku, toshima | 4 | True | `bda32692cc84bcc1…` | 1,264,426 |
| `53394577_bldg_6697_op.gml` | bunkyo, toshima | 2 | True | `28a5cb38592e98db…` | 2,906,355 |
| `53394578_bldg_6697_op.gml` | bunkyo, toshima | 2 | True | `d278e6fe4791717c…` | 1,653,890 |
| `53394579_bldg_6697_op.gml` | bunkyo, toshima | 2 | True | `571b32fe7efb37fe…` | 997,922 |
| `53394580_bldg_6697_op.gml` | nakano, nerima | 2 | True | `6deab5511effcb89…` | 901,139 |
| `53394583_bldg_6697_op.gml` | nakano, nerima | 2 | True | `7db5b6bbc99dacb8…` | 977,957 |
| `53394584_bldg_6697_op.gml` | itabashi, nerima, toshima | 3 | True | `33cd58f36926968d…` | 1,030,203 |
| `53394585_bldg_6697_op.gml` | itabashi, toshima | 2 | True | `f87682996bd32b6b…` | 1,138,390 |
| `53394586_bldg_6697_op.gml` | itabashi, toshima | 2 | True | `e41f7e95dc9e51f6…` | 1,296,413 |
| `53394587_bldg_6697_op.gml` | kita, toshima | 2 | True | `c67afc3a45b5bdd4…` | 1,283,445 |
| `53394588_bldg_6697_op.gml` | kita, toshima | 2 | True | `5cfc09d3180b4a14…` | 1,272,324 |
| `53394589_bldg_6697_op.gml` | bunkyo, kita, toshima | 3 | True | `f5286f3193573834…` | 1,097,598 |
| `53394593_bldg_6697_op.gml` | itabashi, nerima | 2 | True | `a98268f13ee2d5c6…` | 974,436 |
| `53394594_bldg_6697_op.gml` | itabashi, nerima | 2 | True | `627b1888885e0427…` | 856,021 |
| `53394595_bldg_6697_op.gml` | itabashi, toshima | 2 | True | `5da2f1a92305ceec…` | 1,380,807 |
| `53394596_bldg_6697_op.gml` | itabashi, toshima | 2 | True | `fa5fdddae746c973…` | 1,804,789 |
| `53394597_bldg_6697_op.gml` | itabashi, kita, toshima | 3 | True | `a6041b461b15963b…` | 1,435,617 |
| `53394598_bldg_6697_op.gml` | kita, toshima | 2 | True | `0126b89ab7b6fa7d…` | 1,244,468 |
| `53394599_bldg_6697_op.gml` | kita, toshima | 2 | True | `c3f2fe6eb0b44aab…` | 1,067,380 |
| `53394600_bldg_6697_op.gml` | chiyoda, chuo, minato | 3 | True | `69beab1f44b16fc9…` | 2,407,430 |
| `53394601_bldg_6697_op.gml` | chiyoda, chuo | 2 | True | `ffe81e7d77906398…` | 3,753,266 |
| `53394603_bldg_6697_op.gml` | chuo, koto | 2 | False | `DIFFERS: 63cbcfb…` | 1,087,064 |
| `53394611_bldg_6697_op.gml` | chiyoda, chuo | 2 | True | `c0c40659191c5ad7…` | 2,768,541 |
| `53394613_bldg_6697_op.gml` | chuo, koto | 2 | False | `DIFFERS: 04648d1…` | 764,738 |
| `53394617_bldg_6697_op.gml` | edogawa, koto | 2 | True | `8ede2c320077bec0…` | 663,360 |
| `53394621_bldg_6697_op.gml` | chiyoda, chuo | 2 | True | `4c5c4b4bfea9e000…` | 4,173,395 |
| `53394622_bldg_6697_op.gml` | chiyoda, chuo | 2 | True | `41407a7e369e930d…` | 2,195,381 |
| `53394623_bldg_6697_op.gml` | chuo, koto, sumida | 3 | False | `DIFFERS: 3e07526…` | 1,011,565 |
| `53394624_bldg_6697_op.gml` | koto, sumida | 2 | False | `DIFFERS: 42f5d49…` | 970,565 |
| `53394627_bldg_6697_op.gml` | edogawa, koto | 2 | True | `05cf563a50571323…` | 666,646 |
| `53394631_bldg_6697_op.gml` | bunkyo, chiyoda | 2 | False | `DIFFERS: db8769b…` | 3,927,393 |
| `53394632_bldg_6697_op.gml` | chiyoda, chuo, taito | 3 | False | `DIFFERS: 58412b2…` | 2,226,564 |
| `53394633_bldg_6697_op.gml` | chuo, sumida, taito | 3 | False | `DIFFERS: 4a77aca…` | 1,277,993 |
| `53394634_bldg_6697_op.gml` | koto, sumida | 2 | False | `DIFFERS: a797a9e…` | 1,008,560 |
| `53394635_bldg_6697_op.gml` | koto, sumida | 2 | False | `DIFFERS: 7eb75d0…` | 1,201,600 |
| `53394637_bldg_6697_op.gml` | edogawa, koto | 2 | True | `028667108f666c84…` | 637,237 |
| `53394640_bldg_6697_op.gml` | bunkyo, chiyoda | 2 | False | `DIFFERS: a278b9d…` | 655,261 |
| `53394641_bldg_6697_op.gml` | bunkyo, chiyoda, taito | 3 | False | `DIFFERS: 2724223…` | 1,826,466 |
| `53394642_bldg_6697_op.gml` | chiyoda, taito | 2 | False | `DIFFERS: 3d6f394…` | 2,977,315 |
| `53394643_bldg_6697_op.gml` | sumida, taito | 2 | False | `DIFFERS: 4ad1f49…` | 1,476,724 |
| `53394645_bldg_6697_op.gml` | koto, sumida | 2 | False | `DIFFERS: 0d02a00…` | 1,044,916 |
| `53394646_bldg_6697_op.gml` | edogawa, koto, sumida | 3 | False | `DIFFERS: 5cd5a0c…` | 1,157,703 |
| `53394647_bldg_6697_op.gml` | edogawa, koto | 2 | True | `dae9ff87c3ef68e0…` | 1,023,789 |
| `53394651_bldg_6697_op.gml` | bunkyo, taito | 2 | False | `DIFFERS: 672a568…` | 744,761 |
| `53394653_bldg_6697_op.gml` | sumida, taito | 2 | False | `DIFFERS: 9227a82…` | 2,471,103 |
| `53394654_bldg_6697_op.gml` | sumida, taito | 2 | False | `DIFFERS: 9b17c13…` | 1,078,280 |
| `53394656_bldg_6697_op.gml` | edogawa, sumida | 2 | False | `DIFFERS: 8312657…` | 907,069 |
| `53394657_bldg_6697_op.gml` | edogawa, katsushika, sumida | 3 | False | `DIFFERS: 1567234…` | 735,405 |
| `53394658_bldg_6697_op.gml` | edogawa, katsushika | 2 | True | `e464ede54a9305dd…` | 1,063,613 |
| `53394659_bldg_6697_op.gml` | edogawa, katsushika | 2 | True | `bf075429b2cce63a…` | 1,076,460 |
| `53394661_bldg_6697_op.gml` | bunkyo, taito | 2 | False | `DIFFERS: 1525a22…` | 1,890,771 |
| `53394662_bldg_6697_op.gml` | arakawa, taito | 2 | False | `DIFFERS: 54857bc…` | 1,928,483 |
| `53394664_bldg_6697_op.gml` | sumida, taito | 2 | False | `DIFFERS: 094fdca…` | 1,703,516 |
| `53394666_bldg_6697_op.gml` | edogawa, katsushika, sumida | 3 | False | `DIFFERS: 080d9c0…` | 932,590 |
| `53394667_bldg_6697_op.gml` | edogawa, katsushika, sumida | 3 | False | `DIFFERS: 7c1682a…` | 376,702 |
| `53394669_bldg_6697_op.gml` | edogawa, katsushika | 2 | True | `30bd2e1b0eb983d1…` | 1,068,009 |
| `53394670_bldg_6697_op.gml` | arakawa, bunkyo, kita | 3 | True | `437cfc58854761e0…` | 1,206,393 |
| `53394671_bldg_6697_op.gml` | arakawa, bunkyo, taito | 3 | False | `DIFFERS: 1ae4c6c…` | 1,473,237 |
| `53394672_bldg_6697_op.gml` | arakawa, taito | 2 | False | `DIFFERS: 74bf87d…` | 1,569,235 |
| `53394673_bldg_6697_op.gml` | arakawa, taito | 2 | False | `DIFFERS: 78910fc…` | 2,192,489 |
| `53394674_bldg_6697_op.gml` | arakawa, sumida, taito | 3 | False | `DIFFERS: 39b14b7…` | 1,102,537 |
| `53394676_bldg_6697_op.gml` | katsushika, sumida | 2 | True | `0ab0c5e20394bb22…` | 573,168 |
| `53394679_bldg_6697_op.gml` | edogawa, katsushika | 2 | True | `a6b6e05a7ac403e1…` | 830,813 |
| `53394680_bldg_6697_op.gml` | arakawa, bunkyo, kita, toshima | 4 | True | `4d4a861738405539…` | 1,114,423 |
| `53394681_bldg_6697_op.gml` | arakawa, kita | 2 | True | `e62d82fb65f951ed…` | 1,039,908 |
| `53394683_bldg_6697_op.gml` | adachi, arakawa | 2 | True | `e08f29b0c680ae40…` | 959,296 |
| `53394684_bldg_6697_op.gml` | adachi, arakawa, sumida | 3 | False | `DIFFERS: 87096a3…` | 222,781 |
| `53394685_bldg_6697_op.gml` | adachi, arakawa, katsushika, sumida | 4 | True | `9aafc5b915042b31…` | 387,829 |
| `53394686_bldg_6697_op.gml` | katsushika, sumida | 2 | False | `DIFFERS: 4322e1c…` | 1,190,130 |
| `53394689_bldg_6697_op.gml` | edogawa, katsushika | 2 | True | `1ae2e49fba96a738…` | 917,871 |
| `53394690_bldg_6697_op.gml` | arakawa, kita | 2 | True | `f5b385ddfae93b71…` | 893,159 |
| `53394691_bldg_6697_op.gml` | arakawa, kita | 2 | True | `99509b53e32a0883…` | 1,437,230 |
| `53394693_bldg_6697_op.gml` | adachi, arakawa | 2 | True | `71b854c2e2de8a42…` | 893,191 |
| `53394695_bldg_6697_op.gml` | adachi, katsushika, sumida | 3 | False | `DIFFERS: 4887493…` | 603,894 |
| `53394780_bldg_6697_op.gml` | edogawa, katsushika | 2 | True | `9dce56f170febb09…` | 1,551,597 |
| `53394790_bldg_6697_op.gml` | edogawa, katsushika | 2 | True | `02265036c694a204…` | 1,500,917 |
| `53395439_bldg_6697_op.gml` | itabashi, nerima | 2 | True | `f544529409073c51…` | 19,530 |
| `53395503_bldg_6697_op.gml` | itabashi, nerima | 2 | True | `b3b9d8dd8f49c13b…` | 730,446 |
| `53395507_bldg_6697_op.gml` | itabashi, kita | 2 | True | `c0335803b1e1e1c4…` | 646,583 |
| `53395509_bldg_6697_op.gml` | adachi, arakawa, kita | 3 | True | `8b9064fd29a8f8a3…` | 1,092,199 |
| `53395513_bldg_6697_op.gml` | itabashi, nerima | 2 | True | `9ba602d47d58b0da…` | 920,850 |
| `53395516_bldg_6697_op.gml` | itabashi, kita | 2 | True | `64573f0e05966521…` | 1,072,731 |
| `53395517_bldg_6697_op.gml` | itabashi, kita | 2 | True | `834ee4b934343068…` | 1,715,788 |
| `53395519_bldg_6697_op.gml` | adachi, kita | 2 | True | `9a6068be54626aa4…` | 1,108,380 |
| `53395520_bldg_6697_op.gml` | itabashi, nerima | 2 | True | `51c2e65aa6507240…` | 609,242 |
| `53395521_bldg_6697_op.gml` | itabashi, nerima | 2 | True | `17f9ffd2d13ac82c…` | 1,029,543 |
| `53395522_bldg_6697_op.gml` | itabashi, nerima | 2 | True | `1c58638f2340d709…` | 934,949 |
| `53395523_bldg_6697_op.gml` | itabashi, nerima | 2 | True | `4a075b3116be254b…` | 1,049,633 |
| `53395526_bldg_6697_op.gml` | itabashi, kita | 2 | True | `754d92282087adac…` | 783,681 |
| `53395528_bldg_6697_op.gml` | adachi, kita | 2 | True | `2cfd203eedd532cc…` | 991,718 |
| `53395529_bldg_6697_op.gml` | adachi, kita | 2 | True | `adddc16b4e96b8fb…` | 530,915 |
| `53395530_bldg_6697_op.gml` | itabashi, nerima | 2 | True | `a2c38861878ff0a2…` | 926,198 |
| `53395535_bldg_6697_op.gml` | itabashi, kita | 2 | True | `266edca35a50d907…` | 620,269 |
| `53395536_bldg_6697_op.gml` | itabashi, kita | 2 | True | `4f0dcca243c82eea…` | 546,888 |
| `53395538_bldg_6697_op.gml` | adachi, kita | 2 | True | `71d4d4eeb391fa32…` | 1,307,632 |
| `53395539_bldg_6697_op.gml` | adachi, kita | 2 | True | `297db79dc6cfcbef…` | 265,329 |
| `53395545_bldg_6697_op.gml` | itabashi, kita | 2 | True | `3441f6239d3d7436…` | 506,022 |
| `53395546_bldg_6697_op.gml` | itabashi, kita | 2 | True | `d490e05073114a54…` | 487,456 |
| `53395549_bldg_6697_op.gml` | adachi, kita | 2 | True | `303f9d6e98b7397b…` | 42,609 |
| `53395555_bldg_6697_op.gml` | itabashi, kita | 2 | True | `d5d890f3a2ee8a2d…` | 478,938 |
| `53395600_bldg_6697_op.gml` | adachi, arakawa, kita | 3 | True | `a35dccccb2fce472…` | 841,634 |
| `53395601_bldg_6697_op.gml` | adachi, arakawa | 2 | True | `70af57aea4eace14…` | 349,537 |
| `53395602_bldg_6697_op.gml` | adachi, arakawa | 2 | True | `0fd881dbedd589f1…` | 341,390 |
| `53395603_bldg_6697_op.gml` | adachi, arakawa | 2 | True | `88a3643d631a4eb4…` | 1,043,470 |
| `53395605_bldg_6697_op.gml` | adachi, katsushika | 2 | True | `a4281ea72a7b7a5b…` | 521,758 |
| `53395606_bldg_6697_op.gml` | adachi, katsushika | 2 | True | `b3b32f579f68a137…` | 1,505,419 |
| `53395610_bldg_6697_op.gml` | adachi, kita | 2 | True | `d34935c93c2d1a93…` | 332,807 |
| `53395615_bldg_6697_op.gml` | adachi, katsushika | 2 | False | `DIFFERS: a12dd24…` | 1,070,374 |
| `53395616_bldg_6697_op.gml` | adachi, katsushika | 2 | False | `DIFFERS: 6c563bf…` | 1,199,483 |
| `53395617_bldg_6697_op.gml` | adachi, katsushika | 2 | False | `DIFFERS: 03566be…` | 1,434,760 |
| `53395618_bldg_6697_op.gml` | adachi, katsushika | 2 | True | `45e8f89913d65980…` | 964,537 |
| `53395620_bldg_6697_op.gml` | adachi, kita | 2 | True | `757c07322a0f080d…` | 250,885 |
| `53395627_bldg_6697_op.gml` | adachi, katsushika | 2 | False | `DIFFERS: c42c412…` | 1,294,961 |
| `53395628_bldg_6697_op.gml` | adachi, katsushika | 2 | False | `DIFFERS: 3a6236c…` | 811,159 |
| `53395637_bldg_6697_op.gml` | adachi, katsushika | 2 | True | `5ebeb102616f8867…` | 885,347 |
| `53395638_bldg_6697_op.gml` | adachi, katsushika | 2 | True | `e1637e24bdac9158…` | 1,000,770 |
| `53395647_bldg_6697_op.gml` | adachi, katsushika | 2 | True | `801e473e1203eec4…` | 998,771 |
| `53395657_bldg_6697_op.gml` | adachi, katsushika | 2 | True | `bb93cc97ddf27d7a…` | 804,811 |
| `53395700_bldg_6697_op.gml` | edogawa, katsushika | 2 | True | `a235658b06fb25da…` | 866,382 |
