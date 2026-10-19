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
    """One box per person, in decision order (rows of up to four), with arrows for influence.

    A person can appear more than once in the decision order (for example the economic
    buyer is consulted early and signs at the end); their box lists every step. People
    who only influence others are shown without a step number.
    """
    import textwrap

    colors = brand["colors"]
    sequence = list(committee.get("decision_sequence") or [])
    steps: dict[str, list[int]] = {}
    for i, pid in enumerate(sequence, start=1):
        steps.setdefault(pid, []).append(i)
    people = list(steps)
    for edge in committee.get("edges", []):
        for pid in (edge["from"], edge["to"]):
            if pid not in people:
                people.append(pid)
    import math

    n = max(len(people), 1)
    rx, ry = 3.3, 1.75  # people sit on an oval, in decision order, clockwise from the top left
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(-rx - 1.25, rx + 1.25)
    ax.set_ylim(-ry - 0.95, ry + 0.7)
    ax.axis("off")
    start_angle = math.pi * 0.75
    pos = {pid: (rx * math.cos(start_angle - 2 * math.pi * i / n), ry * math.sin(start_angle - 2 * math.pi * i / n))
           for i, pid in enumerate(people)}
    line = colors["secondary"] if "secondary" in colors else colors["text"]
    boxes = {}
    for pid in people:
        x, y = pos[pid]
        tag = ", ".join(map(str, steps[pid])) if pid in steps else "influencer"
        role = "\n".join(textwrap.wrap(roles.get(pid, pid), 20))
        boxes[pid] = ax.text(x, y, f"{tag}\n{role}", ha="center", va="center", fontsize=9.5,
                             color=colors["background"], zorder=3, linespacing=1.25,
                             bbox={"boxstyle": "round,pad=0.5", "facecolor": colors["primary"],
                                   "edgecolor": colors["primary"]})
    fig.canvas.draw()  # sizes the boxes so arrows can stop at their edges
    for edge in committee.get("edges", []):
        a, b = edge["from"], edge["to"]
        if a in pos and b in pos and a != b:
            ax.add_patch(FancyArrowPatch(pos[a], pos[b], arrowstyle="-|>", mutation_scale=14,
                                         connectionstyle="arc3,rad=0.08", color=line,
                                         linewidth=LINE_WIDTH.get(edge.get("influence"), 1.2),
                                         patchA=boxes[a].get_bbox_patch(), patchB=boxes[b].get_bbox_patch(),
                                         shrinkA=3, shrinkB=3, zorder=4))
    ax.text(-rx - 1.2, -ry - 0.9, "Numbers show the typical decision order (a person can appear at more than one "
            "step). Thicker arrows mean stronger influence.", fontsize=8, color=colors["text"])
    return _save(fig, path)
