import os
import sys
from typing import Optional

import cv2

from src.core.config import get_camera_settings


def open_camera(camera_index: Optional[int] = None):
    """
    Camera bootstrap.

    Windows:
        CAP_DSHOW

    Linux (incluyendo Raspberry Pi 5):
        CAP_V4L2
    """

    settings = get_camera_settings()

    profile = settings.profile

    if profile == "AUTO":
        profile = "WINDOWS_STABLE" if os.name == "nt" else "LINUX"

    cam_index = settings.index if camera_index is None else int(camera_index)

    if profile == "WINDOWS_STABLE":
        attempts = [
            (cam_index, cv2.CAP_DSHOW),
            (1 - cam_index, cv2.CAP_DSHOW),
        ]
    else:
        attempts = [
            (cam_index, cv2.CAP_V4L2),
            (1 - cam_index, cv2.CAP_V4L2),
            (cam_index, None),
        ]

    for index, backend in attempts:
        cap = None

        try:
            if backend is None:
                cap = cv2.VideoCapture(index)
            else:
                cap = cv2.VideoCapture(index, backend)

            if not cap.isOpened():
                continue

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)
            cap.set(cv2.CAP_PROP_FPS, settings.fps)

            print(
                f"[INFO] Camera opened successfully "
                f"(index={index}, backend={backend})",
                file=sys.stderr,
            )

            return cap

        except Exception as e:
            print(
                f"[DEBUG] Camera open failed "
                f"(index={index}, backend={backend}): {e}",
                file=sys.stderr,
            )

        finally:
            if cap is not None and not cap.isOpened():
                try:
                    cap.release()
                except Exception:
                    pass

    print("[ERROR] Could not open camera", file=sys.stderr)
    return None