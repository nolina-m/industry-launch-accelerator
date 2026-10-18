"""Simple diagrams as PNG images (FR-RND-04): the positioning map and the buying committee map.

Pure Python (matplotlib, no system libraries). Colors come from brand.yaml. The
same data always appears as a table next to the image, so nothing is lost if an
image can't be shown.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

DPI = 150
LINE_WIDTH = {"high": 2.6, "medium": 1.6, "low": 0.9}


def _save(fig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    # No software or date metadata, so the same data gives the same file (FR-RND-05).
    fig.savefig(path, dpi=DPI, bbox_inches="tight", metadata={"Software": None})
    plt.close(fig)
    return path


def positioning_map(overview: dict, names: dict[str, str], brand: dict, path: Path) -> Path:
    pm = overview["positioning_map"]
    colors = brand["colors"]
    accent = (colors.get("accent") or [colors["primary"]])[0]
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axhline(5, color=colors["text"], linewidth=0.5, alpha=0.4)
    ax.axvline(5, color=colors["text"], linewidth=0.5, alpha=0.4)
    for point in pm["points"]:
        ours = point.get("competitor_id") is None
        color = colors["primary"] if ours else accent
        ax.scatter(point["x"], point["y"], s=140 if ours else 90, color=color, zorder=3,
                   marker="*" if ours else "o")
        label = point["label"] if ours else names.get(point["competitor_id"], point["label"])
        ax.annotate(label, (point["x"], point["y"]), textcoords="offset points", xytext=(7, 6),
                    fontsize=8.5, color=colors["text"], weight="bold" if ours else "normal")
    ax.set_xlabel(f"{pm['x_axis']['label']}  ({pm['x_axis']['low']} → {pm['x_axis']['high']})",
                  fontsize=9, color=colors["text"])
    ax.set_ylabel(f"{pm['y_axis']['label']}  ({pm['y_axis']['low']} → {pm['y_axis']['high']})",
                  fontsize=9, color=colors["text"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(colors["text"])
        spine.set_linewidth(0.6)
    return _save(fig, path)


def committee_map(committee: dict, roles: dict[str, str], brand: dict, path: Path) -> Path:
    """Personas as boxes left to right in decision order, arrows for influence."""
    colors = brand["colors"]
    order = list(committee.get("decision_sequence") or [])
    for edge in committee.get("edges", []):
        for pid in (edge["from"], edge["to"]):
            if pid not in order:
                order.append(pid)
    n = max(len(order), 1)
    fig, ax = plt.subplots(figsize=(max(6.4, 1.9 * n), 2.6))
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(-1.15, 0.8)
    ax.axis("off")
    pos = {pid: (i, 0.45 if i % 2 == 0 else -0.45) for i, pid in enumerate(order)}
    for edge in committee.get("edges", []):
        if edge["from"] in pos and edge["to"] in pos and edge["from"] != edge["to"]:
            arrow = FancyArrowPatch(pos[edge["from"]], pos[edge["to"]], arrowstyle="-|>", mutation_scale=12,
                                    connectionstyle="arc3,rad=0.18", color=colors["secondary"]
                                    if "secondary" in colors else colors["text"],
                                    linewidth=LINE_WIDTH.get(edge.get("influence"), 1.2), shrinkA=26, shrinkB=26,
                                    zorder=1)
            ax.add_patch(arrow)
    for i, pid in enumerate(order):
        x, y = pos[pid]
        label = f"{i + 1}. {roles.get(pid, pid)}"
        ax.text(x, y, label, ha="center", va="center", fontsize=8.5, color=colors["background"], zorder=3,
                wrap=True, bbox={"boxstyle": "round,pad=0.5", "facecolor": colors["primary"],
                                 "edgecolor": colors["primary"]})
    ax.text(-0.55, -1.1, "Numbers show the typical decision order. Thicker arrows mean stronger influence.",
            fontsize=7, color=colors["text"])
    return _save(fig, path)
