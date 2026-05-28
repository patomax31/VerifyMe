import os
import sys
from typing import Optional

import cv2

from src.core.config import get_camera_settings, is_raspberry_pi


def _try_picamera2():
    """
    Try picamera2 for Raspberry Pi Camera Module 2 (RECOMMENDED).
    This is the most reliable method on Raspberry Pi 5 Bookworm.
    """
    try:
        from picamera2 import Picamera2
        
        print("[INFO] Initializing Raspberry Pi Camera Module 2 with picamera2...", file=sys.stderr)
        picam2 = Picamera2()
        settings = get_camera_settings()
        
        # Create configuration for RGB format
        config = picam2.create_preview_configuration(
            main={"size": (settings.width, settings.height), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()
        
        # Wrapper to provide OpenCV-compatible interface
        class PiCameraWrapper:
            def __init__(self, camera):
                self.camera = camera
                self.is_open = True
            
            def read(self):
                try:
                    frame_rgb = self.camera.capture_array()
                    if frame_rgb is None or frame_rgb.size == 0:
                        return False, None
                    # Convert RGB to BGR for OpenCV consumers
                    try:
                        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                        return True, frame_bgr
                    except Exception:
                        return True, frame_rgb
                except Exception:
                    return False, None
            
            def release(self):
                try:
                    self.camera.stop()
                    if hasattr(self.camera, "close"):
                        self.camera.close()
                    self.is_open = False
                except Exception:
                    pass
            
            def isOpened(self):
                return self.is_open
            
            def set(self, prop_id, value):
                return False
            
            def get(self, prop_id):
                return -1
        
        print("[SUCCESS] Raspberry Pi Camera Module 2 ready via picamera2!", file=sys.stderr)
        return PiCameraWrapper(picam2)
        
    except ImportError:
        print("[DEBUG] picamera2 not installed, trying fallback methods", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[DEBUG] picamera2 failed: {e}", file=sys.stderr)
        return None


def open_camera(camera_index: Optional[int] = None):
    """
    OpenCV camera bootstrap with priority for picamera2 on Raspberry Pi.
    
    Raspberry Pi 5 + Camera Module 2 priority:
    1. picamera2 (RECOMMENDED)
    2. V4L2 with libcamera
    
    Windows: CAP_DSHOW
    """
    settings = get_camera_settings()
    profile = settings.profile
    if profile == "AUTO":
        if os.name == "nt":
            profile = "WINDOWS_STABLE"
        elif is_raspberry_pi():
            profile = "RASPBERRY_PI"
        else:
            profile = "LINUX"

    # Allow explicit override from function arg
    cam_index = settings.index if camera_index is None else int(camera_index)

    # Priority 1: Try picamera2 for Raspberry Pi (but fall back to V4L2 if unavailable)
    if profile == "RASPBERRY_PI":
        cap = _try_picamera2()
        if cap is not None:
            return cap
        print("[WARN] picamera2 no disponible o falló; intentando V4L2/libcamera como fallback.", file=sys.stderr)
    
    # Priority 2: Try OpenCV backends
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
        try:
            cap = cv2.VideoCapture(index) if backend is None else cv2.VideoCapture(index, backend)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)
                cap.set(cv2.CAP_PROP_FPS, settings.fps)
                return cap
        except Exception:
            pass
        try:
            cap.release()
        except Exception:
            pass
    
    print("[ERROR] Could not open camera", file=sys.stderr)
    print("[FIX] Install picamera2: sudo apt install python3-picamera2", file=sys.stderr)
    return None
