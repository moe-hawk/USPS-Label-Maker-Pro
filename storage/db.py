from __future__ import annotations
import sqlite3
from pathlib import Path
from utils.file_utils import default_db_path

class Database:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else default_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            # check_same_thread=False: the batch JobWorker thread accesses
            # templates_repo and corrections_repo through this same connection.
            # The default True raises ProgrammingError across thread boundaries.
            # WAL mode lets the worker read while the main thread writes job rows.
            self._conn = sqlite3.connect(self.path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def migrate(self) -> None:
        mig_dir = Path(__file__).resolve().parent / "migrations"
        for sql_file in sorted(mig_dir.glob("*.sql")):
            self.conn.executescript(sql_file.read_text(encoding="utf-8"))
        self.conn.commit()

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    def executemany(self, sql: str, seq) -> sqlite3.Cursor:
        cur = self.conn.executemany(sql, seq)
        self.conn.commit()
        return cur

    def query(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, params).fetchall()

    def query_one(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        return self.conn.execute(sql, params).fetchone()
