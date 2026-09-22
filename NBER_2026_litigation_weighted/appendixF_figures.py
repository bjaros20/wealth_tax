"""
Appendix F, Figure 5: California returns and billionaires at or above each
wealth threshold -- reconstruction from FTB income data (this paper), Forbes
(observed), and the Pareto extrapolation of Boll et al. (2025).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8880"
GRID, BAND = "#e6e5e1", "#f2f1ed"
SURF = "#ffffff"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.edgecolor": MUTED, "axes.linewidth": 0.8,
    "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
    "figure.facecolor": SURF, "axes.facecolor": SURF,
    "savefig.facecolor": SURF,
})

def frame(ax, hgrid=True):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    if hgrid:
        ax.yaxis.grid(True, color=GRID, linewidth=0.8, linestyle="-")
    ax.set_axisbelow(True)

def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(f"NPV_plots/{name}.{ext}", dpi=220, bbox_inches="tight")
    plt.close(fig); print("wrote", name)

MARK = dict(markeredgecolor=SURF, markeredgewidth=1.3, markersize=5.5)

# ---------------------------------------------------------------- FIGURE 5
thr   = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
recon = [360.2, 204.4, 91.2, 89.9, 64.9, 59.5, 54.1, 51.9, 51.9]
forbes= [249, 206, 172, 140, 125, 110, 93, 89, 82]
pareto= [617.1, 366.1, 252.8, 189.7, 150, 123, 103.6, 89, 82]

fig, ax = plt.subplots(figsize=(7.0, 4.3))
ax.axvspan(1.0, 1.5, color=BAND, zorder=0)
ax.text(1.25, 20, "unlisted population", ha="center", va="bottom",
        fontsize=8, color=MUTED)

ax.plot(thr, pareto, color=AQUA, ls="--", lw=1.8, marker="^",
        label="Pareto extrapolation", **MARK)
ax.plot(thr, forbes, color=ORANGE, ls="-", lw=1.8, marker="s",
        label="Forbes (observed)", **MARK)
ax.plot(thr, recon, color=BLUE, ls="-", lw=2.0, marker="o",
        label="Reconstruction (this paper)", **MARK)

for x, y, v, c, dx, dy, ha, va in [
    (1,   617.1, "617", AQUA,     9,   7, "left",  "bottom"),
    (1,   360.2, "360", BLUE,     9,   7, "left",  "bottom"),
    (1,   249,   "249", ORANGE,   9, -10, "left",  "top"),
    (1.5, 366.1, "366", AQUA,     9,   7, "left",  "bottom"),
    (1.5, 206,   "206", ORANGE,   9,  13, "left",  "bottom"),
    (1.5, 204.4, "204", BLUE,   -10, -14, "right", "top"),
]:
    ax.annotate(v, (x, y), textcoords="offset points", xytext=(dx, dy),
                fontsize=8.5, color=c, ha=ha, va=va, fontweight="bold")

ax.set_xlim(0.93, 5.12); ax.set_ylim(0, 690)
ax.set_xticks(thr); ax.set_yticks(range(0, 700, 100))
ax.set_xlabel("Wealth threshold (\$ billion)")
ax.set_ylabel("Count at or above threshold")
ax.set_title("California returns and billionaires above each wealth threshold",
             fontsize=10.5, fontweight="bold", color=INK, pad=12)
leg = ax.legend(loc="upper right", frameon=False, fontsize=9, handlelength=2.4)
for t in leg.get_texts(): t.set_color(INK2)
frame(ax)
save(fig, "F1_unlisted_population")
