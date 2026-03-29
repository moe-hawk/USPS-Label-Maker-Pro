from __future__ import annotations
from pathlib import Path
from gui.dialogs.rate_details_dialog import RateDetailsDialog
from gui.theme import CTkButton, CTkCheckBox, CTkComboBox, CTkEntry, CTkFrame, CTkLabel, CTkTextbox, filedialog, messagebox, tk
from gui.widgets.address_form import AddressForm
from gui.widgets.mailpiece_form import MailpieceForm
from gui.widgets.preview_canvas import PreviewPane

class SingleLabelTab(CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.subject_var = tk.StringVar()
        self.provider_var = tk.StringVar(value="USPS")
        self.template_var = tk.StringVar()
        self.standardize_var = tk.BooleanVar(value=False)
        self.auto_accept_var = tk.BooleanVar(value=False)
        self.buy_label_var = tk.BooleanVar(value=False)
        left = CTkFrame(self); left.pack(side="left", fill="y", padx=(8,4), pady=8)
        right = CTkFrame(self); right.pack(side="left", fill="both", expand=True, padx=(4,8), pady=8)
        self.from_form = AddressForm(left, title="From"); self.from_form.pack(fill="x", padx=4, pady=4)
        self.to_form = AddressForm(left, title="To"); self.to_form.pack(fill="x", padx=4, pady=4)
        self.mailpiece_form = MailpieceForm(left); self.mailpiece_form.pack(fill="x", padx=4, pady=4)
        opts = CTkFrame(left); opts.pack(fill="x", padx=4, pady=4)
        CTkLabel(opts, text="Subject / Reference").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        CTkEntry(opts, textvariable=self.subject_var, width=250).grid(row=0, column=1, sticky="ew", padx=4, pady=2)
        CTkLabel(opts, text="Provider").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.provider_combo = CTkComboBox(opts, values=["USPS","EasyPost","Shippo"], variable=self.provider_var, width=220)
        self.provider_combo.grid(row=1, column=1, sticky="ew", padx=4, pady=2)
        CTkLabel(opts, text="Template").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.template_combo = CTkComboBox(opts, values=[], variable=self.template_var, width=220)
        self.template_combo.grid(row=2, column=1, sticky="ew", padx=4, pady=2)
        CTkCheckBox(opts, text="Standardize addresses", variable=self.standardize_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=4, pady=2)
        CTkCheckBox(opts, text="Auto-accept standardized addresses", variable=self.auto_accept_var).grid(row=4, column=0, columnspan=2, sticky="w", padx=4, pady=2)
        CTkCheckBox(opts, text="Buy paid label if provider supports it", variable=self.buy_label_var).grid(row=5, column=0, columnspan=2, sticky="w", padx=4, pady=2)
        opts.grid_columnconfigure(1, weight=1)
        btns = CTkFrame(left); btns.pack(fill="x", padx=4, pady=6)
        for text, cmd in [("Refresh Preview",self.refresh_preview),("Get Quote",self.get_quote),("Generate PDF",self.generate_pdf),("Clear Form",self.clear_all)]:
            CTkButton(btns, text=text, command=cmd).pack(fill="x", pady=2)
        self.preview = PreviewPane(right); self.preview.pack(fill="both", expand=True, padx=6, pady=6)
        quote_frame = CTkFrame(right); quote_frame.pack(fill="x", padx=6, pady=(0,6))
        self.quote_box = CTkTextbox(quote_frame, width=640, height=120)
        self.quote_box.pack(fill="both", expand=True, padx=6, pady=6)
        self.last_quotes = []
        self.refresh_template_choices()

    def refresh_template_choices(self):
        names = [tpl.name for tpl in self.controller.templates_repo.all()] or ["Default #10 Cut Label"]
        try: self.template_combo.configure(values=names)
        except Exception: self.template_combo["values"] = names
        if not self.template_var.get(): self.template_var.set(names[0])

    def _current_objects(self):
        return self.from_form.get_address(), self.to_form.get_address(), self.mailpiece_form.get_mailpiece(), self.subject_var.get().strip()

    def refresh_preview(self):
        try:
            from_addr, to_addr, mailpiece, subject = self._current_objects()
            template = self.controller.templates_repo.get_by_name(self.template_var.get())
            if not template: messagebox.showerror("Template", "Please select a valid template."); return
            self.preview.update_preview(from_addr, to_addr, mailpiece, template, subject)
        except Exception as exc: messagebox.showerror("Preview", str(exc))

    def get_quote(self):
        self.quote_box.delete("1.0", "end")
        try:
            from_addr, to_addr, mailpiece, _ = self._current_objects()
            quotes = self.controller.quote_only(from_addr, to_addr, mailpiece, provider_name=self.provider_var.get())
            self.last_quotes = quotes
            self.quote_box.insert("1.0", "\n".join(q.display_line() for q in quotes))
        except Exception as exc: self.quote_box.insert("1.0", str(exc))

    def generate_pdf(self):
        try:
            from_addr, to_addr, mailpiece, subject = self._current_objects()
            output_dir = filedialog.askdirectory(title="Choose output folder", initialdir=str(self.controller.settings.get("default_output_dir", ""))) or self.controller.settings.get("default_output_dir", "")
            if not output_dir: return
            result = self.controller.generate_single_pdf(
                from_addr, to_addr, mailpiece, self.template_var.get(), output_dir, self.provider_var.get(),
                subject=subject, standardize_addresses=bool(self.standardize_var.get()),
                auto_accept_standardized=bool(self.auto_accept_var.get()), buy_paid_labels=bool(self.buy_label_var.get()))
            self.quote_box.delete("1.0", "end")
            lines = [result["quote_line"], f'Output: {result["output_path"]}']
            if result.get("warnings"): lines.append("Warnings: " + "; ".join(result["warnings"]))
            self.quote_box.insert("1.0", "\n".join(lines))
            messagebox.showinfo("Done", f'Created: {result["output_path"]}')
            self.refresh_preview()
        except Exception as exc: messagebox.showerror("Generate PDF", str(exc))

    def clear_all(self):
        self.from_form.clear(); self.to_form.clear(); self.mailpiece_form.clear()
        self.subject_var.set(""); self.quote_box.delete("1.0", "end")

    def load_contact_as_sender(self, contact): self.from_form.set_address(contact.address)
    def load_contact_as_recipient(self, contact): self.to_form.set_address(contact.address)
