from __future__ import annotations
import queue
from dataclasses import dataclass, field

@dataclass(slots=True)
class JobStarted:
    total: int

@dataclass(slots=True)
class ProgressUpdated:
    current: int
    total: int
    message: str

@dataclass(slots=True)
class RowCompleted:
    row_number: int
    recipient_label: str
    output_path: str
    quote_line: str

@dataclass(slots=True)
class RowFailed:
    row_number: int
    recipient_label: str
    error_message: str
    # Carries the original CSV row so failed rows can be re-exported as a
    # re-importable CSV. Defaults to {} for backwards-compatible callers.
    source_row: dict = field(default_factory=dict)

@dataclass(slots=True)
class AddressCorrectionNeeded:
    row_number: int
    recipient_label: str
    original: object
    suggested: object
    response_queue: queue.Queue

@dataclass(slots=True)
class JobFinished:
    success: int
    failed: int
    output_path: str = ""

@dataclass(slots=True)
class JobCancelled:
    message: str = "Cancelled"
