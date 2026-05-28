import os
import sys
import cv2

from src.core.config import get_camera_settings


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
        
        # Get full sensor resolution to avoid zoom/crop
        sensor_modes = picam2.sensor_modes
        print(f"[DEBUG] Available sensor modes: {len(sensor_modes)} modes", file=sys.stderr)
        
        # CRITICAL FIX: Do NOT specify size in create_preview_configuration()
        # When you specify a size (e.g., 640x480), picamera2 performs internal cropping
        # to fit that size, which creates the zoom/crop artifact on Raspberry Pi 5
        # Instead, capture at full sensor resolution and resize in Python after capture
        config = picam2.create_preview_configuration(
            main={"format": "RGB888"},  # NO size specified - captures full sensor
            raw=None  # Disable raw stream
        )
        
        picam2.configure(config)
        picam2.start()
        
        # Log actual sensor resolution being captured
        import time
        time.sleep(0.5)  # Brief delay to ensure camera starts
        try:
            test_frame = picam2.capture_array()
            if test_frame is not None:
                actual_h, actual_w = test_frame.shape[:2]
                print(f"[INFO] Actual sensor capture: {actual_w}x{actual_h}", file=sys.stderr)
        except Exception:
            pass
        
        # Wrapper to provide OpenCV-compatible interface
        class PiCameraWrapper:
            def __init__(self, camera, target_width, target_height):
                self.camera = camera
                self.is_open = True
                self.target_width = target_width
                self.target_height = target_height
                self.resize_method = cv2.INTER_LANCZOS4  # High-quality downsampling
            
            def read(self):
                try:
                    frame_rgb = self.camera.capture_array()
                    if frame_rgb is None or frame_rgb.size == 0:
                        return False, None
                    
                    # Resize to target dimensions if needed
                    # The resize happens AFTER full sensor capture, preventing internal cropping
                    h, w = frame_rgb.shape[:2]
                    if (w, h) != (self.target_width, self.target_height):
                        frame_rgb = cv2.resize(frame_rgb, (self.target_width, self.target_height), 
                                             interpolation=self.resize_method)
                    
                    # Convert RGB to BGR for OpenCV compatibility
                    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                    return True, frame_bgr
                except Exception as e:
                    print(f"[ERROR] PiCameraWrapper.read() failed: {e}", file=sys.stderr)
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
        return PiCameraWrapper(picam2, settings.width, settings.height)
        
    except ImportError:
        print("[DEBUG] picamera2 not installed, trying fallback methods", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[DEBUG] picamera2 failed: {e}", file=sys.stderr)
        return None


def open_camera():
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
        profile = "WINDOWS_STABLE" if os.name == "nt" else "RASPBERRY_PI"

    camera_index = settings.index
    
    # Priority 1: Try picamera2 for Raspberry Pi
    if profile == "RASPBERRY_PI":
        cap = _try_picamera2()
        if cap is not None:
            return cap
        print("[ERROR] picamera2 is required on Raspberry Pi. No fallback enabled.", file=sys.stderr)
        return None
    
    # Priority 2: Try OpenCV backends
    if profile == "WINDOWS_STABLE":
        attempts = [
            (camera_index, cv2.CAP_DSHOW),
            (1 - camera_index, cv2.CAP_DSHOW),
        ]
    else:
        attempts = [
            (camera_index, cv2.CAP_V4L2),
            (1 - camera_index, cv2.CAP_V4L2),
            (camera_index, None),
        ]

    for index, backend in attempts:
        cap = cv2.VideoCapture(index) if backend is None else cv2.VideoCapture(index, backend)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)
            cap.set(cv2.CAP_PROP_FPS, settings.fps)
            return cap
        cap.release()
    
    print("[ERROR] Could not open camera", file=sys.stderr)
    print("[FIX] Install picamera2: sudo apt install python3-picamera2", file=sys.stderr)
    return None
