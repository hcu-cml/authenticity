"""
Full five-city experiment run for the KDD submission: T1 height regression, T2 roof-type and
building-function classification, T3 cross-source matching -- agnostic vs. provenance-aware,
single-city and cross-city where the label supports it.

Run neo4j_loader.py --cache for each city first (see SETUP_WORKSTATION.md); this script only reads
the cached graph_<city>.pt files, so it never needs Neo4j itself.

SCOPE, and why (see PROGRESS.md S1 city survey for the underlying schema check):
  * T1 height:    all 5 cities. NYC and Zurich have no `measured_height` property at all, so their
                  target is derived from the bounding-box z-extent (t1_regression.load_target).
                  The cross-city leave-one-city-out numbers are this benchmark's central claim, so
                  they use CROSSCITY_SEEDS (10), not the default 3 -- reseeded once specifically to
                  check the effect wasn't noise (it held up; see PROGRESS.md S8-REAL).
  * T2 roof type: only Hamburg and Helsinki carry this label; the other three cities have none.
                  Single-city definitive run on the full Hamburg dump, plus a Hamburg<->Helsinki
                  cross-city transfer test (the only two-city pair where it is meaningful).
  * T2 function:  only Hamburg has usable coverage (Helsinki: 94/2980 buildings, too sparse).
  * T3 matching:  all 5 cities independently, both learned encoders (attr/sage/aware) and two
                  non-learned baselines (spatial-distance, attribute-similarity) -- a true
                  cross-city matching transfer (train the encoder on one city's correspondences,
                  test on another's) is future work.
  * Shallow embeddings (node2vec/metapath2vec) are reported at pilot scale only: their random-walk
    training does not scale to million-node graphs without a much larger batch size than this
    codebase currently uses, and that is out of scope for this run. DGI does not share this limit
    (a real inductive GNN encoder, not a per-node lookup table) and runs at full scale.

Writes results_fullscale.json.
"""
import json

import torch

from neo4j_loader import load_or_cache
import s5_train as S
import t1_regression as T1
import t3_matching as T3
import s8_crosscity as S8
import splits as SP

CITIES = ["hamburg", "helsinki", "nyc", "tokyo", "zurich"]
SEEDS = (0, 1, 2)
CROSSCITY_SEEDS = tuple(range(10))   # T1 cross-city is the headline result -- extra seeds for it
EPOCHS = 150


def load_all():
    print("Loading cached graphs...")
    graphs = {c: load_or_cache(f"graph_{c}.pt", database=c, city=c, verbose=False) for c in CITIES}
    for c in CITIES:
        print(f"  {c:10s} Buildings={graphs[c]['Building'].num_nodes}")
    return graphs


def run_t1(graphs):
    print("\n########## T1 -- height regression ##########")
    out = {"percity": {}, "crosscity": None, "hamburg_partner_ablation": {}, "storeys": {}}

    print("-- per-city honest baseline (spatial CV) --")
    for c in CITIES:
        res, n = T1.run_regression(graphs[c], "height", methods=("mean", "probe", "gnn", "gnn_aware"),
                                   seeds=SEEDS, splits=("spatial_cv",), epochs=EPOCHS, database=c)
        out["percity"][c] = {"res": res, "n": n}
        T1.print_regression(f"height ({c})", res, n)

    print(f"-- cross-city leave-one-city-out ({len(CROSSCITY_SEEDS)} seeds) --")
    targets = [T1.load_target("measured_height", database=c) for c in CITIES]
    cross = S8.crosscity_eval_regression([graphs[c] for c in CITIES], targets,
                                         methods=("probe", "gnn", "gnn_aware"),
                                         seeds=CROSSCITY_SEEDS, epochs=EPOCHS)
    out["crosscity"] = cross
    S8.print_crosscity_regression(cross)

    print("-- Hamburg collinear-partner ablation (does the graph beat a plain probe once the "
          "easy shortcut -- storey count -- is withheld?) --")
    for variant, also_drop in [("with_partner", ()), ("no_partner", ("storeys",))]:
        res, n = T1.run_regression(graphs["hamburg"], "height",
                                   methods=("mean", "probe", "gnn", "gat", "hgt", "han", "rgcn", "gnn_aware"),
                                   seeds=SEEDS, splits=("spatial_cv",), also_drop=also_drop,
                                   epochs=EPOCHS, database="hamburg")
        out["hamburg_partner_ablation"][variant] = {"res": res, "n": n}
        T1.print_regression(f"height, {variant}", res, n)

    print("-- storey count as its own target (only cities that carry it: Hamburg, Tokyo) --")
    for c in ("hamburg", "tokyo"):
        res, n = T1.run_regression(graphs[c], "storeys", methods=("mean", "probe", "gnn", "gnn_aware"),
                                   seeds=SEEDS, splits=("spatial_cv",), epochs=EPOCHS, database=c)
        out["storeys"][c] = {"res": res, "n": n}
        T1.print_regression(f"storeys ({c})", res, n)
    return out


