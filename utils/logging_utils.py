from __future__ import annotations
import logging
from pathlib import Path
from utils.file_utils import default_log_path

def configure_logging(log_path: str | Path | None = None) -> logging.Logger:
    target = Path(log_path) if log_path else default_log_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("usps_label_maker_v24")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(target, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(fh)
    logger.addHandler(logging.StreamHandler())
    return logger
