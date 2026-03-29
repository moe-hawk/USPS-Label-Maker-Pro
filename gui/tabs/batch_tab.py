from __future__ import annotations
from pathlib import Path
from gui.theme import CTkButton, CTkCheckBox, CTkComboBox, CTkEntry, CTkFrame, CTkLabel, CTkTextbox, filedialog, messagebox, tk
from gui.widgets.csv_mapping_table import CSVMappingTable
from gui.widgets.progress_panel import ProgressPanel

class BatchTab(CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.csv_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(controller.settings.get("default_output_dir", "")))
        self.provider_var = tk.StringVar(value="USPS")
        self.template_var = tk.StringVar()
        self.standardize_var = tk.BooleanVar(value=False)
        self.auto_accept_var = tk.BooleanVar(value=False)
        self.buy_label_var = tk.BooleanVar(value=False)
        self.rows = []; self.mapping = {}
        top = CTkFrame(self); top.pack(fill="x", padx=8, pady=8)
        CTkLabel(top, text="CSV File").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        CTkEntry(top, textvariable=self.csv_path_var, width=420).grid(row=0, column=1, sticky="ew", padx=4, pady=2)
        CTkButton(top, text="Browse", command=self._browse_csv).grid(row=0, column=2, padx=4, pady=2)
        CTkLabel(top, text="Output Folder").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        CTkEntry(top, textvariable=self.output_dir_var, width=420).grid(row=1, column=1, sticky="ew", padx=4, pady=2)
        CTkButton(top, text="Browse", command=self._browse_output).grid(row=1, column=2, padx=4, pady=2)
        CTkLabel(top, text="Provider").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.provider_combo = CTkComboBox(top, values=["USPS","EasyPost","Shippo"], variable=self.provider_var, width=220)
        self.provider_combo.grid(row=2, column=1, sticky="w", padx=4, pady=2)
        CTkLabel(top, text="Template").grid(row=3, column=0, sticky="w", padx=4, pady=2)
        self.template_combo = CTkComboBox(top, values=[], variable=self.template_var, width=220)
        self.template_combo.grid(row=3, column=1, sticky="w", padx=4, pady=2)
        CTkCheckBox(top, text="Standardize addresses", variable=self.standardize_var).grid(row=4, column=0, columnspan=2, sticky="w", padx=4, pady=2)
        CTkCheckBox(top, text="Auto-accept standardized", variable=self.auto_accept_var).grid(row=5, column=0, columnspan=2, sticky="w", padx=4, pady=2)
        CTkCheckBox(top, text="Buy paid labels when supported", variable=self.buy_label_var).grid(row=6, column=0, columnspan=2, sticky="w", padx=4, pady=2)
        CTkButton(top, text="Load CSV", command=self.load_csv).grid(row=7, column=0, padx=4, pady=6, sticky="w")
        CTkButton(top, text="Start Batch", command=self.start_batch).grid(row=7, column=1, padx=4, pady=6, sticky="w")
        CTkButton(top, text="Cancel Batch", command=self.controller.cancel_batch).grid(row=7, column=2, padx=4, pady=6, sticky="w")
        top.grid_columnconfigure(1, weight=1)
        body = CTkFrame(self); body.pack(fill="both", expand=True, padx=8, pady=(0,8))
        left = CTkFrame(body); left.pack(side="left", fill="y", padx=(0,4), pady=4)
        right = CTkFrame(body); right.pack(side="left", fill="both", expand=True, padx=(4,0), pady=4)
        self.mapping_widget = CSVMappingTable(left); self.mapping_widget.pack(fill="y", padx=4, pady=4)
        self.progress_panel = ProgressPanel(right); self.progress_panel.pack(fill="x", padx=4, pady=4)
        self.log_box = CTkTextbox(right, width=700, height=400); self.log_box.pack(fill="both", expand=True, padx=4, pady=4)
        self.refresh_template_choices()

    def refresh_template_choices(self):
        names = [tpl.name for tpl in self.controller.templates_repo.all()] or ["Default #10 Cut Label"]
        try: self.template_combo.configure(values=names)
        except Exception: self.template_combo["values"] = names
        if not self.template_var.get(): self.template_var.set(names[0])

    def _browse_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if path: self.csv_path_var.set(path)

    def _browse_output(self):
        path = filedialog.askdirectory()
        if path: self.output_dir_var.set(path)

    def load_csv(self):
        if not self.csv_path_var.get(): self._browse_csv()
        if not self.csv_path_var.get(): return
        try:
            self.rows, self.mapping = self.controller.load_batch_csv(self.csv_path_var.get())
            if not self.rows: messagebox.showwarning("CSV", "No rows found in CSV."); return
            self.mapping_widget.set_headers(list(self.rows[0].keys()), self.mapping)
            self.log_box.delete("1.0", "end")
            self.log_box.insert("1.0", f"Loaded {len(self.rows)} rows from {self.csv_path_var.get()}\n")
        except Exception as exc: messagebox.showerror("CSV", str(exc))

    def start_batch(self):
        if not self.rows: self.load_csv()
        if not self.rows: return
        mapping = self.mapping_widget.get_mapping()
        if not mapping: messagebox.showerror("Batch", "CSV mapping is empty."); return
        self.log_box.delete("1.0", "end")
        self.controller.start_batch_job(
            source_rows=self.rows, mapping=mapping, template_name=self.template_var.get(),
            output_dir=self.output_dir_var.get(), provider_name=self.provider_var.get(),
            standardize_addresses=bool(self.standardize_var.get()),
            auto_accept_standardized=bool(self.auto_accept_var.get()),
            buy_paid_labels=bool(self.buy_label_var.get()))

    def append_log(self, text: str):
        self.log_box.insert("end", text + "\n")
        try: self.log_box.see("end")
        except Exception: pass
