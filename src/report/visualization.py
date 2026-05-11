from __future__ import annotations

from math import pi
from pathlib import Path

import matplotlib.pyplot as plt

from src.scoring import ScoreReport


def save_radar_chart(*, report: ScoreReport, output_path: Path) -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    labels = [d.name for d in report.dimensions]
    values = [float(d.score) for d in report.dimensions]
    if not labels:
        return

    angles = [n / float(len(labels)) * 2 * pi for n in range(len(labels))]
    angles += angles[:1]
    values += values[:1]

    fig = plt.figure(figsize=(7, 7))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    ax.set_rlabel_position(0)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_ylim(0, 100)

    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.18)

    ax.set_title(f"{report.brand} 维度得分雷达图", y=1.08)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