def _to_merged_3class(g):
    """A copy of `g` whose roof-type label is the merged {Flat, Gable-family, Other} scheme instead
    of the raw ALKIS codes. Cross-city transfer combines Hamburg's 7 classes with Helsinki's, whose
    tail is nearly empty (see PROGRESS.md S1/S2); the raw label space would make the rare classes
    vanish on one side of the transfer, same reason the single-city spatial CV uses this merge."""
    y3, names3 = SP.merged_3class(g)
    g2 = g.clone()
    g2["Building"].y = torch.tensor(y3, dtype=torch.long)
    g2["Building"].label_codes = list(range(len(names3)))
    g2["Building"].label_names = names3
    return g2


def run_t2_roof(graphs):
    print("\n########## T2 -- roof-type classification ##########")
    out = {"hamburg": {}, "crosscity": None}

    print("-- Hamburg, full dump (388k buildings) --")
    for m in ("probe", "dgi", "gnn", "gat", "hgt", "han", "rgcn", "gnn_aware"):
        r = S.run_method(graphs["hamburg"], method=m, use_prov=(m == "gnn_aware"),
                         seeds=SEEDS, epochs=EPOCHS, n2v_epochs=50)
        out["hamburg"][m] = r
        S.print_result(m, r)

    print("-- Hamburg <-> Helsinki cross-city transfer (merged 3-class, the only two cities with "
          "this label) --")
    merged = [_to_merged_3class(graphs["hamburg"]), _to_merged_3class(graphs["helsinki"])]
    cross, ncl = S8.crosscity_eval(merged, methods=("gnn", "gnn_aware"), seeds=SEEDS, epochs=EPOCHS)
    out["crosscity"] = cross
    S8.print_crosscity(cross, ncl)
    return out


def run_t2_function(graphs):
    print("\n########## T2 -- building function/use (Hamburg only) ##########")
    out = {}
    for m in ("probe", "dgi", "gnn", "han", "rgcn", "gnn_aware"):
        r = S.run_method(graphs["hamburg"], method=m, use_prov=(m == "gnn_aware"), seeds=SEEDS,
                         epochs=EPOCHS, n2v_epochs=50, splitter=SP.make_splits_function)
        out[m] = r
        S.print_result(m, r)
    return out


def run_t1_roof_material(graphs):
    """T1's cross-source-completion instance: an external ML model predicts roof material for
    ~50% of Hamburg buildings; we predict it for the rest from graph structure. `probe` (no OSM
    exposure by construction) vs. the graph methods (which can see the matched OsmBuilding via
    message passing) IS the circularity check the task needs -- see PROGRESS.md's addendum for why
    that comparison is the right one given this schema (every edge out of Building touches OSM)."""
    print("\n########## T1 -- roof-material imputation, cross-source completion (Hamburg only) ##########")
    out = {}
    methods_use_prov = {"probe": False, "probe_prov": True, "gnn": False, "gat": False, "hgt": False,
                        "han": False, "rgcn": False, "dgi": False, "gnn_aware": True}
    for label, use_prov in methods_use_prov.items():
        m = label.replace("probe_prov", "probe")
        r = S.run_method(graphs["hamburg"], method=m, use_prov=use_prov, seeds=SEEDS, epochs=EPOCHS,
                         n2v_epochs=50, splitter=SP.make_splits_roof_material)
        out[label] = r
        S.print_result(label, r)
    return out


def run_t3(graphs):
    print("\n########## T3 -- cross-source matching, per city ##########")
    out = {}
    for c in CITIES:
        out[c] = {}
        for kind in ("spatial", "attrsim", "attr", "sage", "aware"):
            out[c][kind] = T3.run_matching(graphs[c], kind=kind, seeds=SEEDS, epochs=EPOCHS, k_neg=5)
        T3.print_matching(out[c])
    return out


def main():
    graphs = load_all()
    results = {
        "T1": run_t1(graphs),
        "T2_roof": run_t2_roof(graphs),
        "T2_function": run_t2_function(graphs),
        "T2_roof_material": run_t1_roof_material(graphs),
        "T3": run_t3(graphs),
        "_meta": {
            "seeds": list(SEEDS), "crosscity_seeds": list(CROSSCITY_SEEDS),
            "epochs": EPOCHS, "cities": CITIES,
            "n_buildings": {c: graphs[c]["Building"].num_nodes for c in CITIES},
        },
    }
    with open("results_fullscale.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nwrote results_fullscale.json")


if __name__ == "__main__":
    main()
