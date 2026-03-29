from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List

@dataclass(slots=True)
class Address:
    name: str = ""
    company: str = ""
    line1: str = ""
    line2: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    postal_code_plus4: str = ""
    country: str = "US"
    phone: str = ""
    email: str = ""

    def formatted_postal_code(self) -> str:
        base = (self.postal_code or "").strip()
        plus4 = (self.postal_code_plus4 or "").strip()
        if plus4 and base and "+" not in base and "-" not in base:
            return f"{base}-{plus4}"
        return base or plus4

    def lines(self) -> List[str]:
        lines: List[str] = []
        if self.name.strip():
            lines.append(self.name.strip())
        if self.company.strip():
            lines.append(self.company.strip())
        if self.line1.strip():
            lines.append(self.line1.strip())
        if self.line2.strip():
            lines.append(self.line2.strip())
        city_state_zip = " ".join(
            part for part in [
                f"{self.city.strip()}," if self.city.strip() else "",
                self.state.strip(),
                self.formatted_postal_code(),
            ] if part
        ).strip()
        if city_state_zip:
            lines.append(city_state_zip.replace(" ,", ","))
        return lines

    def as_dict(self) -> Dict[str, str]:
        return asdict(self)

    def short_label(self) -> str:
        parts = [self.name or self.company, self.line1, f"{self.city}, {self.state} {self.formatted_postal_code()}"]
        return ", ".join(part.strip() for part in parts if part and part.strip())

    def is_minimally_complete(self) -> bool:
        return bool(self.line1.strip() and self.city.strip() and self.state.strip() and self.postal_code.strip())
