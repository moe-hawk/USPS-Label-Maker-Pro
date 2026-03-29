from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from models.address import Address

@dataclass(slots=True)
class AddressCorrection:
    original: Address
    suggested: Address
    accepted: bool | None = None
    source: str = "USPS"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
