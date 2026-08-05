"""Fill the three missing Table 4 (tab:repL-main) cells on the laptop GPU (8 GB), from the cached
Hamburg graph (no Neo4j needed):
  - GAT (agnostic)  building-use macro-F1  (T2 function, spatial CV)   [amp/fp16 to fit 8 GB]
  - HGT             building-use macro-F1  (T2 function, spatial CV)   [fp32 full-batch]
  - DGI (self-sup)  height R^2             (T1, with storey kept, spatial CV)
Reports mean +/- std over 3 seeds, like Table 5. Writes missing_cells.json.
Note: raw height is only in Neo4j; the cache has the z-scored 'height' feature, used here as the
regression target (R^2 of a linear probe is ~scale-invariant) with height dropped from the encoder input.
"""
import json, time
import numpy as np
import torch
from sklearn.linear_model import Ridge
from torch_geometric.nn import DeepGraphInfomax

from neo4j_loader import load_or_cache
import s5_train as S
import splits as SP
from t1_regression import reg_metrics

SEEDS = (0, 1, 2)
EPOCHS = 150
g = load_or_cache("graph_hamburg.pt", verbose=False)
dev = S.pick_device()
print("device", dev, "| Buildings", g["Building"].num_nodes, flush=True)
out = {}


def clear():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def stamp(msg, t0):
    print(f"{msg} ({time.time()-t0:.0f}s)", flush=True)


# ---- 1. GAT building function (amp/fp16 full-batch) ----
t0 = time.time()
r = S.run_method(g, method="gat", seeds=SEEDS, splits=("spatial_cv",),
                 splitter=SP.make_splits_function, epochs=EPOCHS, amp=True)
out["T2function_GAT_macroF1"] = [round(r["spatial_cv"]["macro_mean"], 3), round(r["spatial_cv"]["macro_std"], 3)]
stamp(f"GAT building-use macro-F1 = {out['T2function_GAT_macroF1']}", t0); clear()

# ---- 2. HGT building function (fp32 full-batch) ----
t0 = time.time()
r = S.run_method(g, method="hgt", seeds=SEEDS, splits=("spatial_cv",),
                 splitter=SP.make_splits_function, epochs=EPOCHS)
out["T2function_HGT_macroF1"] = [round(r["spatial_cv"]["macro_mean"], 3), round(r["spatial_cv"]["macro_std"], 3)]
stamp(f"HGT building-use macro-F1 = {out['T2function_HGT_macroF1']}", t0); clear()

# ---- 3. DGI height R^2 (keep storey, drop height; spatial CV; Ridge probe) ----
fn = g["Building"].feat_names
target = g["Building"].x[:, fn.index("height")].numpy().astype(float)   # z-scored height
valid = np.ones(len(target), bool)                                      # Hamburg height coverage = full
pos = g["Building"].pos.numpy()


def dgi_embeddings(seed):
    S.set_seed(seed)
    d = g.clone()
    d["Building"].x = S.building_features(g, use_prov=False, drop=["height"])
    order = list(d.node_types)
    hom, off, tot = S._homogeneous_edge_index(d)
    x = S._padded_homogeneous_features(d, order, off, tot).to(dev)
    hom = hom.to(dev)
    c = {**S.CFG, "n2v_epochs": 50}
    dgi = DeepGraphInfomax(c["hidden"], S._DGIEncoder(c["hidden"]), S._dgi_summary, S._dgi_corruption).to(dev)
    opt = torch.optim.Adam(dgi.parameters(), lr=c["lr"])
    dgi.train()
    for _ in range(c["n2v_epochs"]):
        opt.zero_grad(); pz, nz, sm = dgi(x, hom); dgi.loss(pz, nz, sm).backward(); opt.step()
    dgi.eval()
    with torch.no_grad():
        z, _, _ = dgi(x, hom)
    b0, nb = off["Building"], d["Building"].num_nodes
    emb = z.cpu().numpy()[b0:b0 + nb]
    del x, hom, dgi, z; clear()
    return emb


t0 = time.time()
r2s = []
for s in SEEDS:
    emb = dgi_embeddings(s)
    folds, _ = SP.spatial_kfold(pos, s, k=5, labeled=valid)
    oof = np.full(len(target), np.nan)
    for tr, te in folds:
        tr, te = tr.numpy(), te.numpy()
        reg = Ridge(alpha=1.0).fit(emb[tr], target[tr])
        oof[te] = reg.predict(emb[te])
    m = ~np.isnan(oof)
    r2s.append(reg_metrics(target[m], oof[m])["R2"])
    print(f"  DGI seed {s} R2 = {r2s[-1]:.3f}", flush=True)
out["T1height_DGI_R2"] = [round(float(np.mean(r2s)), 3), round(float(np.std(r2s)), 3)]
stamp(f"DGI height R2 = {out['T1height_DGI_R2']}", t0)

json.dump(out, open("missing_cells.json", "w"), indent=2)
print("DONE " + json.dumps(out), flush=True)
