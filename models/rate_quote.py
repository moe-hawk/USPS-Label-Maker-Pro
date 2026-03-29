from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class RateQuote:
    provider: str
    service_name: str
    amount_usd: float
    currency: str = "USD"
    retail_or_commercial: str = "retail"
    estimated_forever_stamps: int = 0
    notes: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)

    def display_line(self) -> str:
        flavor = f" ({self.retail_or_commercial})" if self.retail_or_commercial else ""
        return f"{self.provider} - {self.service_name}: ${self.amount_usd:.2f}{flavor}"
