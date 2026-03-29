from __future__ import annotations
import queue, threading
from jobs.event_bus import (AddressCorrectionNeeded, JobCancelled, JobFinished,
    JobStarted, ProgressUpdated, RowCompleted, RowFailed)
from jobs.queue_models import JobRequest
from utils.exceptions import CancelledError

class JobWorker(threading.Thread):
    def __init__(self, request: JobRequest, service, event_queue: queue.Queue, cancel_event: threading.Event) -> None:
        super().__init__(daemon=True)
        self.request = request
        self.service = service
        self.event_queue = event_queue
        self.cancel_event = cancel_event

    def run(self) -> None:
        try:
            self._run()
        except CancelledError:
            self.event_queue.put(JobCancelled())
        except Exception as exc:
            self.event_queue.put(RowFailed(row_number=-1, recipient_label="(job)", error_message=str(exc)))
            self.event_queue.put(JobFinished(success=0, failed=1))

    def _run(self) -> None:
        total = len(self.request.source_rows)
        self.event_queue.put(JobStarted(total=total))
        success = failed = 0
        last_output = ""
        for idx, row in enumerate(self.request.source_rows, start=1):
            if self.cancel_event.is_set():
                raise CancelledError()
            self.event_queue.put(ProgressUpdated(current=idx - 1, total=total, message=f"Processing row {idx} of {total}"))
            try:
                result = self.service.process_batch_row(
                    row_number=idx, row=row, mapping=self.request.mapping,
                    template_name=self.request.template_name, output_dir=self.request.output_dir,
                    provider_name=self.request.provider_name,
                    standardize_addresses=self.request.standardize_addresses,
                    auto_accept_standardized=self.request.auto_accept_standardized,
                    buy_paid_labels=self.request.buy_paid_labels,
                    correction_callback=self._ask_user_about_correction)
                success += 1
                last_output = result.get("output_path", "") or last_output
                self.event_queue.put(RowCompleted(
                    row_number=idx, recipient_label=result.get("recipient_label", ""),
                    output_path=result.get("output_path", ""), quote_line=result.get("quote_line", "")))
            except Exception as exc:
                failed += 1
                self.event_queue.put(RowFailed(
                    row_number=idx,
                    recipient_label=str(row.get("to_company") or row.get("to_name") or ""),
                    error_message=str(exc),
                    source_row=dict(row)))
            self.event_queue.put(ProgressUpdated(current=idx, total=total, message=f"Completed {idx} of {total}"))
        self.event_queue.put(JobFinished(success=success, failed=failed, output_path=last_output))

    def _ask_user_about_correction(self, row_number: int, recipient_label: str, original, suggested) -> bool:
        response_q: queue.Queue = queue.Queue()
        self.event_queue.put(AddressCorrectionNeeded(
            row_number=row_number, recipient_label=recipient_label,
            original=original, suggested=suggested, response_queue=response_q))
        return bool(response_q.get())
