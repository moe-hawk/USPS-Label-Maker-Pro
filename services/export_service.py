from __future__ import annotations
import json
from pathlib import Path
from utils.csv_utils import write_csv

class ExportService:
    def export_failed_rows(self, path: str | Path, rows: list[dict]) -> None:
        """Write failed job rows to a CSV re-importable for correction and re-run.

        When the batch worker stored the original CSV row in original_address_json
        we unpack it back to top-level columns so the output has the same layout
        as the import template. Rows without stored source data are exported as-is.
        """
        if not rows:
            return
        expanded: list[dict] = []
        for row in rows:
            raw_json = row.get("original_address_json", "")
            source: dict = {}
            if raw_json:
                try:
                    parsed = json.loads(raw_json)
                    if isinstance(parsed, dict):
                        source = parsed
                except Exception:
                    pass
            if source:
                record = dict(source)
                record["_row_number"] = row.get("row_number", "")
                record["_error"] = row.get("error_message", "")
            else:
                record = dict(row)
            expanded.append(record)
        all_keys: list[str] = []
        seen: set[str] = set()
        for record in expanded:
            for key in record:
                if key not in seen:
                    all_keys.append(key)
                    seen.add(key)
        write_csv(path, all_keys, expanded)
