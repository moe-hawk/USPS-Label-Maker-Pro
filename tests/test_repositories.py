from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from storage.db import Database
from storage.repositories.contacts_repo import ContactsRepository
from storage.repositories.templates_repo import TemplatesRepository
from models.contact import Contact
from models.address import Address

def run():
    db = Database("repo_test.sqlite3"); db.migrate()
    contacts = ContactsRepository(db)
    templates = TemplatesRepository(db); templates.ensure_defaults()
    saved = contacts.save(Contact(label="Test", address=Address(line1="1 Main", city="Albany", state="NY", postal_code="12231")))
    assert saved.id is not None
    assert contacts.get(saved.id) is not None
    assert templates.all()
    print("test_repositories passed")

if __name__ == "__main__":
    run()
