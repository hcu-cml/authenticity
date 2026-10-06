"""T3 matching rerun (tab:repL-match) with the fixed protocol, all five cities, seeds 0-2.

For each city: non-learned spatial / attrsim (protocol-independent, run once) and the learned
attr / sage (V0, agnostic GraphSAGE) / aware (V1, Eq. 1) encoders under BOTH protocols of
t3_matching.train_encoder -- "legacy" (the paper's numbers, reproduced for pairing) and "disjoint"
(fixed: supervision edges removed from the message-passing graph). Same split as the paper: 30% of
ENRICHED_BY edges held out (random, per seed), k=5 spatially nearest non-matching OSM buildings as
hard negatives, dot-product decoder, BCE, 150 epochs, CFG defaults. Writes results/t3_runs.jsonl.
"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
BDIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BDIR)
import _setup_paths  # noqa: E402,F401  (adds shared/, t1_imputation/, ... to sys.path)
import s5_train as S       # noqa: E402
import t3_matching as T3   # noqa: E402

RES = os.path.join(HERE, "..", "results")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cities", default="helsinki,zurich,hamburg,nyc,tokyo")
    ap.add_argument("--kinds", default="spatial,attrsim,attr,sage,aware")
    ap.add_argument("--protocols", default="disjoint,legacy")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--out", default=os.path.join(RES, "t3_runs.jsonl"))
    a = ap.parse_args()
    device = S.pick_device()
    done = set()
    if os.path.exists(a.out):
        done = {(r["city"], r["kind"], r["protocol"], r["seed"]) for r in map(json.loads, open(a.out))}
    for city in a.cities.split(","):
        g = torch.load(os.path.join(BDIR, f"graph_{city}.pt"), weights_only=False)
        for seed in [int(s) for s in a.seeds.split(",")]:
            for kind in a.kinds.split(","):
                protos = ["n/a"] if kind in T3.NONLEARNED_KINDS else a.protocols.split(",")
                for proto in protos:
                    if (city, kind, proto, seed) in done:
                        continue
                    if device.type == "cuda":
                        torch.cuda.reset_peak_memory_stats()
                    t0 = time.time()
                    r = T3.run_matching(g, kind=kind, seeds=(seed,), epochs=150, k_neg=5,
                                        protocol="disjoint" if proto == "n/a" else proto, device=device)
                    rec = {"task": "T3_matching", "city": city, "kind": kind, "protocol": proto, "seed": seed,
                           "AUC": r["AUC"][0], "AP": r["AP"][0], "Hits@1": r["Hits@1"][0],
                           "n_pos": r["n_pos"], "n_test": r["n_test"], "runtime_s": round(time.time() - t0, 2),
                           "peak_vram_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)
                           if device.type == "cuda" else None}
                    with open(a.out, "a") as f:
                        f.write(json.dumps(rec) + "\n")
                    print(f"[{time.strftime('%H:%M:%S')}] {city:8s} {kind:8s} {proto:8s} s{seed} "
                          f"AUC={rec['AUC']:.3f} AP={rec['AP']:.3f} Hits@1={rec['Hits@1']:.3f} "
                          f"({rec['runtime_s']:.0f}s, {rec['peak_vram_gb']} GB)", flush=True)
                    if device.type == "cuda":
                        torch.cuda.empty_cache()
        del g


if __name__ == "__main__":
    main()
