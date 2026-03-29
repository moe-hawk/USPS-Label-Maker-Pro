from __future__ import annotations
import math
from models.address import Address
from models.mailpiece import Mailpiece
from models.rate_quote import RateQuote
from utils.exceptions import ProviderError
from utils.measurements import ceil_stamps

class PostageService:
    def __init__(self, settings: dict) -> None:
        self.settings = settings

    def get_quotes(self, provider, from_addr: Address, to_addr: Address, mailpiece: Mailpiece) -> list[RateQuote]:
        try:
            quotes = provider.quote(from_addr, to_addr, mailpiece)
        except Exception:
            if mailpiece.mail_class in {"letter", "flat"}:
                return [self.fallback_estimate(mailpiece)]
            raise
        forever = float(self.settings.get("forever_stamp_price", 0.78))
        for quote in quotes:
            quote.estimated_forever_stamps = ceil_stamps(quote.amount_usd, forever)
        return quotes

    def fallback_estimate(self, mailpiece: Mailpiece) -> RateQuote:
        forever = float(self.settings.get("forever_stamp_price", 0.78))
        addl_oz = float(self.settings.get("letter_additional_ounce_price", 0.29))
        nonmach = float(self.settings.get("nonmachinable_surcharge", 0.49))
        flat_1oz = float(self.settings.get("flat_1oz_price", 1.63))
        length = max(mailpiece.width_in, mailpiece.height_in)
        height = min(mailpiece.width_in, mailpiece.height_in)
        ratio = (length / height) if height else 0
        if mailpiece.mail_class == "letter" and length <= 11.5 and height <= 6.125 and mailpiece.thickness_in <= 0.25 and mailpiece.weight_oz <= 3.5:
            extra_ounces = max(0, math.ceil(mailpiece.weight_oz - 1.0))
            amount = forever + extra_ounces * addl_oz
            notes = "Fallback retail letter estimate."
            if mailpiece.nonmachinable or (ratio and (ratio < 1.3 or ratio > 2.5)):
                amount += nonmach
                notes += " Nonmachinable surcharge included."
            return RateQuote(provider="Local Estimate", service_name="Stamped Letter",
                amount_usd=round(amount, 2), retail_or_commercial="retail",
                estimated_forever_stamps=ceil_stamps(round(amount, 2), forever), notes=notes)
        if mailpiece.mail_class in {"flat", "letter"} and length <= 15 and height <= 12 and mailpiece.thickness_in <= 0.75 and mailpiece.weight_oz <= 13:
            price = flat_1oz
            current_oz = 1.0
            while current_oz < math.ceil(mailpiece.weight_oz):
                current_oz += 1.0
                if current_oz <= 4: price += 0.27
                elif current_oz <= 9: price += 0.28
                else: price += 0.30
            return RateQuote(provider="Local Estimate", service_name="Large Envelope / Flat",
                amount_usd=round(price, 2), retail_or_commercial="retail",
                estimated_forever_stamps=ceil_stamps(round(price, 2), forever),
                notes="Fallback retail flat estimate.")
        raise ProviderError("Could not retrieve a live quote and no local fallback is available for this package type.")
