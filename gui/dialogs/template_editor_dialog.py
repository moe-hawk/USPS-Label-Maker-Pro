from __future__ import annotations
from models.template import Template
from gui.theme import CTkButton, CTkCheckBox, CTkComboBox, CTkEntry, CTkFrame, CTkLabel, CTkToplevel, filedialog, tk

class TemplateEditorDialog(CTkToplevel):
    def __init__(self, master, template: Template | None = None):
        super().__init__(master)
        self.title("Template")
        self.geometry("560x560")
        self.grab_set()
        self.result: Template | None = None
        tpl = template or Template()
        self.vars = {
            "name": tk.StringVar(value=tpl.name), "output_mode": tk.StringVar(value=tpl.output_mode),
            "envelope_width_in": tk.StringVar(value=str(tpl.envelope_width_in)),
            "envelope_height_in": tk.StringVar(value=str(tpl.envelope_height_in)),
            "logo_path": tk.StringVar(value=tpl.logo_path), "show_logo": tk.BooleanVar(value=tpl.show_logo),
            "return_x": tk.StringVar(value=str(tpl.return_x)), "return_y": tk.StringVar(value=str(tpl.return_y)),
            "to_x": tk.StringVar(value=str(tpl.to_x)), "to_y": tk.StringVar(value=str(tpl.to_y)),
            "font_name": tk.StringVar(value=tpl.font_name), "font_size": tk.StringVar(value=str(tpl.font_size)),
            "include_stamp_box": tk.BooleanVar(value=tpl.include_stamp_box),
            "include_subject": tk.BooleanVar(value=tpl.include_subject),
        }
        frame = CTkFrame(self); frame.pack(fill="both", expand=True, padx=12, pady=12)
        fields = [("Name","name"),("Output Mode","output_mode"),("Envelope Width (in)","envelope_width_in"),
            ("Envelope Height (in)","envelope_height_in"),("Logo Path","logo_path"),
            ("Return X (in)","return_x"),("Return Y (in)","return_y"),
            ("To X (in)","to_x"),("To Y (in)","to_y"),("Font Name","font_name"),("Font Size","font_size")]
        row = 0
        for label, key in fields:
            CTkLabel(frame, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=4)
            if key == "output_mode":
                CTkComboBox(frame, values=["cut_label","envelope","avery_5160","avery_8160","avery_5260"],
                    variable=self.vars[key], width=280).grid(row=row, column=1, sticky="ew", padx=4, pady=4)
            else:
                CTkEntry(frame, textvariable=self.vars[key], width=280).grid(row=row, column=1, sticky="ew", padx=4, pady=4)
            row += 1
        CTkButton(frame, text="Browse Logo", command=self._browse_logo).grid(row=4, column=2, padx=4, pady=4)
        CTkCheckBox(frame, text="Show logo", variable=self.vars["show_logo"]).grid(row=row, column=0, sticky="w", padx=4, pady=4)
        CTkCheckBox(frame, text="Include stamp box", variable=self.vars["include_stamp_box"]).grid(row=row, column=1, sticky="w", padx=4, pady=4)
        row += 1
        CTkCheckBox(frame, text="Include subject/reference", variable=self.vars["include_subject"]).grid(row=row, column=0, sticky="w", padx=4, pady=4)
        row += 1
        btns = CTkFrame(self); btns.pack(fill="x", padx=12, pady=(0,12))
        CTkButton(btns, text="Cancel", command=self.destroy).pack(side="right", padx=6)
        CTkButton(btns, text="Save", command=self._save).pack(side="right", padx=6)
        self.template_id = tpl.id; self.created_at = tpl.created_at; self.updated_at = tpl.updated_at

    def _browse_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg *.webp")])
        if path: self.vars["logo_path"].set(path)

    def _save(self):
        self.result = Template(
            id=self.template_id, name=self.vars["name"].get().strip(),
            output_mode=self.vars["output_mode"].get().strip(),
            envelope_width_in=float(self.vars["envelope_width_in"].get() or 0),
            envelope_height_in=float(self.vars["envelope_height_in"].get() or 0),
            logo_path=self.vars["logo_path"].get().strip(),
            show_logo=bool(self.vars["show_logo"].get()),
            return_x=float(self.vars["return_x"].get() or 0), return_y=float(self.vars["return_y"].get() or 0),
            to_x=float(self.vars["to_x"].get() or 0), to_y=float(self.vars["to_y"].get() or 0),
            font_name=self.vars["font_name"].get().strip() or "Helvetica",
            font_size=int(float(self.vars["font_size"].get() or 11)),
            include_stamp_box=bool(self.vars["include_stamp_box"].get()),
            include_subject=bool(self.vars["include_subject"].get()),
            created_at=self.created_at, updated_at=self.updated_at)
        self.destroy()
