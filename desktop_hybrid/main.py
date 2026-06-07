from __future__ import annotations

import os
import sys

# Configure Qt backend for PyQt6 (required for pywebview on Raspberry Pi)
os.environ.setdefault("QT_API", "pyqt6")


def _is_raspberry_pi() -> bool:
    try:
        with open("/proc/device-tree/model", "r", encoding="utf-8", errors="ignore") as fh:
            return "raspberry" in fh.read().lower()
    except Exception:
        return False


def _set_raspberry_defaults() -> None:
    if not _is_raspberry_pi():
        return

    os.environ.setdefault("CAMERA_PROFILE", "RASPBERRY_PI")
    os.environ.setdefault("PICAMERA_FORMAT", "BGR888")
    os.environ.setdefault("CAMERA_SWAP_RB", "1")
    os.environ.setdefault("CAMERA_ROTATE", "180")
    os.environ.setdefault("CAMERA_WIDTH", "640")
    os.environ.setdefault("CAMERA_HEIGHT", "480")
    os.environ.setdefault("CAMERA_FPS", "20")
    os.environ.setdefault("HARDWARE_ENABLED", "0")
    os.environ.setdefault("LIVENESS_ALLOW_FACE_FALLBACK", "0")


_set_raspberry_defaults()

from app.runner import run_desktop_app


if __name__ == "__main__":
    sys.exit(run_desktop_app())
