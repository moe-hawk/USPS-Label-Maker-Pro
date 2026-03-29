from __future__ import annotations
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import createBarcodeDrawing
from utils.measurements import inch

def draw_postnet(canvas, zip_text: str, x: float, y: float, bar_width: float = 0.015, bar_height: float = 0.18) -> None:
    digits = "".join(ch for ch in zip_text if ch.isdigit())
    if len(digits) not in {5, 9, 11}: return
    drawing = createBarcodeDrawing("POSTNET", value=digits, barWidth=bar_width * 72, barHeight=bar_height * 72)
    renderPDF.draw(drawing, canvas, x, y)

def draw_internal_job_barcode(canvas, value: str, x: float, y: float, width: float = 1.8, height: float = 0.35) -> None:
    safe = value[:32] if value else "JOB"
    drawing = createBarcodeDrawing("Code128", value=safe, barWidth=0.6, barHeight=height * 72)
    renderPDF.draw(drawing, canvas, x, y)
