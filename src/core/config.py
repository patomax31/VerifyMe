import os
import platform


def _get_env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class CameraSettings:
    def __init__(self) -> None:
        self.index = int(os.getenv("CAMERA_INDEX", "0"))
        self.profile = os.getenv("CAMERA_PROFILE", "AUTO").strip().upper()
        self.width = int(os.getenv("CAMERA_WIDTH", "640"))
        self.height = int(os.getenv("CAMERA_HEIGHT", "480"))
        self.fps = int(os.getenv("CAMERA_FPS", "60"))
        self.rotate = int(os.getenv("CAMERA_ROTATE", "0"))
        self.flip_horizontal = os.getenv("CAMERA_FLIP_HORIZONTAL", "0").strip().lower() in {"1", "true", "yes", "on"}
        self.flip_vertical = os.getenv("CAMERA_FLIP_VERTICAL", "0").strip().lower() in {"1", "true", "yes", "on"}
        self.picamera_format = os.getenv("PICAMERA_FORMAT", "BGR888").strip().upper()
        self.swap_rb = os.getenv("CAMERA_SWAP_RB", "0").strip().lower() in {"1", "true", "yes", "on"}


class RecognitionSettings:
    def __init__(self) -> None:
        self.scale = _get_env_float("RECOGNITION_SCALE", 0.25)
        self.tolerance = _get_env_float("RECOGNITION_TOLERANCE", 0.5)
        self.access_cooldown_seconds = _get_env_float("ACCESS_COOLDOWN_SECONDS", 8.0)


def get_camera_settings() -> CameraSettings:
    return CameraSettings()


def get_recognition_settings() -> RecognitionSettings:
    return RecognitionSettings()


def is_raspberry_pi() -> bool:
    """Detecta si la ejecución es sobre una Raspberry Pi.

    Intenta usar la arquitectura y el contenido de /proc/device-tree/model
    como heurística. Devuelve True ante dudas en máquinas ARM.
    """
    try:
        arch = platform.machine().lower()
        if "arm" in arch or "aarch" in arch:
            try:
                with open("/proc/device-tree/model", "r") as fh:
                    model = fh.read().lower()
                    return "raspberry" in model
            except Exception:
                # No podemos leer el modelo, pero la arquitectura es ARM: asumir Raspberry
                return True
    except Exception:
        pass
    return False
