from __future__ import annotations
import requests
from models.address import Address
from models.mailpiece import Mailpiece
from models.rate_quote import RateQuote
from providers.base import ShippingProvider
from utils.exceptions import ProviderError

class ShippoProvider(ShippingProvider):
    def __init__(self, settings: dict) -> None:
        self.api_token = settings.get("shippo_api_token", "").strip()
        self.base_url = "https://api.goshippo.com"

    def _headers(self) -> dict:
        if not self.api_token: raise ProviderError("Shippo API token is not configured.")
        return {"Authorization": f"ShippoToken {self.api_token}", "Content-Type": "application/json"}

    def provider_name(self) -> str: return "Shippo"

    def validate_address(self, address: Address) -> Address:
        payload = {"name": address.name, "company": address.company,
            "street1": address.line1, "street2": address.line2, "city": address.city,
            "state": address.state, "zip": address.formatted_postal_code(),
            "country": address.country, "phone": address.phone, "email": address.email, "validate": True}
        resp = requests.post(f"{self.base_url}/addresses/", json=payload, headers=self._headers(), timeout=30)
        if resp.status_code >= 400:
            raise ProviderError(f"Shippo address validation failed: {resp.status_code} {resp.text}")
        data = resp.json()
        validation = data.get("validation_results", {})
        if validation and validation.get("is_valid") is False:
            raise ProviderError(f"Shippo marked the address invalid: {validation}")
        return Address(
            name=data.get("name") or address.name, company=data.get("company") or address.company,
            line1=data.get("street1") or address.line1, line2=data.get("street2") or address.line2,
            city=data.get("city") or address.city, state=data.get("state") or address.state,
            postal_code=data.get("zip") or address.postal_code, country=data.get("country") or address.country,
            phone=data.get("phone") or address.phone, email=data.get("email") or address.email)

    def quote(self, from_address: Address, to_address: Address, mailpiece: Mailpiece) -> list[RateQuote]:
        payload = {
            "address_from": self._addr(from_address), "address_to": self._addr(to_address),
            "parcels": [{"length": str(max(mailpiece.width_in, mailpiece.height_in)),
                "width": str(min(mailpiece.width_in, mailpiece.height_in)),
                "height": str(max(mailpiece.thickness_in, 0.1)), "distance_unit": "in",
                "weight": str(max(mailpiece.weight_oz, 0.1)), "mass_unit": "oz"}],
            "async": False}
        resp = requests.post(f"{self.base_url}/shipments/", json=payload, headers=self._headers(), timeout=30)
        if resp.status_code >= 400:
            raise ProviderError(f"Shippo shipment quote failed: {resp.status_code} {resp.text}")
        data = resp.json()
        rates = []
        for rate in data.get("rates", []):
            try:
                # Evaluate attributes list explicitly to avoid operator-precedence bugs.
                attrs = rate.get("attributes") or []
                tier = "commercial" if "COMMERCIAL" in attrs else "retail"
                rates.append(RateQuote(provider="Shippo",
                    service_name=rate.get("servicelevel", {}).get("name") or rate.get("provider", "Rate"),
                    amount_usd=float(rate.get("amount") or 0),
                    retail_or_commercial=tier, raw=rate))
            except Exception: continue
        if not rates: raise ProviderError(f"Shippo response returned no rates: {data}")
        return sorted(rates, key=lambda r: r.amount_usd)

    def purchase_label(self, from_address: Address, to_address: Address, mailpiece: Mailpiece, service_hint: str | None = None) -> dict:
        parcel = {"length": str(max(mailpiece.width_in, mailpiece.height_in)),
            "width": str(min(mailpiece.width_in, mailpiece.height_in)),
            "height": str(max(mailpiece.thickness_in, 0.1)), "distance_unit": "in",
            "weight": str(max(mailpiece.weight_oz, 0.1)), "mass_unit": "oz"}
        shipment = requests.post(f"{self.base_url}/shipments/",
            json={"address_from": self._addr(from_address), "address_to": self._addr(to_address),
                "parcels": [parcel], "async": False},
            headers=self._headers(), timeout=30)
        if shipment.status_code >= 400:
            raise ProviderError(f"Shippo shipment create failed: {shipment.status_code} {shipment.text}")
        shipment_data = shipment.json()
        rates = shipment_data.get("rates", [])
        if not rates: raise ProviderError("Shippo returned no rates to purchase.")
        chosen = rates[0]
        if service_hint:
            for rate in rates:
                if service_hint.lower() in str(rate.get("servicelevel", {}).get("name", "")).lower():
                    chosen = rate; break
        trans = requests.post(f"{self.base_url}/transactions/",
            json={"rate": chosen["object_id"], "async": False},
            headers=self._headers(), timeout=30)
        if trans.status_code >= 400:
            raise ProviderError(f"Shippo label purchase failed: {trans.status_code} {trans.text}")
        return trans.json()

    def _addr(self, address: Address) -> dict:
        return {"name": address.name, "company": address.company, "street1": address.line1,
            "street2": address.line2, "city": address.city, "state": address.state,
            "zip": address.formatted_postal_code(), "country": address.country,
            "phone": address.phone, "email": address.email}
