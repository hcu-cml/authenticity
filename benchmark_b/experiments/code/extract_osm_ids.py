"""Hamburg OsmBuilding / OsmPOI ids in the loader's node order (ORDER BY elementId), verified against the
cached graph's positions -- needed to map M-set (gml_id, osm_id) pairs onto graph edges (B3)."""
import os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_targets import kit_password, BDIR, OUT

def main(city="hamburg"):
    from neo4j import GraphDatabase
    g = torch.load(os.path.join(BDIR, f"graph_{city}.pt"), weights_only=False)
    drv = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", kit_password()))
    with drv.session(database="neo4j") as s:
        rows = s.run("MATCH (o:OsmBuilding) RETURN elementId(o) AS eid, o.id AS id, o.center_x AS cx, "
                     "o.center_y AS cy ORDER BY eid").data()
    drv.close()
    pos = g["OsmBuilding"].pos.numpy().astype(np.float64)
    assert len(rows) == pos.shape[0], (len(rows), pos.shape)
    c = np.array([[r["cx"] or 0.0, r["cy"] or 0.0] for r in rows], dtype=np.float32).astype(np.float64)
    bad = int((np.abs(c - pos).max(1) > 1e-3).sum())
    print(f"OsmBuilding n={len(rows)}, misaligned={bad}")
    assert bad == 0
    np.savez_compressed(os.path.join(OUT, f"{city}_osm_ids.npz"), osm_id=np.array([r["id"] for r in rows], dtype=object))

if __name__ == "__main__":
    main(*sys.argv[1:])
