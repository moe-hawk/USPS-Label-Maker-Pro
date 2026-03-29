from __future__ import annotations
from pathlib import Path
from models.address import Address
from models.mailpiece import Mailpiece
from utils.csv_utils import load_csv_rows, autodetect_mapping, resolve
from utils.measurements import normalize_zip, to_bool, to_float

class ImportService:
    def load_with_mapping(self, csv_path: str | Path, mapping: dict | None = None) -> tuple[list[dict[str, str]], dict[str, str]]:
        rows = load_csv_rows(csv_path)
        final_mapping = mapping or autodetect_mapping(list(rows[0].keys()) if rows else [])
        return rows, final_mapping

    def row_to_objects(self, row: dict[str, str], mapping: dict[str, str]) -> tuple[Address, Address, Mailpiece, str, str]:
        from_zip, from_plus4 = normalize_zip(resolve(row, mapping, "from_zip"))
        to_zip, to_plus4 = normalize_zip(resolve(row, mapping, "to_zip"))
        from_address = Address(
            name=resolve(row, mapping, "from_name"), company=resolve(row, mapping, "from_company"),
            line1=resolve(row, mapping, "from_line1"), line2=resolve(row, mapping, "from_line2"),
            city=resolve(row, mapping, "from_city"), state=resolve(row, mapping, "from_state"),
            postal_code=from_zip, postal_code_plus4=from_plus4)
        to_address = Address(
            name=resolve(row, mapping, "to_name"), company=resolve(row, mapping, "to_company"),
            line1=resolve(row, mapping, "to_line1"), line2=resolve(row, mapping, "to_line2"),
            city=resolve(row, mapping, "to_city"), state=resolve(row, mapping, "to_state"),
            postal_code=to_zip, postal_code_plus4=to_plus4)
        mailpiece = Mailpiece(
            mail_class=(resolve(row, mapping, "mail_class") or "letter").strip().lower(),
            width_in=to_float(resolve(row, mapping, "width_in"), 9.5),
            height_in=to_float(resolve(row, mapping, "height_in"), 4.125),
            thickness_in=to_float(resolve(row, mapping, "thickness_in"), 0.02),
            weight_oz=to_float(resolve(row, mapping, "weight_oz"), 1.0),
            nonmachinable=to_bool(resolve(row, mapping, "nonmachinable")),
            output_mode=(resolve(row, mapping, "output_mode") or "cut_label").strip().lower())
        return from_address, to_address, mailpiece, resolve(row, mapping, "subject"), resolve(row, mapping, "notes")
