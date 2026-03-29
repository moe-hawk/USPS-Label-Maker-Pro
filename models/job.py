from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(slots=True)
class LabelJob:
    id: int | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    mode: str = "single"
    source_file: str = ""
    output_file: str = ""
    total_rows: int = 0
    success_rows: int = 0
    failed_rows: int = 0
    status: str = "pending"
    notes: str = ""
