from __future__ import annotations
from PIL import ImageTk
from gui.theme import tk, ttk
from pdf.preview_renderer import PreviewRenderer

class PreviewPane(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.renderer = PreviewRenderer()
        self.label = ttk.Label(self, text="Preview will appear here.")
        self.label.pack(fill="both", expand=True, padx=8, pady=8)
        self._img = None

    def update_preview(self, from_address, to_address, mailpiece, template, subject=""):
        img = self.renderer.render(from_address, to_address, mailpiece, template, subject=subject)
        self._img = ImageTk.PhotoImage(img)
        self.label.configure(image=self._img, text="")
