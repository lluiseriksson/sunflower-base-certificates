"""Generate 3 publication-grade 300-DPI figures for Paper 14.

Author: Lluis Eriksson
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGDIR = ROOT / "paper" / "figures"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.titlesize": 10.5,
    "axes.labelsize": 10,
    "legend.fontsize": 8.0,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "axes.grid": True,
    "grid.alpha": 0.28,
})


def make_fig1() -> None:
    d = json.loads((RESULTS / "exp2_extremal_2_uniform.json").read_text(encoding="utf-8"))
    rows = d["rows"]
    rs = [x["r"] for x in rows]
    gains = [x["base_gain"] for x in rows]
    cols = ["#1565c0" if x["parity"] == "odd" else "#d84315" for x in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.2), constrained_layout=True)

    # Panel (a): Odd vs Even parity gain b_r(k=2) - (r - 1)
    ax1.bar(rs, gains, color=cols, edgecolor="black", lw=0.7, width=0.68)
    ax1.axhline(0.5, color="#1565c0", ls="--", lw=1.2, label=r"Odd limit $\sqrt{r(r-1)} - (r-1) \to \frac{1}{2}$")
    ax1.axhline(0.25, color="#d84315", ls=":", lw=1.3, label=r"Even limit $\sqrt{(r-1)^2+\frac{r-2}{2}} - (r-1) \to \frac{1}{4}$")
    ax1.set_xticks(rs[::2])
    ax1.set_ylim(0, 0.58)
    ax1.set_xlabel(r"Sunflower petal count $r$")
    ax1.set_ylabel(r"Base gain $M_r(2)^{1/2} - (r - 1)$")
    ax1.set_title("(a) Odd vs. Even Parity Dichotomy in $2$-Uniform Base Gain")
    ax1.legend(loc="lower right", frameon=True, framealpha=0.92, fontsize=7.6)

    # Panel (b): Supermultiplicative Base Tower for r = 3
    levels = [r"$k=1$" + "\n($m=2$)", r"$k=2$" + "\n($2K_3, m=6$)",
              r"$k=3$" + "\n(Hemi-Icos., $m=20$)", r"$k=4$" + "\n(AHS, $m=79$)"]
    vals = [2.0, 6 ** 0.5, 20 ** (1 / 3), 79 ** 0.25]
    bar_cols = ["#78909c", "#1565c0", "#2e7d32", "#6a1b9a"]
    bars = ax2.bar(levels, vals, color=bar_cols, edgecolor="black", lw=0.7, width=0.55)
    for b, v in zip(bars, vals):
        ax2.text(b.get_x() + b.get_width() / 2, v + 0.04, f"{v:.4f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    ax2.axhline(2.0, color="black", ls="--", lw=1.1, label=r"Trivial block bound $r - 1 = 2$")
    ax2.set_ylim(0, 3.45)
    ax2.set_ylabel(r"Lower bound on $b_3 = \sup_k M_3(k)^{1/k}$")
    ax2.set_title(r"(b) Supermultiplicative Base Tower for $r=3$ ($k \leq 3$ Mode-1; $k=4$ AHS)")
    ax2.legend(loc="lower right", frameon=True, framealpha=0.92, fontsize=8.0)

    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGDIR / "fig1_extremal_base_tower.png", bbox_inches="tight")
    plt.close(fig)


def make_fig2() -> None:
    d = json.loads((RESULTS / "exp3_crossover_atlas.json").read_text(encoding="utf-8"))
    curves = d["curves"]
    colors = {"3": "#1565c0", "4": "#2e7d32", "5": "#c62828"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.2), constrained_layout=True)

    for r_str in ["3", "4", "5"]:
        pts = curves[r_str]
        Bs = [p["B"] for p in pts]
        ks = [p["k_star"] for p in pts]
        rats = [p["ratio_k_star_over_B_div_rm1"] for p in pts]
        col = colors[r_str]
        ax1.plot(Bs, ks, "o-", color=col, lw=2.0, ms=5.0, label=rf"$r = {r_str}$")
        ax2.plot(Bs, rats, "s-", color=col, lw=2.0, ms=5.0, label=rf"$r = {r_str}$")

    ax1.set_xlabel(r"Fixed-petal exponential base $B$")
    ax1.set_ylabel(r"Exact first crossover $k^*(r, B)$ ($B^k < k!(r-1)^k$)")
    ax1.set_title(r"(a) Exact Big-Integer Crossover $k^*(r, B)$ vs. Erdős–Rado")
    ax1.legend(loc="upper left", frameon=True, framealpha=0.92)

    ax2.axhline(d["stirling_e"], color="black", ls="--", lw=1.3, label=r"Stirling limit $e \approx 2.7183$")
    ax2.set_xlabel(r"Fixed-petal exponential base $B$")
    ax2.set_ylabel(r"Normalized crossover $k^*(r,B) / (B / (r-1))$")
    ax2.set_ylim(1.88, 3.05)
    ax2.set_title(r"(b) Stirling Convergence $k^*(r,B) \sim e \cdot \frac{B}{r-1}$")
    ax2.legend(loc="lower right", frameon=True, framealpha=0.92)

    fig.savefig(FIGDIR / "fig2_erdos_rado_crossover.png", bbox_inches="tight")
    plt.close(fig)


def make_fig3() -> None:
    d = json.loads((RESULTS / "exp4_log_bounds_comparison.json").read_text(encoding="utf-8"))
    rows = d["rows"]
    ks = [r["k"] for r in rows]
    er = [r["log2_erdos_rado"] for r in rows]
    alwz = [r["log2_alwz_proxy"] for r in rows]
    b10 = [r["log2_fixed_B10"] for r in rows]
    b20 = [r["log2_fixed_B20"] for r in rows]
    lb = [r["log2_hemi_icosa_lb"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.2), constrained_layout=True)

    ax1.plot(ks, er, "k--", lw=2.0, label=r"Erdős–Rado $\log_2(k!\,2^k)$")
    ax1.plot(ks, alwz, "-.", color="#ef6c00", lw=1.9, label=r"ALWZ proxy $k \log_2(12\log_2(3k))$")
    ax1.plot(ks, b20, "s-", color="#c62828", lw=1.8, ms=3.8, label=r"Fixed-base $B=20$: $k\log_2 20$")
    ax1.plot(ks, b10, "o-", color="#1565c0", lw=1.8, ms=3.8, label=r"Fixed-base $B=10$: $k\log_2 10$")
    ax1.plot(ks, lb, "-", color="#2e7d32", lw=2.2, label=r"Certified lower bound $k\log_2(20^{1/3})$")
    ax1.set_xlabel(r"Set uniformity $k$ ($r = 3$ petals)")
    ax1.set_ylabel(r"$\log_2(\text{family size bound})$")
    ax1.set_title(r"(a) Linear Fixed-Base Growth vs. Superlinear $k!$ & $\log k$")
    ax1.legend(loc="upper left", frameon=True, framealpha=0.92, fontsize=7.5)

    # Panel (b): Per-coordinate effective base log2(bound)/k
    ax2.plot(ks, [e / k for e, k in zip(er, ks)], "k--", lw=2.0, label=r"Erdős–Rado $\frac{1}{k}\log_2(k!2^k)$")
    ax2.plot(ks, [a / k for a, k in zip(alwz, ks)], "-.", color="#ef6c00", lw=1.9, label=r"ALWZ $\log_2(12\log_2(3k))$")
    ax2.axhline(np.log2(20.0), color="#c62828", lw=1.8, label=r"Fixed-base $B = 20$ ($\log_2 20 \approx 4.32$)")
    ax2.axhline(np.log2(10.0), color="#1565c0", lw=1.8, label=r"Fixed-base $B = 10$ ($\log_2 10 \approx 3.32$)")
    ax2.axhline(np.log2(20.0) / 3.0, color="#2e7d32", lw=2.2, label=r"Certified LB $\frac{1}{3}\log_2 20 \approx 1.44$")
    ax2.set_xlabel(r"Set uniformity $k$ ($r = 3$ petals)")
    ax2.set_ylabel(r"Effective log-base $\frac{1}{k}\log_2(\text{bound})$")
    ax2.set_ylim(0.8, 7.2)
    ax2.set_title(r"(b) Collapse of Effective Base Under Fixed-Petal Theorem")
    ax2.legend(loc="upper left", frameon=True, framealpha=0.92, fontsize=7.5)

    fig.savefig(FIGDIR / "fig3_log_bounds_comparison.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    make_fig1()
    make_fig2()
    make_fig3()
    print("[FIGURES] Generated 3 publication-grade 300-DPI figures in paper/figures/.")


if __name__ == "__main__":
    main()
