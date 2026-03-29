from __future__ import annotations

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

from gui.main_window import MainWindow
from utils.file_utils import env_path


def main() -> None:
    if load_dotenv:
        try:
            load_dotenv(env_path())
        except Exception:
            pass
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
