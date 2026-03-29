from __future__ import annotations
from gui.dialogs.contact_editor_dialog import ContactEditorDialog
from gui.theme import CTkButton, CTkEntry, CTkFrame, CTkLabel, messagebox, tk, ttk

class ContactsTab(CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.search_var = tk.StringVar()
        top = CTkFrame(self); top.pack(fill="x", padx=8, pady=8)
        CTkLabel(top, text="Search").pack(side="left", padx=4)
        CTkEntry(top, textvariable=self.search_var, width=260).pack(side="left", padx=4)
        for text, cmd in [("Refresh",self.refresh),("Add",self.add_contact),("Edit",self.edit_contact),
                ("Delete",self.delete_contact),("Use as From",self.use_as_from),("Use as To",self.use_as_to)]:
            CTkButton(top, text=text, command=cmd).pack(side="left", padx=4)
        cols = ("id","label","name","company","city","state","zip")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        for col in cols:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=110 if col != "label" else 180)
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0,8))
        self.refresh()

    def selected_contact(self):
        sel = self.tree.selection()
        if not sel: return None
        return self.controller.contacts_repo.get(int(self.tree.item(sel[0], "values")[0]))

    def refresh(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for c in self.controller.contacts_repo.all(self.search_var.get().strip()):
            self.tree.insert("", "end", values=(c.id, c.label, c.address.name, c.address.company, c.address.city, c.address.state, c.address.formatted_postal_code()))

    def add_contact(self):
        dlg = ContactEditorDialog(self); self.wait_window(dlg)
        if dlg.result: self.controller.contacts_repo.save(dlg.result); self.refresh()

    def edit_contact(self):
        contact = self.selected_contact()
        if not contact: messagebox.showwarning("Contacts", "Select a contact first."); return
        dlg = ContactEditorDialog(self, contact); self.wait_window(dlg)
        if dlg.result: self.controller.contacts_repo.save(dlg.result); self.refresh()

    def delete_contact(self):
        contact = self.selected_contact()
        if not contact: messagebox.showwarning("Contacts", "Select a contact first."); return
        if messagebox.askyesno("Delete", f"Delete contact '{contact.label}'?"):
            self.controller.contacts_repo.delete(contact.id); self.refresh()

    def use_as_from(self):
        contact = self.selected_contact()
        if contact: self.controller.single_tab.load_contact_as_sender(contact)

    def use_as_to(self):
        contact = self.selected_contact()
        if contact: self.controller.single_tab.load_contact_as_recipient(contact)
