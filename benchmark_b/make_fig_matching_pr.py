"""
Figure 2 (fig_matching_pr.pdf): precision-recall curves for T3 matching, one panel per city,
comparing the spatial-distance baseline against the attribute-only, agnostic, and aware encoders
(the two other non-learned baselines/encoders are left off to keep each panel readable -- their
AUC/AP numbers are in Table repL-match). Built from raw scores saved by the T3 rerun
(t3_pr_curves.pkl, seed 0 only per city/kind) -- that file is a large scratch artifact, not meant
to be committed; regenerate it by rerunning t3_matching.run_matching(..., return_scores=True).
"""
import pickle
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve

with open("t3_pr_curves.pkl", "rb") as f:
    curves = pickle.load(f)

CITIES = ["hamburg", "helsinki", "nyc", "tokyo", "zurich"]
SHOW = [("spatial", "#4C4C4C", "-"), ("attr", "#3B7EA1", "-"), ("sage", "#D97706", "--"),
       ("aware", "#D97706", "-")]
LABELS = {"spatial": "spatial-distance", "attr": "attribute-only", "sage": "agnostic GNN",
         "aware": "aware GNN"}

fig, axes = plt.subplots(1, 5, figsize=(15, 3.2), sharey=True)
for ax, city in zip(axes, CITIES):
    for kind, color, style in SHOW:
        y, s = curves[city][kind][0]                 # first seed only, for a clean single curve
        prec, rec, _ = precision_recall_curve(y, s)
        ax.plot(rec, prec, color=color, linestyle=style, linewidth=1.5, label=LABELS[kind])
    ax.set_title(city.capitalize() if city != "nyc" else "NYC", fontsize=10)
    ax.set_xlabel("Recall", fontsize=9)
    ax.set_ylim(0, 1.02)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
axes[0].set_ylabel("Precision", fontsize=9)
axes[-1].legend(fontsize=8, frameon=False, loc="lower left")

fig.suptitle("T3 cross-source matching: precision--recall, hard negatives", fontsize=11)
fig.tight_layout()
fig.savefig("fig_matching_pr.pdf")
print("wrote fig_matching_pr.pdf")
