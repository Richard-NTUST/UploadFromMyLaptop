#!/usr/bin/env python3
"""Plot a consolidated WINLAB offered-load sweep with run-quality markers."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


FULL_COLOR = "#2563eb"
DIAGNOSTIC_COLOR = "#f59e0b"


def annotate(ax, x, y, fmt: str) -> None:
    for xv, yv in zip(x, y):
        if pd.notna(yv):
            ax.annotate(fmt.format(yv), (xv, yv), xytext=(0, 7),
                        textcoords="offset points", ha="center", fontsize=8)


def scatter_by_quality(ax, frame: pd.DataFrame, column: str) -> None:
    for diagnostic, color, label, marker in (
        (False, FULL_COLOR, "complete", "o"),
        (True, DIAGNOSTIC_COLOR, "incomplete diagnostic", "^"),
    ):
        subset = frame[frame["diagnostic"] == diagnostic]
        subset = subset[pd.notna(subset[column])]
        if not subset.empty:
            ax.scatter(subset["offered_load_mbps"], subset[column], color=color,
                       marker=marker, s=55, zorder=4, label=label)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_png", type=Path)
    args = parser.parse_args()

    frame = pd.read_csv(args.input_csv).sort_values("offered_load_mbps")
    frame["diagnostic"] = frame["status"].str.lower().ne("complete")

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    offered = frame["offered_load_mbps"]

    ax = axes[0, 0]
    ax.plot(offered, offered, color="#94a3b8", linestyle="--", linewidth=1.2,
            label="offered = delivered")
    ax.plot(offered, frame["rx_throughput_mbps"], color="#334155", linewidth=1.5)
    scatter_by_quality(ax, frame, "rx_throughput_mbps")
    annotate(ax, offered, frame["rx_throughput_mbps"], "{:.1f}")
    ax.set(title="Delivered UE throughput", xlabel="Offered load (Mbps)",
           ylabel="Mean received throughput (Mbps)")
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.plot(offered, frame["avg_power_w"], color="#334155", linewidth=1.5)
    ax.errorbar(
        offered,
        frame["avg_power_w"],
        yerr=[
            frame["avg_power_w"] - frame["min_power_w"],
            frame["max_power_w"] - frame["avg_power_w"],
        ],
        fmt="none",
        ecolor="#64748b",
        elinewidth=1,
        capsize=4,
        alpha=0.8,
        zorder=2,
        label="observed min–max",
    )
    scatter_by_quality(ax, frame, "avg_power_w")
    annotate(ax, offered, frame["avg_power_w"], "{:.2f} W")
    ax.set(title="Pegatron O-RU active power", xlabel="Offered load (Mbps)",
           ylabel="Outlet 2 mean active power (W)")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    ax.plot(offered, frame["energy_per_bit_nj"], color="#334155", linewidth=1.5)
    scatter_by_quality(ax, frame, "energy_per_bit_nj")
    annotate(ax, offered, frame["energy_per_bit_nj"], "{:.1f}")
    ax.set(title="Energy per delivered bit", xlabel="Offered load (Mbps)",
           ylabel="O-RU energy (nJ/bit)")

    ax = axes[1, 1]
    colors = [DIAGNOSTIC_COLOR if value else FULL_COLOR for value in frame["diagnostic"]]
    ax.bar(offered.astype(int).astype(str), frame["completion_pct"], color=colors,
           edgecolor="#334155", linewidth=0.5)
    annotate(ax, offered.astype(int).astype(str), frame["completion_pct"], "{:.1f}%")
    ax.axhline(80, color="#64748b", linestyle="--", linewidth=1, label="80% diagnostic threshold")
    ax.set_ylim(0, 110)
    ax.set(title="Run completeness", xlabel="Offered load (Mbps)",
           ylabel="Completion (%)")
    ax.legend(fontsize=8)

    for ax in axes.flat:
        ax.grid(True, alpha=0.22)

    fig.suptitle("OAI latest baseline load sweep — 5 Aug 2026", fontsize=15)
    args.output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output_png, dpi=180)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
