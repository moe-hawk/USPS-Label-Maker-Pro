from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models.address import Address
from models.mailpiece import Mailpiece
from services.validation_service import ValidationService

def run():
    svc = ValidationService()
    assert svc.validate_address(Address(line1="1 Main St", city="Albany", state="NY", postal_code="12231")).ok()
    assert svc.validate_mailpiece(Mailpiece(mail_class="letter", width_in=9.5, height_in=4.125, thickness_in=0.02, weight_oz=1.0)).ok()
    print("test_validation passed")

if __name__ == "__main__":
    run()
