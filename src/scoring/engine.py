from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .dimensions import compute_brand_maturity, compute_demand_fit, compute_innovation, compute_product_quality, compute_value_for_money
from .models import DimensionResult, ScoreReport
from .utils import clamp


def compute_score_report(
    *,
    brand_info: Mapping[str, Any],
    company_info: Mapping[str, Any] | None,
    products_info: Mapping[str, Any],
    traffic_info: Mapping[str, Any],
    review_info: list[Mapping[str, Any]],
) -> ScoreReport:
    domain = brand_info.get("domain", brand_info)
    if isinstance(domain, Mapping):
        brand_name = str(domain.get("merchant_name") or domain.get("name") or "unknown")
        brand_domain = domain
    else:
        brand_name = "unknown"
        brand_domain = {}

    dims: list[DimensionResult] = [
        compute_brand_maturity(brand_domain, traffic_info, review_info),
        compute_product_quality(review_info),
        compute_demand_fit(brand_domain, traffic_info),
        compute_value_for_money(products_info, review_info),
        compute_innovation(products_info),
    ]

    weights: dict[str, float] = {
        "品牌成熟度": 0.22,
        "产品质量": 0.26,
        "市场需求匹配度": 0.22,
        "性价比": 0.18,
        "创新力": 0.12,
    }

    used = [(d, weights.get(d.name, 0.0)) for d in dims if weights.get(d.name, 0.0) > 0.0]
    weight_sum = sum(w for _, w in used)
    total_score = sum(d.score * w for d, w in used) / weight_sum if weight_sum > 0 else 50.0
    total_conf = sum(d.confidence * w for d, w in used) / weight_sum if weight_sum > 0 else 0.3

    meta: dict[str, Any] = {
        "weights": weights,
        "company_summary_present": company_info is not None,
    }

    return ScoreReport(
        brand=brand_name,
        total_score=float(clamp(total_score, 0.0, 100.0)),
        total_confidence=float(clamp(total_conf, 0.0, 1.0)),
        dimensions=dims,
        meta=meta,
    )

