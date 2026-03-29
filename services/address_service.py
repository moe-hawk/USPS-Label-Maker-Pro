from __future__ import annotations
from models.address import Address
from models.correction import AddressCorrection
from storage.repositories.corrections_repo import CorrectionsRepository

class AddressService:
    def __init__(self, corrections_repo: CorrectionsRepository | None = None) -> None:
        self.corrections_repo = corrections_repo

    def standardize(self, provider, address: Address) -> Address:
        return provider.validate_address(address)

    def diff_addresses(self, original: Address, suggested: Address) -> list[tuple[str, str, str]]:
        diffs = []
        fields = [
            ("name", original.name, suggested.name),
            ("company", original.company, suggested.company),
            ("line1", original.line1, suggested.line1),
            ("line2", original.line2, suggested.line2),
            ("city", original.city, suggested.city),
            ("state", original.state, suggested.state),
            ("postal_code", original.formatted_postal_code(), suggested.formatted_postal_code()),
        ]
        for field, old, new in fields:
            if (old or "").strip() != (new or "").strip():
                diffs.append((field, old or "", new or ""))
        return diffs

    def save_correction(self, original: Address, suggested: Address, accepted: bool | None, source: str = "USPS") -> None:
        if not self.corrections_repo:
            return
        self.corrections_repo.add(AddressCorrection(original=original, suggested=suggested, accepted=accepted, source=source))
