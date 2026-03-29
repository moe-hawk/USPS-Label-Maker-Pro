from __future__ import annotations
import math, re
from typing import Any

def normalize_zip(value: str) -> tuple[str, str]:
    digits = re.sub(r"[^0-9]", "", value or "")
    if len(digits) >= 9:
        return digits[:5], digits[5:9]
    return digits[:5], ""

def zip_join(base: str, plus4: str = "") -> str:
    if base and plus4:
        return f"{base}-{plus4}"
    return base or plus4

def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(str(value).strip())
    except Exception:
        return default

def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except Exception:
        return default

def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}

def ceil_stamps(postage: float, forever_rate: float) -> int:
    forever_rate = max(float(forever_rate), 0.01)
    return max(1, math.ceil(float(postage) / forever_rate))

def inch(value: float) -> float:
    return value * 72.0
