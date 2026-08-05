"""
load_from_neo4j() — instantiate a CityGML+OSM urban KG as a PyG HeteroData.

This is step S3 of the study log: the formal object G = (V, E, τ, X) built in memory. It targets
roof-type node classification on `Building`, structured so BOTH benchmark arms work:

  * provenance-AGNOSTIC (notebook 1):  data['Building'].x  (intrinsic features) + graph structure.
  * provenance-AWARE   (notebook 2):  additionally
        data['Building'].x_prov                                (coverage / agreement features)
        data['Building','enriched_by','OsmBuilding'].edge_weight (confidence  w_ce, = jaccard)
        node-type `.source` tags                               (source typing  W_{s(e)})

PORTABILITY (other cities may lack facades / roof material / whole node types):
  The loader introspects the live schema (db.labels / db.relationshipTypes /
  db.schema.nodeTypeProperties) and DROPS any node type, feature, edge type, or label that is
  absent — it never assumes a property exists. Feature widths therefore vary per city; the PyG
  lazy modules (Linear(-1,...), SAGEConv((-1,-1),...)) absorb that with no code change. What was
  kept/dropped is recorded in `data.provenance_report` for the log.

SCALE (full dataset, big workstation):
  Node/edge reads are paged (SKIP/LIMIT over elementId order) so no single Cypher result buffers
  the whole graph at once. Bump `batch_size`. Training-side scaling (mini-batching, AMP, device)
  lives in s5_train.py.

LEAKAGE (README §1 pt 3):
  Label sources (HAS_ROOF_TYPE→RoofType, HAS_FUNCTION→BuildingFunction) are read ONLY to build y;
  those node types and edges are never added to the graph. Enforced by an assertion.

Env: NEO4J_URI (default neo4j://127.0.0.1:7687), NEO4J_USER (neo4j), NEO4J_PASSWORD.
"""
import os
import numpy as np
import torch
from torch_geometric.data import HeteroData

