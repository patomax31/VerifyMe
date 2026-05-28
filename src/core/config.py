import os


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


class RecognitionSettings:
    def __init__(self) -> None:
        self.scale = _get_env_float("RECOGNITION_SCALE", 0.5)
        self.tolerance = _get_env_float("RECOGNITION_TOLERANCE", 0.5)
        self.access_cooldown_seconds = _get_env_float("ACCESS_COOLDOWN_SECONDS", 8.0)


def get_camera_settings() -> CameraSettings:
    return CameraSettings()


def get_recognition_settings() -> RecognitionSettings:
    return RecognitionSettings()
