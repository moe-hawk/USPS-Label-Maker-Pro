from __future__ import annotations
from models.address import Address
from gui.theme import CTkFrame, CTkEntry, CTkLabel, tk

class AddressForm(CTkFrame):
    def __init__(self, master=None, title: str = "Address"):
        super().__init__(master)
        self.vars = {name: tk.StringVar() for name in ["name","company","line1","line2","city","state","postal_code","postal_code_plus4","country","phone","email"]}
        CTkLabel(self, text=title).grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=(4,6))
        for idx, (label, key) in enumerate([("Name","name"),("Company","company"),("Line 1","line1"),("Line 2","line2"),
                ("City","city"),("State","state"),("ZIP","postal_code"),("Plus4","postal_code_plus4"),
                ("Country","country"),("Phone","phone"),("Email","email")], start=1):
            CTkLabel(self, text=label).grid(row=idx, column=0, sticky="w", padx=4, pady=2)
            CTkEntry(self, textvariable=self.vars[key], width=220).grid(row=idx, column=1, sticky="ew", padx=4, pady=2)
        self.grid_columnconfigure(1, weight=1)
        self.vars["country"].set("US")

    def get_address(self) -> Address: return Address(**{k: v.get() for k, v in self.vars.items()})
    def set_address(self, address: Address) -> None:
        for key, var in self.vars.items(): var.set(getattr(address, key, ""))
    def clear(self) -> None:
        for var in self.vars.values(): var.set("")
        self.vars["country"].set("US")
