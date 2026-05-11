from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.scoring import ScoreReport


def render_markdown_report(*, report: ScoreReport, llm_summary: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    lines.append(f"# 品牌评分报告：{report.brand}")
    lines.append("")
    lines.append(f"- 生成时间：{now}")
    lines.append(f"- 综合得分：{report.total_score:.2f} / 100")
    lines.append(f"- 综合置信度：{report.total_confidence:.2f}（0-1）")
    lines.append("")
    lines.append("## 维度得分")
    lines.append("")
    lines.append("| 维度 | 得分(0-100) | 置信度(0-1) | 计算依据（简述） |")
    lines.append("|---|---:|---:|---|")
    for d in report.dimensions:
        brief = d.rationale.replace("\n", " ").strip()
        lines.append(f"| {d.name} | {d.score:.2f} | {d.confidence:.2f} | {brief} |")
    lines.append("")
    lines.append("## LLM 综合诊断（100-200字）")
    lines.append("")
    lines.append(llm_summary.strip())
    lines.append("")
    lines.append("## 评分明细（关键指标）")
    lines.append("")
    for d in report.dimensions:
        lines.append(f"### {d.name}")
        lines.append("")
        metrics: dict[str, Any] = d.metrics or {}
        if not metrics:
            lines.append("（无）")
            lines.append("")
            continue
        for k, v in metrics.items():
            lines.append(f"- {k}: {v}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

