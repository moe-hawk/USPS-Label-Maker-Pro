from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

MailClass = Literal["letter", "flat", "package"]
OutputMode = Literal["envelope", "cut_label", "avery_5160", "avery_8160", "avery_5260"]

@dataclass(slots=True)
class Mailpiece:
    mail_class: MailClass = "letter"
    width_in: float = 9.5
    height_in: float = 4.125
    thickness_in: float = 0.02
    weight_oz: float = 1.0
    envelope_name: str = "#10 Business Envelope"
    nonmachinable: bool = False
    output_mode: OutputMode = "cut_label"
    processing_category: str = "LETTERS"
    mailing_date: str = ""

    def max_dimension(self) -> float:
        return max(self.width_in, self.height_in)

    def min_dimension(self) -> float:
        return min(self.width_in, self.height_in)