NEO4J_URI  = os.environ.get("NEO4J_URI",  "neo4j://127.0.0.1:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PWD  = os.environ.get("NEO4J_PASSWORD")

# metapath2vec template for this schema (Building↔OsmBuilding↔Building↔OsmPOI↔Building).
METAPATH = [
    ("Building", "enriched_by", "OsmBuilding"),
    ("OsmBuilding", "rev_enriched_by", "Building"),
    ("Building", "has_poi", "OsmPOI"),
    ("OsmPOI", "rev_has_poi", "Building"),
]

# ------------------------------------------------------------------ config (declarative & portable)
# Each feature: (out_name, property_or_special, kind). Absent properties are dropped automatically.
#   kinds: "num" z-score · "log_area" bbox→log1p area · "storeys" mask+median · "bool" 0/1
#          "onehot:<vocabkey>" one-hot over a fixed vocab
VOCAB = {"roof_shape": ["flat", "gabled", "hipped", "pitched", "pyramidal"]}

NODE_SPECS = {
    "Building": {
        "coords": ("center_x", "center_y"),
        "features": [
            ("height", "measured_height", "num"),
            ("log_area", "__bbox__", "log_area"),
            ("storeys", "storeys_above_ground", "storeys"),
            ("ground_z", "ground_z", "num"),
        ],
        "prov_features": [
            ("osm_match_count", "osm_match_count", "num"),
            ("osm_best_jaccard", "osm_best_jaccard", "num"),
            ("osm_shared", "osm_shared", "bool"),
            ("matched", "matched", "bool"),
            ("lod3_confidence", "lod3_confidence", "num"),
            ("lod3_enriched", "lod3_enriched", "bool"),
        ],
        "source": "citygml",
    },
    "OsmBuilding": {
        "coords": ("center_x", "center_y"),
        "features": [
            ("cx", "center_x", "num"),
            ("cy", "center_y", "num"),
            ("roof_shape", "osm_roof_shape", "onehot:roof_shape"),
            ("levels", "osm_building_levels", "num"),
        ],
        "source": "osm",
    },
    "OsmPOI": {
        "coords": ("center_x", "center_y"),
        "features": [
            ("cx", "center_x", "num"),
            ("cy", "center_y", "num"),
        ],
        "source": "osm",
    },
}

# (src_type, REL, dst_type, weight_property, out_relname). Added only if both endpoints + rel exist.
EDGE_SPECS = [
    ("Building", "ENRICHED_BY", "OsmBuilding", "jaccard", "enriched_by"),
    ("Building", "HAS_POI", "OsmPOI", "distance_m", "has_poi"),
]

# Labels read purely to build y; their nodes/edges are NEVER added to the graph (leakage guard).
# Three independent targets, each optional per city -- see PROGRESS.md S1/S2/S8-REAL for the
# per-city survey: roof type (Hamburg + Helsinki), building function/use (Hamburg only at usable
# coverage), and ML-predicted roof material (Hamburg only -- it's a model output, not a relation,
# so it has no `via_relation`, just the direct property).
LABEL_SPECS = {
    "roof": {
        "node": "Building",
        "via_relation": ("HAS_ROOF_TYPE", "RoofType", "code", "name"),
        "property_fallback": "roof_type_code",
    },
    "function": {
        "node": "Building",
        "via_relation": ("HAS_FUNCTION", "BuildingFunction", "code", "name"),
        "property_fallback": "function_code",
    },
    "roof_material": {
        "node": "Building",
        "via_relation": None,
        "property_fallback": "predictedroofmaterial",
    },
}
LABEL_SPEC = LABEL_SPECS["roof"]  # back-compat alias: most of this module only ever reads roof type


# --------------------------------------------------------------------------------- helpers
def _z(a):
    a = np.asarray(a, dtype=np.float32)
    if a.ndim == 1:
        a = a.reshape(-1, 1)
    return (a - a.mean(0)) / (a.std(0) + 1e-6)


def _to_float(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _schema(session):
    """Discover what actually exists: labels, relationship types, and props per label."""
    labels = {r["label"] for r in
              session.run("CALL db.labels() YIELD label RETURN label").data()}
    rels = {r["relationshipType"] for r in
            session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType").data()}
    props = {}
    for r in session.run("CALL db.schema.nodeTypeProperties() "
                         "YIELD nodeLabels, propertyName RETURN nodeLabels, propertyName").data():
        for lb in r["nodeLabels"]:
            props.setdefault(lb, set()).add(r["propertyName"])
    return labels, rels, props


def _run_paged(session, query, batch_size):
    """Run `query` (must accept $skip/$limit and an ORDER BY for a stable page order) page by page
    and concatenate the rows. Shared by node and edge reads below."""
    rows, skip = [], 0
    while True:
        chunk = session.run(query, skip=skip, limit=batch_size).data()
        rows.extend(chunk)
        if len(chunk) < batch_size:
            break
        skip += batch_size
    return rows


def _read_paged(session, label, return_props, batch_size):
    """Page nodes of `label` by elementId; RETURN elementId + requested props (nullable)."""
    proj = ", ".join(f"n.`{p}` AS `{p}`" for p in return_props)
    q = (f"MATCH (n:`{label}`) RETURN elementId(n) AS eid"
         f"{', ' + proj if proj else ''} ORDER BY eid SKIP $skip LIMIT $limit")
    return _run_paged(session, q, batch_size)


def _read_edges_paged(session, src, rel, dst, weight_prop, batch_size):
    """Page (src)-[rel]->(dst) edges by (src, dst) elementId, carrying an edge weight property
    (defaulting to 1.0 where absent, e.g. non-confidence relations like POI proximity)."""
    wp = f", coalesce(r.`{weight_prop}`, 1.0) AS w" if weight_prop else ", 1.0 AS w"
    q = (f"MATCH (a:`{src}`)-[r:`{rel}`]->(b:`{dst}`) "
         f"RETURN elementId(a) AS src, elementId(b) AS dst{wp} "
         f"ORDER BY src, dst SKIP $skip LIMIT $limit")
    return _run_paged(session, q, batch_size)


def _build_matrix(rows, feat_specs, present):
    """Assemble a feature matrix from the specs whose property is present. Returns (matrix, kept, dropped)."""
    cols, kept, dropped, colnames = [], [], [], []
    for name, prop, kind in feat_specs:
        if kind == "log_area":
            need = ["bbox_min_x", "bbox_max_x", "bbox_min_y", "bbox_max_y"]
            if not all(p in present for p in need):
                dropped.append(name); continue
            area = np.array([
                max(_to_float(r.get("bbox_max_x")) - _to_float(r.get("bbox_min_x")), 0.0) *
                max(_to_float(r.get("bbox_max_y")) - _to_float(r.get("bbox_min_y")), 0.0)
                for r in rows])
            cols.append(_z(np.log1p(area))); kept.append(name); colnames.append(name); continue
        if kind.startswith("onehot:"):
            if prop not in present:
                dropped.append(name); continue
            vocab = VOCAB[kind.split(":", 1)[1]]
            idx = {v: i for i, v in enumerate(vocab)}
            M = np.zeros((len(rows), len(vocab)), dtype=np.float32)
            for i, r in enumerate(rows):
                v = r.get(prop) or ""
                if v in idx:
                    M[i, idx[v]] = 1.0
            cols.append(M); kept.append(name); colnames += [f"{name}={v}" for v in vocab]; continue
        if prop not in present:
            dropped.append(name); continue
        if kind == "num":
            cols.append(_z([_to_float(r.get(prop)) for r in rows])); kept.append(name); colnames.append(name)
        elif kind == "bool":
            cols.append(np.array([[1.0 if r.get(prop) else 0.0] for r in rows], dtype=np.float32))
            kept.append(name); colnames.append(name)
        elif kind == "storeys":
            v = np.array([_to_float(r.get(prop)) for r in rows])
            pres = (v > 0).astype(np.float32)
            med = np.median(v[v > 0]) if (v > 0).any() else 0.0
            cols.append(_z(np.where(v > 0, v, med)))
            cols.append(pres.reshape(-1, 1)); kept.append(name + "+mask")
            colnames += [name, name + "_mask"]
        else:
            raise ValueError(f"unknown kind {kind}")
    if cols:
        return np.concatenate(cols, axis=1).astype(np.float32), kept, dropped, colnames
    return np.zeros((len(rows), 0), dtype=np.float32), kept, dropped, colnames


def _bbox_props_needed(specs):
    return ["bbox_min_x", "bbox_max_x", "bbox_min_y", "bbox_max_y"] \
        if any(k == "log_area" for _, _, k in specs) else []


def _read_label(session, spec, id_maps, labels, rels, props):
    """Read one categorical label (e.g. roof type) via its lookup relation, falling back to a raw
    property if the relation is absent (or if the spec has no relation at all -- e.g. an ML-predicted
    property like roof material, which is a plain field, not a lookup edge). Returns
    (y, codes, names) or (None, None, None) if this city has no usable signal for this label.

    Data-quality guard: some cities concatenate multiple sub-feature codes into one string
    (e.g. Helsinki roof codes like "1000;2100" when a building has several roof faces). Such
    composite values are not a clean single class, so they are treated as unlabeled rather than
    silently becoming their own bogus category.
    """
    node, via_relation, fallback = spec["node"], spec["via_relation"], spec.get("property_fallback")
    if node not in id_maps:
        return None, None, None
    y_by_eid = {}
    if via_relation is not None:
        rel, tgt, code_prop, name_prop = via_relation
        if rel in rels and tgt in labels:
            for r in session.run(
                f"MATCH (b:`{node}`)-[:`{rel}`]->(t:`{tgt}`) "
                f"RETURN elementId(b) AS eid, t.`{code_prop}` AS code, t.`{name_prop}` AS name"
            ).data():
                if r["code"] is not None and ";" not in str(r["code"]):
                    y_by_eid[r["eid"]] = (r["code"], r.get("name") or r["code"])
    if not y_by_eid and fallback and fallback in props.get(node, set()):
        for r in session.run(f"MATCH (b:`{node}`) RETURN elementId(b) AS eid, b.`{fallback}` AS code").data():
            if r["code"] is not None and ";" not in str(r["code"]):
                y_by_eid[r["eid"]] = (r["code"], r["code"])
    if not y_by_eid:
        return None, None, None

    code2name = {c: n for c, n in y_by_eid.values()}
    codes = sorted(code2name)
    code2y = {c: i for i, c in enumerate(codes)}
    names = [code2name[c] for c in codes]
    y = np.full(len(id_maps[node]), -1, dtype=np.int64)  # -1 = unlabeled
    for eid, i in id_maps[node].items():
        if eid in y_by_eid:
            y[i] = code2y[y_by_eid[eid][0]]
    return torch.tensor(y, dtype=torch.long), codes, names


# --------------------------------------------------------------------------------- main
def load_from_neo4j(uri=NEO4J_URI, user=NEO4J_USER, pwd=NEO4J_PWD, batch_size=50000,
                    database=None, city=None, verbose=True):
    """Load one graph. `database` selects a named Neo4j database (multi-city: one DBMS, one DB per
    city). `city` tags the result (`data.city`) for the cross-city harness."""
    from neo4j import GraphDatabase
    if pwd is None:
        raise RuntimeError("Set NEO4J_PASSWORD in the environment.")
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    d = HeteroData()
    report = {"nodes": {}, "edges": {}, "dropped_node_types": [], "dropped_edges": [], "label": {}}
    id_maps = {}

    with driver.session(database=database) if database else driver.session() as s:
        labels, rels, props = _schema(s)

        # -------- node types (skip absent labels) --------
        for nt, spec in NODE_SPECS.items():
            if nt not in labels:
                report["dropped_node_types"].append(nt); continue
            present = props.get(nt, set())
            feat_props = {p for _, p, k in spec["features"]
                          if not p.startswith("__") and not k.startswith("onehot:")} \
                | {p for _, p, k in spec["features"] if k.startswith("onehot:")}
            prov_props = {p for _, p, _ in spec.get("prov_features", [])}
            coord_props = set(spec.get("coords", ()))
            want = (feat_props | prov_props | coord_props
                    | set(_bbox_props_needed(spec["features"]))) & present
            rows = _read_paged(s, nt, sorted(want), batch_size)
            id_maps[nt] = {r["eid"]: i for i, r in enumerate(rows)}

            x, kept, dropped, colnames = _build_matrix(rows, spec["features"], present)
            d[nt].x = torch.tensor(x, dtype=torch.float)
            d[nt].feat_names = colnames
            d[nt].source = spec.get("source", "unknown")
            report["nodes"][nt] = {"n": len(rows), "feat_dim": x.shape[1],
                                   "kept": kept, "dropped": dropped}
            if spec.get("prov_features"):
                xp, kp, dp, pnames = _build_matrix(rows, spec["prov_features"], present)
                if xp.shape[1]:
                    d[nt].x_prov = torch.tensor(xp, dtype=torch.float)
                    d[nt].prov_names = pnames
                    report["nodes"][nt]["prov_kept"] = kp
            cx, cy = spec.get("coords", (None, None))
            if cx in present and cy in present:
                d[nt].pos = torch.tensor(
                    np.stack([[_to_float(r.get(cx)) for r in rows],
                              [_to_float(r.get(cy)) for r in rows]], 1), dtype=torch.float)
            d[nt]._rows = rows  # keep for label read (removed before return)

        # -------- labels (read only; never added as nodes/edges) --------
        for key, spec in LABEL_SPECS.items():
            y, codes, names = _read_label(s, spec, id_maps, labels, rels, props)
            if y is None:
                continue
            ln = spec["node"]
            if key == "roof":  # back-compat attribute names used throughout the rest of the codebase
                d[ln].y, d[ln].label_codes, d[ln].label_names = y, codes, names
            else:
                d[ln][f"y_{key}"] = y
                d[ln][f"{key}_codes"], d[ln][f"{key}_names"] = codes, names
            report["label"][key] = {"classes": len(codes), "names": names,
                                    "n_labeled": int((y >= 0).sum())}

        # -------- edges (skip if endpoints/rel absent) --------
        for src, rel, dst, wprop, outname in EDGE_SPECS:
            if src not in id_maps or dst not in id_maps or rel not in rels:
                report["dropped_edges"].append(outname); continue
            sm, dm = id_maps[src], id_maps[dst]
            e = _read_edges_paged(s, src, rel, dst, wprop, batch_size)
            si, di, w = [], [], []
            for r in e:
                if r["src"] in sm and r["dst"] in dm:
                    si.append(sm[r["src"]]); di.append(dm[r["dst"]]); w.append(_to_float(r["w"], 1.0))
            ei = torch.tensor(np.stack([si, di], 0), dtype=torch.long) if si else torch.empty((2, 0), dtype=torch.long)
            ew = torch.tensor(w, dtype=torch.float)
            d[src, outname, dst].edge_index = ei
            d[src, outname, dst].edge_weight = ew
            d[dst, "rev_" + outname, src].edge_index = ei.flip(0)
            d[dst, "rev_" + outname, src].edge_weight = ew
            report["edges"][outname] = ei.size(1)

    driver.close()

    for nt in d.node_types:          # drop scratch
        if "_rows" in d[nt]:
            del d[nt]._rows
    d.provenance_report = report
    d.city = city or (database or "default")

    for spec in LABEL_SPECS.values():
        if spec["via_relation"] is not None:
            assert spec["via_relation"][1] not in d.node_types, "leakage: label node in graph"
    if verbose:
        _print_shapes(d)
    return d


def _print_shapes(d):
    r = d.provenance_report
    print("=== HeteroData: G = (V, E, τ, X) ===")
    for nt in d.node_types:
        info = r["nodes"].get(nt, {})
        extra = " +prov[%d]" % d[nt].x_prov.size(1) if "x_prov" in d[nt] else ""
        drop = f"  dropped={info['dropped']}" if info.get("dropped") else ""
        print(f"  {nt:12s} n={d[nt].num_nodes:6d}  feat_dim={d[nt].x.size(1)}{extra}{drop}")
    for (s_, rel, t_) in d.edge_types:
        print(f"  ({s_} -{rel}-> {t_})".ljust(50), f"edges={d[s_, rel, t_].edge_index.size(1)}")
    if r["dropped_node_types"]:
        print("  (absent node types skipped:", r["dropped_node_types"], ")")
    if d.node_types and "y" in d[LABEL_SPEC["node"]]:
        lab = d[LABEL_SPEC["node"]]
        y = lab.y.numpy(); y = y[y >= 0]
        u, c = np.unique(y, return_counts=True)
        print(f"\nlabel: {len(lab.label_names)} classes, {len(y)} labeled")
        for cls, cnt in zip(u.tolist(), c.tolist()):
            print(f"  {cls}  {lab.label_names[cls]:22s} n={cnt}")
        print("  majority frac: %.3f" % (c.max() / c.sum()))
        assert lab.x.size(0) == lab.num_nodes
        for (s_, rel, t_) in d.edge_types:
            ei = d[s_, rel, t_].edge_index
            if ei.numel():
                assert int(ei[0].max()) < d[s_].num_nodes and int(ei[1].max()) < d[t_].num_nodes
        print("[assertions passed] shapes consistent, indices in-range, no label node in graph.")
    if "y_function" in d[LABEL_SPEC["node"]]:
        info = r["label"]["function"]
        print(f"function label: {info['classes']} classes, {info['n_labeled']} labeled")


def load_or_cache(path="graph.pt", rebuild=False, **kw):
    """Load the HeteroData from a cached file if present, else pull from Neo4j and cache it.

    Neo4j is only needed the FIRST time (or when rebuild=True). After that, training runs off the
    cached tensor with no database — copy `graph.pt` to the workstation and you need not host Neo4j
    there at all (for the current single-city dump). For the multi-city run, rebuild against that DB.
    """
    import os
    if not rebuild and os.path.exists(path):
        d = torch.load(path, weights_only=False)
        print(f"[cache] loaded {path}")
        return d
    d = load_from_neo4j(**kw)
    torch.save(d, path)
    print(f"[cache] wrote {path}")
    return d


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--database", default="hamburg", help="named Neo4j database to read")
    p.add_argument("--city", default=None, help="tag for data.city (defaults to --database)")
    p.add_argument("--cache", metavar="PATH", nargs="?", const="graph.pt", default=None,
                  help="extract once and cache to this .pt file (default graph.pt)")
    args = p.parse_args()
    city = args.city or args.database
    if args.cache:
        load_or_cache(args.cache, rebuild=True, database=args.database, city=city)
    else:
        load_from_neo4j(database=args.database, city=city)
