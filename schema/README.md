# Per-city schema text

These files are the **exact bytes** every evaluated model received as its context for that city. Nothing else was given: no database access, no tools, no retrieval, no example gold queries.

| City | File |
| --- | --- |
| Hamburg | `hamburg_citygml2_lod2_2025.gml.txt` |
| Helsinki | `helsinki_citygml2_lod2_2019.gml.txt` |
| Zurich | `zurich.txt` |
| New York | `nyc.txt` |
| Tokyo | `tokyo.txt` |

The filenames are the `dataset` value carried by each question plus `.txt`, which is how `benchmark_a/harness/evaluate_model.py` resolves them. Keep the names if you re-run the harness, otherwise context parity breaks silently.

Each file is the graph schema as introspected from that city's live graph (node labels with their properties, relationship types, and the patterns that connect them), cached once so that a run months later cannot diverge from what an earlier backend saw.

## Two things to know about this text

**It is sampled, so rare structure can be missing.** Schema introspection samples the graph, and a label or relationship that exists on a handful of nodes can be dropped from the generated text. Two real cases: Hamburg's `HAS_LOD3_FACADE` edge and its `lod3_confidence`, `lod3_method`, and `lod3_source` properties (17 of 388,267 buildings), and Tokyo's single `Room` node with its `HAS_INTERIOR_ROOM` edge (1 in 2 M buildings). Where a gap was known it was patched into the cached text explicitly; where it was not, a model refusing a question about the missing structure was scored as a legitimate refusal rather than a template bug, since the model had no way to know.

**It does not state the query idioms.** The CRS semantics of the R-tree layers, the height sentinels, and the primary-match rule are properties of the data that a model has to infer or ask about. They are documented for humans in [../docs/GRAPH_SCHEMA.md](../docs/GRAPH_SCHEMA.md), and deliberately not injected into the model context, because inferring them is part of what the benchmark measures.

## Regenerating

Restore a city and run the harness; if a cache file for that dataset is absent it is regenerated from the live graph. Delete a file only if you intend to change the context, and note that doing so makes your numbers incomparable with the shipped baselines.
