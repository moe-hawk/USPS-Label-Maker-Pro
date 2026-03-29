from __future__ import annotations
from models.contact import Contact
from gui.theme import CTkButton, CTkFrame, CTkToplevel, CTkEntry, CTkLabel, tk
from gui.widgets.address_form import AddressForm

class ContactEditorDialog(CTkToplevel):
    def __init__(self, master, contact: Contact | None = None):
        super().__init__(master)
        self.title("Contact")
        self.geometry("520x640")
        self.grab_set()
        self.result: Contact | None = None
        self.label_var = tk.StringVar(value=contact.label if contact else "")
        self.subject_var = tk.StringVar(value=contact.subject if contact else "")
        self.tags_var = tk.StringVar(value=contact.tags if contact else "")
        self.notes_var = tk.StringVar(value=contact.notes if contact else "")
        top = CTkFrame(self); top.pack(fill="x", padx=10, pady=10)
        for idx, (label, var) in enumerate([("Label",self.label_var),("Default Subject",self.subject_var),("Tags",self.tags_var),("Notes",self.notes_var)]):
            CTkLabel(top, text=label).grid(row=idx, column=0, sticky="w", padx=4, pady=2)
            CTkEntry(top, textvariable=var, width=320).grid(row=idx, column=1, sticky="ew", padx=4, pady=2)
        self.address_form = AddressForm(self, title="Recipient / Sender Address")
        self.address_form.pack(fill="both", expand=True, padx=10, pady=(0,10))
        if contact: self.address_form.set_address(contact.address)
        btns = CTkFrame(self); btns.pack(fill="x", padx=10, pady=(0,10))
        CTkButton(btns, text="Cancel", command=self.destroy).pack(side="right", padx=6)
        CTkButton(btns, text="Save", command=self._save).pack(side="right", padx=6)
        self.contact_id = contact.id if contact else None
        self.created_at = contact.created_at if contact else None
        self.updated_at = contact.updated_at if contact else None

    def _save(self):
        self.result = Contact(
            id=self.contact_id, label=self.label_var.get().strip(),
            subject=self.subject_var.get().strip(), tags=self.tags_var.get().strip(),
            notes=self.notes_var.get().strip(), address=self.address_form.get_address(),
            created_at=self.created_at or Contact().created_at,
            updated_at=self.updated_at or Contact().updated_at)
        self.destroy()
