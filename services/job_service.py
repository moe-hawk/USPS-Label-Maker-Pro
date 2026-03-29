from __future__ import annotations
import json
from pathlib import Path
from models.job import LabelJob
from pdf.avery_renderer import AveryRenderer
from pdf.envelope_renderer import EnvelopeRenderer
from pdf.label_renderer import LabelRenderer
from providers.easypost.provider import EasyPostProvider
from providers.shippo.provider import ShippoProvider
from providers.usps.provider import USPSProvider
from services.address_service import AddressService
from services.import_service import ImportService
from services.postage_service import PostageService
from services.validation_service import ValidationService
from storage.repositories.jobs_repo import JobsRepository
from storage.repositories.templates_repo import TemplatesRepository
from utils.csv_utils import resolve
from utils.exceptions import ProviderError, ValidationError
from utils.file_utils import ensure_dir, sanitize_filename

class JobService:
    def __init__(self, settings: dict, templates_repo: TemplatesRepository,
                 jobs_repo: JobsRepository, address_service: AddressService) -> None:
        self.settings = settings
        self.templates_repo = templates_repo
        self.jobs_repo = jobs_repo
        self.address_service = address_service
        self.validation = ValidationService()
        self.importer = ImportService()
        self.postage = PostageService(settings)
        self.label_renderer = LabelRenderer()
        self.envelope_renderer = EnvelopeRenderer()
        self.avery_renderer = AveryRenderer()
        # Provider instances are cached so USPSAuth's OAuth token survives
        # across all rows in a batch job instead of being discarded per row.
        self._provider_cache: dict[str, object] = {}

    def provider_for_name(self, provider_name: str):
        name = (provider_name or self.settings.get("provider", "USPS")).upper()
        if name not in self._provider_cache:
            if name == "USPS":
                self._provider_cache[name] = USPSProvider(self.settings)
            elif name == "EASYPOST":
                self._provider_cache[name] = EasyPostProvider(self.settings)
            elif name == "SHIPPO":
                self._provider_cache[name] = ShippoProvider(self.settings)
            else:
                raise ProviderError(f"Unknown provider: {provider_name}")
        return self._provider_cache[name]

    def invalidate_provider_cache(self) -> None:
        """Call after settings change so stale credentials are not reused."""
        self._provider_cache.clear()

    def create_job(self, mode: str, source_file: str = "", total_rows: int = 0) -> LabelJob:
        job = LabelJob(mode=mode, source_file=source_file, total_rows=total_rows, status="running")
        return self.jobs_repo.save(job)

    def finalize_job(self, job: LabelJob, success: int, failed: int, output_file: str = "") -> LabelJob:
        job.success_rows = success
        job.failed_rows = failed
        job.output_file = output_file
        job.status = "complete" if failed == 0 else "complete_with_errors"
        return self.jobs_repo.save(job)

    def fail_job(self, job: LabelJob, notes: str) -> None:
        job.status = "failed"
        job.notes = notes
        self.jobs_repo.save(job)

    def process_single(self, from_address, to_address, mailpiece, template_name: str,
                       output_dir: str, provider_name: str, subject: str = "",
                       standardize_addresses: bool = False, auto_accept_standardized: bool = False,
                       buy_paid_labels: bool = False, correction_callback=None) -> dict:
        row = {
            "from_name": from_address.name, "from_company": from_address.company,
            "from_line1": from_address.line1, "from_line2": from_address.line2,
            "from_city": from_address.city, "from_state": from_address.state,
            "from_zip": from_address.formatted_postal_code(),
            "to_name": to_address.name, "to_company": to_address.company,
            "to_line1": to_address.line1, "to_line2": to_address.line2,
            "to_city": to_address.city, "to_state": to_address.state,
            "to_zip": to_address.formatted_postal_code(),
            "subject": subject, "weight_oz": str(mailpiece.weight_oz),
            "width_in": str(mailpiece.width_in), "height_in": str(mailpiece.height_in),
            "thickness_in": str(mailpiece.thickness_in), "mail_class": mailpiece.mail_class,
            "output_mode": mailpiece.output_mode,
            "nonmachinable": str(mailpiece.nonmachinable).lower(), "notes": "",
        }
        mapping = {k: k for k in row}
        return self.process_batch_row(
            row_number=1, row=row, mapping=mapping, template_name=template_name,
            output_dir=output_dir, provider_name=provider_name,
            standardize_addresses=standardize_addresses,
            auto_accept_standardized=auto_accept_standardized,
            buy_paid_labels=buy_paid_labels, correction_callback=correction_callback)

    def process_batch_row(self, row_number: int, row: dict, mapping: dict[str, str],
                          template_name: str, output_dir: str, provider_name: str,
                          standardize_addresses: bool, auto_accept_standardized: bool,
                          buy_paid_labels: bool, correction_callback=None) -> dict:
        from_address, to_address, mailpiece, subject, notes = self.importer.row_to_objects(row, mapping)
        template = self.templates_repo.get_by_name(template_name)
        if not template:
            raise ValidationError(f"Template not found: {template_name}")

        # Read the raw CSV cell directly: ImportService always defaults
        # mailpiece.output_mode to "cut_label" when the column is absent, so
        # using mailpiece.output_mode would silently override Avery templates.
        csv_mode = resolve(row, mapping, "output_mode").strip().lower()
        effective_mode = csv_mode or template.output_mode

        validation = self.validation.combine(
            self.validation.validate_address(from_address, "From address"),
            self.validation.validate_address(to_address, "To address"),
            self.validation.validate_mailpiece(mailpiece),
            self.validation.preview_overflow_check(to_address.lines(), from_address.lines(), template))
        self.validation.raise_on_errors(validation)

        provider = self.provider_for_name(provider_name)

        corrected_to = to_address
        if standardize_addresses:
            suggested = self.address_service.standardize(provider, to_address)
            diffs = self.address_service.diff_addresses(to_address, suggested)
            if diffs:
                accept = auto_accept_standardized
                if correction_callback is not None and not auto_accept_standardized:
                    accept = bool(correction_callback(row_number, to_address.short_label(), to_address, suggested))
                self.address_service.save_correction(to_address, suggested, accept, provider.provider_name())
                if accept:
                    corrected_to = suggested

        corrected_from = from_address
        if standardize_addresses:
            try:
                suggested_from = self.address_service.standardize(provider, from_address)
                diffs = self.address_service.diff_addresses(from_address, suggested_from)
                if diffs:
                    self.address_service.save_correction(from_address, suggested_from,
                        True if auto_accept_standardized else None, provider.provider_name())
                    if auto_accept_standardized:
                        corrected_from = suggested_from
            except Exception:
                pass

        quotes = self.postage.get_quotes(provider, corrected_from, corrected_to, mailpiece)
        best_quote = quotes[0]
        postage_text = f"Estimated postage: ${best_quote.amount_usd:.2f} | Forever stamps: {best_quote.estimated_forever_stamps}"
        recipient_label = corrected_to.short_label()[:120]
        output_dir = str(ensure_dir(output_dir))
        stem = sanitize_filename(f"{row_number:03d}-{corrected_to.company or corrected_to.name or 'label'}")

        if effective_mode == "envelope":
            output_path = str(Path(output_dir) / f"{stem}.pdf")
            self.envelope_renderer.render(output_path, corrected_from, corrected_to, mailpiece, template, subject=subject, postage_text=postage_text)
        elif effective_mode.startswith("avery_"):
            output_path = str(Path(output_dir) / f"{stem}.pdf")
            self.avery_renderer.render(output_path, [{"from_address": corrected_from, "to_address": corrected_to, "subject": subject}], template, effective_mode)
        else:
            output_path = str(Path(output_dir) / f"{stem}.pdf")
            self.label_renderer.render(output_path, corrected_from, corrected_to, mailpiece, template, subject=subject, postage_text=postage_text)

        purchase_data = None
        if buy_paid_labels and provider.provider_name() in {"EasyPost", "Shippo"}:
            purchase_data = provider.purchase_label(corrected_from, corrected_to, mailpiece, service_hint=best_quote.service_name)

        return {
            "recipient_label": recipient_label, "output_path": output_path,
            "quote_line": best_quote.display_line(), "best_quote": best_quote,
            "purchase_data": purchase_data, "warnings": validation.warnings,
            "suggestions": validation.suggestions,
            "corrected_to": corrected_to, "corrected_from": corrected_from,
        }
