from __future__ import annotations
import csv
from pathlib import Path
from typing import Iterable

FIELD_ALIASES = {
    "from_name": ["from_name", "sender_name", "return_name", "from fullname"],
    "from_company": ["from_company", "sender_company", "return_company", "from company"],
    "from_line1": ["from_line1", "from_address1", "sender_line1", "return_line1", "from street"],
    "from_line2": ["from_line2", "from_address2", "sender_line2", "return_line2", "from street2"],
    "from_city": ["from_city", "sender_city", "return_city"],
    "from_state": ["from_state", "sender_state", "return_state"],
    "from_zip": ["from_zip", "sender_zip", "return_zip", "from_zipcode"],
    "to_name": ["to_name", "recipient_name", "mail_to_name"],
    "to_company": ["to_company", "recipient_company", "mail_to_company"],
    "to_line1": ["to_line1", "to_address1", "recipient_line1", "to street"],
    "to_line2": ["to_line2", "to_address2", "recipient_line2", "to street2"],
    "to_city": ["to_city", "recipient_city"],
    "to_state": ["to_state", "recipient_state"],
    "to_zip": ["to_zip", "recipient_zip", "to_zipcode"],
    "subject": ["subject", "memo", "reference", "job_name"],
    "notes": ["notes", "comments"],
    "weight_oz": ["weight_oz", "weight", "ounces"],
    "width_in": ["width_in", "width", "envelope_width_in"],
    "height_in": ["height_in", "height", "envelope_height_in"],
    "thickness_in": ["thickness_in", "thickness"],
    "output_mode": ["output_mode", "mode", "label_mode"],
    "mail_class": ["mail_class", "class", "piece_type"],
    "nonmachinable": ["nonmachinable", "odd_shape", "rigid", "non_machinable"],
}

def load_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def headers_from_rows(rows: list[dict[str, str]]) -> list[str]:
    return list(rows[0].keys()) if rows else []

def autodetect_mapping(headers: list[str]) -> dict[str, str]:
    lowered = {h.strip().lower(): h for h in headers}
    mapping: dict[str, str] = {}
    for canonical, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias.strip().lower() in lowered:
                mapping[canonical] = lowered[alias.strip().lower()]
                break
    return mapping

def resolve(row: dict[str, str], mapping: dict[str, str], field_name: str) -> str:
    header = mapping.get(field_name, "")
    return row.get(header, "") if header else ""

def write_csv(path: str | Path, headers: list[str], rows: Iterable[dict[str, str]]) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def sample_template_rows() -> list[dict[str, str]]:
    return [{
        "from_name": "Mohamed Soliman", "from_company": "BlueAnchor Security LLC",
        "from_line1": "11762 Marsden St", "from_line2": "", "from_city": "Jamaica",
        "from_state": "NY", "from_zip": "11434-2230", "to_name": "",
        "to_company": "Department of State Division of Corporations, State Records and Uniform Commercial Code",
        "to_line1": "One Commerce Plaza", "to_line2": "99 Washington Avenue",
        "to_city": "Albany", "to_state": "NY", "to_zip": "12231",
        "subject": "DBA Filing", "weight_oz": "1.0", "width_in": "9.5",
        "height_in": "4.125", "thickness_in": "0.02", "output_mode": "cut_label",
        "mail_class": "letter", "nonmachinable": "false", "notes": "",
    }]
