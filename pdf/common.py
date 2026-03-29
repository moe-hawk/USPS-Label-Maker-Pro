from __future__ import annotations
from pathlib import Path
from typing import Iterable
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

def wrap_line(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    words = text.split()
    if not words: return [""]
    lines = [words[0]]
    for word in words[1:]:
        candidate = f"{lines[-1]} {word}"
        if stringWidth(candidate, font_name, font_size) <= max_width:
            lines[-1] = candidate
        else:
            lines.append(word)
    return lines

def draw_text_block(canvas: Canvas, x: float, y: float, lines: Iterable[str], width: float,
                    font_name: str = "Helvetica", font_size: int = 11, leading: float = 13, bold: bool = False) -> float:
    f = f"{font_name}-Bold" if bold and not font_name.endswith("-Bold") else font_name
    canvas.setFont(f, font_size)
    current_y = y
    for line in lines:
        for wrapped in wrap_line(line, f, font_size, width):
            canvas.drawString(x, current_y, wrapped)
            current_y -= leading
    return current_y

def draw_logo(canvas: Canvas, logo_path: str, x: float, y: float, max_w: float, max_h: float) -> None:
    if not logo_path: return
    p = Path(logo_path)
    if not p.exists(): return
    with Image.open(p) as img:
        img = img.convert("RGBA")
        img_w, img_h = img.size
    scale = min(max_w / img_w, max_h / img_h)
    canvas.drawImage(ImageReader(str(p)), x, y - img_h * scale, width=img_w * scale, height=img_h * scale, mask="auto")

def draw_stamp_box(canvas: Canvas, x: float, y: float, width: float, height: float) -> None:
    canvas.setStrokeColor(colors.HexColor("#555555"))
    canvas.rect(x, y, width, height, stroke=1, fill=0)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(x + width / 2, y + height / 2 - 3, "Stamp")
