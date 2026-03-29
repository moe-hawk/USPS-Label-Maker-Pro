from __future__ import annotations
import os, platform, subprocess
from pathlib import Path
from gui.theme import CTkButton, CTkFrame, filedialog, messagebox, ttk
from services.export_service import ExportService

class JobsTab(CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.export_service = ExportService()
        top = CTkFrame(self); top.pack(fill="x", padx=8, pady=8)
        CTkButton(top, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        CTkButton(top, text="Open Output", command=self.open_output).pack(side="left", padx=4)
        CTkButton(top, text="Export Failed Rows", command=self.export_failed_rows).pack(side="left", padx=4)
        cols = ("id","created_at","mode","status","rows","success","failed","output")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        for col in cols:
            self.tree.heading(col, text=col.replace("_"," ").title())
            self.tree.column(col, width=110 if col != "output" else 280)
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0,8))
        self.refresh()

    def selected_job_id(self):
        sel = self.tree.selection()
        if not sel: return None
        return int(self.tree.item(sel[0], "values")[0])

    def refresh(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for job in self.controller.jobs_repo.all():
            self.tree.insert("", "end", values=(job.id, job.created_at[:19], job.mode, job.status, job.total_rows, job.success_rows, job.failed_rows, job.output_file))

    def open_output(self):
        job_id = self.selected_job_id()
        if not job_id: messagebox.showwarning("Jobs", "Select a job first."); return
        job = self.controller.jobs_repo.get(job_id)
        if not job or not job.output_file: messagebox.showwarning("Jobs", "No output file recorded for this job."); return
        path = Path(job.output_file)
        target = path if path.exists() else path.parent
        try:
            system = platform.system()
            if system == "Windows": os.startfile(str(target))
            elif system == "Darwin": subprocess.Popen(["open", str(target)])
            else: subprocess.Popen(["xdg-open", str(target)])
        except Exception:
            messagebox.showinfo("Output", str(target))

    def export_failed_rows(self):
        job_id = self.selected_job_id()
        if not job_id: messagebox.showwarning("Jobs", "Select a job first."); return
        rows = [r for r in self.controller.jobs_repo.rows_for_job(job_id) if r.get("status") != "success"]
        if not rows: messagebox.showinfo("Jobs", "No failed rows for this job."); return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile=f"job-{job_id}-failed.csv")
        if not path: return
        self.export_service.export_failed_rows(path, rows)
        messagebox.showinfo("Jobs", f"Exported failed rows to {path}")
