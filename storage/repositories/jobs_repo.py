from __future__ import annotations
from datetime import datetime
from models.job import LabelJob
from storage.db import Database

class JobsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def all(self) -> list[LabelJob]:
        return [LabelJob(**dict(r)) for r in self.db.query("SELECT * FROM jobs ORDER BY created_at DESC")]

    def get(self, job_id: int) -> LabelJob | None:
        row = self.db.query_one("SELECT * FROM jobs WHERE id = ?", (job_id,))
        return LabelJob(**dict(row)) if row else None

    def save(self, job: LabelJob) -> LabelJob:
        if job.id is None:
            cur = self.db.execute(
                "INSERT INTO jobs (created_at,mode,source_file,output_file,total_rows,success_rows,failed_rows,status,notes) VALUES (?,?,?,?,?,?,?,?,?)",
                (job.created_at, job.mode, job.source_file, job.output_file,
                 job.total_rows, job.success_rows, job.failed_rows, job.status, job.notes))
            job.id = int(cur.lastrowid)
        else:
            self.db.execute(
                "UPDATE jobs SET source_file=?,output_file=?,total_rows=?,success_rows=?,failed_rows=?,status=?,notes=? WHERE id=?",
                (job.source_file, job.output_file, job.total_rows, job.success_rows,
                 job.failed_rows, job.status, job.notes, job.id))
        return job

    def add_row_result(self, job_id: int, row_number: int, recipient_label: str, status: str,
                       error_message: str = "", original_address_json: str = "",
                       corrected_address_json: str = "", quote_json: str = "", output_path: str = "") -> None:
        self.db.execute(
            "INSERT INTO job_rows (job_id,row_number,recipient_label,status,error_message,original_address_json,corrected_address_json,quote_json,output_path,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (job_id, row_number, recipient_label, status, error_message,
             original_address_json, corrected_address_json, quote_json,
             output_path, datetime.utcnow().isoformat()))

    def rows_for_job(self, job_id: int) -> list[dict]:
        return [dict(r) for r in self.db.query("SELECT * FROM job_rows WHERE job_id=? ORDER BY row_number", (job_id,))]
