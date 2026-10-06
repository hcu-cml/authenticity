"""B5 -- release facts: split/fold assignment files, label-availability matrix, environment record.

Outputs (in ../release/):
  splits/<city>_folds.csv.gz   gml_id + spatial 5-fold id (KMeans tiles, splits.spatial_kfold) per task
                               and seed (-1 = not labelled for that task); the cross-city held-out
                               "fold" is simply the city column (leave-one-city-out).
  seeds.json                   seed lists per experiment.
  label_availability.csv/.md   labelled Buildings per task x city (the task-availability matrix).
  environment.txt              torch/PyG/CUDA/driver/GPU + pip freeze.
"""
import json, os, subprocess, sys

import numpy as np
import pandas as pd
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
BDIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BDIR)
import _setup_paths  # noqa: E402,F401  (adds shared/, t1_imputation/, ... to sys.path)
import splits as SP     # noqa: E402

CITIES = ["hamburg", "helsinki", "nyc", "tokyo", "zurich"]
OUT = os.path.join(HERE, "..", "release")
SEEDS_T6 = [0, 1, 2]


def folds_of(pos, labeled, seed):
    if labeled.sum() < 5:
        return np.full(len(labeled), -1)
    _, blocks = SP.spatial_kfold(pos, seed, k=5, labeled=labeled)
    return blocks


def main():
    os.makedirs(os.path.join(OUT, "splits"), exist_ok=True)
    rows = []
    for c in CITIES:
        g = torch.load(os.path.join(BDIR, f"graph_{c}.pt"), weights_only=False)
        tg = np.load(os.path.join(HERE, "..", "targets", f"{c}.npz"), allow_pickle=True)
        b = g["Building"]
        n = b.num_nodes
        pos = b.pos.numpy()
        h, st = tg["height"], tg["storeys"]
        labels = {"T1_height": ~np.isnan(h), "T1_storeys": ~np.isnan(st)}
        if "y" in b and "label_codes" in b:
            y3, _ = SP.merged_3class(g)
            labels["T2_roof_type"] = (b.y.numpy() >= 0)
            if y3 is not None:
                labels["T2_roof_type_3class"] = (y3 >= 0)
        if "y_function" in b:
            labels["T2_function"] = b.y_function.numpy() >= 0
        if "y_roof_material" in b:
            labels["T1_roof_material"] = b.y_roof_material.numpy() >= 0
        et = ("Building", "enriched_by", "OsmBuilding")
        n_pairs = int(g[et].edge_index.size(1)) if et in g.edge_types else 0
        multi = 0
        if et in g.edge_types:
            deg = np.bincount(g[et].edge_index[0].numpy(), minlength=n)
            multi = int((deg >= 2).sum())
        rows.append({"city": c, "buildings": n,
                     **{k: int(v.sum()) for k, v in labels.items()},
                     "T3_enriched_by_pairs": n_pairs,
                     "buildings_with_>=2_osm_matches": multi})
        df = pd.DataFrame({"gml_id": tg["gml_id"], "city": c})
        fold_tasks = {"T1_height": labels["T1_height"]}
        if c == "hamburg":
            for k in ("T2_roof_type_3class", "T2_function", "T1_roof_material", "T1_storeys"):
                fold_tasks[k] = labels[k]
        if c == "tokyo":
            fold_tasks["T1_storeys"] = labels["T1_storeys"]
        for task, lab in fold_tasks.items():
            for s in SEEDS_T6:
                df[f"fold_{task}_seed{s}"] = folds_of(pos, lab, s)
        df.to_csv(os.path.join(OUT, "splits", f"{c}_folds.csv.gz"), index=False)
        print(c, "done", flush=True)
    av = pd.DataFrame(rows).set_index("city").T
    av.to_csv(os.path.join(OUT, "label_availability.csv"))
    with open(os.path.join(OUT, "label_availability.md"), "w") as f:
        f.write(av.fillna(0).astype(int).to_markdown() + "\n")
    print(av)
    json.dump({"table6_single_city": SEEDS_T6, "table6_spatial_folds_k": 5,
               "table7_crosscity_and_B1": list(range(10)), "table17_original": SEEDS_T6,
               "B2": list(range(10)), "B4": SEEDS_T6, "B3_export": [0],
               "note": "S.set_seed(seed) before every model fit; spatial folds = KMeans(n_clusters=5, "
                       "n_init=10, random_state=seed) on labelled Buildings' (center_x, center_y)."},
              open(os.path.join(OUT, "seeds.json"), "w"), indent=2)
    env = [f"python {sys.version.split()[0]}", f"torch {torch.__version__} (CUDA runtime {torch.version.cuda})"]
    import torch_geometric
    env.append(f"torch_geometric {torch_geometric.__version__}")
    env.append(subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                               "--format=csv,noheader"], capture_output=True, text=True).stdout.strip())
    env.append("\n# pip freeze\n" + subprocess.run([sys.executable, "-m", "pip", "freeze"],
                                                  capture_output=True, text=True).stdout)
    open(os.path.join(OUT, "environment.txt"), "w").write("\n".join(env))


if __name__ == "__main__":
    main()
