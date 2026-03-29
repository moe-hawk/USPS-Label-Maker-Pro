from __future__ import annotations
from dataclasses import dataclass, field
from models.address import Address
from models.mailpiece import Mailpiece
from models.template import Template
from utils.exceptions import ValidationError
from utils.measurements import ceil_stamps

@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    def ok(self) -> bool:
        return not self.errors

class ValidationService:
    def validate_address(self, address: Address, label: str = "Address") -> ValidationResult:
        result = ValidationResult()
        if not address.line1.strip(): result.errors.append(f"{label}: street line 1 is required.")
        if not address.city.strip(): result.errors.append(f"{label}: city is required.")
        if not address.state.strip(): result.errors.append(f"{label}: state is required.")
        if not address.postal_code.strip(): result.errors.append(f"{label}: ZIP code is required.")
        if len(address.company) > 48: result.warnings.append(f"{label}: company line is very long and may wrap.")
        return result

    def validate_mailpiece(self, mailpiece: Mailpiece) -> ValidationResult:
        result = ValidationResult()
        if mailpiece.weight_oz <= 0: result.errors.append("Weight must be greater than zero.")
        if mailpiece.width_in <= 0 or mailpiece.height_in <= 0: result.errors.append("Width and height must be greater than zero.")
        if mailpiece.thickness_in <= 0: result.errors.append("Thickness must be greater than zero.")
        length = max(mailpiece.width_in, mailpiece.height_in)
        height = min(mailpiece.width_in, mailpiece.height_in)
        ratio = (length / height) if height else 0
        if mailpiece.mail_class == "letter":
            if length > 11.5 or height > 6.125 or mailpiece.thickness_in > 0.25 or mailpiece.weight_oz > 3.5:
                result.warnings.append("Letter exceeds standard machinable letter limits and may price as a flat.")
            if ratio and (ratio < 1.3 or ratio > 2.5):
                result.warnings.append("Aspect ratio is outside USPS machinable letter range (1.3-2.5).")
        elif mailpiece.mail_class == "flat":
            if length > 15 or height > 12 or mailpiece.thickness_in > 0.75 or mailpiece.weight_oz > 13:
                result.errors.append("Flat exceeds common First-Class large-envelope size/weight guidance.")
        elif mailpiece.mail_class == "package":
            if mailpiece.thickness_in < 0.1:
                result.suggestions.append("Package thickness was rounded to 0.1 in for API quoting.")
        return result

    def preview_overflow_check(self, to_lines: list[str], from_lines: list[str], template: Template) -> ValidationResult:
        result = ValidationResult()
        if any(len(line) > 46 for line in to_lines): result.warnings.append("Recipient address contains a long line that may wrap.")
        if any(len(line) > 42 for line in from_lines): result.warnings.append("Return address contains a long line that may wrap.")
        if template.show_logo and template.logo_path and len(from_lines) > 4:
            result.suggestions.append("A smaller logo or slightly lower return block may improve fit.")
        return result

    def combine(self, *results: ValidationResult) -> ValidationResult:
        merged = ValidationResult()
        for r in results:
            merged.errors.extend(r.errors)
            merged.warnings.extend(r.warnings)
            merged.suggestions.extend(r.suggestions)
        return merged

    def raise_on_errors(self, result: ValidationResult) -> None:
        if result.errors:
            raise ValidationError("\n".join(result.errors))
