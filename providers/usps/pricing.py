from __future__ import annotations
from datetime import date
from typing import Any
import requests
from models.address import Address
from models.mailpiece import Mailpiece
from models.rate_quote import RateQuote
from utils.exceptions import ProviderError
from utils.measurements import normalize_zip

def _extract_amounts(node: Any, results: list[float]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            lk = str(key).lower()
            if isinstance(value, (int, float)) and lk in {"price","postage","amount","totalprice","totalbaseprice","baseprice"}:
                if float(value) > 0: results.append(float(value))
            _extract_amounts(value, results)
    elif isinstance(node, list):
        for child in node: _extract_amounts(child, results)

def _best_amount(data: dict) -> float | None:
    results: list[float] = []
    _extract_amounts(data, results)
    return min(results) if results else None

class USPSPricingAPI:
    def __init__(self, base_url: str, token_getter, account_type: str = "EPS", account_number: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.token_getter = token_getter
        self.account_type = account_type
        self.account_number = account_number

    def quote(self, from_address: Address, to_address: Address, mailpiece: Mailpiece) -> list[RateQuote]:
        if mailpiece.mail_class in {"letter", "flat"}:
            return [self._quote_letter_rates(mailpiece)]
        return [self._quote_package(from_address, to_address, mailpiece)]

    def _quote_letter_rates(self, mailpiece: Mailpiece) -> RateQuote:
        payload = {
            "weight": float(mailpiece.weight_oz),
            "length": float(max(mailpiece.width_in, mailpiece.height_in)),
            "height": float(min(mailpiece.width_in, mailpiece.height_in)),
            "thickness": float(mailpiece.thickness_in),
            "processingCategory": "LETTERS" if mailpiece.mail_class == "letter" else "FLATS",
            "mailingDate": mailpiece.mailing_date or str(date.today()),
            "nonMachinableIndicators": {
                "hasClosureDevices": bool(mailpiece.nonmachinable), "isPolybagged": False,
                "hasLooseItems": False, "isRigid": bool(mailpiece.nonmachinable),
                "isSelfMailer": False, "isBooklet": False, "hasWrappedItems": False,
                "isOddShaped": bool(mailpiece.nonmachinable)},
        }
        resp = requests.post(f"{self.base_url}/prices/v3/letter-rates/search",
            headers={"Authorization": f"Bearer {self.token_getter()}"}, json=payload, timeout=30)
        if resp.status_code >= 400:
            raise ProviderError(f"USPS letter-rates API failed: {resp.status_code} {resp.text}")
        data = resp.json()
        amount = _best_amount(data)
        if amount is None:
            raise ProviderError(f"USPS letter-rates response could not be parsed: {data}")
        return RateQuote(provider="USPS", service_name="Letter Rates", amount_usd=amount, retail_or_commercial="retail", raw=data)

    def _quote_package(self, from_address: Address, to_address: Address, mailpiece: Mailpiece) -> RateQuote:
        origin_zip, _ = normalize_zip(from_address.formatted_postal_code())
        dest_zip, _ = normalize_zip(to_address.formatted_postal_code())
        if not origin_zip or not dest_zip:
            raise ProviderError("USPS package pricing requires origin and destination ZIP codes.")
        payload = {
            "originZIPCode": origin_zip, "destinationZIPCode": dest_zip,
            "weight": float(mailpiece.weight_oz),
            "length": float(max(mailpiece.width_in, mailpiece.height_in)),
            "width": float(min(mailpiece.width_in, mailpiece.height_in)),
            "height": float(max(mailpiece.thickness_in, 0.1)),
            "mailClass": "USPS_GROUND_ADVANTAGE", "processingCategory": "MACHINABLE",
            "destinationEntryFacilityType": "NONE", "priceType": "RETAIL",
            "mailingDate": mailpiece.mailing_date or str(date.today()),
        }
        if self.account_number:
            payload["accountType"] = self.account_type
            payload["accountNumber"] = self.account_number
        resp = requests.post(f"{self.base_url}/prices/v3/base-rates/search",
            headers={"Authorization": f"Bearer {self.token_getter()}"}, json=payload, timeout=30)
        if resp.status_code >= 400:
            raise ProviderError(f"USPS package pricing failed: {resp.status_code} {resp.text}")
        data = resp.json()
        amount = _best_amount(data)
        if amount is None:
            raise ProviderError(f"USPS package pricing response could not be parsed: {data}")
        return RateQuote(provider="USPS", service_name="USPS Ground Advantage", amount_usd=amount, retail_or_commercial="retail", raw=data)
