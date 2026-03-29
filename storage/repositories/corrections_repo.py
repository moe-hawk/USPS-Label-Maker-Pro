from __future__ import annotations
import json
from models.correction import AddressCorrection
from storage.db import Database

class CorrectionsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, correction: AddressCorrection) -> None:
        self.db.execute(
            "INSERT INTO address_corrections (source,original_address_json,suggested_address_json,accepted,created_at) VALUES (?,?,?,?,?)",
            (correction.source, json.dumps(correction.original.as_dict()),
             json.dumps(correction.suggested.as_dict()),
             None if correction.accepted is None else int(correction.accepted),
             correction.created_at))
