from __future__ import annotations
import requests
from models.address import Address
from models.mailpiece import Mailpiece
from models.rate_quote import RateQuote
from providers.base import ShippingProvider
from utils.exceptions import ProviderError

class EasyPostProvider(ShippingProvider):
    def __init__(self, settings: dict) -> None:
        self.api_key = settings.get("easypost_api_key", "").strip()
        self.base_url = "https://api.easypost.com/v2"

    def _headers(self) -> dict: return {"Content-Type": "application/json"}
    def _auth(self) -> tuple[str, str]:
        if not self.api_key: raise ProviderError("EasyPost API key is not configured.")
        return (self.api_key, "")

    def provider_name(self) -> str: return "EasyPost"

    def validate_address(self, address: Address) -> Address:
        payload = {"address": {
            "company": address.company, "name": address.name,
            "street1": address.line1, "street2": address.line2,
            "city": address.city, "state": address.state,
            "zip": address.formatted_postal_code(), "country": address.country,
            "phone": address.phone, "email": address.email, "verify": ["delivery"]}}
        resp = requests.post(f"{self.base_url}/addresses", json=payload, headers=self._headers(), auth=self._auth(), timeout=30)
        if resp.status_code >= 400:
            raise ProviderError(f"EasyPost address validation failed: {resp.status_code} {resp.text}")
        data = resp.json()
        return Address(
            name=data.get("name") or address.name, company=data.get("company") or address.company,
            line1=data.get("street1") or address.line1, line2=data.get("street2") or address.line2,
            city=data.get("city") or address.city, state=data.get("state") or address.state,
            postal_code=data.get("zip") or address.postal_code, country=data.get("country") or address.country,
            phone=data.get("phone") or address.phone, email=data.get("email") or address.email)

    def quote(self, from_address: Address, to_address: Address, mailpiece: Mailpiece) -> list[RateQuote]:
        payload = {"shipment": {
            "from_address": self._addr(from_address), "to_address": self._addr(to_address),
            "parcel": {"length": max(mailpiece.width_in, mailpiece.height_in),
                "width": min(mailpiece.width_in, mailpiece.height_in),
                "height": max(mailpiece.thickness_in, 0.1), "weight": max(mailpiece.weight_oz, 0.1)}}}
        resp = requests.post(f"{self.base_url}/shipments", json=payload, headers=self._headers(), auth=self._auth(), timeout=30)
        if resp.status_code >= 400:
            raise ProviderError(f"EasyPost shipment quote failed: {resp.status_code} {resp.text}")
        data = resp.json()
        rates = []
        for rate in data.get("rates", []):
            try:
                rates.append(RateQuote(provider="EasyPost",
                    service_name=f'{rate.get("carrier","")}{rate.get("service","")}'.strip(),
                    amount_usd=float(rate.get("rate", 0) or 0),
                    retail_or_commercial=(rate.get("rate_type") or "").lower(), raw=rate))
            except Exception: continue
        if not rates: raise ProviderError(f"EasyPost response returned no rates: {data}")
        return sorted(rates, key=lambda r: r.amount_usd)

    def purchase_label(self, from_address: Address, to_address: Address, mailpiece: Mailpiece, service_hint: str | None = None) -> dict:
        payload = {"shipment": {
            "from_address": self._addr(from_address), "to_address": self._addr(to_address),
            "parcel": {"length": max(mailpiece.width_in, mailpiece.height_in),
                "width": min(mailpiece.width_in, mailpiece.height_in),
                "height": max(mailpiece.thickness_in, 0.1), "weight": max(mailpiece.weight_oz, 0.1)}}}
        shipment = requests.post(f"{self.base_url}/shipments", json=payload, headers=self._headers(), auth=self._auth(), timeout=30)
        if shipment.status_code >= 400:
            raise ProviderError(f"EasyPost shipment create failed: {shipment.status_code} {shipment.text}")
        shipment_data = shipment.json()
        rates = shipment_data.get("rates", [])
        if not rates: raise ProviderError("EasyPost returned no rates to purchase.")
        chosen = rates[0]
        if service_hint:
            for rate in rates:
                if service_hint.lower() in f'{rate.get("carrier","")}{rate.get("service","")}'.lower():
                    chosen = rate; break
        buy_resp = requests.post(f"{self.base_url}/shipments/{shipment_data['id']}/buy",
            json={"rate": {"id": chosen["id"]}}, headers=self._headers(), auth=self._auth(), timeout=30)
        if buy_resp.status_code >= 400:
            raise ProviderError(f"EasyPost buy label failed: {buy_resp.status_code} {buy_resp.text}")
        return buy_resp.json()

    def _addr(self, address: Address) -> dict:
        return {"company": address.company, "name": address.name, "street1": address.line1,
            "street2": address.line2, "city": address.city, "state": address.state,
            "zip": address.formatted_postal_code(), "country": address.country,
            "phone": address.phone, "email": address.email}
