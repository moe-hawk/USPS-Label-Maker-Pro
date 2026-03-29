from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from models.address import Address

@dataclass(slots=True)
class Contact:
    id: int | None = None
    label: str = ""
    subject: str = ""
    tags: str = ""
    notes: str = ""
    address: Address = field(default_factory=Address)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
