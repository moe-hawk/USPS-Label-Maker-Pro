from __future__ import annotations
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from models.address import Address
from models.mailpiece import Mailpiece
from models.template import Template
from pdf.envelope_renderer import EnvelopeRenderer
from utils.measurements import inch

class LabelRenderer:
    def __init__(self) -> None:
        self.envelope = EnvelopeRenderer()

    def render(self, path: str | Path, from_address: Address, to_address: Address,
               mailpiece: Mailpiece, template: Template, subject: str = "", postage_text: str = "") -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        c = canvas.Canvas(str(path), pagesize=letter)
        page_w, page_h = letter
        label_w = inch(max(mailpiece.width_in, mailpiece.height_in))
        label_h = inch(min(mailpiece.width_in, mailpiece.height_in))
        x = (page_w - label_w) / 2
        y = (page_h - label_h) / 2
        c.setStrokeColor(colors.HexColor("#A0AEC0"))
        c.setDash(4, 2)
        c.rect(x, y, label_w, label_h, stroke=1, fill=0)
        c.setDash()
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#667085"))
        c.drawString(x, y - 12, "Cut along the outline and tape or glue to your envelope.")
        c.saveState()
        c.translate(x, y)
        self.envelope._draw(c, label_w, label_h, from_address, to_address, template, subject, postage_text)
        c.restoreState()
        c.showPage()
        c.save()
        return path
