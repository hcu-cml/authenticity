"""Extract the T1 height target (and a few label-side properties) per city ONCE and cache them as
.npz, so the experiment reruns never need Neo4j again.

Why: the July B Neo4j (Enterprise eval) licence has expired; the Benchmark A kit's Neo4j 2025.10.1
Community serves the same five city graphs (one Docker volume per city, read-only). The target is
read exactly like t1_regression.load_target (ORDER BY elementId, same sentinel handling), and the
row order is VERIFIED against the cached graph_<city>.pt by comparing each Building's raw
center_x/center_y with data['Building'].pos -- if they don't match, we abort rather than misalign.

Usage: python extract_targets.py <city>   (the kit Neo4j must have <city> live on 127.0.0.1:7687)
"""
import os, sys, time
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
BDIR = os.path.abspath(os.path.join(HERE, "..", ".."))           # KDD_Benchmark/
KIT_ENV = os.path.join(BDIR, "..", "KDD_BenchmarkA", "benchA_rerun_kit_v1.0.1", "benchA_rerun_kit", ".env")
OUT = os.path.join(HERE, "..", "targets")


def kit_password():
    for line in open(KIT_ENV):
        if line.startswith("NEO4J_PASSWORD="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("no NEO4J_PASSWORD in kit .env")


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


def main(city):
    from neo4j import GraphDatabase
    t0 = time.time()
    drv = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", kit_password()))
    with drv.session(database="neo4j") as s:
        live = s.run("MATCH (x:Dataset) RETURN x.name AS n").single()["n"]
        print("live dataset:", live)
        rows = s.run("MATCH (b:Building) RETURN elementId(b) AS eid, b.id AS gid, "
                     "b.measured_height AS h, b.storeys_above_ground AS st, "
                     "b.bbox_min_z AS zmin, b.bbox_max_z AS zmax, "
                     "b.center_x AS cx, b.center_y AS cy, "
                     "b.predictedroofmaterial AS rm, b.osm_match_type AS mt "
                     "ORDER BY eid").data()
    drv.close()
    print(f"{len(rows)} Buildings read in {time.time()-t0:.0f}s")

    h = np.array([_f(r["h"]) for r in rows]); st = np.array([_f(r["st"]) for r in rows])
    zmin = np.array([_f(r["zmin"]) for r in rows]); zmax = np.array([_f(r["zmax"]) for r in rows])
    cx = np.array([_f(r["cx"]) for r in rows]); cy = np.array([_f(r["cy"]) for r in rows])

    # --- identical to t1_regression.load_target("measured_height") ---
    t = h.copy()
    t[np.abs(t) >= 9999] = np.nan
    miss = np.isnan(t)
    t[miss] = (zmax - zmin)[miss]
    t[t <= 0] = np.nan
    # storeys, identical to load_target("storeys_above_ground")
    s_ = st.copy(); s_[np.abs(s_) >= 9999] = np.nan; s_[s_ <= 0] = np.nan

    # --- alignment check against the cached graph ---
    g = torch.load(os.path.join(BDIR, f"graph_{city}.pt"), weights_only=False)
    pos = g["Building"].pos.numpy().astype(np.float64)
    assert pos.shape[0] == len(rows), f"count mismatch: graph {pos.shape[0]} vs db {len(rows)}"
    c = np.stack([np.nan_to_num(cx), np.nan_to_num(cy)], 1)
    # loader stored float32(_to_float(.., default 0.0))
    dev = np.abs(c.astype(np.float32).astype(np.float64) - pos).max(1)
    bad = int((dev > 1e-3).sum())
    print(f"alignment: max |dpos| = {dev.max():.6f}, rows off by >1mm: {bad}")
    assert bad == 0, "row order differs from the cached graph -- refusing to write a misaligned target"

    os.makedirs(OUT, exist_ok=True)
    np.savez_compressed(os.path.join(OUT, f"{city}.npz"),
                        height=t, storeys=s_, gml_id=np.array([r["gid"] for r in rows], dtype=object),
                        roof_material=np.array([r["rm"] or "" for r in rows], dtype=object),
                        osm_match_type=np.array([r["mt"] or "" for r in rows], dtype=object),
                        live_dataset=live)
    print(f"{city}: height n={int((~np.isnan(t)).sum())}, from bbox={int(miss.sum())}, "
          f"storeys n={int((~np.isnan(s_)).sum())}; wrote targets/{city}.npz ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main(sys.argv[1])
