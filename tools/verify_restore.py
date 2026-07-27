#!/usr/bin/env python3
"""
verify_restore.py — check a restored AuthentiCity graph against the manifest that
was written when its dump was created.

Never trust a multi-gigabyte restore silently. This compares the live graph with
`dumps/counts/<city>_counts.txt`, confirms the expected Neo4j Spatial R-tree
layers exist and actually answer a query, and exits non-zero on any mismatch.
Run it before reporting any number from a restored graph.

Usage:
    python tools/verify_restore.py --city hamburg
    python tools/verify_restore.py --city tokyo --uri bolt://localhost:7687

Credentials default to the shipped Docker configuration and can be overridden
with --user/--password or the NEO4J_USER / NEO4J_PASSWORD environment variables.
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    from neo4j import GraphDatabase
except ImportError:                                            # pragma: no cover
    sys.exit("the neo4j Python driver is required: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
COUNTS_DIR = ROOT / "dumps" / "counts"

CITIES = ["hamburg", "helsinki", "zurich", "nyc", "tokyo"]

# manifest key -> (human label, Cypher returning a single count)
CHECKS = {
    "nodes":       ("nodes",              "MATCH (n) RETURN count(n) AS n"),
    "rels":        ("relationships",      "MATCH ()-[r]->() RETURN count(r) AS n"),
    "buildings":   ("Building nodes",     "MATCH (b:Building) RETURN count(b) AS n"),
    "OsmFeatures": ("OsmFeature nodes",   "MATCH (o:OsmFeature) RETURN count(o) AS n"),
    "ENRICHED_BY": ("ENRICHED_BY edges",  "MATCH ()-[r:ENRICHED_BY]->() RETURN count(r) AS n"),
    "HAS_POI":     ("HAS_POI edges",      "MATCH ()-[r:HAS_POI]->() RETURN count(r) AS n"),
    "CityObjects": ("CityObject nodes",   "MATCH (c:CityObject) RETURN count(c) AS n"),
    "bridges":     ("Bridge nodes",       "MATCH (b:Bridge) RETURN count(b) AS n"),
    "roofmat_predicted": ("buildings with a roof-material prediction",
                          "MATCH (b:Building) WHERE b.predictedroofmaterial IS NOT NULL "
                          "RETURN count(b) AS n"),
    "lod3_enriched": ("buildings with reconstructed LoD3 facades",
                      "MATCH (b:Building)-[:HAS_LOD3_FACADE]->() "
                      "RETURN count(DISTINCT b) AS n"),
    "id_synthesized": ("buildings on a synthesized id",
                       "MATCH (b:Building) WHERE b.id_synthesized "
                       "RETURN count(b) AS n"),
}

# R-tree layers each city must have. lod3_features is Hamburg-only.
EXPECTED_LAYERS = {c: ["features", "osm_features"] for c in CITIES}
EXPECTED_LAYERS["hamburg"] = ["features", "osm_features", "lod3_features"]


def parse_manifest(path: Path) -> dict:
    """Read the 'Verification counts:' block of a counts manifest."""
    expected, in_block = {}, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().lower().startswith("verification counts"):
            in_block = True
            continue
        if not in_block:
            continue
        m = re.match(r"\s+(\S+)\s+(\d+)", line)
        if m:
            expected[m.group(1)] = int(m.group(2))
    return expected


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--city", required=True, choices=CITIES)
    ap.add_argument("--uri", default=os.environ.get("NEO4J_URI", "bolt://localhost:7687"))
    ap.add_argument("--user", default=os.environ.get("NEO4J_USER", "neo4j"))
    ap.add_argument("--password", default=os.environ.get("NEO4J_PASSWORD", "neo4jneo4j"))
    ap.add_argument("--skip-spatial", action="store_true",
                    help="skip the R-tree checks (use if the Spatial plugin is absent)")
    args = ap.parse_args()

    manifest = COUNTS_DIR / f"{args.city}_counts.txt"
    if not manifest.exists():
        sys.exit(f"no manifest for {args.city}: {manifest}")
    expected = parse_manifest(manifest)
    if not expected:
        sys.exit(f"could not parse verification counts from {manifest}")

    print(f"city      : {args.city}")
    print(f"manifest  : {manifest.relative_to(ROOT)}")
    print(f"database  : {args.uri}\n")

    failures, checked = [], 0
    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password),
                                  notifications_min_severity="OFF")
    try:
        with driver.session() as session:
            # the dataset actually loaded, as a first sanity signal
            datasets = [(r["name"], r["crs"], r["source_crs"]) for r in session.run(
                "MATCH (d:Dataset) RETURN d.name AS name, d.crs AS crs, "
                "d.source_crs AS source_crs ORDER BY name")]
            for name, crs, source_crs in datasets:
                extra = f", reprojected from {source_crs}" if source_crs and source_crs != crs else ""
                print(f"  dataset   {name} ({crs}{extra})")
            if not datasets:
                failures.append("no Dataset node found: is this the right database?")
            print()

            for key, (label, query) in CHECKS.items():
                if key not in expected:
                    continue          # not part of this city's manifest, e.g. no LoD3
                actual = session.run(query).single()["n"]
                ok = actual == expected[key]
                checked += 1
                mark = "OK  " if ok else "FAIL"
                print(f"  [{mark}] {label:48} {actual:>12,}  expected {expected[key]:>12,}")
                if not ok:
                    failures.append(f"{label}: {actual} != {expected[key]}")

            if not args.skip_spatial:
                print()
                try:
                    layers = {r["name"] for r in session.run(
                        "CALL spatial.layers() YIELD name RETURN name")}
                except Exception as exc:                       # plugin missing
                    failures.append(f"spatial.layers() failed ({exc.__class__.__name__}): "
                                    "the Neo4j Spatial plugin is required for the spatial "
                                    "benchmark category")
                    layers = set()
                for want in EXPECTED_LAYERS[args.city]:
                    ok = want in layers
                    print(f"  [{'OK  ' if ok else 'FAIL'}] R-tree layer {want}")
                    if not ok:
                        failures.append(f"missing R-tree layer: {want}")
                if "features" in layers:
                    # a real query through the index, not just its presence: a 500 m
                    # window centred on an actual building must contain that building
                    row = session.run(
                        "MATCH (b:Building) WITH b LIMIT 1 "
                        "WITH b.center_x AS cx, b.center_y AS cy "
                        "CALL spatial.intersects('features', 'POLYGON((' + "
                        " toString(cx-500)+' '+toString(cy-500)+','+toString(cx+500)+' '+toString(cy-500)+','+"
                        " toString(cx+500)+' '+toString(cy+500)+','+toString(cx-500)+' '+toString(cy+500)+','+"
                        " toString(cx-500)+' '+toString(cy-500)+'))') YIELD node "
                        "RETURN count(node) AS n").single()
                    found = row["n"] if row else 0
                    ok = found > 0
                    print(f"  [{'OK  ' if ok else 'FAIL'}] R-tree bbox query answered "
                          f"({found:,} features in a 1 km window around a building)")
                    if not ok:
                        failures.append("the features R-tree returned nothing for a window "
                                        "centred on a building: the index is not usable")
    finally:
        driver.close()

    print()
    if failures:
        print(f"VERIFICATION FAILED ({len(failures)} problem(s)):")
        for f in failures:
            print("  !", f)
        print("\nReload the dump and re-run before reporting any number from this graph.")
        return 1
    print(f"VERIFICATION PASSED: {checked} count(s) and "
          f"{len(EXPECTED_LAYERS[args.city]) if not args.skip_spatial else 0} "
          f"spatial layer(s) match the manifest.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
