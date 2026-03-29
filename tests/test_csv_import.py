from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.import_service import ImportService
from utils.csv_utils import sample_template_rows, write_csv

def run():
    path = Path("sample.csv")
    rows = sample_template_rows()
    write_csv(path, list(rows[0].keys()), rows)
    loaded, mapping = ImportService().load_with_mapping(path)
    assert loaded
    assert mapping.get("to_line1")
    print("test_csv_import passed")

if __name__ == "__main__":
    run()
