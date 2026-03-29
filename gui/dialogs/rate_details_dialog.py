from __future__ import annotations
import json
from gui.theme import CTkButton, CTkFrame, CTkLabel, CTkTextbox, CTkToplevel

class RateDetailsDialog(CTkToplevel):
    def __init__(self, master, quote):
        super().__init__(master)
        self.title("Rate Details")
        self.geometry("720x520")
        self.grab_set()
        CTkLabel(self, text=quote.display_line()).pack(anchor="w", padx=12, pady=(12,6))
        box = CTkTextbox(self, width=680, height=420)
        box.pack(fill="both", expand=True, padx=12, pady=6)
        box.insert("1.0", json.dumps(quote.raw, indent=2))
        CTkButton(self, text="Close", command=self.destroy).pack(pady=(0,12))
