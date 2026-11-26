# The graph dumps

The five city graphs are large binary databases, so they are archived on Zenodo rather than in git:

**<https://doi.org/10.5281/zenodo.21547211>**

| City | File | Size | Nodes | Relationships | Buildings |
| --- | --- | --: | --: | --: | --: |
| Hamburg | `authenticity_hamburg_v1_0.dump` | 3.07 GiB | 17,440,924 | 26,299,391 | 388,267 |
| Helsinki | `authenticity_helsinki_v1_0.dump` | 0.15 GiB | 414,459 | 619,964 | 2,980 |
| Zurich | `authenticity_zurich_v1_0.dump` | 5.57 GiB | 41,508,371 | 45,548,405 | 102,668 |
| New York | `authenticity_nyc_v1_0.dump` | 6.81 GiB | 45,797,985 | 54,207,134 | 1,083,437 |
| Tokyo | `authenticity_tokyo_v1_0.dump` | 11.32 GiB | 74,409,400 | 91,949,234 | 2,005,762 |
| | **total** | **26.91 GiB** | **179,571,139** | **218,624,128** | **3,583,114** |

Written by **Neo4j 2025.10.1**. A dump loads into that version or newer, never older. Restoring: [../docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md).

License: CC BY 4.0, with the OpenStreetMap-derived content under ODbL 1.0 ((c) OpenStreetMap contributors) and each source layer under its provider's license. Terms and attribution strings: [../DATA_LICENSES.md](../DATA_LICENSES.md).

Each dump has a counts manifest in [counts/](counts/), so you can read a graph's exact provenance before downloading gigabytes. The manifests and the changelog name each dump by its build-time file name (`neo4j_<city>_..._202607xx.dump`); Zenodo serves the same archives under the release names in the table above.

## What a counts manifest tells you

Each file records, for one dump:

- the Neo4j version and the date it was written,
- the source CityGML (file or tile directory), its CRS, its building count, and whether coordinates were reprojected at ingest,
- the identity-resolution outcome, that is how many features were deduplicated and how many split onto synthesized ids, and the confirmation that no building was lost,
- the OSM extract fused in and how many features it contributed,
- for Hamburg, the derived-layer coverage,
- the outcome of the completeness census and the anomaly gates, including which flags were investigated and found benign,
- the on-disk store size and the compressed dump size,
- a **verification counts** block: the exact numbers a correct restore must reproduce.

That last block is what [../tools/verify_restore.py](../tools/verify_restore.py) checks automatically:

```bash
python tools/verify_restore.py --city hamburg
```

## One city at a time

Each dump is a complete `neo4j` database, so one Neo4j instance holds one city. To work with several cities, either restore them in turn into the same instance, or give each its own container and volume. The benchmark harness assumes one city is live and evaluates only the questions whose `dataset` matches it.

## Working without Neo4j

`python tools/export_tables.py --out export/<city>` turns a restored graph into node and edge tables (Parquet or CSV) with the provenance columns as first-class fields. Full geometry stays in the dump: the tables carry geometry summaries (centroid, bounding box, surface counts), because 165 M geometry nodes do not belong in a feature table.
