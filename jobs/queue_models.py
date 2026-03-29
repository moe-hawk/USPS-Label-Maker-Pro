from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class JobRequest:
    mode: str
    source_rows: list[dict]
    mapping: dict[str, str]
    template_name: str
    output_dir: str
    provider_name: str
    standardize_addresses: bool
    auto_accept_standardized: bool
    buy_paid_labels: bool = False
    skip_positions: set[int] = field(default_factory=set)
