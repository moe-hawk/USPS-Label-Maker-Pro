from __future__ import annotations
from gui.theme import CTkButton, CTkFrame, CTkLabel, CTkToplevel, tk

class AddressCorrectionDialog(CTkToplevel):
    def __init__(self, master, original, suggested, recipient_label: str = ""):
        super().__init__(master)
        self.title("Address Correction")
        self.result = False
        self.geometry("720x420")
        self.grab_set()
        CTkLabel(self, text=f"Suggested standardized address for: {recipient_label}").pack(anchor="w", padx=12, pady=(12,8))
        body = CTkFrame(self)
        body.pack(fill="both", expand=True, padx=12, pady=8)
        left = CTkFrame(body); left.pack(side="left", fill="both", expand=True, padx=(0,6))
        right = CTkFrame(body); right.pack(side="left", fill="both", expand=True, padx=(6,0))
        CTkLabel(left, text="Original").pack(anchor="w", padx=8, pady=(8,4))
        for line in original.lines(): CTkLabel(left, text=line).pack(anchor="w", padx=8, pady=2)
        CTkLabel(right, text="Suggested").pack(anchor="w", padx=8, pady=(8,4))
        for line in suggested.lines(): CTkLabel(right, text=line).pack(anchor="w", padx=8, pady=2)
        btns = CTkFrame(self); btns.pack(fill="x", padx=12, pady=(8,12))
        CTkButton(btns, text="Keep Original", command=self._reject).pack(side="right", padx=6)
        CTkButton(btns, text="Use Suggested", command=self._accept).pack(side="right", padx=6)

    def _accept(self): self.result = True; self.destroy()
    def _reject(self): self.result = False; self.destroy()
