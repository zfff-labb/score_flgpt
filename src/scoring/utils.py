from __future__ import annotations

import math
from typing import Any


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def log_scale_score(value: float | None, low: float, high: float) -> float | None:
    if value is None:
        return None
    if value <= 0 or low <= 0 or high <= 0 or high <= low:
        return None
    lv = math.log10(value)
    l0 = math.log10(low)
    l1 = math.log10(high)
    return 100.0 * clamp((lv - l0) / (l1 - l0), 0.0, 1.0)


def linear_score(value: float | None, low: float, high: float) -> float | None:
    if value is None:
        return None
    if high <= low:
        return None
    return 100.0 * clamp((value - low) / (high - low), 0.0, 1.0)


def piecewise_score(value: float | None, breaks: list[tuple[float, float]]) -> float | None:
    if value is None:
        return None
    for threshold, score in sorted(breaks, key=lambda x: x[0]):
        if value <= threshold:
            return float(score)
    return float(breaks[-1][1])


def sample_size_confidence(n: int | None, target: int, min_conf: float = 0.2) -> float:
    if n is None or n <= 0:
        return min_conf
    return clamp(min_conf + (1.0 - min_conf) * (n / float(target)), min_conf, 1.0)

