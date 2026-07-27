# Neo4j plugins

The plugin JARs are not redistributed in this repository (licensing, and a combined 90 MB). Download them into this directory before `docker compose build neo4j`. Match the Neo4j version: **2025.10.1**.

| Plugin | Needed for | Where to get it |
| --- | --- | --- |
| **APOC** 2025.10.1 | schema introspection, which the benchmark harness uses to build the per-city context | <https://neo4j.com/labs/apoc/> and the releases of <https://github.com/neo4j/apoc> |
| **Neo4j Spatial** 2025.10.x | the `spatial.*` R-tree procedures. **Required** for the spatial question category and for `tools/verify_restore.py`; take the "with dependencies" build | <https://github.com/neo4j-contrib/spatial> |
| Graph Data Science 2.23.x | optional, only for embedding and graph-algorithm work | <https://neo4j.com/deployment-center/> |
| GenAI plugin 2025.10.1 | optional, only if you want in-database embedding procedures | ships with Neo4j distributions |

Expected filenames (the Dockerfile copies everything in this directory, so exact names do not matter):

```text
apoc-2025.10.1-core.jar
neo4j-spatial-server-plugin-2025.10.0-with-dependencies.jar
neo4j-graph-data-science-2.23.0.jar          # optional
neo4j-genai-plugin-2025.10.1.jar             # optional
```

After starting the container, confirm the two required plugins are live:

```cypher
CALL spatial.layers() YIELD name RETURN name;   // expect 'features' and 'osm_features'
CALL apoc.meta.schema() YIELD value RETURN count(value);
```

If `spatial.layers()` raises "there is no procedure with the name", the JAR is missing or does not match the Neo4j version. The R-tree index structures themselves live inside the dumps as ordinary graph content, so nothing needs rebuilding: only the procedures that read them come from the plugin.
