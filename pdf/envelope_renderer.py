from __future__ import annotations
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from models.address import Address
from models.mailpiece import Mailpiece
from models.template import Template
from pdf.barcode import draw_postnet
from pdf.common import draw_logo, draw_stamp_box, draw_text_block
from utils.measurements import inch

class EnvelopeRenderer:
    def render(self, path: str | Path, from_address: Address, to_address: Address,
               mailpiece: Mailpiece, template: Template, subject: str = "",
               postage_text: str = "", job_code: str = "") -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        page_w = inch(max(mailpiece.width_in, mailpiece.height_in))
        page_h = inch(min(mailpiece.width_in, mailpiece.height_in))
        c = canvas.Canvas(str(path), pagesize=(page_w, page_h))
        self._draw(c, page_w, page_h, from_address, to_address, template, subject, postage_text, job_code)
        c.showPage()
        c.save()
        return path

    def _draw(self, c, page_w, page_h, from_address, to_address, template,
              subject="", postage_text="", job_code="") -> None:
        margin = 0.28 * 72
        return_x = template.return_x * 72
        return_y = page_h - (template.return_y * 72)
        dest_x = template.to_x * 72
        dest_y = page_h - (template.to_y * 72)
        if template.show_logo and template.logo_path:
            draw_logo(c, template.logo_path, margin, page_h - margin, max_w=1.1 * 72, max_h=0.65 * 72)
        c.setFillColor(HexColor("#111111"))
        draw_text_block(c, return_x, return_y, from_address.lines(), width=2.6 * 72,
            font_name=template.font_name, font_size=max(template.font_size - 1, 8), leading=10)
        draw_text_block(c, dest_x, dest_y, to_address.lines(), width=3.8 * 72,
            font_name=template.font_name, font_size=max(template.font_size + 1, 11), leading=14, bold=True)
        if template.include_stamp_box:
            draw_stamp_box(c, page_w - margin - (1.1 * 72), page_h - margin - (0.9 * 72), 1.1 * 72, 0.9 * 72)
        if postage_text:
            c.setFont("Helvetica", 8)
            c.drawString(margin, 8, postage_text)
        if subject and template.include_subject:
            c.setFont("Helvetica", 8)
            c.drawRightString(page_w - margin, 8, f"Subject: {subject[:48]}")
        draw_postnet(c, to_address.formatted_postal_code(), dest_x, max(10, dest_y - 55))
