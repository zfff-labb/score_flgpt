from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class DimensionResult:
    name: str
    score: float
    confidence: float
    metrics: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScoreReport:
    brand: str
    total_score: float
    total_confidence: float
    dimensions: list[DimensionResult]
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "brand": self.brand,
            "total_score": self.total_score,
            "total_confidence": self.total_confidence,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "meta": self.meta,
        }

