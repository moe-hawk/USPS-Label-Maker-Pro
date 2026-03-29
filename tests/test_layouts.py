from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models.address import Address
from models.mailpiece import Mailpiece
from models.template import Template
from pdf.label_renderer import LabelRenderer
from pdf.envelope_renderer import EnvelopeRenderer
from pdf.avery_renderer import AveryRenderer

def run():
    out = Path("tests_out"); out.mkdir(exist_ok=True)
    from_addr = Address(company="BlueAnchor Security", line1="11762 Marsden St", city="Jamaica", state="NY", postal_code="11434")
    to_addr = Address(company="Department of State", line1="99 Washington Avenue", city="Albany", state="NY", postal_code="12231")
    tpl = Template(name="Test", output_mode="cut_label")
    LabelRenderer().render(out / "label.pdf", from_addr, to_addr, Mailpiece(), tpl)
    EnvelopeRenderer().render(out / "env.pdf", from_addr, to_addr, Mailpiece(output_mode="envelope"), tpl)
    AveryRenderer().render(out / "avery.pdf", [{"from_address": from_addr, "to_address": to_addr, "subject": ""}], Template(name="Avery", output_mode="avery_5160"), "avery_5160")
    assert (out / "label.pdf").exists()
    assert (out / "env.pdf").exists()
    assert (out / "avery.pdf").exists()
    print("test_layouts passed")

if __name__ == "__main__":
    run()
