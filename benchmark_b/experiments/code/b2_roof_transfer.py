"""B2 -- Hamburg <-> Helsinki roof-type transfer (Table 17 protocol) with the B1 variants
and seeds 0-9.

Protocol = run_full_experiments.run_t2_roof's cross-city block: both graphs mapped to the merged
3-class label (Flat / Gable-family / Other, splits.merged_3class), combined with
s8_crosscity.combine_cities([hamburg, helsinki]), train on all labelled Buildings of one city, test
on all labelled Buildings of the other; macro-F1 over the 3 classes; 150 epochs, CFG defaults.
Variants as in b1_crosscity_ablation.py: V0 = 'gnn', V1 = 'gnn_aware', V2 = 'gnn_aware' with
uniform weights, V3 = 'gnn_aware' without x_prov. The roof label is read via a relation the loader
never adds to the graph, so there is no input column to drop here (unlike B1).

Writes results/b2_runs.jsonl (one line per run, resumable).
"""
import argparse, json, os, sys, time

import numpy as np
import torch
from sklearn.metrics import f1_score, accuracy_score

HERE = os.path.dirname(os.path.abspath(__file__))
BDIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BDIR)
import _setup_paths  # noqa: E402,F401  (adds shared/, t1_imputation/, ... to sys.path)
sys.path.insert(0, HERE)
import s5_train as S                                   # noqa: E402
import s8_crosscity as S8                              # noqa: E402
from run_full_experiments import _to_merged_3class     # noqa: E402
from b1_crosscity_ablation import code_hash            # noqa: E402

RES = os.path.join(HERE, "..", "results")


def predict(v, d, y, train, ncl, seed, device, c):
    tm = torch.tensor(train)
    if v == "V0":
        return S.gnn_predict(d, y, tm, ncl, seed, False, device=device, **c)
    if v == "V1":
        return S.gnn_aware_predict(d, y, tm, ncl, seed, True, device=device, **c)
    if v == "V2":
        saved = S.CONFIDENCE_RELS
        S.CONFIDENCE_RELS = set()
        try:
            return S.gnn_aware_predict(d, y, tm, ncl, seed, True, device=device, **c)
        finally:
            S.CONFIDENCE_RELS = saved
    if v == "V3":
        # gnn_aware_predict hard-codes use_prov=True; replicate it without x_prov
        S.set_seed(seed)
        from torch_geometric.nn import to_hetero
        import torch.nn.functional as F
        xd, ed = S._device_graph(d, use_prov=False, device=device)
        ewd = S._norm_edge_weight_dict(d, device)
        model = to_hetero(S.ProvGNN(c["hidden"], ncl, c["dropout"]), d.metadata(), aggr="sum").to(device)
        with torch.no_grad():
            model(xd, ed, ewd)
        opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
        yb, tr = y.to(device), tm.to(device)
        for _ in range(c["epochs"]):
            model.train(); opt.zero_grad()
            F.cross_entropy(model(xd, ed, ewd)["Building"][tr], yb[tr]).backward(); opt.step()
        model.eval()
        with torch.no_grad():
            return model(xd, ed, ewd)["Building"].argmax(1).cpu()
    raise ValueError(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", default="V0,V1,V2,V3")
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--out", default=os.path.join(RES, "b2_runs.jsonl"))
    a = ap.parse_args()
    lo, hi = a.seeds.split("-")
    seeds = range(int(lo), int(hi) + 1)
    device = S.pick_device()
    c = {k: v for k, v in S.CFG.items()}
    graphs = []
    for city in ("hamburg", "helsinki"):
        g = torch.load(os.path.join(BDIR, f"graph_{city}.pt"), weights_only=False)
        g.city = city
        g2 = _to_merged_3class(g); g2.city = city
        graphs.append(g2)
    d = S8.combine_cities(graphs)
    y = d["Building"].y
    ncl = int(y[y >= 0].max()) + 1
    cid, lab = d["Building"].city_id.numpy(), y.numpy() >= 0
    done = set()
    if os.path.exists(a.out):
        done = {(r["held_out"], r["variant"], r["seed"]) for r in map(json.loads, open(a.out))}
    chash = code_hash()
    for seed in seeds:
        for i, held in enumerate(d.cities):
            test, train = (cid == i) & lab, (cid != i) & lab
            for v in a.variants.split(","):
                if (held, v, seed) in done:
                    continue
                t1 = time.time()
                pred = predict(v, d, y, train, ncl, seed, device, c).numpy()
                yt, yp = y.numpy()[test], pred[test]
                rec = {"task": "T2_roof_crosscity_3class", "held_out": held, "variant": v, "seed": seed,
                       "macro_f1": float(f1_score(yt, yp, labels=list(range(ncl)), average="macro",
                                                  zero_division=0)),
                       "per_class_f1": f1_score(yt, yp, labels=list(range(ncl)), average=None,
                                                zero_division=0).round(4).tolist(),
                       "accuracy": float(accuracy_score(yt, yp)), "class_names": d["Building"].label_names,
                       "test_class_counts": np.bincount(yt, minlength=ncl).tolist(),
                       "n_test": int(test.sum()), "n_train": int(train.sum()),
                       "runtime_s": round(time.time() - t1, 2), "epochs": c["epochs"], "code": chash}
                with open(a.out, "a") as f:
                    f.write(json.dumps(rec) + "\n")
                print(f"[{time.strftime('%H:%M:%S')}] held={held:8s} {v} s{seed} "
                      f"F1={rec['macro_f1']:.4f} ({rec['runtime_s']:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
