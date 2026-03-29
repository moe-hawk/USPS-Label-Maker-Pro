from __future__ import annotations
from models.address import Address
from models.mailpiece import Mailpiece
from models.rate_quote import RateQuote
from providers.base import ShippingProvider
from providers.usps.addresses import USPSAddressesAPI
from providers.usps.auth import USPSAuth
from providers.usps.pricing import USPSPricingAPI

class USPSProvider(ShippingProvider):
    def __init__(self, settings: dict) -> None:
        base_url = "https://apis-tem.usps.com" if settings.get("usps_use_test_env", True) else "https://apis.usps.com"
        self.auth = USPSAuth(base_url, settings.get("usps_client_id", ""), settings.get("usps_client_secret", ""))
        self.address_api = USPSAddressesAPI(base_url, self.auth.token)
        self.pricing_api = USPSPricingAPI(base_url, self.auth.token, settings.get("usps_account_type", "EPS"), settings.get("usps_account_number", ""))

    def provider_name(self) -> str: return "USPS"
    def validate_address(self, address: Address) -> Address: return self.address_api.get_address(address)
    def quote(self, from_address: Address, to_address: Address, mailpiece: Mailpiece) -> list[RateQuote]:
        return self.pricing_api.quote(from_address, to_address, mailpiece)
