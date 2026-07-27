# Getting started

From nothing to a queryable city graph in four steps. Budget 20 minutes plus download time for Hamburg; longer for Tokyo.

---

## 0. What you need

| | Minimum | Comfortable | Notes |
| --- | --- | --- | --- |
| Disk (Hamburg) | 20 GiB | 40 GiB | 3.07 GiB dump plus a 14.8 GiB store plus write-ahead logs |
| Disk (Tokyo) | 115 GiB | 150 GiB | 11.3 GiB dump plus a 99.2 GiB store |
| RAM (Hamburg) | 16 GiB | 32 GiB | see the sizing note in step 2 |
| RAM (Tokyo) | 32 GiB | 64 GiB+ | large graphs want a large page cache |
| Software | Docker, or a local Neo4j **2025.10.1 or newer** | | a dump loads only into the same or a newer version |
| Python | 3.11+ | 3.14 | only for the tools and the benchmark harness |

**Start with Hamburg.** It is the smallest full-stack city (all four provenance layers) and every derived-layer feature can be exercised on it. Add others only when you need cross-city results.

Install the Python dependencies for the tooling:

```bash
pip install -r requirements.txt
```

---

## 1. Download a dump

The five graphs are on Zenodo: **<https://doi.org/10.5281/zenodo.21547211>**

| City | File | Size |
| --- | --- | --- |
| Hamburg | `neo4j_hamburg_lod2_roofmats_lod3_osm_20260717.dump` | 3.07 GiB |
| Helsinki | `neo4j_helsinki_lod2_osm_20260716.dump` | 0.15 GiB |
| Zurich | `neo4j_zurich_lod2_osm_20260716.dump` | 5.57 GiB |
| New York | `neo4j_nyc_lod2_osm_20260716.dump` | 6.81 GiB |
| Tokyo | `neo4j_tokyo_bcore_osm_20260717.dump` | 11.32 GiB |

Each dump has a companion `*_counts.txt` recording its exact provenance and the counts to verify after a restore. Copies of those manifests are in [../dumps/counts/](../dumps/counts/) so you can check them before downloading anything. Zenodo publishes an MD5 per file; verify it, especially for the multi-gigabyte files. For the largest files prefer the Zenodo REST API or a command-line downloader over the browser uploader path.

---

## 2. Bring up Neo4j and load the dump

The shipped Docker service pins the matching Neo4j version and enables the plugins the graphs need.

```bash
cd docker
cp -r /path/to/downloaded/dumps ./backups     # or point the volume at your own path
# fetch the plugin JARs once (see docker/plugins/README.md for what and why)
docker compose build neo4j
```

Load a dump into the `neo4j` database of a **stopped** instance, then start it:

```bash
docker compose run --rm --entrypoint "" neo4j \
  neo4j-admin database load neo4j --from-path=/backups --overwrite-destination
docker compose up -d neo4j
```

On Windows, run these from PowerShell rather than a POSIX shell: a bash-style `-v` mount of a Windows path can silently fail to mount, after which the load exits with no data and no useful error.

Neo4j is ready when <http://localhost:7474> answers. Default credentials in the shipped configuration are `neo4j` / `neo4jneo4j`; change them for anything beyond a local workstation, and never expose port 7687 or 7474 to a network with these defaults.

**Sizing.** The shipped `docker/conf/neo4j.conf` requests a 16 GiB heap and a 32 GiB page cache, which suits a machine with roughly 64 GiB or more available to Docker. Keep `heap + pagecache` below about 80 % of what the Docker VM actually sees (`docker info | grep "Total Memory"`), otherwise Neo4j will fail to start or swap. On a 16 GiB machine, 4 GiB heap and 6 GiB page cache will restore and query Hamburg; queries touching large parts of the store will simply be slower, because these workloads are random-access index lookups over the whole graph and an undersized page cache makes them disk bound.

