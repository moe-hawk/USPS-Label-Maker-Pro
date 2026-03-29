from __future__ import annotations
import json, os, queue, threading
from pathlib import Path
from gui.dialogs.address_correction_dialog import AddressCorrectionDialog
from gui.tabs.batch_tab import BatchTab
from gui.tabs.contacts_tab import ContactsTab
from gui.tabs.jobs_tab import JobsTab
from gui.tabs.settings_tab import SettingsTab
from gui.tabs.single_label_tab import SingleLabelTab
from gui.tabs.templates_tab import TemplatesTab
from gui.theme import CTk, CTkButton, CTkFrame, CTkLabel, CTkTabview, messagebox, setup_theme, tk, ttk
from jobs.event_bus import AddressCorrectionNeeded, JobCancelled, JobFinished, JobStarted, ProgressUpdated, RowCompleted, RowFailed
from jobs.queue_models import JobRequest
from jobs.worker import JobWorker
from services.address_service import AddressService
from services.import_service import ImportService
from services.job_service import JobService
from services.postage_service import PostageService
from storage.db import Database
from storage.repositories.contacts_repo import ContactsRepository
from storage.repositories.corrections_repo import CorrectionsRepository
from storage.repositories.jobs_repo import JobsRepository
from storage.repositories.settings_repo import SettingsRepository
from storage.repositories.templates_repo import TemplatesRepository
from utils.logging_utils import configure_logging

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.title("USPS Label Maker V2.4")
        self.geometry("1420x940")
        self.minsize(1180, 760)
        self.logger = configure_logging()
        self.db = Database(); self.db.migrate()
        self.settings_repo = SettingsRepository(self.db)
        self.settings = self.settings_repo.load()
        setup_theme(self.settings.get("theme", "system"))
        self.contacts_repo = ContactsRepository(self.db)
        self.templates_repo = TemplatesRepository(self.db); self.templates_repo.ensure_defaults()
        self.jobs_repo = JobsRepository(self.db)
        self.corrections_repo = CorrectionsRepository(self.db)
        self.address_service = AddressService(self.corrections_repo if self.settings.get("save_corrections", True) else None)
        self.job_service = JobService(self.settings, self.templates_repo, self.jobs_repo, self.address_service)
        self.import_service = ImportService()
        self.postage_service = PostageService(self.settings)
        self.event_queue: queue.Queue = queue.Queue()
        self.batch_worker: JobWorker | None = None
        self.batch_cancel_event = threading.Event()
        self.active_job = None
        self._build_ui()
        self.after(150, self._poll_events)

    def _build_ui(self):
        top = CTkFrame(self); top.pack(fill="x", padx=8, pady=(8,0))
        CTkLabel(top, text="USPS Label Maker V2.4").pack(side="left", padx=8, pady=8)
        CTkButton(top, text="Export CSV Template", command=self.export_csv_template).pack(side="right", padx=8, pady=8)
        self.tabview = CTkTabview(self); self.tabview.pack(fill="both", expand=True, padx=8, pady=8)
        for name in ["Single Label","Batch / CSV","Contacts","Templates","Jobs / History","Settings"]:
            self.tabview.add(name)
        self.single_tab = SingleLabelTab(self.tabview.tab("Single Label"), self); self.single_tab.pack(fill="both", expand=True)
        self.batch_tab = BatchTab(self.tabview.tab("Batch / CSV"), self); self.batch_tab.pack(fill="both", expand=True)
        self.contacts_tab = ContactsTab(self.tabview.tab("Contacts"), self); self.contacts_tab.pack(fill="both", expand=True)
        self.templates_tab = TemplatesTab(self.tabview.tab("Templates"), self); self.templates_tab.pack(fill="both", expand=True)
        self.jobs_tab = JobsTab(self.tabview.tab("Jobs / History"), self); self.jobs_tab.pack(fill="both", expand=True)
        self.settings_tab = SettingsTab(self.tabview.tab("Settings"), self); self.settings_tab.pack(fill="both", expand=True)
        status = CTkFrame(self); status.pack(fill="x", padx=8, pady=(0,8))
        self.status_var = tk.StringVar(value="Ready")
        CTkLabel(status, textvariable=self.status_var).pack(side="left", padx=8, pady=6)

    def save_settings(self, settings: dict):
        self.settings = settings
        self.settings_repo.save(settings)
        self.address_service = AddressService(self.corrections_repo if self.settings.get("save_corrections", True) else None)
        self.job_service = JobService(self.settings, self.templates_repo, self.jobs_repo, self.address_service)
        self.postage_service = PostageService(self.settings)
        try: setup_theme(self.settings.get("theme", "system"))
        except Exception: pass

    def export_csv_template(self):
        from utils.csv_utils import sample_template_rows, write_csv
        from gui.theme import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="label-template.csv", filetypes=[("CSV","*.csv")])
        if not path: return
        rows = sample_template_rows()
        write_csv(path, list(rows[0].keys()), rows)
        messagebox.showinfo("Template", f"Saved CSV template to {path}")

    def quote_only(self, from_addr, to_addr, mailpiece, provider_name: str):
        provider = self.job_service.provider_for_name(provider_name)
        return self.postage_service.get_quotes(provider, from_addr, to_addr, mailpiece)

    def generate_single_pdf(self, from_addr, to_addr, mailpiece, template_name: str, output_dir: str,
                             provider_name: str, subject: str = "", standardize_addresses: bool = False,
                             auto_accept_standardized: bool = False, buy_paid_labels: bool = False):
        job = self.job_service.create_job(mode="single", total_rows=1)
        self.active_job = job
        try:
            result = self.job_service.process_single(
                from_addr, to_addr, mailpiece, template_name, output_dir, provider_name, subject=subject,
                standardize_addresses=standardize_addresses, auto_accept_standardized=auto_accept_standardized,
                buy_paid_labels=buy_paid_labels, correction_callback=self.ask_correction_sync)
            self.jobs_repo.add_row_result(job.id, 1, result["recipient_label"], "success", "", "", "", result["best_quote"].display_line(), result["output_path"])
            self.job_service.finalize_job(job, success=1, failed=0, output_file=result["output_path"])
            self.jobs_tab.refresh(); return result
        except Exception as exc:
            self.jobs_repo.add_row_result(job.id, 1, "(single)", "failed", str(exc))
            self.job_service.fail_job(job, str(exc)); self.jobs_tab.refresh(); raise

    def load_batch_csv(self, csv_path: str):
        return self.import_service.load_with_mapping(csv_path)

    def start_batch_job(self, source_rows, mapping, template_name, output_dir, provider_name,
                        standardize_addresses, auto_accept_standardized, buy_paid_labels):
        if self.batch_worker and self.batch_worker.is_alive():
            messagebox.showwarning("Batch", "A batch job is already running."); return
        self.batch_cancel_event.clear()
        self.active_job = self.job_service.create_job(mode="batch", source_file="", total_rows=len(source_rows))
        request = JobRequest(mode="batch", source_rows=source_rows, mapping=mapping, template_name=template_name,
            output_dir=output_dir, provider_name=provider_name, standardize_addresses=standardize_addresses,
            auto_accept_standardized=auto_accept_standardized, buy_paid_labels=buy_paid_labels)
        self.batch_worker = JobWorker(request, self.job_service, self.event_queue, self.batch_cancel_event)
        self.batch_worker.start(); self.status_var.set("Batch job started.")

    def cancel_batch(self):
        if self.batch_worker and self.batch_worker.is_alive():
            self.batch_cancel_event.set(); self.status_var.set("Cancelling batch...")
        else:
            messagebox.showinfo("Batch", "No running batch job.")

    def ask_correction_sync(self, row_number: int, recipient_label: str, original, suggested) -> bool:
        dlg = AddressCorrectionDialog(self, original, suggested, recipient_label)
        self.wait_window(dlg); return dlg.result

    def _poll_events(self):
        try:
            while True:
                self._handle_event(self.event_queue.get_nowait())
        except queue.Empty:
            pass
        self.after(150, self._poll_events)

    def _handle_event(self, event):
        if isinstance(event, JobStarted):
            self.batch_tab.progress_panel.update(0, event.total, "Job started")
            self.batch_tab.append_log(f"Job started: {event.total} rows"); return
        if isinstance(event, ProgressUpdated):
            self.batch_tab.progress_panel.update(event.current, event.total, event.message)
            self.status_var.set(event.message); return
        if isinstance(event, RowCompleted):
            self.batch_tab.append_log(f"Row {event.row_number}: OK - {event.recipient_label} - {event.quote_line}")
            if self.active_job:
                self.active_job.success_rows += 1
                self.jobs_repo.add_row_result(self.active_job.id, event.row_number, event.recipient_label, "success", "", "", "", event.quote_line, event.output_path)
            return
        if isinstance(event, RowFailed):
            self.batch_tab.append_log(f"Row {event.row_number}: FAILED - {event.error_message}")
            if self.active_job:
                self.active_job.failed_rows += 1
                source_json = json.dumps(event.source_row) if event.source_row else ""
                self.jobs_repo.add_row_result(self.active_job.id, event.row_number, event.recipient_label, "failed", event.error_message, source_json)
            return
        if isinstance(event, AddressCorrectionNeeded):
            event.response_queue.put(self.ask_correction_sync(event.row_number, event.recipient_label, event.original, event.suggested)); return
        if isinstance(event, JobFinished):
            if self.active_job:
                self.job_service.finalize_job(self.active_job, success=event.success, failed=event.failed, output_file=event.output_path)
            self.batch_tab.progress_panel.update(event.success + event.failed, max(event.success + event.failed, 1), f"Finished: {event.success} success, {event.failed} failed")
            self.batch_tab.append_log(f"Finished: {event.success} success / {event.failed} failed")
            self.jobs_tab.refresh(); self.status_var.set("Batch complete"); return
        if isinstance(event, JobCancelled):
            if self.active_job:
                self.active_job.status = "cancelled"; self.jobs_repo.save(self.active_job)
            self.batch_tab.append_log("Batch cancelled"); self.jobs_tab.refresh(); self.status_var.set("Batch cancelled"); return
