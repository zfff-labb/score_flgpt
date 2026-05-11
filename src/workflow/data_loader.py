from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_sample_data(data_dir: Path) -> dict[str, Any]:
    return {
        "brand": load_json(data_dir / "brand-info.json"),
        "company": load_json(data_dir / "company-info.json"),
        "products": load_json(data_dir / "products-info.json"),
        "traffic": load_json(data_dir / "traffic-info.json"),
        "reviews": load_json(data_dir / "review-info.json"),
    }