**Plugins.** [Neo4j Spatial](https://github.com/neo4j-contrib/spatial) is **required** for the R-tree procedures (`spatial.intersects`, `spatial.withinDistance`), which the spatial benchmark category depends on. [APOC](https://neo4j.com/labs/apoc/) is required for schema introspection as the harness performs it. Graph Data Science and GenAI are optional and only needed for embedding work. The R-tree index structures themselves are ordinary graph content inside the dumps: nothing is rebuilt on load, but the procedures that read them come from the plugin.

---

## 3. Verify the restore

Never trust a multi-gigabyte restore silently. This checks the live graph against the manifest that was written when the dump was created:

```bash
python tools/verify_restore.py --city hamburg
```

It compares node, relationship, building, OSM feature, `ENRICHED_BY`, and `HAS_POI` counts against [../dumps/counts/](../dumps/counts/), confirms the expected R-tree layers exist and answer a bounding-box query, and exits non-zero on any mismatch. Run it before you report any number from a restored graph.

Equivalent manual check:

```cypher
MATCH (n)                     RETURN count(n) AS nodes;          // 17,440,924 for Hamburg
MATCH ()-[r]->()              RETURN count(r) AS relationships;  // 26,299,391
MATCH (b:Building)            RETURN count(b) AS buildings;      // 388,267
MATCH (o:OsmFeature)          RETURN count(o) AS osm_features;   // 1,188,139
MATCH ()-[r:ENRICHED_BY]->()  RETURN count(r) AS correspondences;// 373,211
```

---

## 4. First queries

Read [GRAPH_SCHEMA.md](GRAPH_SCHEMA.md) before writing your own. A few that exercise what makes this dataset different:

**Where do the authoritative and the crowd-sourced source disagree about height?**

```cypher
MATCH (b:Building)-[:ENRICHED_BY {is_primary: true}]->(o:OsmFeature)
WHERE o.osm_height IS NOT NULL AND b.measured_height > -999
  AND abs(toFloat(o.osm_height) - b.measured_height) > 3.0
RETURN b.id, b.measured_height AS authoritative, o.osm_height AS crowd_sourced
ORDER BY abs(toFloat(o.osm_height) - b.measured_height) DESC, b.id ASC
LIMIT 20;
```

**A coverage-aware aggregate: never report a bare count over a partially covered attribute.**

```cypher
MATCH (b:Building)
WITH count(b) AS total,
     count(CASE WHEN b.predictedroofmaterial IS NOT NULL THEN 1 END) AS covered
RETURN covered, total, round(100.0 * covered / total * 10) / 10.0 AS coverage_pct;
```

**Provenance-filtered retrieval: use only authoritative evidence.**

```cypher
MATCH (b:Building)
WHERE b.measured_height > -999            // authoritative attribute, not osm_height
RETURN round(avg(b.measured_height) * 100) / 100.0 AS avg_height_m;
```

**Spatial, with the R-tree.** Note that the layers store Cartesian coordinates in the city's own metric CRS, so a metre radius must be expressed as a window plus an exact distance recheck rather than as a `withinDistance` radius, which is interpreted in kilometres against a geographic layer:

```cypher
MATCH (b0:Building {id: $anchor_id}) WITH b0, b0.location AS c
CALL spatial.intersects('features', 'POLYGON(('
  + toString(c.x-100)+' '+toString(c.y-100)+',' + toString(c.x+100)+' '+toString(c.y-100)+','
  + toString(c.x+100)+' '+toString(c.y+100)+',' + toString(c.x-100)+' '+toString(c.y+100)+','
  + toString(c.x-100)+' '+toString(c.y-100)+'))') YIELD node
WITH b0, node WHERE node:Building AND node.id <> b0.id
  AND point.distance(b0.location, node.location) <= 100
RETURN count(node) AS buildings_within_100m;
```

This is verbatim the idiom the benchmark's proximity gold queries use, so it is verified against all five graphs.

**Confidence-weighted correspondences, kept rather than collapsed.**

```cypher
MATCH (b:Building)-[r:ENRICHED_BY]->(o:OsmFeature)
RETURN r.match_type, count(*) AS edges,
       round(avg(r.jaccard) * 1000) / 1000.0 AS mean_jaccard
ORDER BY edges DESC;
```

More worked examples with verified answers: every question in [../benchmark_a/questions/dev.jsonl](../benchmark_a/questions/dev.jsonl) ships with its gold Cypher and its materialized answer.

---

## 5. Where to go next

- **Evaluate a model on the query benchmark**: [../benchmark_a/README.md](../benchmark_a/README.md).
- **Work without Neo4j**: `python tools/export_tables.py --out export/hamburg` writes backend-neutral node and edge tables (CSV, or Parquet if `pyarrow` is installed) with the provenance columns as first-class fields.
- **Representation learning**: [../benchmark_b/README.md](../benchmark_b/README.md).
- **Understand what was validated and how**: [QUALITY_GATES.md](QUALITY_GATES.md).
- **Rebuild a graph from its sources**: [REPRODUCE.md](REPRODUCE.md).

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Failed to load database: unsupported store version` | dump written by a newer Neo4j than yours | use Neo4j 2025.10.1 or newer |
| `load` exits 0 but the graph is empty | on Windows, a bash-style volume mount silently failed | run the `docker` command from PowerShell |
| `There is no procedure with the name spatial.intersects` | Neo4j Spatial plugin missing | add the plugin JAR and restart, see `docker/plugins/README.md` |
| Neo4j will not start after configuring memory | heap plus page cache exceeds what the VM has | lower both in `docker/conf/neo4j.conf` |
| Spatial queries return nothing on a correct-looking radius | `withinDistance` reads kilometres against a geographic layer, the layers are Cartesian metres | use the window plus `point.distance` idiom above |
| A query over a whole city never finishes | one spatial procedure call per row does not scale | bound the query to a window first, then filter exactly |
| Height aggregates on Tokyo look absurd | PLATEAU `-9999` height and `9999` storey sentinels | filter with `measured_height > -999` |
| `verify_restore.py` reports a mismatch | wrong dump, partial load, or a modified graph | reload from the dump and re-verify before reporting anything |
