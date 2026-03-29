from __future__ import annotations
from gui.theme import CTkButton, CTkCheckBox, CTkComboBox, CTkEntry, CTkFrame, CTkLabel, filedialog, messagebox, tk

class SettingsTab(CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.vars = {k: tk.StringVar(value=str(v)) for k, v in controller.settings.items()}
        self.bool_vars = {
            "usps_use_test_env": tk.BooleanVar(value=bool(controller.settings.get("usps_use_test_env", True))),
            "always_accept_standardized": tk.BooleanVar(value=bool(controller.settings.get("always_accept_standardized", False))),
            "save_corrections": tk.BooleanVar(value=bool(controller.settings.get("save_corrections", True))),
            "buy_paid_labels": tk.BooleanVar(value=bool(controller.settings.get("buy_paid_labels", False))),
        }
        frame = CTkFrame(self); frame.pack(fill="both", expand=True, padx=8, pady=8)
        fields = [("Theme","theme"),("Default Provider","provider"),("USPS Client ID","usps_client_id"),
            ("USPS Client Secret","usps_client_secret"),("USPS Account Type","usps_account_type"),
            ("USPS Account Number","usps_account_number"),("EasyPost API Key","easypost_api_key"),
            ("Shippo API Token","shippo_api_token"),("Default Output Dir","default_output_dir"),
            ("Forever Stamp Price","forever_stamp_price"),("Letter Additional Oz Price","letter_additional_ounce_price"),
            ("Nonmachinable Surcharge","nonmachinable_surcharge"),("Flat 1oz Price","flat_1oz_price"),("Default Logo","default_logo")]
        row = 0
        for label, key in fields:
            CTkLabel(frame, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=3)
            if key == "theme":
                CTkComboBox(frame, values=["system","light","dark"], variable=self.vars[key], width=320).grid(row=row, column=1, sticky="ew", padx=4, pady=3)
            elif key == "provider":
                CTkComboBox(frame, values=["USPS","EasyPost","Shippo"], variable=self.vars[key], width=320).grid(row=row, column=1, sticky="ew", padx=4, pady=3)
            else:
                CTkEntry(frame, textvariable=self.vars[key], width=320).grid(row=row, column=1, sticky="ew", padx=4, pady=3)
            if key in {"default_output_dir","default_logo"}:
                CTkButton(frame, text="Browse", command=lambda k=key: self._browse(k)).grid(row=row, column=2, padx=4, pady=3)
            row += 1
        for key, label in [("usps_use_test_env","Use USPS test environment"),
                ("always_accept_standardized","Always accept standardized addresses"),
                ("save_corrections","Save correction history"),
                ("buy_paid_labels","Default to buying paid labels when supported")]:
            CTkCheckBox(frame, text=label, variable=self.bool_vars[key]).grid(row=row, column=0, columnspan=2, sticky="w", padx=4, pady=3)
            row += 1
        CTkButton(frame, text="Save Settings", command=self.save_settings).grid(row=row, column=0, padx=4, pady=10, sticky="w")
        frame.grid_columnconfigure(1, weight=1)

    def _browse(self, key: str):
        path = filedialog.askdirectory() if key == "default_output_dir" else filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg *.webp")])
        if path: self.vars[key].set(path)

    def save_settings(self):
        settings = dict(self.controller.settings)
        for key, var in self.vars.items(): settings[key] = var.get()
        for key, var in self.bool_vars.items(): settings[key] = bool(var.get())
        for key in ["forever_stamp_price","letter_additional_ounce_price","nonmachinable_surcharge","flat_1oz_price"]:
            try: settings[key] = float(settings[key])
            except Exception: pass
        self.controller.save_settings(settings)
        messagebox.showinfo("Settings", "Settings saved.")
