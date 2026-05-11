from __future__ import annotations

from pathlib import Path
from typing import Any

from src.scoring import ScoreReport, compute_score_report

from .data_loader import load_sample_data


def run_scoring_workflow(*, data_dir: Path) -> ScoreReport:
    raw: dict[str, Any] = load_sample_data(data_dir)
    return compute_score_report(
        brand_info=raw["brand"],
        company_info=raw.get("company"),
        products_info=raw["products"],
        traffic_info=raw["traffic"],
        review_info=raw["reviews"],
    )

