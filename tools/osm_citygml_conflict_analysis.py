#!/usr/bin/env python3
"""
osm_citygml_conflict_analysis.py — whole-city OSM × CityGML conflict / duplication stats.

For the AuthentiCity (KDD 2027) paper. After `ingest_osm.py` has fused OSM into the
pykci graph, this quantifies two kinds of CityGML↔OSM disagreement over the SAME
physical buildings, computed entirely as **Cypher queries over the knowledge graph**
(no external GIS join): the R-tree spatial index scoped the candidate footprints during
fusion, and the resulting `ENRICHED_BY` edges (carrying `match_type`, `jaccard`,
`overlap_ratio`) plus the namespaced `osm_*` / `predictedroofmaterial` properties make
both analyses plain graph traversals.

  1. GEOMETRIC / TOPOLOGICAL correspondence — how the two sources partition the same
     footprints into 1:1 / 1:n / n:1 / n:m cases (who models a building as one polygon
     vs. several). Read from the `match_type` on `ENRICHED_BY` edges; component counts
     per case are taken from the fusion summary produced by ingest_osm.py.

  2. ATTRIBUTE DUPLICATION / CONFLICT — where BOTH sources describe roof material
     (OSM `roof:material`, copied onto the enriched building as `osm_roof_material`, vs.
     our ML `predictedroofmaterial`), how often they agree once the OSM free-text
     vocabulary is folded to the 5 ML classes. This is the "dual-sourced attribute"
     story: for some cities OSM adds a second, independent roof opinion per building;
     for others there is no overlap at all.

Usage:
    py bench/osm_citygml_conflict_analysis.py \
        --dataset hamburg_citygml2_lod2_2025_roofmats.gml \
        --summary output/hamburg-260629.osm_osm_summary.md --city hamburg
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "neo4jneo4j")

# ── OSM roof:material free-text → the 5 ML roof-material classes ──────────────
# ML classes (predictedroofmaterial): roof_tiles, tar_paper, concrete, metal, glass.
# Unmapped values (slate, eternit, wood, shingle, thatch, plastic, grass, …) → None,
# reported separately, never silently forced into a class.
OSM_ROOFMAT_TO_ML = {
    "roof_tiles": "roof_tiles", "tile": "roof_tiles", "tiles": "roof_tiles",
    "clay": "roof_tiles", "clay_tiles": "roof_tiles", "terracotta": "roof_tiles",
    "ceramic": "roof_tiles", "pantile": "roof_tiles",
    "metal": "metal", "metal_sheet": "metal", "sheet_metal": "metal",
    "copper": "metal", "zinc": "metal", "tin": "metal", "steel": "metal",
    "aluminium": "metal", "aluminum": "metal", "lead": "metal",
    "corrugated_iron": "metal", "iron": "metal", "trapezium": "metal", "trapezoidal": "metal",
    "glass": "glass", "acrylic_glass": "glass",
    "concrete": "concrete", "reinforced_concrete": "concrete",
    "tar_paper": "tar_paper", "bitumen": "tar_paper", "asphalt": "tar_paper",
    "roofing_felt": "tar_paper", "felt": "tar_paper", "tar": "tar_paper", "gravel": "tar_paper",
}


def normalize_osm_roofmat(raw):
    if not raw:
        return None
    v = str(raw).strip().lower()
    for tok in v.replace(",", ";").split(";"):
        tok = tok.strip()
        if tok in OSM_ROOFMAT_TO_ML:
            return OSM_ROOFMAT_TO_ML[tok]
    return None


def one(sess, q, **kw):
    return sess.run(q, **kw).single()


def main():
    ap = argparse.ArgumentParser(description="OSM × CityGML conflict / duplication statistics (graph queries).")
    ap.add_argument("--dataset", help="Target Dataset name (for the report header)")
    ap.add_argument("--summary", help="Path to the ingest_osm.py summary .md (for component-case counts)")
    ap.add_argument("--city", default="city", help="City label for the report")
    args = ap.parse_args()

    fusion_summary = {}
    if args.summary and Path(args.summary).exists():
        txt = Path(args.summary).read_text(encoding="utf-8")
        m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
        if m:
            fusion_summary = json.loads(m.group(1))

    driver = GraphDatabase.driver(
        NEO4J_URI, auth=NEO4J_AUTH,
        notifications_disabled_classifications={"DEPRECATION", "UNRECOGNIZED"})
    driver.verify_connectivity()

    with driver.session(database="neo4j") as sess:
        # ── base counts ───────────────────────────────────────────────────────
        pyk_total = one(sess, "MATCH (b:Building) RETURN count(b) AS c")["c"]
        pyk_rm = one(sess, "MATCH (b:Building) WHERE b.predictedroofmaterial IS NOT NULL "
                           "RETURN count(b) AS c")["c"]
        osm_bld = one(sess, "MATCH (o:OsmFeature {osm_kind:'building'}) RETURN count(o) AS c")["c"]
        osm_bld_rm = one(sess, "MATCH (o:OsmFeature {osm_kind:'building'}) "
                               "WHERE o.osm_roof_material IS NOT NULL RETURN count(o) AS c")["c"]
        pyk_matched = one(sess, "MATCH (b:Building)-[:ENRICHED_BY]->(:OsmFeature) "
                                "RETURN count(DISTINCT b) AS c")["c"]
        osm_matched = one(sess, "MATCH (:Building)-[:ENRICHED_BY]->(o:OsmFeature) "
                                "RETURN count(DISTINCT o) AS c")["c"]
        pois = one(sess, "MATCH (:Building)-[:HAS_POI]->(:OsmFeature) RETURN count(*) AS c")["c"]

        # ── footprint correspondence: distinct bldgs / OSM per case ────────────
        case_rows = list(sess.run(
            "MATCH (b:Building)-[r:ENRICHED_BY]->(o:OsmFeature {osm_kind:'building'}) "
            "RETURN r.match_type AS case, count(DISTINCT b) AS pyk, "
            "count(DISTINCT o) AS osm, count(r) AS edges"))
        by_case = {r["case"]: {"pykci": r["pyk"], "osm": r["osm"], "edges": r["edges"]}
                   for r in case_rows}

        # ── roof-material duplication / conflict ───────────────────────────────
        rm_rows = list(sess.run(
            "MATCH (b:Building) WHERE b.predictedroofmaterial IS NOT NULL "
            "AND b.osm_roof_material IS NOT NULL "
            "RETURN b.predictedroofmaterial AS ml, toLower(toString(b.osm_roof_material)) AS osm, "
            "count(*) AS n ORDER BY n DESC"))
        dual = agree = disagree = unmappable = 0
        confusion = defaultdict(lambda: defaultdict(int))
        raw_vals = defaultdict(int)
        for r in rm_rows:
            ml, osm_raw, n = r["ml"], r["osm"], r["n"]
            dual += n
            raw_vals[osm_raw] += n
            osm_ml = normalize_osm_roofmat(osm_raw)
            if osm_ml is None:
                unmappable += n
            elif osm_ml == ml:
                agree += n
                confusion[ml][osm_ml] += n
            else:
                disagree += n
                confusion[ml][osm_ml] += n

        # ── numeric dual-sourced attributes: height + storeys ──────────────────
        hrow = one(sess, """
          MATCH (b:Building) WHERE b.osm_height IS NOT NULL AND b.measured_height IS NOT NULL
            AND toFloat(b.measured_height) > -999
          WITH toFloat(b.osm_height) AS oh, b.measured_height AS mh
          WHERE oh IS NOT NULL AND oh > -999
          WITH abs(oh - mh) AS d
          RETURN count(*) AS n, round(avg(d) * 100) / 100.0 AS mean_d,
                 round(percentileCont(d, 0.5) * 100) / 100.0 AS median_d,
                 sum(CASE WHEN d <= 2.0 THEN 1 ELSE 0 END) AS within_2m,
                 sum(CASE WHEN d > 5.0 THEN 1 ELSE 0 END) AS over_5m""")
        srow = one(sess, """
          MATCH (b:Building) WHERE b.osm_building_levels IS NOT NULL
            AND b.storeys_above_ground IS NOT NULL
          WITH toFloat(b.osm_building_levels) AS ol, toFloat(b.storeys_above_ground) AS al
          WHERE ol IS NOT NULL AND al IS NOT NULL
          RETURN count(*) AS n, sum(CASE WHEN ol = al THEN 1 ELSE 0 END) AS exact,
                 sum(CASE WHEN abs(ol - al) <= 1 THEN 1 ELSE 0 END) AS within_1""")
        rm_net_new = one(sess, "MATCH (b:Building) WHERE b.osm_roof_material IS NOT NULL "
                               "AND b.predictedroofmaterial IS NULL RETURN count(b) AS c")["c"]

        report = {
            "city": args.city,
            "dataset": args.dataset,
            "counts": {
                "pykci_buildings": pyk_total,
                "pykci_with_pred_roofmat": pyk_rm,
                "osm_buildings": osm_bld,
                "osm_buildings_with_roofmat": osm_bld_rm,
                "pykci_buildings_matched": pyk_matched,
                "osm_buildings_matched": osm_matched,
                "pykci_enrich_rate": round(pyk_matched / pyk_total, 4) if pyk_total else 0.0,
                "osm_match_rate": round(osm_matched / osm_bld, 4) if osm_bld else 0.0,
                "pois_attached": pois,
            },
            "footprint_correspondence": {
                "by_case_buildings": by_case,
                "components_per_case": fusion_summary.get("match_cases", {}),
                "fusion_summary_by_kind": fusion_summary.get("by_kind", {}),
                "orphans": fusion_summary.get("orphans"),
                "orphans_by_reason": fusion_summary.get("orphans_by_reason", {}),
            },
            "roof_material_conflict": {
                "dual_sourced_buildings": dual,
                "agree": agree,
                "disagree": disagree,
                "osm_value_unmappable_to_ml": unmappable,
                "agreement_rate_over_mappable": round(agree / (agree + disagree), 4)
                                                if (agree + disagree) else None,
                "osm_roofmat_on_unpredicted_buildings": rm_net_new,
                "osm_roofmat_raw_values": dict(sorted(raw_vals.items(), key=lambda kv: -kv[1])),
                "confusion_ml_pred_x_osm": {p: dict(c) for p, c in confusion.items()},
            },
            "height_conflict": dict(hrow) if hrow and hrow["n"] else {"n": 0},
            "storeys_conflict": dict(srow) if srow and srow["n"] else {"n": 0},
        }

    driver.close()
    md = render_markdown(report)
    for outdir in (Path("output/stats"), Path("bench/out")):
        outdir.mkdir(parents=True, exist_ok=True)
    stem = f"osm_conflict_{args.city}"
    (Path("output/stats") / f"{stem}.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (Path("output/stats") / f"{stem}.md").write_text(md, encoding="utf-8")
    (Path("bench/out") / f"{stem}.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"\nWrote output/stats/{stem}.json and bench/out/{stem}.md")


def render_markdown(r):
    c, fc, rm = r["counts"], r["footprint_correspondence"], r["roof_material_conflict"]
    L = []
    A = L.append
    A(f"# OSM × CityGML conflict analysis — {r['city']}\n")
    A(f"Dataset `{r['dataset']}`. All figures computed by Cypher queries over the fused graph.\n")
    A("## 1. Footprint correspondence (geometric / topological)\n")
    A(f"- CityGML (pykci) buildings: **{c['pykci_buildings']:,}**")
    A(f"- OSM buildings: **{c['osm_buildings']:,}**")
    A(f"- CityGML buildings enriched (≥1 OSM match): **{c['pykci_buildings_matched']:,}** "
      f"({c['pykci_enrich_rate']*100:.1f} %)")
    A(f"- OSM buildings matched: **{c['osm_buildings_matched']:,}** "
      f"({c['osm_match_rate']*100:.1f} %)\n")
    A("| Case | Components | CityGML bldgs | OSM bldgs | edges |")
    A("|------|-----------:|--------------:|----------:|------:|")
    comps = fc["components_per_case"]
    for case in ("1:1", "1:n", "n:1", "n:m"):
        bc = fc["by_case_buildings"].get(case, {})
        A(f"| {case} | {comps.get(case, 0):,} | {bc.get('pykci', 0):,} | "
          f"{bc.get('osm', 0):,} | {bc.get('edges', 0):,} |")
    A("")
    A("## 2. Roof-material attribute duplication / conflict\n")
    A(f"- CityGML buildings with ML-predicted roof material: **{c['pykci_with_pred_roofmat']:,}**")
    A(f"- OSM buildings carrying `roof:material`: **{c['osm_buildings_with_roofmat']:,}**")
    A(f"- **Dual-sourced** buildings (ML prediction AND matched OSM `roof:material`): "
      f"**{rm['dual_sourced_buildings']:,}**")
    if rm["dual_sourced_buildings"]:
        A(f"  - agree (OSM vocab folded to the 5 ML classes): **{rm['agree']:,}**")
        A(f"  - disagree: **{rm['disagree']:,}**")
        A(f"  - OSM value with no ML class: {rm['osm_value_unmappable_to_ml']:,}")
        if rm["agreement_rate_over_mappable"] is not None:
            A(f"  - agreement over mappable pairs: **{rm['agreement_rate_over_mappable']*100:.1f} %**")
    A("\nRaw OSM `roof:material` values on dual-sourced buildings:\n")
    if rm["osm_roofmat_raw_values"]:
        A("| value | count |")
        A("|-------|------:|")
        for v, n in list(rm["osm_roofmat_raw_values"].items())[:25]:
            A(f"| {v} | {n:,} |")
    else:
        A("_(none)_")
    if rm["confusion_ml_pred_x_osm"]:
        cols = sorted({k for d in rm["confusion_ml_pred_x_osm"].values() for k in d})
        A("\nConfusion (rows = ML prediction, cols = OSM normalized):\n")
        A("| ML \\ OSM | " + " | ".join(cols) + " |")
        A("|" + "---|" * (len(cols) + 1))
        for p, d in sorted(rm["confusion_ml_pred_x_osm"].items()):
            A(f"| {p} | " + " | ".join(str(d.get(cc, 0)) for cc in cols) + " |")
    hc, sc = r.get("height_conflict", {}), r.get("storeys_conflict", {})
    if hc.get("n"):
        A("\n## 2b. Height duplication / conflict (surveyed vs OSM)\n")
        A(f"- Dual-sourced (numeric `osm_height` AND surveyed `measured_height`): **{hc['n']:,}**")
        A(f"  - median |Δh| = **{hc['median_d']} m**, mean {hc['mean_d']} m")
        A(f"  - within 2 m: {hc['within_2m']:,} ({hc['within_2m']/hc['n']*100:.1f} %)"
          f" · off by >5 m: {hc['over_5m']:,} ({hc['over_5m']/hc['n']*100:.1f} %)")
    if sc.get("n"):
        A("\n## 2c. Storeys duplication / conflict (ALKIS vs OSM levels)\n")
        A(f"- Dual-sourced (`osm_building_levels` AND `storeys_above_ground`): **{sc['n']:,}**")
        A(f"  - exact agreement: {sc['exact']:,} ({sc['exact']/sc['n']*100:.1f} %)"
          f" · within ±1: {sc['within_1']:,} ({sc['within_1']/sc['n']*100:.1f} %)")
    if rm.get("osm_roofmat_on_unpredicted_buildings") is not None:
        A(f"\n- OSM roof material on buildings WITHOUT an ML prediction (net-new coverage): "
          f"**{rm['osm_roofmat_on_unpredicted_buildings']:,}**")
    A("\n## 3. Other OSM contributions\n")
    A(f"- OSM features by kind: `{fc['fusion_summary_by_kind']}`")
    A(f"- POIs attached to a containing building: **{c['pois_attached']:,}**")
    if fc.get("orphans") is not None:
        A(f"- Net-new OSM orphans (no cadastral counterpart): **{fc['orphans']:,}** "
          f"`{fc.get('orphans_by_reason', {})}`")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
