from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(slots=True)
class Template:
    id: int | None = None
    name: str = "Default #10"
    output_mode: str = "cut_label"
    envelope_width_in: float = 9.5
    envelope_height_in: float = 4.125
    logo_path: str = ""
    show_logo: bool = False
    return_x: float = 0.45
    return_y: float = 0.35
    to_x: float = 3.2
    to_y: float = 2.15
    font_name: str = "Helvetica"
    font_size: int = 11
    include_stamp_box: bool = True
    include_subject: bool = False
    # default_factory so each instance gets its own construction timestamp
    # instead of sharing the stale module-load-time string a class-level
    # default would produce.
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
