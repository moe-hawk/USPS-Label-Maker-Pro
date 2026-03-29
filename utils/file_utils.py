from __future__ import annotations
import os, re
from pathlib import Path

def app_home() -> Path:
    root = Path.home() / ".usps_label_maker_v24"
    root.mkdir(parents=True, exist_ok=True)
    return root

def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def sanitize_filename(text: str, fallback: str = "label") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._ -]+", "", text or "").strip()
    cleaned = re.sub(r"\s+", " ", cleaned).replace("/", "-")
    return cleaned or fallback

def default_output_dir() -> Path:
    return ensure_dir(app_home() / "exports")

def default_db_path() -> Path:
    return app_home() / "app.sqlite3"

def default_log_path() -> Path:
    return ensure_dir(app_home() / "logs") / "app.log"

def env_path() -> Path:
    return app_home() / ".env"

def asset_copy_name(src: str | Path) -> str:
    return sanitize_filename(Path(src).name, "asset")
