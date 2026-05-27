from __future__ import annotations

import os
import sys

# Configure Qt backend for PyQt6 (required for pywebview on Raspberry Pi)
os.environ.setdefault("QT_API", "pyqt6")

from app.runner import run_desktop_app


if __name__ == "__main__":
    sys.exit(run_desktop_app())
