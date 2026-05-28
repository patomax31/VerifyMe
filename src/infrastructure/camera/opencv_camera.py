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
        
        # Debug: Get camera capabilities
        try:
            full_res = picam2.camera_properties.get("PixelArraySize")
            print(f"[DEBUG] Full sensor resolution: {full_res}", file=sys.stderr)
        except Exception as e:
            print(f"[DEBUG] Could not get sensor resolution: {e}", file=sys.stderr)
            full_res = None
        
        # Strategy: Request FULL sensor resolution to avoid ISP crop/zoom
        # Then resize in software to the desired output resolution
        capture_width = settings.width
        capture_height = settings.height
        
        if full_res and len(full_res) >= 2:
            # Use full sensor for maximum FOV, avoid internal cropping
            capture_width = full_res[0]
            capture_height = full_res[1]
            print(f"[DEBUG] Will capture at full sensor: {capture_width}x{capture_height}, then resize to {settings.width}x{settings.height}", 
                file=sys.stderr)
        
        # Create configuration with full resolution to avoid ISP crop
        config = picam2.create_preview_configuration(
            main={"size": (capture_width, capture_height), "format": "RGB888"},
            lores=None,  # No low-res stream
            raw=None     # No raw stream
        )
        
        # Remove any ISP transformations
        if "scaler" in config:
            del config["scaler"]
        if "crop" in config:
            del config["crop"]
        
        picam2.configure(config)
        
        # Optimize exposure for better brightness (full sensor capture needs more light)
        try:
            picam2.set_controls({
                "ExposureTime": 30000,    # 30ms exposure time for better brightness
                "AnalogueGain": 4.0,      # 4x gain to compensate for full sensor capture
                "AwbMode": 1,             # Auto white balance
            })
            print("[DEBUG] Camera exposure optimized for full sensor capture", file=sys.stderr)
        except Exception as e:
            print(f"[DEBUG] Could not set all camera controls: {e}", file=sys.stderr)
            try:
                picam2.set_controls({
                    "AnalogueGain": 2.0,
                })
            except Exception:
                pass
        
        picam2.start()
        
        # Wrapper to provide OpenCV-compatible interface
        class PiCameraWrapper:
            def __init__(self, camera, target_width, target_height):
                self.camera = camera
                self.is_open = True
                self.target_width = target_width
                self.target_height = target_height
                self.frame_count = 0
            
            def read(self):
                try:
                    frame_rgb = self.camera.capture_array()
                    if frame_rgb is None or frame_rgb.size == 0:
                        return False, None
                    
                    # Log actual resolution on first frames for debugging
                    if self.frame_count < 1:
                        h, w = frame_rgb.shape[:2]
                        print(f"[DEBUG] First frame: {w}x{h}, will resize to {self.target_width}x{self.target_height}", 
                            file=sys.stderr)
                        self.frame_count = 1
                    
                    # Resize to target dimensions
                    h, w = frame_rgb.shape[:2]
                    if (w, h) != (self.target_width, self.target_height):
                        frame_rgb = cv2.resize(frame_rgb, (self.target_width, self.target_height), 
                                            interpolation=cv2.INTER_AREA)
                    
                    # Convert RGB to BGR for OpenCV compatibility
                    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                    return True, frame_bgr
                except Exception as e:
                    if self.frame_count == 0:
                        print(f"[ERROR] First frame failed: {e}", file=sys.stderr)
                    self.frame_count = -1
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
