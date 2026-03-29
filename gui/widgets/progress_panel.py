from __future__ import annotations
from gui.theme import CTkFrame, CTkLabel, CTkProgressBar, tk

class ProgressPanel(CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.status_var = tk.StringVar(value="Idle")
        self.counts_var = tk.StringVar(value="0 / 0")
        CTkLabel(self, textvariable=self.status_var).pack(anchor="w", padx=8, pady=(8,4))
        CTkLabel(self, textvariable=self.counts_var).pack(anchor="w", padx=8, pady=(0,4))
        self.bar = CTkProgressBar(self)
        self.bar.pack(fill="x", padx=8, pady=(4,8))
        try: self.bar.set(0)
        except Exception: self.bar["value"] = 0

    def update(self, current: int, total: int, message: str):
        self.status_var.set(message)
        self.counts_var.set(f"{current} / {total}")
        frac = 0 if total <= 0 else current / total
        try: self.bar.set(frac)
        except Exception: self.bar["value"] = frac * 100
