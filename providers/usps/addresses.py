from __future__ import annotations
import requests
from models.address import Address
from utils.exceptions import ProviderError
from utils.measurements import normalize_zip

class USPSAddressesAPI:
    def __init__(self, base_url: str, token_getter) -> None:
        self.base_url = base_url.rstrip("/")
        self.token_getter = token_getter

    def get_address(self, address: Address) -> Address:
        if not address.line1.strip():
            raise ProviderError("USPS validation needs street address line 1.")
        if not (address.city.strip() and address.state.strip()) and not address.postal_code.strip():
            raise ProviderError("USPS validation needs city/state or ZIP code.")
        params = {"streetAddress": address.line1.strip()}
        if address.line2.strip(): params["secondaryAddress"] = address.line2.strip()
        if address.city.strip(): params["city"] = address.city.strip()
        if address.state.strip(): params["state"] = address.state.strip()
        if address.postal_code.strip():
            base, _ = normalize_zip(address.formatted_postal_code())
            if base: params["ZIPCode"] = base
        resp = requests.get(f"{self.base_url}/addresses/v3/address",
            headers={"Authorization": f"Bearer {self.token_getter()}"}, params=params, timeout=30)
        if resp.status_code >= 400:
            raise ProviderError(f"USPS address validation failed: {resp.status_code} {resp.text}")
        return self._parse_address_response(address, resp.json())

    def _parse_address_response(self, original: Address, data: dict) -> Address:
        ab = data.get("address") or data.get("result") or data
        return Address(
            name=original.name, company=original.company,
            line1=str(ab.get("streetAddress") or ab.get("deliveryAddress") or ab.get("addressLine1") or original.line1).strip(),
            line2=str(ab.get("secondaryAddress") or ab.get("addressLine2") or original.line2).strip(),
            city=str(ab.get("city") or (ab.get("cityState") or {}).get("city") or original.city).strip(),
            state=str(ab.get("state") or (ab.get("cityState") or {}).get("state") or original.state).strip(),
            postal_code=str(ab.get("ZIPCode") or ab.get("zipCode") or ab.get("postalCode") or original.postal_code).strip(),
            postal_code_plus4=str(ab.get("ZIPPlus4") or ab.get("plus4") or ab.get("postalCodePlus4") or original.postal_code_plus4).strip(),
            country=original.country, phone=original.phone, email=original.email)
