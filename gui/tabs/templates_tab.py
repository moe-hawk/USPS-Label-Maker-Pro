from __future__ import annotations
from gui.dialogs.template_editor_dialog import TemplateEditorDialog
from gui.theme import CTkButton, CTkFrame, messagebox, ttk

class TemplatesTab(CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        top = CTkFrame(self); top.pack(fill="x", padx=8, pady=8)
        for text, cmd in [("Refresh",self.refresh),("Add",self.add_template),("Edit",self.edit_template),("Delete",self.delete_template)]:
            CTkButton(top, text=text, command=cmd).pack(side="left", padx=4)
        cols = ("id","name","output_mode","width","height","logo","subject")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        for col in cols:
            self.tree.heading(col, text=col.replace("_"," ").title())
            self.tree.column(col, width=120 if col != "name" else 200)
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0,8))
        self.refresh()

    def selected_template(self):
        sel = self.tree.selection()
        if not sel: return None
        return self.controller.templates_repo.get(int(self.tree.item(sel[0], "values")[0]))

    def refresh(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for tpl in self.controller.templates_repo.all():
            self.tree.insert("", "end", values=(tpl.id, tpl.name, tpl.output_mode, tpl.envelope_width_in, tpl.envelope_height_in, "yes" if tpl.show_logo else "no", "yes" if tpl.include_subject else "no"))
        self.controller.single_tab.refresh_template_choices()
        self.controller.batch_tab.refresh_template_choices()

    def add_template(self):
        dlg = TemplateEditorDialog(self); self.wait_window(dlg)
        if dlg.result: self.controller.templates_repo.save(dlg.result); self.refresh()

    def edit_template(self):
        tpl = self.selected_template()
        if not tpl: messagebox.showwarning("Templates", "Select a template first."); return
        dlg = TemplateEditorDialog(self, tpl); self.wait_window(dlg)
        if dlg.result: self.controller.templates_repo.save(dlg.result); self.refresh()

    def delete_template(self):
        tpl = self.selected_template()
        if not tpl: messagebox.showwarning("Templates", "Select a template first."); return
        if messagebox.askyesno("Delete", f"Delete template '{tpl.name}'?"):
            self.controller.templates_repo.delete(tpl.id); self.refresh()
