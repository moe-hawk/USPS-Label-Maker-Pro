from __future__ import annotations
import json, os
from storage.db import Database
from utils.file_utils import app_home

DEFAULTS = {
    "theme": "system", "provider": "USPS",
    "usps_client_id": os.getenv("USPS_CLIENT_ID", ""),
    "usps_client_secret": os.getenv("USPS_CLIENT_SECRET", ""),
    "usps_use_test_env": True,
    "usps_account_type": os.getenv("USPS_ACCOUNT_TYPE", "EPS"),
    "usps_account_number": os.getenv("USPS_ACCOUNT_NUMBER", ""),
    "easypost_api_key": os.getenv("EASYPOST_API_KEY", ""),
    "shippo_api_token": os.getenv("SHIPPO_API_TOKEN", ""),
    "default_output_dir": str(app_home() / "exports"),
    "forever_stamp_price": 0.78, "letter_additional_ounce_price": 0.29,
    "nonmachinable_surcharge": 0.49, "flat_1oz_price": 1.63,
    "default_logo": "", "always_accept_standardized": False,
    "save_corrections": True, "buy_paid_labels": False, "preview_scale": 1.0,
}

class SettingsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def load(self) -> dict:
        settings = dict(DEFAULTS)
        for row in self.db.query("SELECT key, value FROM app_settings"):
            try:
                settings[row["key"]] = json.loads(row["value"])
            except Exception:
                settings[row["key"]] = row["value"]
        return settings

    def save(self, settings: dict) -> None:
        self.db.execute("DELETE FROM app_settings")
        for key, value in settings.items():
            self.db.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, json.dumps(value)))
