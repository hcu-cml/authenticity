# Reference environment

What the released graphs and the reported numbers were produced on, and what you need to reproduce them.

---

## Machine used for construction and evaluation

| Component | Value |
| --- | --- |
| CPU | AMD Ryzen Threadripper PRO 9955WX, 16 cores / 32 threads |
| RAM | 127 GiB |
| Storage | NVMe SSD |
| OS | Windows 11 (build 10.0.26200) |
| Container runtime | Docker Desktop with the WSL2 backend |
| Database | Neo4j 2025.10.1 (Docker image `neo4j:2025.10.1`) |
| Neo4j memory | 16 GiB heap, 32 GiB page cache |
| Neo4j plugins | APOC 2025.10.1, Neo4j Spatial 2025.10.0, GDS 2.23.0, GenAI 2025.10.1 |
| Python | 3.14 |
| GDAL | `ogr2ogr` CLI from a QGIS 3.44 installation (OSM clipping and reprojection) |
| GPU (Benchmark B only) | NVIDIA RTX PRO 6000, 96 GB, with PyTorch Geometric |

Python-side parallelism self-adapts and is capped: the OSM fusion and its census use `min(16, cpu_count)` workers, and the CityGML ingest takes `--writers` (default `min(8, cpu_count)`) with idempotent `MERGE` batches and transient-lock retry.

Total construction cost on this machine: **6.64 h wall clock across all five cities** (Hamburg 24.4 min, Helsinki 2.5 min, Zurich 41.2 min, New York 1.52 h, Tokyo 3.98 h). Per-stage times: [REPRODUCE.md](REPRODUCE.md).

---

## Minimum environment to use the release

You do not need the machine above to work with the data.

| Task | Needs |
| --- | --- |
| Restore and query Hamburg | Neo4j 2025.10.1+, 20 GiB free disk, 16 GiB RAM (4 GiB heap, 6 GiB page cache) |
| Restore and query Tokyo | Neo4j 2025.10.1+, 115 GiB free disk, 32 GiB RAM or more |
| Spatial questions | plus the Neo4j Spatial plugin |
| Harness schema introspection | plus the APOC plugin |
| Re-score cached baselines | the above, plus Python 3.11+ and the `neo4j` driver |
| Evaluate a local model | plus Ollama |
| Evaluate a commercial model | plus its SDK and an API key |
| Backend-neutral table export | Python 3.11+, `neo4j`, and optionally `pyarrow` for Parquet |
| Representation learning | a GPU is strongly recommended at city scale |

**Neo4j version is a hard constraint.** The dumps are written by 2025.10.1 and `neo4j-admin database load` accepts only the same or a newer version.

**Page cache dominates performance.** These workloads are random-access index lookups over the whole store, and the stores are 0.28 to 99 GiB. An undersized page cache (the image default is 512 MB) makes everything disk bound; that was the single largest slowdown observed during construction. Keep `heap + pagecache` under roughly 80 % of what the container actually sees (`docker info | grep "Total Memory"`), otherwise Neo4j will fail to start or swap.

---

## Shipped configuration

[../docker/](../docker/) contains a `docker compose` service pinned to Neo4j 2025.10.1 with a configuration file matching the one used for construction, and a note on which plugin JARs to fetch and why. Adjust the two memory settings in `docker/conf/neo4j.conf` to your machine before the first start.

## Software versions used for the reported baselines

| | Value |
| --- | --- |
| Local open-weight model | `qwen2.5-coder:7b`, Ollama, `Q4_K_M` quantization |
| Commercial model | Claude Sonnet 5, run closed book with schema-only context |
| Context given to both | byte-identical per-city schema text from [../schema/](../schema/) |
| Query timeout during scoring | 20 s per query |

Latency is recorded in the results files for completeness but is not comparable across the two backends: the cached commercial run's timing covers Cypher execution only, while the Ollama run's covers model inference plus execution.
