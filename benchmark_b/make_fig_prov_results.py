"""
Figure 1 (fig_prov_results.pdf) for the representation-learning section: does provenance-aware
aggregation (Eq. 1) help, and where? One signed bar per task/regime = (aware metric - agnostic
metric), so the figure answers the question directly instead of asking the reader to compare two
absolute bars per group. Source numbers: results.json["fullscale"] (see PROGRESS.md S8-REAL).

Blue = provenance-aware wins, orange = agnostic wins -- a colorblind-safe diverging pair, plus a
hatch on the losing color so the figure still reads in grayscale print.
"""
import matplotlib.pyplot as plt

# (label, delta, note). Deltas computed directly from results.json; see PROGRESS.md S8-REAL for the
# full per-city numbers this aggregates (cross-city rows are the mean over held-out cities).
ROWS = [
    ("T1 height\n(single-city, Hamburg)", 0.733 - 0.730, "R²"),
    ("T1 height\n(cross-city, mean of 5, 10 seeds)", 0.075, "R²"),
    ("T1 roof material\n(cross-source completion, Hamburg)", 0.316 - 0.314, "macro-F1"),
    ("T2 roof type\n(single-city, Hamburg)", 0.559 - 0.556, "macro-F1"),
    ("T2 roof type\n(cross-city, mean of 2)", 0.003, "macro-F1"),
    ("T2 building use\n(single-city, Hamburg)", 0.476 - 0.462, "macro-F1"),
    ("T3 matching\n(mean of 5 cities)", 0.033, "ROC-AUC"),
]

BLUE, ORANGE = "#3B7EA1", "#D97706"   # diverging pair, CVD-safe at this lightness/chroma separation

fig, ax = plt.subplots(figsize=(6.4, 3.6))
labels = [r[0] for r in ROWS]
deltas = [r[1] for r in ROWS]
y = range(len(ROWS))

colors = [BLUE if d >= 0 else ORANGE for d in deltas]
hatches = [None if d >= 0 else "///" for d in deltas]
bars = ax.barh(list(y), deltas, color=colors, height=0.6, edgecolor="white", linewidth=0.5)
for bar, hatch in zip(bars, hatches):
    if hatch:
        bar.set_hatch(hatch)

for yi, (d, (_, _, unit)) in zip(y, [(r[1], r) for r in ROWS]):
    align = "left" if d >= 0 else "right"
    pad = 0.004 if d >= 0 else -0.004
    ax.text(d + pad, yi, f"{d:+.3f} {unit}", va="center", ha=align, fontsize=9, color="#333333")

ax.axvline(0, color="#999999", linewidth=1)
ax.set_yticks(list(y), labels, fontsize=9.5)
ax.invert_yaxis()
ax.set_xlabel("aware $-$ agnostic  (positive = provenance-aware wins)", fontsize=10)
ax.set_xlim(-0.03, 0.44)
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#cccccc")
ax.tick_params(left=False)
ax.set_axisbelow(True)
ax.grid(axis="x", color="#eeeeee", linewidth=0.8)

ax.set_title("Provenance-aware vs. agnostic embeddings, by task", fontsize=11, pad=10)
fig.tight_layout()
fig.savefig("fig_prov_results.pdf")
print("wrote fig_prov_results.pdf")
