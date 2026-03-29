from __future__ import annotations
from gui.theme import CTkComboBox, CTkFrame, CTkLabel, tk

FIELDS = ["from_name","from_company","from_line1","from_line2","from_city","from_state","from_zip",
    "to_name","to_company","to_line1","to_line2","to_city","to_state","to_zip",
    "subject","notes","weight_oz","width_in","height_in","thickness_in","output_mode","mail_class","nonmachinable"]

class CSVMappingTable(CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.vars = {}
        CTkLabel(self, text="CSV Mapping").grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=(4,6))
        for idx, field in enumerate(FIELDS, start=1):
            CTkLabel(self, text=field).grid(row=idx, column=0, sticky="w", padx=4, pady=2)
            var = tk.StringVar(value="")
            combo = CTkComboBox(self, values=[""], variable=var, width=220)
            combo.grid(row=idx, column=1, sticky="ew", padx=4, pady=2)
            self.vars[field] = (var, combo)
        self.grid_columnconfigure(1, weight=1)

    def set_headers(self, headers: list[str], mapping: dict[str, str]):
        values = [""] + headers
        for field, (var, combo) in self.vars.items():
            try: combo.configure(values=values)
            except Exception: combo["values"] = values
            var.set(mapping.get(field, ""))

    def get_mapping(self) -> dict[str, str]:
        return {field: var.get() for field, (var, _) in self.vars.items() if var.get()}
