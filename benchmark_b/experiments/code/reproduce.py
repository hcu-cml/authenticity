"""One command per table. Run from this directory with the project venv:

    python reproduce.py table6     # Table 6 (tab:repL-main): Hamburg roof type / building use / height, 3 seeds
    python reproduce.py table7     # Table 7 (tab:repL-crosscity), CORRECTED: T1 height leave-one-city-out, probe/V0/V1/V5,
                                   #   10 seeds, target column removed from the inputs (protocol "guarded")
    python reproduce.py table7_july  # the July/submitted Table 7 protocol (drop=[], target column left in the
                                   #   inputs -- see README.md, Corrections), for comparison only
    python reproduce.py table17    # Table 17 / Table 7 bottom: Hamburg<->Helsinki roof-type transfer, V0/V1, 3 seeds
    python reproduce.py t3         # T3 matching (tab:repL-match), 5 cities, 3 seeds, corrected + July protocol
    python reproduce.py b1         # B1 ablation: V0-V5 x {guarded, t7} x 10 seeds
    python reproduce.py b2         # B2 ablation: V0-V3, 10 seeds
    python reproduce.py b4         # B4 baselines: LightGBM, LightGBM+1hop, Simple-HGN (+ anchors), 3 seeds
    python reproduce.py report     # aggregate everything into results/*.csv + results/TABLES.md

Prerequisites: graph_<city>.pt caches in KDD_Benchmark/ (neo4j_loader.py --cache) and targets/<city>.npz
(extract_targets.py <city>, once per city, with that city live in Neo4j). After that no Neo4j is needed:
t1_regression.load_target is redirected to the cached targets below (identical values and row order --
extract_targets.py verifies the order against each graph's Building positions).
"""
import os, subprocess, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BDIR = os.path.abspath(os.path.join(HERE, "..", ".."))
PY = sys.executable


def _patch_targets():
    sys.path.insert(0, BDIR)
    import _setup_paths  # noqa: E402,F401  (adds shared/, t1_imputation/, ... to sys.path)
    import t1_regression as T1
    prop2key = {"measured_height": "height", "storeys_above_ground": "storeys"}

    def load_target(prop, database=None):
        return np.load(os.path.join(HERE, "..", "targets", f"{database}.npz"),
                       allow_pickle=True)[prop2key[prop]]
    T1.load_target = load_target


def table6():
    _patch_targets()
    import json
    import torch
    import s5_train as S, t1_regression as T1, splits as SP
    g = torch.load(os.path.join(BDIR, "graph_hamburg.pt"), weights_only=False)
    out = {"roof": {}, "function": {}, "height": None}
    for m in ("probe", "dgi", "gnn", "gat", "hgt", "han", "rgcn", "gnn_aware"):
        out["roof"][m] = S.run_method(g, method=m, use_prov=(m == "gnn_aware"), seeds=(0, 1, 2),
                                      epochs=150, n2v_epochs=50)
        S.print_result(m, out["roof"][m])
    for m in ("probe", "dgi", "gnn", "han", "rgcn", "gnn_aware"):
        out["function"][m] = S.run_method(g, method=m, use_prov=(m == "gnn_aware"), seeds=(0, 1, 2),
                                          epochs=150, n2v_epochs=50, splitter=SP.make_splits_function)
        S.print_result(m, out["function"][m])
    res, n = T1.run_regression(g, "height", methods=("mean", "probe", "gnn", "gat", "hgt", "han", "rgcn",
                                                     "gnn_aware"), seeds=(0, 1, 2), splits=("spatial_cv",),
                               epochs=150, database="hamburg")
    T1.print_regression("height (hamburg)", res, n)
    out["height"] = res
    json.dump(out, open(os.path.join(HERE, "..", "results", "table6_rerun.json"), "w"), indent=1, default=str)


def run(script, *args):
    subprocess.run([PY, os.path.join(HERE, script), *args], check=True, cwd=HERE)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what == "table6":
        table6()
    elif what == "table7":
        run("b1_crosscity_ablation.py", "--variants", "probe,V0,V1,V5", "--protocols", "guarded", "--seeds", "0-9")
    elif what == "table7_july":
        run("b1_crosscity_ablation.py", "--variants", "probe,V0,V1", "--protocols", "t7", "--seeds", "0-9")
    elif what == "table17":
        run("b2_roof_transfer.py", "--variants", "V0,V1", "--seeds", "0-2")
    elif what == "t3":
        run("t3_rerun.py")
    elif what == "b1":
        run("b1_crosscity_ablation.py", "--variants", "V2,V0,V1,V3,V4,V5,probe", "--protocols", "guarded,t7")
    elif what == "b2":
        run("b2_roof_transfer.py", "--variants", "V0,V1,V2,V3", "--seeds", "0-9")
    elif what == "b4":
        run("b4_baselines.py")
    elif what == "report":
        run("make_report.py")
    else:
        print(__doc__)
