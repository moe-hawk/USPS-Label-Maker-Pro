from __future__ import annotations
from datetime import datetime
from models.template import Template
from storage.db import Database

class TemplatesRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def all(self) -> list[Template]:
        return [self._row_to_template(r) for r in self.db.query("SELECT * FROM templates ORDER BY name")]

    def get(self, template_id: int) -> Template | None:
        row = self.db.query_one("SELECT * FROM templates WHERE id = ?", (template_id,))
        return self._row_to_template(row) if row else None

    def get_by_name(self, name: str) -> Template | None:
        row = self.db.query_one("SELECT * FROM templates WHERE name = ?", (name,))
        return self._row_to_template(row) if row else None

    def save(self, template: Template) -> Template:
        now = datetime.utcnow().isoformat()
        template.updated_at = now
        if template.id is None:
            template.created_at = now
            cur = self.db.execute(
                "INSERT INTO templates (name,output_mode,envelope_width_in,envelope_height_in,logo_path,show_logo,return_x,return_y,to_x,to_y,font_name,font_size,include_stamp_box,include_subject,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (template.name, template.output_mode, template.envelope_width_in, template.envelope_height_in,
                 template.logo_path, int(template.show_logo), template.return_x, template.return_y,
                 template.to_x, template.to_y, template.font_name, template.font_size,
                 int(template.include_stamp_box), int(template.include_subject),
                 template.created_at, template.updated_at))
            template.id = int(cur.lastrowid)
        else:
            self.db.execute(
                "UPDATE templates SET name=?,output_mode=?,envelope_width_in=?,envelope_height_in=?,logo_path=?,show_logo=?,return_x=?,return_y=?,to_x=?,to_y=?,font_name=?,font_size=?,include_stamp_box=?,include_subject=?,updated_at=? WHERE id=?",
                (template.name, template.output_mode, template.envelope_width_in, template.envelope_height_in,
                 template.logo_path, int(template.show_logo), template.return_x, template.return_y,
                 template.to_x, template.to_y, template.font_name, template.font_size,
                 int(template.include_stamp_box), int(template.include_subject),
                 template.updated_at, template.id))
        return template

    def delete(self, template_id: int) -> None:
        self.db.execute("DELETE FROM templates WHERE id = ?", (template_id,))

    def ensure_defaults(self) -> None:
        if self.all():
            return
        for name, mode, w, h in [
            ("Default #10 Cut Label", "cut_label", 9.5, 4.125),
            ("Default #10 Envelope Print", "envelope", 9.5, 4.125),
            ("Avery 5160 Sheet", "avery_5160", 2.625, 1.0),
            ("Avery 8160 Sheet", "avery_8160", 2.625, 1.0),
            ("Avery 5260 Sheet", "avery_5260", 2.625, 1.0),
        ]:
            self.save(Template(name=name, output_mode=mode, envelope_width_in=w, envelope_height_in=h))

    def _row_to_template(self, row) -> Template:
        return Template(
            id=row["id"], name=row["name"], output_mode=row["output_mode"],
            envelope_width_in=row["envelope_width_in"], envelope_height_in=row["envelope_height_in"],
            logo_path=row["logo_path"], show_logo=bool(row["show_logo"]),
            return_x=row["return_x"], return_y=row["return_y"],
            to_x=row["to_x"], to_y=row["to_y"],
            font_name=row["font_name"], font_size=row["font_size"],
            include_stamp_box=bool(row["include_stamp_box"]),
            include_subject=bool(row["include_subject"]),
            created_at=row["created_at"], updated_at=row["updated_at"])
