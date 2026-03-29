from __future__ import annotations
from abc import ABC, abstractmethod
from models.address import Address
from models.mailpiece import Mailpiece
from models.rate_quote import RateQuote

class ShippingProvider(ABC):
    @abstractmethod
    def provider_name(self) -> str: ...
    @abstractmethod
    def validate_address(self, address: Address) -> Address: ...
    @abstractmethod
    def quote(self, from_address: Address, to_address: Address, mailpiece: Mailpiece) -> list[RateQuote]: ...
    def purchase_label(self, from_address: Address, to_address: Address, mailpiece: Mailpiece, service_hint: str | None = None) -> dict:
        raise NotImplementedError(f"{self.provider_name()} does not implement label purchasing")
