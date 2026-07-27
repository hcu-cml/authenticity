# Tools

Small, dependency-light utilities. All read a live Neo4j graph or the files in this repository; none modify a graph.

| Tool | Purpose |
| --- | --- |
| [verify_restore.py](verify_restore.py) | check a restored city graph against the manifest written at dump time: node, relationship, building, OSM, correspondence, and derived-layer counts, plus the R-tree layers and a real index query. **Run this before reporting any number from a restored graph.** |
| [export_tables.py](export_tables.py) | export a graph to backend-neutral node and edge tables (Parquet with `pyarrow`, otherwise CSV) with provenance as first-class columns, for consumers who do not want a Neo4j dependency |
| [osm_citygml_conflict_analysis.py](osm_citygml_conflict_analysis.py) | measure cross-source disagreement per city: how many buildings carry a value from more than one source for the same attribute, and how far apart those values are. Reproduces the reports in [../quality/](../quality/) |
| [build_template_inventory.py](build_template_inventory.py) | regenerate `benchmark_a/template_inventory.{md,csv}` from the shipped question files and the template module. No database needed |

```bash
pip install -r ../requirements.txt

python tools/verify_restore.py --city hamburg
python tools/export_tables.py --out export/hamburg
python tools/osm_citygml_conflict_analysis.py --dataset hamburg_citygml2_lod2_2025.gml
python tools/build_template_inventory.py --check
```

Connection defaults are `bolt://localhost:7687` with the credentials from the shipped Docker configuration; override with `--uri`, `--user`, `--password`, or the `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` environment variables.

## Notes

**`export_tables.py` pages over source nodes, not over rows.** A row-keyed cursor would silently drop the remaining edges of whichever node straddles a batch boundary; batching whole nodes cannot lose an edge. Verified against the dump manifests: the exported edge counts match exactly.

**Tables summarize geometry rather than exporting it.** Centroid, bounding box, and surface counts are included; the 165 M geometry nodes of the corpus stay in the dumps, which remain the source of truth for anything geometric.

**A table that is empty for a city is skipped, not written empty**, and `manifest.json` records that it had zero rows. Absent layers are normal: only Hamburg has `edges_has_lod3_facade`, and only Helsinki and Tokyo have non-building city objects.
