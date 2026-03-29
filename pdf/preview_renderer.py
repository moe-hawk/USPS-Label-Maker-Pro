from __future__ import annotations
from PIL import Image, ImageDraw, ImageFont
from models.address import Address
from models.mailpiece import Mailpiece
from models.template import Template

class PreviewRenderer:
    def render(self, from_address: Address, to_address: Address, mailpiece: Mailpiece,
               template: Template, subject: str = "", width: int = 700, height: int = 360) -> Image.Image:
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        border = 12
        draw.rounded_rectangle((border, border, width - border, height - border), radius=14, outline=(150, 160, 170), width=2)
        try:
            font = ImageFont.truetype("arial.ttf", 15)
            font_small = ImageFont.truetype("arial.ttf", 12)
            font_big = ImageFont.truetype("arialbd.ttf", 19)
        except Exception:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_big = ImageFont.load_default()
        draw.text((32, 28), "Return address", fill=(80, 80, 80), font=font_small)
        y = 48
        for line in from_address.lines():
            draw.text((32, y), line, fill=(20, 20, 20), font=font_small)
            y += 16
        dest_x, dest_y = 250, 110
        for line in to_address.lines():
            draw.text((dest_x, dest_y), line, fill=(10, 10, 10), font=font_big if line == to_address.lines()[0] else font)
            dest_y += 24 if line == to_address.lines()[0] else 20
        draw.rectangle((width - 115, 28, width - 30, 88), outline=(90, 90, 90), width=2)
        draw.text((width - 86, 52), "STAMP", fill=(90, 90, 90), font=font_small)
        if subject and template.include_subject:
            draw.text((32, height - 28), f"Subject: {subject[:48]}", fill=(60, 60, 60), font=font_small)
        return image
