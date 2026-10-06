"""B3 prep -- export roof-material predictions for EVERY Hamburg Building, so the R-set (manually orthophoto-verified labels) can be scored the moment the labels arrive (score_b3.py).

Per method, seed 0 (Table 6/roof-material configuration, run once):
  oof_<m>     spatial 5-fold out-of-fold prediction (splits.make_splits_roof_material, raw 5 classes):
              defined for buildings WITH an ML label (each tested exactly once); -1 otherwise.
  imp_<m>     imputation: trained on ALL ML-labelled buildings, predicted for every building; this is
              the prediction to score on R-set buildings WITHOUT an ML label (the true imputation targets).
Methods: probe (attr-only), gnn (V0, agnostic GraphSAGE), gnn_aware (V1), rgcn (tied-best non-aware GNN
in tab:repL-roofmat), lgbm_1hop (strongest non-graph baseline from B4).
Leakage: the model inputs never contain OSM roof:material (OsmBuilding features are cx, cy,
roof_shape one-hot, levels -- asserted below); OSM roof:material must not be used as a verified label.

Writes results/b3_roofmat_predictions.csv.gz (gml_id, ml_label, fold, oof_*, imp_*).
"""
import os, sys, time

import numpy as np
import pandas as pd
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
BDIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BDIR); sys.path.insert(0, HERE)
import _setup_paths  # noqa: E402,F401  (adds shared/, t1_imputation/, ... to sys.path)
import s5_train as S            # noqa: E402
import splits as SP             # noqa: E402
import b4_baselines             # noqa: E402,F401  (registers lgbm_1hop in S.METHODS)

METHODS = ["probe", "gnn", "gnn_aware", "rgcn", "lgbm_1hop"]
SEED = 0


def main():
    device = S.pick_device()
    data = torch.load(os.path.join(BDIR, "graph_hamburg.pt"), weights_only=False)
    assert not any("material" in f for f in data["OsmBuilding"].feat_names), "OSM roof material in inputs"
    tg = np.load(os.path.join(HERE, "..", "targets", "hamburg.npz"), allow_pickle=True)
    names = data["Building"].roof_material_names
    sp = SP.make_splits_roof_material(data, SEED, k=5)["spatial_cv"]
    y, ncl = sp["y"], sp["n_classes"]
    fold = np.full(data["Building"].num_nodes, -1)
    for k, (_, te) in enumerate(sp["folds"]):
        fold[te.numpy()] = k
    df = pd.DataFrame({"gml_id": tg["gml_id"],
                       "ml_label": [names[v] if v >= 0 else "" for v in y.numpy()],
                       "db_predictedroofmaterial": tg["roof_material"], "spatial_fold": fold})
    assert ((df.ml_label != "") == (df.db_predictedroofmaterial != "")).all()
    lab = torch.tensor(y.numpy() >= 0)
    for m in METHODS:
        t0 = time.time()
        _, oof, _, _ = S.oof_predictions(data, m, SEED, use_prov=(m == "gnn_aware"), device=device,
                                         splitter=SP.make_splits_roof_material)
        imp = S.METHODS[m](data, y, lab, ncl, SEED, m == "gnn_aware", device=device).numpy()
        df[f"oof_{m}"] = [names[v] if v >= 0 else "" for v in oof]
        df[f"imp_{m}"] = [names[v] for v in imp]
        print(f"{m}: done in {time.time()-t0:.0f}s", flush=True)
    out = os.path.join(HERE, "..", "results", "b3_roofmat_predictions.csv.gz")
    df.to_csv(out, index=False)
    print("wrote", out, len(df))


if __name__ == "__main__":
    main()
