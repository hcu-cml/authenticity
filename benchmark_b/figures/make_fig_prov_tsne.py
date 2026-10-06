"""
Figure 4 (fig_prov_tsne.pdf): 2D t-SNE of Hamburg canonical-entity (Building) embeddings, agnostic
vs. provenance-aware encoder, colored by roof type, by OSM evidence coverage, and by ML-predicted
roof material (unlabeled buildings -- the ~50% the ML layer didn't cover -- grayed out, since T1's
roof-material task is precisely about predicting those). Reuses the exact encoders already
evaluated for T3 matching (t3_matching._embed_fn) -- the same learned embedding space the paper's
numbers are about, not a separate model trained just for this plot.

October 2026: uses the FIXED T3 protocol (protocol="disjoint"); the July figure came from the
legacy protocol (training positives in the message-passing graph, see t3_matching.train_encoder) and is
kept in the git history. Also writes fig_prov_tsne_metrics.json: k-NN label
purity of OSM coverage / ML-roof-material coverage in the FULL embedding (not the t-SNE), so the
caption's claims rest on a number, and the plain data-level association of the two coverage flags.

Run after graph_hamburg.pt exists (see run_full_experiments.py). Subsamples to a few thousand
buildings before running t-SNE (2D embedding of hundreds of thousands of points is both slow and
unreadable as a scatter plot).
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import _setup_paths  # noqa: F401

import json

import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.neighbors import NearestNeighbors

from neo4j_loader import load_or_cache
import t3_matching as T3

N_SUBSAMPLE = 4000
N_PURITY = 50000      # buildings used for the k-NN purity check (full-dimensional embedding)
K_NN = 10
PROTOCOL = "disjoint"
SEED = 0

BLUE, ORANGE = "#3B7EA1", "#D97706"


def get_embeddings(data, kind):
    r = T3.run_matching(data, kind=kind, seeds=(SEED,), epochs=150, k_neg=5, return_embeddings=True,
                        protocol=PROTOCOL)
    print(f"{kind}: T3 AUC={r['AUC'][0]:.3f} Hits@1={r['Hits@1'][0]:.3f} ({r['protocol']})", flush=True)
    return r["embeddings"]["Building"]


def knn_purity(emb, flag, k=K_NN):
    """Share of each point's k nearest neighbours (cosine, full embedding) with the same flag, and the
    chance level p^2 + (1-p)^2 a structure-free embedding would give."""
    nn = NearestNeighbors(n_neighbors=k + 1, metric="cosine").fit(emb)
    nb = nn.kneighbors(emb, return_distance=False)[:, 1:]
    p = flag.mean()
    return {"purity": float((flag[nb] == flag[:, None]).mean()), "chance": float(p**2 + (1 - p)**2),
            "share_true": float(p)}


def main():
    data = load_or_cache("graph_hamburg.pt", verbose=False)
    n = data["Building"].num_nodes
    rng = np.random.default_rng(SEED)
    idx = rng.choice(n, size=min(N_SUBSAMPLE, n), replace=False)

    roof = data["Building"].y.numpy()[idx]              # -1 = unlabeled
    roof_names = data["Building"].label_names
    roofmat = data["Building"].y_roof_material.numpy()[idx]   # -1 = not covered by the ML layer
    roofmat_names = data["Building"].roof_material_names
    # Fix (October 2026): OSM coverage = the building has >= 1 ENRICHED_BY edge (84.9% in Hamburg). The July
    # version used the osm_shared flag, which means "its OSM counterpart is shared with other CityGML
    # buildings" (12.4%), not "has an OSM match" -- the old legend was wrong.
    deg = np.bincount(data[T3.EDGE].edge_index[0].numpy(), minlength=n)
    has_osm_all = deg > 0
    has_osm = has_osm_all[idx]

    ml_all = data["Building"].y_roof_material.numpy() >= 0
    a, b = has_osm_all, ml_all
    metrics = {"protocol": PROTOCOL, "seed": SEED, "k": K_NN,
               "data_level": {"P(ML covered)": float(b.mean()),
                              "P(ML covered | OSM match)": float(b[a].mean()),
                              "P(ML covered | no OSM match)": float(b[~a].mean()),
                              "phi(OSM match, ML covered)": float(np.corrcoef(a, b)[0, 1])}}
    pidx = rng.choice(n, size=min(N_PURITY, n), replace=False)

    fig, axes = plt.subplots(2, 3, figsize=(11.5, 7.5))
    for row, kind in enumerate(["sage", "aware"]):
        full = get_embeddings(data, kind)
        metrics[kind] = {"osm_coverage": knn_purity(full[pidx], has_osm_all[pidx]),
                         "ml_coverage": knn_purity(full[pidx], ml_all[pidx])}
        print(kind, metrics[kind], flush=True)
        emb = full[idx]
        z = TSNE(n_components=2, random_state=SEED, init="pca", perplexity=30).fit_transform(emb)
        tag = "agnostic" if kind == "sage" else "aware"

        ax = axes[row][0]
        for cls in sorted(set(roof.tolist()) - {-1}):
            m = roof == cls
            ax.scatter(z[m, 0], z[m, 1], s=4, alpha=0.6, label=roof_names[cls])
        ax.set_title(f"{tag}: colored by roof type", fontsize=9)
        if row == 0:
            ax.legend(fontsize=6, markerscale=2, loc="best")

        ax = axes[row][1]
        ax.scatter(z[~has_osm, 0], z[~has_osm, 1], s=4, alpha=0.4, color="#999999", label="no OSM match")
        ax.scatter(z[has_osm, 0], z[has_osm, 1], s=4, alpha=0.6, color=BLUE, label="has OSM match")
        ax.set_title(f"{tag}: colored by OSM coverage", fontsize=9)
        if row == 0:
            ax.legend(fontsize=6, markerscale=2, loc="best")

        ax = axes[row][2]
        ax.scatter(z[roofmat < 0, 0], z[roofmat < 0, 1], s=4, alpha=0.25, color="#cccccc",
                  label="not ML-covered")
        for cls in sorted(set(roofmat.tolist()) - {-1}):
            m = roofmat == cls
            ax.scatter(z[m, 0], z[m, 1], s=4, alpha=0.6, label=roofmat_names[cls])
        ax.set_title(f"{tag}: colored by roof material", fontsize=9)
        if row == 0:
            ax.legend(fontsize=6, markerscale=2, loc="best")

    for ax in axes.flat:
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    fig.suptitle(f"Hamburg Building embeddings, t-SNE (n={len(idx)} subsampled)", fontsize=11)
    fig.tight_layout()
    fig.savefig("fig_prov_tsne.pdf")
    json.dump(metrics, open("fig_prov_tsne_metrics.json", "w"), indent=1)
    print(json.dumps(metrics, indent=1))
    print("wrote fig_prov_tsne.pdf")


if __name__ == "__main__":
    main()
