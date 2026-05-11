from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from .models import DimensionResult
from .utils import clamp, linear_score, log_scale_score, piecewise_score, sample_size_confidence, safe_float


def _get_nested(obj: Mapping[str, Any], keys: list[str]) -> Any:
    cur: Any = obj
    for k in keys:
        if not isinstance(cur, Mapping) or k not in cur:
            return None
        cur = cur[k]
    return cur


def compute_brand_maturity(brand: Mapping[str, Any], traffic: Mapping[str, Any], reviews: list[Mapping[str, Any]]) -> DimensionResult:
    created_at = pd.to_datetime(brand.get("created_at"), errors="coerce")
    age_years = None
    if pd.notna(created_at):
        created_at_utc = created_at.tz_convert("UTC") if created_at.tzinfo is not None else created_at.tz_localize("UTC")
        age_years = float((pd.Timestamp(datetime.now(timezone.utc)) - created_at_utc) / pd.Timedelta(days=365.25))

    estimated_visits = safe_float(brand.get("estimated_visits"))
    estimated_sales = safe_float(brand.get("estimated_sales"))
    employee_count = safe_float(brand.get("employee_count"))
    product_count = safe_float(brand.get("product_count"))

    contact_info = brand.get("contact_info", [])
    social_followers = 0.0
    if isinstance(contact_info, list):
        for item in contact_info:
            if isinstance(item, Mapping):
                f = safe_float(item.get("followers"))
                if f is not None:
                    social_followers += f

    visits_latest = safe_float(_get_nested(traffic, ["Engagments", "Visits"]))

    age_score = linear_score(age_years, low=0.0, high=8.0)
    visits_score = log_scale_score(visits_latest or estimated_visits, low=50_000, high=2_000_000)
    followers_score = log_scale_score(social_followers, low=1_000, high=1_000_000)
    employee_score = log_scale_score(employee_count, low=20, high=500)
    catalog_score = linear_score(product_count, low=5, high=80)

    components: list[tuple[str, float | None, float]] = [
        ("age_score", age_score, 0.25),
        ("visits_score", visits_score, 0.30),
        ("followers_score", followers_score, 0.20),
        ("employee_score", employee_score, 0.15),
        ("catalog_score", catalog_score, 0.10),
    ]

    used = [(name, s, w) for name, s, w in components if s is not None]
    if not used:
        return DimensionResult(
            name="品牌成熟度",
            score=50.0,
            confidence=0.2,
            metrics={"reason": "missing_signals"},
            rationale="关键成熟度信号缺失，使用默认中性分。",
        )

    weight_sum = sum(w for _, _, w in used)
    score = sum(float(s) * w for _, s, w in used) / weight_sum

    confidence = 0.65
    if age_years is None:
        confidence -= 0.10
    if (visits_latest or estimated_visits) is None:
        confidence -= 0.10
    if social_followers <= 0:
        confidence -= 0.05
    confidence = clamp(confidence, 0.2, 0.95)

    rationale = "综合品牌年龄、访问规模、社媒触达、员工规模与产品丰富度估算成熟度。"
    return DimensionResult(
        name="品牌成熟度",
        score=float(score),
        confidence=float(confidence),
        metrics={
            "age_years": age_years,
            "estimated_visits": estimated_visits,
            "visits_latest_month": visits_latest,
            "estimated_sales": estimated_sales,
            "employee_count": employee_count,
            "product_count": product_count,
            "social_followers_total": social_followers,
            **{n: s for n, s, _ in used},
        },
        rationale=rationale,
    )


def compute_product_quality(reviews: list[Mapping[str, Any]]) -> DimensionResult:
    df = pd.DataFrame(reviews)
    if df.empty or "stars" not in df.columns:
        return DimensionResult(name="产品质量", score=50.0, confidence=0.2, metrics={"reason": "no_reviews"}, rationale="缺少可用的用户评分数据。")

    df["stars"] = pd.to_numeric(df["stars"], errors="coerce")
    df = df.dropna(subset=["stars"])
    if df.empty:
        return DimensionResult(name="产品质量", score=50.0, confidence=0.2, metrics={"reason": "no_numeric_stars"}, rationale="用户评分字段无法解析为数值。")

    n = int(len(df))
    avg = float(df["stars"].mean())
    low_ratio = float((df["stars"] <= 2).mean())

    base = clamp((avg - 1.0) / 4.0, 0.0, 1.0) * 100.0
    penalty = 25.0 * clamp(low_ratio / 0.25, 0.0, 1.0)
    score = clamp(base - penalty, 0.0, 100.0)

    confidence = sample_size_confidence(n, target=200, min_conf=0.25)

    return DimensionResult(
        name="产品质量",
        score=float(score),
        confidence=float(confidence),
        metrics={
            "review_count": n,
            "avg_stars": avg,
            "low_star_ratio": low_ratio,
            "base_score_from_avg": base,
            "penalty_low_star_ratio": penalty,
        },
        rationale="以平均星级为主，并对低分占比进行惩罚；置信度随评价样本量提升。",
    )


