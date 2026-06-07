"""Detección de parpadeo con landmarks (EAR) y baseline adaptativo por persona."""

from __future__ import annotations

import math
import os
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import cv2
import face_recognition

CALIBRATION_SAMPLES = 5

if not hasattr(face_recognition, "face_locations"):
    origin = getattr(face_recognition, "__file__", None) or getattr(face_recognition, "__path__", None)
    raise RuntimeError(
        "Invalid face_recognition module. Expected the face_recognition package with face_locations. "
        f"Loaded from: {origin}"
    )


def _dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _eye_aspect_ratio(eye: List[Tuple[float, float]]) -> float:
    """EAR clásico para 6 puntos del ojo (orden dlib / face_recognition)."""
    if len(eye) < 6:
        return 0.28
    v1 = _dist(eye[1], eye[5])
    v2 = _dist(eye[2], eye[4])
    h = _dist(eye[0], eye[3])
    if h < 1e-6:
        return 0.28
    return (v1 + v2) / (2.0 * h)


def mean_ear_from_landmarks(landmarks: Dict[str, Any]) -> Optional[float]:
    left = landmarks.get("left_eye") or []
    right = landmarks.get("right_eye") or []
    if len(left) < 6 or len(right) < 6:
        return None
    return (_eye_aspect_ratio(left) + _eye_aspect_ratio(right)) / 2.0


def _resize_long_edge(frame_bgr: Any, max_side: int = 720) -> Any:
    h, w = frame_bgr.shape[:2]
    m = max(h, w)
    if m <= max_side:
        return frame_bgr
    s = max_side / float(m)
    return cv2.resize(frame_bgr, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)


def _normalized_face_box(loc: Tuple[int, int, int, int], width: int, height: int) -> Dict[str, float]:
    top, right, bottom, left = loc
    return {
        "x": max(0.0, min(1.0, left / float(width))),
        "y": max(0.0, min(1.0, top / float(height))),
        "width": max(0.0, min(1.0, (right - left) / float(width))),
        "height": max(0.0, min(1.0, (bottom - top) / float(height))),
    }


def _haar_face_box_from_frame_bgr(frame_bgr: Any) -> Optional[Dict[str, float]]:
    cascade_path = getattr(cv2, "data", None)
    if cascade_path is None:
        return None
    xml_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(xml_path)
    if detector.empty():
        return None

    small = _resize_long_edge(frame_bgr, 720)
    h, w = small.shape[:2]
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=3,
        minSize=(32, 32),
    )
    if len(faces) < 1:
        return None
    x, y, fw, fh = max(faces, key=lambda item: item[2] * item[3])
    return {
        "x": max(0.0, min(1.0, x / float(w))),
        "y": max(0.0, min(1.0, y / float(h))),
        "width": max(0.0, min(1.0, fw / float(w))),
        "height": max(0.0, min(1.0, fh / float(h))),
    }


def ear_from_frame_bgr(frame_bgr: Any) -> Optional[float]:
    """EAR promedio con un solo rostro; redimensiona para fluidez y usa upsample HOG."""
    ear, _ = ear_and_face_box_from_frame_bgr(frame_bgr)
    return ear


def ear_and_face_box_from_frame_bgr(frame_bgr: Any) -> Tuple[Optional[float], Optional[Dict[str, float]]]:
    """EAR promedio y caja normalizada de un solo rostro."""
    small = _resize_long_edge(frame_bgr, 720)
    h, w = small.shape[:2]
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    locs = face_recognition.face_locations(rgb, number_of_times_to_upsample=1, model="hog")
    if len(locs) != 1:
        return None, _haar_face_box_from_frame_bgr(frame_bgr)
    face_box = _normalized_face_box(locs[0], w, h)
    marks = face_recognition.face_landmarks(rgb, locs)
    if not marks:
        return None, face_box
    return mean_ear_from_landmarks(marks[0]), face_box


