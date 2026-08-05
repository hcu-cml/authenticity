"""
Figure 3 (fig_crosscity.pdf): T1 height leave-one-city-out R^2, agnostic vs. aware, one group of
bars per held-out city, error bars over seeds. A direct plot of Table repL-crosscity -- prefers the
10-seed rerun (results.json["fullscale"]["T1"]["crosscity_10seed"]) if present, since that is the
version whose statistical power was actually checked; falls back to the original 3-seed run.
"""
import json
import matplotlib.pyplot as plt
import numpy as np

with open("results.json") as f:
    results = json.load(f)

T1 = results["fullscale"]["T1"]
KEY = "crosscity_10seed" if "crosscity_10seed" in T1 else "crosscity"
cross = T1[KEY]
n_seeds = len(results["fullscale"]["_meta"]["seeds"]) if KEY == "crosscity" else 10

CITIES = ["hamburg", "helsinki", "nyc", "tokyo", "zurich"]
BLUE, ORANGE = "#3B7EA1", "#D97706"

agn_mean = [cross[c]["gnn"]["R2"][0] for c in CITIES]
agn_std = [cross[c]["gnn"]["R2"][1] for c in CITIES]
awa_mean = [cross[c]["gnn_aware"]["R2"][0] for c in CITIES]
awa_std = [cross[c]["gnn_aware"]["R2"][1] for c in CITIES]

x = np.arange(len(CITIES))
w = 0.35

fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.bar(x - w / 2, agn_mean, w, yerr=agn_std, capsize=3, color=BLUE, label="agnostic GNN")
ax.bar(x + w / 2, awa_mean, w, yerr=awa_std, capsize=3, color=ORANGE, label="aware GNN")

ax.set_xticks(x, [c.capitalize() if c != "nyc" else "NYC" for c in CITIES])
ax.set_ylabel("$R^2$ (leave-one-city-out)")
ax.axhline(0, color="#999999", linewidth=1)
ax.legend(fontsize=9, frameon=False)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
ax.set_axisbelow(True)
ax.grid(axis="y", color="#eeeeee", linewidth=0.8)
ax.set_title(f"T1 height, cross-city transfer (mean over {n_seeds} seeds)", fontsize=11)

fig.tight_layout()
fig.savefig("fig_crosscity.pdf")
print(f"wrote fig_crosscity.pdf (using {KEY}, {n_seeds} seeds)")
