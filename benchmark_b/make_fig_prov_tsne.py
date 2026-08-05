"""
Figure 4 (fig_prov_tsne.pdf): 2D t-SNE of Hamburg canonical-entity (Building) embeddings, agnostic
vs. provenance-aware encoder, colored by roof type, by OSM evidence coverage, and by ML-predicted
roof material (unlabeled buildings -- the ~50% the ML layer didn't cover -- grayed out, since T1's
roof-material task is precisely about predicting those). Reuses the exact encoders already
evaluated for T3 matching (t3_matching._embed_fn) -- the same learned embedding space the paper's
numbers are about, not a separate model trained just for this plot.

Run after graph_hamburg.pt exists (see run_full_experiments.py). Subsamples to a few thousand
buildings before running t-SNE (2D embedding of hundreds of thousands of points is both slow and
unreadable as a scatter plot).
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

from neo4j_loader import load_or_cache
import t3_matching as T3

N_SUBSAMPLE = 4000
SEED = 0

BLUE, ORANGE = "#3B7EA1", "#D97706"


def get_embeddings(data, kind):
    r = T3.run_matching(data, kind=kind, seeds=(SEED,), epochs=150, k_neg=5, return_embeddings=True)
    return r["embeddings"]["Building"]


def main():
    data = load_or_cache("graph_hamburg.pt", verbose=False)
    n = data["Building"].num_nodes
    rng = np.random.default_rng(SEED)
    idx = rng.choice(n, size=min(N_SUBSAMPLE, n), replace=False)

    roof = data["Building"].y.numpy()[idx]              # -1 = unlabeled
    roof_names = data["Building"].label_names
    roofmat = data["Building"].y_roof_material.numpy()[idx]   # -1 = not covered by the ML layer
    roofmat_names = data["Building"].roof_material_names
    # osm_shared is stored as a raw 0/1 flag (unlike the other, z-scored prov features), so it's
    # the one column that means literally "has OSM overlap" without needing to invert the z-score.
    shared_col = data["Building"].prov_names.index("osm_shared")
    has_osm = (data["Building"].x_prov[:, shared_col].numpy() > 0.5)[idx]

    fig, axes = plt.subplots(2, 3, figsize=(11.5, 7.5))
    for row, kind in enumerate(["sage", "aware"]):
        emb = get_embeddings(data, kind)[idx]
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
    print("wrote fig_prov_tsne.pdf")


if __name__ == "__main__":
    main()