@dataclass
class BlinkSessionState:
    created: float = field(default_factory=time.monotonic)
    verified: bool = False
    verified_until: float = 0.0

    ear_hist: List[float] = field(default_factory=list)
    baseline: Optional[float] = None

    low_streak: int = 0
    in_blink: bool = False
    blinks: int = 0
    fallback_face_since: Optional[float] = None
    fallback_face_score: int = 0

    def push_ear(self, ear: Optional[float]) -> str:
        """
        Baseline = mediana de ojos "abiertos" al inicio; parpadeo = caída relativa + reapertura.
        Más tolerante que umbrales fijos para distancias y formas de ojo distintas.
        """
        if ear is None:
            return "no_face"

        self.ear_hist.append(float(ear))
        if len(self.ear_hist) > 48:
            self.ear_hist.pop(0)

        if self.baseline is None:
            if len(self.ear_hist) < CALIBRATION_SAMPLES:
                return "tracking"
            chunk = self.ear_hist[-10:]
            med = statistics.median(chunk)
            upper = [x for x in chunk if x >= med * 0.92]
            base = statistics.mean(upper) if upper else med
            self.baseline = max(0.14, min(0.55, float(base)))
            return "tracking"

        b = self.baseline
        # Cierre: por debajo de una fracción del baseline o caída absoluta clara
        closed = ear < b * 0.58 or ear < b - 0.055
        if closed:
            self.low_streak += 1
        else:
            self.low_streak = 0

        if not self.in_blink and self.low_streak >= 2:
            self.in_blink = True

        # Reapertura: vuelve cerca del baseline (más laxo que el umbral "abierto" inicial fijo)
        reopened = ear >= b * 0.87
        if self.in_blink and reopened and self.low_streak == 0:
            self.blinks += 1
            self.in_blink = False
            if self.blinks >= 1:
                self.verified = True
                self.verified_until = time.monotonic() + 22.0
                return "ready"

        if not self.in_blink:
            return "need_blink"
        return "need_blink"

    def is_verification_valid(self) -> bool:
        return self.verified and time.monotonic() <= self.verified_until


_LIVENESS: Dict[str, BlinkSessionState] = {}
_LAST_DEBUG_LOG = 0.0


def cleanup_liveness_sessions(max_age: float = 180.0) -> None:
    now = time.monotonic()
    dead = [sid for sid, st in _LIVENESS.items() if now - st.created > max_age]
    for sid in dead:
        _LIVENESS.pop(sid, None)


def start_liveness_session() -> str:
    import secrets

    cleanup_liveness_sessions()
    sid = secrets.token_urlsafe(12)
    _LIVENESS[sid] = BlinkSessionState()
    return sid


def push_liveness_frame(session_id: str, frame_bgr: Any) -> Tuple[str, str, Optional[Dict[str, float]]]:
    """
    Procesa un frame. Devuelve (estado, mensaje_ui).
    estado: no_face | tracking | need_blink | ready
    """
    cleanup_liveness_sessions()
    st = _LIVENESS.get(session_id)
    if st is None:
        return "error", "Sesión de liveness inválida. Reinicia la cámara.", None

    global _LAST_DEBUG_LOG
    ear, face_box = ear_and_face_box_from_frame_bgr(frame_bgr)
    now = time.monotonic()
    allow_face_fallback = os.getenv("LIVENESS_ALLOW_FACE_FALLBACK", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
        "si",
    }
    if face_box and allow_face_fallback:
        if st.fallback_face_since is None:
            st.fallback_face_since = now
        st.fallback_face_score = min(8, st.fallback_face_score + 1)
    else:
        st.fallback_face_since = None
        st.fallback_face_score = max(0, st.fallback_face_score - 1)

    if ear is None and face_box and allow_face_fallback:
        if st.fallback_face_score >= 3:
            st.verified = True
            st.verified_until = now + 22.0
            state = "ready"
        else:
            state = "tracking"
    else:
        state = st.push_ear(ear)
        if (
            face_box
            and allow_face_fallback
            and state in {"tracking", "need_blink"}
            and st.fallback_face_since is not None
            and st.fallback_face_score >= 4
        ):
            st.verified = True
            st.verified_until = now + 22.0
            state = "ready"
    if now - _LAST_DEBUG_LOG >= 1.0:
        if os.getenv("LIVENESS_DEBUG_FRAME", "0").strip().lower() in {"1", "true", "yes", "on", "si"}:
            try:
                cv2.imwrite("/tmp/verifyme-liveness-frame.jpg", frame_bgr)
            except Exception:
                pass
        print(
            f"[LIVENESS] state={state} ear={ear if ear is not None else 'None'} "
            f"face_box={'yes' if face_box else 'no'}",
            flush=True,
        )
        _LAST_DEBUG_LOG = now
    if state == "no_face":
        if face_box:
            return "no_face", "Rostro detectado. Acércate, mira de frente y mejora la luz.", face_box
        return "no_face", "Coloca un rostro frente a la cámara.", face_box
    if state == "tracking":
        if ear is None:
            return "tracking", "Rostro detectado. Mira de frente a la cámara.", face_box
        progress = min(CALIBRATION_SAMPLES, len(st.ear_hist))
        return "tracking", f"Rostro detectado. Calibrando ojos ({progress}/{CALIBRATION_SAMPLES})...", face_box
    if state == "need_blink":
        return "need_blink", "Parpadea una vez de forma natural (sin taparte la cara).", face_box
    if state == "ready":
        return "ready", "Listo. Identificando…", face_box
    return "need_blink", "Parpadea una vez de forma natural (sin taparte la cara).", face_box


def liveness_session_ready(session_id: str) -> bool:
    st = _LIVENESS.get(session_id)
    if st is None:
        return False
    return st.is_verification_valid()
