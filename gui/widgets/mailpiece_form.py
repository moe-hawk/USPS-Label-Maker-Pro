from __future__ import annotations
from models.mailpiece import Mailpiece
from gui.theme import CTkCheckBox, CTkComboBox, CTkEntry, CTkFrame, CTkLabel, tk

ENVELOPE_PRESETS = {
    "#10 Business Envelope": (9.5, 4.125), "A6 Envelope": (6.5, 4.75),
    "A7 Envelope": (7.25, 5.25), "6 x 9 Envelope": (9.0, 6.0),
    "9 x 12 Envelope": (12.0, 9.0), "Custom": (0.0, 0.0),
}

class MailpieceForm(CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.vars = {
            "mail_class": tk.StringVar(value="letter"), "output_mode": tk.StringVar(value="cut_label"),
            "envelope_name": tk.StringVar(value="#10 Business Envelope"),
            "width_in": tk.StringVar(value="9.5"), "height_in": tk.StringVar(value="4.125"),
            "thickness_in": tk.StringVar(value="0.02"), "weight_oz": tk.StringVar(value="1.0"),
            "nonmachinable": tk.BooleanVar(value=False),
        }
        CTkLabel(self, text="Mailpiece").grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=(4,6))
        row = 1
        for label, key, values in [
            ("Class","mail_class",["letter","flat","package"]),
            ("Output","output_mode",["cut_label","envelope","avery_5160","avery_8160","avery_5260"]),
            ("Preset","envelope_name",list(ENVELOPE_PRESETS.keys())),
        ]:
            CTkLabel(self, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)
            combo = CTkComboBox(self, values=values, variable=self.vars[key], width=220)
            combo.grid(row=row, column=1, sticky="ew", padx=4, pady=2)
            if key == "envelope_name":
                def _apply(*_):
                    w, h = ENVELOPE_PRESETS.get(self.vars["envelope_name"].get(), (0, 0))
                    if w and h:
                        self.vars["width_in"].set(str(w))
                        self.vars["height_in"].set(str(h))
                try: combo.configure(command=lambda _=None: _apply())
                except Exception: pass
            row += 1
        for label, key in [("Width (in)","width_in"),("Height (in)","height_in"),
                           ("Thickness (in)","thickness_in"),("Weight (oz)","weight_oz")]:
            CTkLabel(self, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)
            CTkEntry(self, textvariable=self.vars[key], width=220).grid(row=row, column=1, sticky="ew", padx=4, pady=2)
            row += 1
        CTkCheckBox(self, text="Nonmachinable / rigid", variable=self.vars["nonmachinable"]).grid(row=row, column=0, columnspan=2, sticky="w", padx=4, pady=4)
        self.grid_columnconfigure(1, weight=1)

    def get_mailpiece(self) -> Mailpiece:
        return Mailpiece(
            mail_class=self.vars["mail_class"].get().strip().lower(),
            output_mode=self.vars["output_mode"].get().strip().lower(),
            envelope_name=self.vars["envelope_name"].get(),
            width_in=float(self.vars["width_in"].get() or 0),
            height_in=float(self.vars["height_in"].get() or 0),
            thickness_in=float(self.vars["thickness_in"].get() or 0),
            weight_oz=float(self.vars["weight_oz"].get() or 0),
            nonmachinable=bool(self.vars["nonmachinable"].get()))

    def set_mailpiece(self, mailpiece: Mailpiece) -> None:
        for key in ["mail_class","output_mode","envelope_name"]: self.vars[key].set(getattr(mailpiece, key))
        self.vars["width_in"].set(str(mailpiece.width_in)); self.vars["height_in"].set(str(mailpiece.height_in))
        self.vars["thickness_in"].set(str(mailpiece.thickness_in)); self.vars["weight_oz"].set(str(mailpiece.weight_oz))
        self.vars["nonmachinable"].set(bool(mailpiece.nonmachinable))

    def clear(self) -> None:
        self.vars["mail_class"].set("letter"); self.vars["output_mode"].set("cut_label")
        self.vars["envelope_name"].set("#10 Business Envelope")
        self.vars["width_in"].set("9.5"); self.vars["height_in"].set("4.125")
        self.vars["thickness_in"].set("0.02"); self.vars["weight_oz"].set("1.0")
        self.vars["nonmachinable"].set(False)