def compute_demand_fit(brand: Mapping[str, Any], traffic: Mapping[str, Any]) -> DimensionResult:
    estimated_sales = safe_float(brand.get("estimated_sales"))
    product_count = safe_float(brand.get("product_count"))

    visits_ts = traffic.get("EstimatedMonthlyVisits", {})
    growth = None
    if isinstance(visits_ts, Mapping) and len(visits_ts) >= 2:
        s = pd.Series(visits_ts)
        s.index = pd.to_datetime(s.index, errors="coerce")
        s = s.dropna().sort_index()
        if len(s) >= 2 and float(s.iloc[-2]) > 0:
            growth = float(s.iloc[-1] / float(s.iloc[-2]) - 1.0)

    sales_score = log_scale_score(estimated_sales, low=5_000_000, high=1_000_000_000)
    catalog_score = linear_score(product_count, low=5, high=80)
    growth_score = None if growth is None else clamp((growth + 0.3) / 0.6, 0.0, 1.0) * 100.0

    components: list[tuple[str, float | None, float]] = [
        ("sales_score", sales_score, 0.55),
        ("catalog_score", catalog_score, 0.25),
        ("growth_score", growth_score, 0.20),
    ]
    used = [(name, s, w) for name, s, w in components if s is not None]
    if not used:
        return DimensionResult(
            name="市场需求匹配度",
            score=50.0,
            confidence=0.2,
            metrics={"reason": "missing_signals"},
            rationale="缺少销量/流量趋势等关键需求信号。",
        )

    weight_sum = sum(w for _, _, w in used)
    score = sum(float(s) * w for _, s, w in used) / weight_sum

    confidence = 0.6
    if estimated_sales is None:
        confidence -= 0.15
    if growth is None:
        confidence -= 0.10
    confidence = clamp(confidence, 0.2, 0.9)

    return DimensionResult(
        name="市场需求匹配度",
        score=float(score),
        confidence=float(confidence),
        metrics={
            "estimated_sales": estimated_sales,
            "product_count": product_count,
            "visit_mom_growth": growth,
            **{n: s for n, s, _ in used},
        },
        rationale="用销售规模作为主要需求代理指标，辅以产品覆盖与近月访问量变化。",
    )


def compute_value_for_money(products: Mapping[str, Any], reviews: list[Mapping[str, Any]]) -> DimensionResult:
    product_list = products.get("products", [])
    prices: list[float] = []
    avail: list[bool] = []
    if isinstance(product_list, list):
        for p in product_list:
            if not isinstance(p, Mapping):
                continue
            for v in p.get("variants", []) or []:
                if not isinstance(v, Mapping):
                    continue
                price = safe_float(v.get("price"))
                if price is not None:
                    prices.append(price)
                a = v.get("available")
                if isinstance(a, bool):
                    avail.append(a)

    median_price = float(pd.Series(prices).median()) if prices else None
    available_ratio = float(pd.Series(avail).mean()) if avail else None

    price_score = piecewise_score(
        median_price,
        breaks=[
            (5.0, 100.0),
            (10.0, 85.0),
            (20.0, 70.0),
            (35.0, 55.0),
            (50.0, 40.0),
            (10_000_000.0, 25.0),
        ],
    )

    df = pd.DataFrame(reviews)
    complaint_ratio = None
    if not df.empty:
        text = (df.get("bodyPositive", "").fillna("").astype(str) + "\n" + df.get("bodyNegative", "").fillna("").astype(str)).str.lower()
        hits = text.str.contains("expensive") | text.str.contains("price") | text.str.contains("too sweet")
        complaint_ratio = float(hits.mean())

    complaint_penalty = 0.0 if complaint_ratio is None else 30.0 * clamp(complaint_ratio / 0.25, 0.0, 1.0)

    score = 50.0
    used_parts: dict[str, float] = {}
    if price_score is not None:
        score = 0.8 * price_score + 0.2 * 100.0
        used_parts["price_score"] = float(price_score)
    score = clamp(score - complaint_penalty, 0.0, 100.0)

    confidence = 0.55
    if median_price is None:
        confidence -= 0.15
    if complaint_ratio is None:
        confidence -= 0.10
    confidence = clamp(confidence, 0.2, 0.85)

    return DimensionResult(
        name="性价比",
        score=float(score),
        confidence=float(confidence),
        metrics={
            "variant_price_median": median_price,
            "variant_available_ratio": available_ratio,
            "review_complaint_ratio_proxy": complaint_ratio,
            "complaint_penalty": complaint_penalty,
            **used_parts,
        },
        rationale="以变体价格中位数为主，并参考评价中“价格/过甜”等敏感词的出现频率进行惩罚。",
    )


def compute_innovation(products: Mapping[str, Any]) -> DimensionResult:
    product_list = products.get("products", [])
    if not isinstance(product_list, list) or not product_list:
        return DimensionResult(name="创新力", score=50.0, confidence=0.2, metrics={"reason": "no_products"}, rationale="缺少产品发布时间信息。")

    df = pd.DataFrame(product_list)
    df["published_at"] = pd.to_datetime(df.get("published_at"), errors="coerce", utc=True)
    now = pd.Timestamp.now(tz="UTC")
    cutoff = now - pd.Timedelta(days=365)

    recent = df[df["published_at"].notna() & (df["published_at"] >= cutoff)]
    recent_count = int(len(recent))
    total = int(len(df))

    recent_ratio = recent_count / total if total > 0 else 0.0
    score = clamp(recent_ratio / 0.35, 0.0, 1.0) * 100.0

    confidence = sample_size_confidence(total, target=60, min_conf=0.35)
    return DimensionResult(
        name="创新力",
        score=float(score),
        confidence=float(confidence),
        metrics={
            "products_total": total,
            "products_published_last_365d": recent_count,
            "recent_publish_ratio": recent_ratio,
        },
        rationale="以过去 365 天内上新占比衡量新品活跃度。",
    )
