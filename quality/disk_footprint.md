# pykci disk footprint per city and source-layer configuration

Store = `/data/databases/neo4j` (transaction logs excluded: transient WAL,
listed separately). Measured **additively at each ingestion stage** because
Neo4j does not shrink store files on delete. Dump = compressed
`neo4j-admin database dump` snapshot size where one was taken
(see docker/SNAPSHOTS.md). Regenerate this file by re-running
`bench/measure_disk_footprint.py` after any stage.

| City | Stage | Date | Nodes | Edges | Store (GiB) | Tx logs (GiB) | Dump (GiB) | Notes |
|------|-------|------|------:|------:|------------:|--------------:|-----------:|-------|
| hamburg | citygml_pure | 2026-06-19 | 15,160,000 | 21,250,000 | 11.40 | — | — | pure CityGML LoD2 (no roof materials), measured in eval/tool_comparison/comparison_2026-06-19.md (11.4 GiB store) |
| hamburg | full_stack | 2026-07-09 | 17,442,794 | 26,301,261 | 15.67 | 2.03 | 2.89 | CityGML LoD2 + ML roof materials (194,799) + LoD3 facades (3,404 nodes) + full OSM fusion (2,257,536 nodes / ~5.03M edges incl. R-tree). OSM layer delta vs. citygml_pure ≈ +4.25 GiB store |
| hamburg | lod3 | 2026-07-16 | 15,167,377 | 21,254,137 | 12.96 | 3.03 | — |  |
| hamburg | citygml | 2026-07-17 | 15,162,184 | 21,248,642 | 12.71 | 3.04 | — |  |
| hamburg | citygml_osm | 2026-07-17 | 17,437,512 | 26,295,677 | 14.77 | 7.34 | — |  |
| hamburg | citygml_osm_roofmat | 2026-07-17 | 17,437,512 | 26,295,677 | 14.77 | 7.59 | — |  |
| hamburg | full | 2026-07-17 | 17,440,924 | 26,299,391 | 14.77 | 7.59 | — |  |
| hamburg_hafencity | citygml_lod3 | 2026-07-12 | 5,962 | 7,986 | 0.00 | 0.25 | — |  |
| hamburg_hafencity | citygml_osm | 2026-07-12 | 11,688 | 21,120 | 0.00 | 0.25 | — |  |
| helsinki | citygml | 2026-07-16 | 325,298 | 414,136 | 0.22 | 0.50 | — |  |
| helsinki | citygml_osm | 2026-07-16 | 414,459 | 619,964 | 0.28 | 0.75 | — |  |
| nyc | citygml | 2026-07-16 | 39,996,645 | 42,163,517 | 27.89 | 3.40 | — |  |
| nyc | citygml_osm | 2026-07-16 | 45,797,985 | 54,207,134 | 31.90 | 6.58 | — |  |
| nyc_da4 | citygml | 2026-07-12 | 491,642 | 524,970 | 0.25 | 0.51 | — |  |
| nyc_da4 | citygml_osm | 2026-07-12 | 576,520 | 699,820 | 0.32 | 0.76 | — |  |
| tokyo | citygml | 2026-07-17 | 64,532,720 | 72,929,529 | 91.92 | 3.64 | — |  |
| tokyo | citygml_osm | 2026-07-17 | 74,409,400 | 91,949,234 | 99.18 | 4.55 | — |  |
| tokyo_tile | citygml | 2026-07-12 | 34,722 | 38,166 | 0.06 | 0.25 | — |  |
| tokyo_tile | citygml_osm | 2026-07-12 | 41,334 | 51,745 | 0.06 | 0.25 | — |  |
| zurich | citygml | 2026-07-16 | 37,972,748 | 38,178,082 | 27.06 | 3.10 | — |  |
| zurich | citygml_osm | 2026-07-16 | 41,508,371 | 45,548,405 | 30.21 | 9.65 | — |  |
| zurich_tile | citygml | 2026-07-12 | 59,948 | 60,514 | 0.00 | 0.25 | — |  |
| zurich_tile | citygml_osm | 2026-07-12 | 63,391 | 67,306 | 0.00 | 0.25 | — |  |

Layer deltas within a city are differences between consecutive stage rows;
per-layer node attribution is exact via the provenance `source` property
(`osm:*`, `lod3:*` vs. the CityGML filename).

## Hamburg per-layer breakdown

| Layer configuration | Nodes | Edges | Store (GiB) | Basis |
|---------------------|------:|------:|------------:|-------|
| purely CityGML (LoD2) | 15.16 M | 21.25 M | 11.40 | measured (tool-comparison benchmark, 2026-06-19) |
| + ML roof materials | +0 | +0 | +0.01 | estimated: 194,799 `predictedroofmaterial` property records (values inline), ~8 MB |
| + LoD3 reconstructed | +3,404 | +3,404 | +0.01 | estimated from counts: `Lod3Facade` nodes + `HAS_LOD3_FACADE`/geometry edges + verbatim coordinate strings |
| + OSM enriched | +2,257,536 | +5,029,244 | +4.25 | measured by stage difference (15.67 − 11.40 − est. 0.02); incl. all tags, geometry chain, 373,211 `ENRICHED_BY`, 22,219 `HAS_POI`, and the 1,188,139-entry `osm_features` R-tree |
| **full stack (= dump snapshot)** | **17.44 M** | **26.30 M** | **15.67** | measured 2026-07-09; dump 2.89 GiB, tx logs 2.03 GiB |

OSM edge composition: 3,445,675 outgoing from `osm:*` nodes (geometry chain,
`PART_OF`, `LOCATED_IN`) + 373,211 `ENRICHED_BY` + 22,219 `HAS_POI` +
1,188,139 `RTREE_REFERENCE`. Edge reconciliation: 26.30 M − 5.03 M (OSM) −
3,404 (LoD3) ≈ 21.27 M ≈ the benchmark's 21.25 M CityGML edges.

For the remaining cities (Zurich, Helsinki, Tokyo, New York: CityGML + OSM
only), capture exactly two stages: `citygml` right after `ingest_citygml.py`
and `citygml_osm` right after `ingest_osm.py`.
