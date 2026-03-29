from __future__ import annotations
from pathlib import Path
from reportlab.pdfgen import canvas
from models.address import Address
from models.template import Template
from pdf.common import draw_logo, draw_text_block
from pdf.layout_presets import AVERY_PRESETS
from utils.measurements import inch

class AveryRenderer:
    def render(self, path: str | Path, jobs: list[dict], template: Template,
               output_mode: str, skip_positions: set[int] | None = None) -> Path:
        preset = AVERY_PRESETS[output_mode]
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        c = canvas.Canvas(str(path), pagesize=(inch(preset["page_width"]), inch(preset["page_height"])))
        page_w = inch(preset["page_width"])
        page_h = inch(preset["page_height"])
        skip_positions = skip_positions or set()
        page_capacity = preset["cols"] * preset["rows"]
        label_index = 0
        for job in jobs:
            # Bound guard prevents infinite loop if skip_positions contains
            # indices >= page_capacity.
            while label_index in skip_positions and label_index < page_capacity:
                label_index += 1
            if label_index >= page_capacity:
                c.showPage()
                label_index = 0
                # Re-check after page reset so position 0 on a new page is
                # correctly skipped when included in skip_positions.
                while label_index in skip_positions and label_index < page_capacity:
                    label_index += 1
            col = label_index % preset["cols"]
            row = label_index // preset["cols"]
            x = inch(preset["margin_left"] + col * preset["pitch_x"])
            y_top = page_h - inch(preset["margin_top"] + row * preset["pitch_y"])
            self._draw_label(c, x, y_top, inch(preset["label_width"]), inch(preset["label_height"]),
                job["from_address"], job["to_address"], template, job.get("subject", ""))
            label_index += 1
        c.showPage()
        c.save()
        return path

    def _draw_label(self, c, x, y_top, w, h, from_address: Address,
                    to_address: Address, template: Template, subject: str) -> None:
        if template.show_logo and template.logo_path:
            draw_logo(c, template.logo_path, x + 4, y_top - 4, max_w=0.45 * 72, max_h=0.2 * 72)
        draw_text_block(c, x + 4, y_top - 8, from_address.lines()[:3], width=w - 8,
            font_name=template.font_name, font_size=6, leading=7)
        draw_text_block(c, x + 12, y_top - 32, to_address.lines(), width=w - 16,
            font_name=template.font_name, font_size=8, leading=9, bold=True)
        if subject and template.include_subject:
            c.setFont("Helvetica", 5)
            c.drawRightString(x + w - 4, y_top - h + 8, subject[:36])
