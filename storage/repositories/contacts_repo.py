from __future__ import annotations
from datetime import datetime
from models.address import Address
from models.contact import Contact
from storage.db import Database

class ContactsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def all(self, search: str = "") -> list[Contact]:
        if search:
            like = f"%{search}%"
            rows = self.db.query(
                "SELECT * FROM contacts WHERE label LIKE ? OR company LIKE ? OR name LIKE ? OR city LIKE ? OR state LIKE ? ORDER BY updated_at DESC",
                (like, like, like, like, like))
        else:
            rows = self.db.query("SELECT * FROM contacts ORDER BY updated_at DESC")
        return [self._row_to_contact(r) for r in rows]

    def get(self, contact_id: int) -> Contact | None:
        row = self.db.query_one("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        return self._row_to_contact(row) if row else None

    def save(self, contact: Contact) -> Contact:
        now = datetime.utcnow().isoformat()
        contact.updated_at = now
        if contact.id is None:
            contact.created_at = now
            cur = self.db.execute(
                "INSERT INTO contacts (label,subject,tags,notes,name,company,line1,line2,city,state,postal_code,postal_code_plus4,country,phone,email,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (contact.label, contact.subject, contact.tags, contact.notes,
                 contact.address.name, contact.address.company, contact.address.line1, contact.address.line2,
                 contact.address.city, contact.address.state, contact.address.postal_code,
                 contact.address.postal_code_plus4, contact.address.country,
                 contact.address.phone, contact.address.email, contact.created_at, contact.updated_at))
            contact.id = int(cur.lastrowid)
        else:
            self.db.execute(
                "UPDATE contacts SET label=?,subject=?,tags=?,notes=?,name=?,company=?,line1=?,line2=?,city=?,state=?,postal_code=?,postal_code_plus4=?,country=?,phone=?,email=?,updated_at=? WHERE id=?",
                (contact.label, contact.subject, contact.tags, contact.notes,
                 contact.address.name, contact.address.company, contact.address.line1, contact.address.line2,
                 contact.address.city, contact.address.state, contact.address.postal_code,
                 contact.address.postal_code_plus4, contact.address.country,
                 contact.address.phone, contact.address.email, contact.updated_at, contact.id))
        return contact

    def delete(self, contact_id: int) -> None:
        self.db.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))

    def _row_to_contact(self, row) -> Contact:
        return Contact(
            id=row["id"], label=row["label"], subject=row["subject"],
            tags=row["tags"], notes=row["notes"],
            address=Address(name=row["name"], company=row["company"], line1=row["line1"],
                line2=row["line2"], city=row["city"], state=row["state"],
                postal_code=row["postal_code"], postal_code_plus4=row["postal_code_plus4"],
                country=row["country"], phone=row["phone"], email=row["email"]),
            created_at=row["created_at"], updated_at=row["updated_at"])
