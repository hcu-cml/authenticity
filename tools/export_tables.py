#!/usr/bin/env python3
"""
export_tables.py — export a restored AuthentiCity graph to backend-neutral node
and edge tables, with provenance as first-class columns.

For consumers who do not want a Neo4j dependency in their training loop or their
analysis: the graph becomes flat tables (Parquet when `pyarrow` is installed,
otherwise CSV) that load directly into pandas, PyTorch Geometric, DGL, DuckDB, or
a relational database.

What it writes into --out:

    nodes_building.{parquet,csv}   one row per Building, with authoritative
                                   attributes, the mirrored osm_* scalars, the
                                   roof-material prediction columns, geometry
                                   summaries, and provenance
    nodes_osmfeature.{...}         one row per OsmFeature, with its tags,
                                   classification, match flag and reason
    nodes_cityobject.{...}         non-building city objects (bridges, roads, ...)
    edges_enriched_by.{...}        cross-source correspondences with
                                   jaccard / overlap_ratio / match_type / is_primary
    edges_has_poi.{...}            point-of-interest attachments with distance_m
    edges_located_in.{...}         building to district containment
    edges_has_lod3_facade.{...}    reconstructed-facade anchors with confidence
    manifest.json                  row counts, the dataset, the CRS, the column
                                   lists, and the exact queries used

Every table is streamed in keyed batches, so memory stays flat even on Tokyo
(2 M buildings, 3.8 M OSM features).

Usage:
    python tools/export_tables.py --out export/hamburg
    python tools/export_tables.py --out export/tokyo --batch-size 100000
    python tools/export_tables.py --out export/hamburg --only nodes_building
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from neo4j import GraphDatabase
except ImportError:                                            # pragma: no cover
    sys.exit("the neo4j Python driver is required: pip install -r requirements.txt")

try:
    import pyarrow                                             # noqa: F401
    import pyarrow.parquet                                     # noqa: F401
    HAVE_ARROW = True
except ImportError:
    HAVE_ARROW = False


# Each table: the keyed-batch query (ordered by a stable key so pagination is
# deterministic) and the columns it produces. Geometry is summarized rather than
# exported vertex by vertex; the dumps remain the source of truth for full
# geometry, and 165 M geometry nodes do not belong in a feature table.
TABLES = {
    "nodes_building": """
        MATCH (b:Building) WHERE b.id > $cursor
        WITH b ORDER BY b.id LIMIT $limit
        OPTIONAL MATCH (b)-[:LOCATED_IN]->(d:District)
        OPTIONAL MATCH (b)-[:HAS_FUNCTION]->(f:BuildingFunction)
        OPTIONAL MATCH (b)-[:HAS_ROOF_TYPE]->(rt:RoofType)
        OPTIONAL MATCH (b)-[:HAS_BOUNDARY]->(s:BoundarySurface)
        WITH b, d, f, rt, count(s) AS n_boundary_surfaces
        OPTIONAL MATCH (b)-[e:ENRICHED_BY]->(:OsmFeature)
        WITH b, d, f, rt, n_boundary_surfaces, count(e) AS n_osm_edges,
             max(e.jaccard) AS best_jaccard
        RETURN b.id AS id, b.source AS source,
               b.source_gml_id AS source_gml_id, b.id_synthesized AS id_synthesized,
               b.name AS name, d.id AS district_id,
               b.measured_height AS measured_height,
               b.storeys_above_ground AS storeys_above_ground,
               b.storeys_below_ground AS storeys_below_ground,
               b.function_code AS function_code, f.name AS function_name,
               b.roof_type_code AS roof_type_code, rt.name AS roof_type_name,
               b.usage_code AS usage_code, b.class_code AS class_code,
               b.center_x AS center_x, b.center_y AS center_y,
               b.ground_z AS ground_z,
               b.bbox_min_x AS bbox_min_x, b.bbox_min_y AS bbox_min_y,
               b.bbox_min_z AS bbox_min_z, b.bbox_max_x AS bbox_max_x,
               b.bbox_max_y AS bbox_max_y, b.bbox_max_z AS bbox_max_z,
               n_boundary_surfaces AS n_boundary_surfaces,
               b.osm_height AS osm_height,
               b.osm_building AS osm_building, b.osm_building_levels AS osm_building_levels,
               b.osm_roof_shape AS osm_roof_shape, b.osm_roof_material AS osm_roof_material,
               b.osm_amenity AS osm_amenity, b.osm_name AS osm_name,
               b.osm_match_type AS osm_match_type, b.osm_match_count AS osm_match_count,
               b.osm_best_jaccard AS osm_best_jaccard, b.osm_shared AS osm_shared,
               b.addr_street AS addr_street, b.addr_postcode AS addr_postcode,
               n_osm_edges AS n_enriched_by_edges, best_jaccard AS max_edge_jaccard,
               b.predictedroofmaterial AS predicted_roof_material,
               b.predicted_roof_material_0_coverage AS predicted_roof_material_coverage,
               b.predicted_roof_material_count AS predicted_roof_material_count,
               b.predicted_roof_material_source AS predicted_roof_material_source,
               b.lod3_confidence AS lod3_confidence, b.lod3_method AS lod3_method
    """,
    "nodes_osmfeature": """
        MATCH (o:OsmFeature) WHERE o.id > $cursor
        WITH o ORDER BY o.id LIMIT $limit
        RETURN o.id AS id, o.osm_id AS osm_id, o.osm_kind AS osm_kind,
               [l IN labels(o) WHERE l STARTS WITH 'Osm' AND l <> 'OsmFeature'][0] AS osm_label,
               o.source AS source, o.matched AS matched,
               o.unmatched_reason AS unmatched_reason,
               o.osm_name AS name, o.osm_building AS building,
               o.osm_height AS height, o.osm_building_levels AS building_levels,
               o.osm_roof_shape AS roof_shape, o.osm_roof_material AS roof_material,
               o.osm_amenity AS amenity, o.osm_shop AS shop, o.osm_operator AS operator,
               o.addr_street AS addr_street, o.addr_housenumber AS addr_housenumber,
               o.addr_postcode AS addr_postcode, o.addr_city AS addr_city,
               o.center_x AS center_x, o.center_y AS center_y,
               o.bbox_min_x AS bbox_min_x, o.bbox_min_y AS bbox_min_y,
               o.bbox_max_x AS bbox_max_x, o.bbox_max_y AS bbox_max_y,
               o.other_tags AS other_tags
    """,
    "nodes_cityobject": """
        MATCH (c:CityObject) WHERE c.id > $cursor
        WITH c ORDER BY c.id LIMIT $limit
        RETURN c.id AS id, c.source AS source,
               [l IN labels(c) WHERE NOT l IN ['CityObject', 'Entity']][0] AS module,
               c.name AS name, c.class_code AS class_code,
               c.function_code AS function_code, c.usage_code AS usage_code,
               c.center_x AS center_x, c.center_y AS center_y,
               c.bbox_min_x AS bbox_min_x, c.bbox_min_y AS bbox_min_y,
               c.bbox_max_x AS bbox_max_x, c.bbox_max_y AS bbox_max_y
    """,
    # Edge tables page over their SOURCE NODE, never over rows: a row-keyed
    # `id > cursor` would silently drop the remaining edges of whichever node
    # straddles a batch boundary. Batching whole nodes cannot lose an edge.
    "edges_enriched_by": """
        MATCH (a:{label}) WHERE a.id > $cursor
        WITH a ORDER BY a.id LIMIT $limit
        MATCH (a)-[r:ENRICHED_BY]->(o:OsmFeature)
        RETURN a.id AS src_id, '{label}' AS src_label,
               o.id AS dst_osm_node_id, o.osm_id AS dst_osm_id, o.osm_kind AS dst_osm_kind,
               r.jaccard AS jaccard, r.overlap_ratio AS overlap_ratio,
               r.intersection_area AS intersection_area,
               r.match_type AS match_type, r.is_primary AS is_primary
    """,
    "edges_has_poi": """
        MATCH (b:{label}) WHERE b.id > $cursor
        WITH b ORDER BY b.id LIMIT $limit
        MATCH (b)-[r:HAS_POI]->(o:OsmFeature)
        RETURN b.id AS building_id, o.id AS poi_node_id, o.osm_id AS poi_osm_id,
               o.osm_amenity AS amenity, o.osm_shop AS shop, o.osm_name AS name,
               r.distance_m AS distance_m
    """,
    "edges_located_in": """
        MATCH (b:{label}) WHERE b.id > $cursor
        WITH b ORDER BY b.id LIMIT $limit
        MATCH (b)-[:LOCATED_IN]->(d:District)
        RETURN b.id AS building_id, d.id AS district_id, d.name AS district_name
    """,
    "edges_has_lod3_facade": """
        MATCH (b:{label}) WHERE b.id > $cursor
        WITH b ORDER BY b.id LIMIT $limit
        MATCH (b)-[r:HAS_LOD3_FACADE]->(s)
        RETURN b.id AS building_id, s.id AS surface_id, s.surface_type AS surface_type,
               r.confidence AS confidence, r.method AS method,
               r.method_version AS method_version, r.lod AS lod,
               r.source AS source, r.source_type AS source_type
    """,
}

# per table: the alias the pagination cursor reads, and the driving label(s).
# A table with several driving labels is exported by running the same query once
# per label and concatenating (ENRICHED_BY starts at buildings and at other city
# objects, which have separate label indexes).
CURSOR_ALIAS = {
    "nodes_building": "id", "nodes_osmfeature": "id", "nodes_cityobject": "id",
    "edges_enriched_by": "src_id", "edges_has_poi": "building_id",
    "edges_located_in": "building_id", "edges_has_lod3_facade": "building_id",
}
DRIVING_LABELS = {
    "edges_enriched_by": ["Building", "CityObject"],
    "edges_has_poi": ["Building"],
    "edges_located_in": ["Building"],
    "edges_has_lod3_facade": ["Building"],
}


def write_table(rows, columns, out_dir: Path, name: str, fmt: str) -> Path:
    path = out_dir / f"{name}.{fmt}"
    if fmt == "parquet":
        import pyarrow as pa
        import pyarrow.parquet as pq
        table = pa.table({c: pa.array([r.get(c) for r in rows]) for c in columns})
        pq.write_table(table, path, compression="snappy")
    else:
        import csv
        with path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--only", action="append", choices=sorted(TABLES),
                    help="export only this table (repeatable)")
    ap.add_argument("--batch-size", type=int, default=50_000)
    ap.add_argument("--format", choices=["parquet", "csv"],
                    default="parquet" if HAVE_ARROW else "csv")
    ap.add_argument("--uri", default=os.environ.get("NEO4J_URI", "bolt://localhost:7687"))
    ap.add_argument("--user", default=os.environ.get("NEO4J_USER", "neo4j"))
    ap.add_argument("--password", default=os.environ.get("NEO4J_PASSWORD", "neo4jneo4j"))
    args = ap.parse_args()

    if args.format == "parquet" and not HAVE_ARROW:
        sys.exit("parquet output needs pyarrow: pip install pyarrow (or use --format csv)")

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = args.only or list(TABLES)

    manifest = {"format": args.format, "batch_size": args.batch_size, "tables": {}}
    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password),
                                  notifications_min_severity="OFF")
    try:
        with driver.session() as session:
            datasets = [dict(r) for r in session.run(
                "MATCH (d:Dataset) RETURN d.name AS name, d.crs AS crs, "
                "d.source_crs AS source_crs ORDER BY d.name")]
            manifest["datasets"] = datasets
            for d in datasets:
                print(f"dataset: {d['name']} ({d['crs']})")

            for name in wanted:
                cursor_col = CURSOR_ALIAS[name]
                rows, columns = [], None
                for label in DRIVING_LABELS.get(name, [None]):
                    query = TABLES[name].replace("{label}", label) if label else TABLES[name]
                    cursor = ""
                    while True:
                        batch = [dict(r) for r in session.run(
                            query, cursor=cursor, limit=args.batch_size)]
                        if not batch:
                            break
                        if columns is None:
                            columns = list(batch[0].keys())
                        rows.extend(batch)
                        new_cursor = batch[-1][cursor_col]
                        if new_cursor == cursor:  # one node wider than a whole batch
                            break
                        cursor = new_cursor
                        print(f"  {name}: {len(rows):,} rows", end="\r", flush=True)
                if not rows:
                    print(f"  {name}: 0 rows (absent in this city), skipped")
                    manifest["tables"][name] = {"rows": 0, "written": False,
                                                "query": " ".join(query.split())}
                    continue
                path = write_table(rows, columns, out_dir, name, args.format)
                print(f"  {name}: {len(rows):,} rows -> {path.name}          ")
                manifest["tables"][name] = {"rows": len(rows), "written": True,
                                           "columns": columns,
                                           "file": path.name,
                                           "query": " ".join(query.split())}
    finally:
        driver.close()

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out_dir}")
    print("manifest.json records the row counts, column lists, and the exact "
          "queries used, so any table can be traced back to the graph.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
