from __future__ import annotations

from typing import Any

from src.scoring import ScoreReport


def build_diagnosis_prompt(report: ScoreReport) -> str:
    dims = [
        {
            "name": d.name,
            "score": round(float(d.score), 2),
            "confidence": round(float(d.confidence), 2),
            "metrics": d.metrics,
        }
        for d in report.dimensions
    ]

    payload: dict[str, Any] = {
        "brand": report.brand,
        "total_score": round(float(report.total_score), 2),
        "total_confidence": round(float(report.total_confidence), 2),
        "dimensions": dims,
    }

    return (
        "你将收到一个品牌的多维度量化评分结果（包含置信度与关键指标）。\n"
        "请输出一段中文综合评分总结，严格控制在 100-200 字。\n"
        "要求：\n"
        "1) 必须点名 2-3 个最强优势与 1-2 个主要风险；\n"
        "2) 必须体现置信度不足的维度要谨慎表述；\n"
        "3) 不要出现任何英文、不要输出列表、不要输出标题、只输出一段话。\n"
        "\n"
        f"评分结果（JSON）：\n{payload}"
    )

