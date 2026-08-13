from dataclasses import dataclass
from time import monotonic
from typing import Dict, List, Optional, Tuple

import face_recognition
import numpy as np

from src.application.auth_service import AuthService
from .ports import FaceMatcherPort, PklBiometricRepositoryPort


def _is_face_encoding_vector(value: object) -> bool:
    return isinstance(value, np.ndarray) and value.ndim == 1 and value.shape[0] == 128


@dataclass
class LoginFrameResult:
    message: str
    color: Tuple[int, int, int]
    match_index: Optional[int] = None


class LoginUseCase:
    def __init__(
        self,
        auth_service: AuthService,
        matcher: FaceMatcherPort,
        pkl_repository: Optional[PklBiometricRepositoryPort] = None,
        tolerance: float = 0.5,
        cooldown_seconds: float = 8.0,
    ) -> None:
        self.auth_service = auth_service
        self.matcher = matcher
        self.pkl_repository = pkl_repository
        self.tolerance = tolerance
        self.cooldown_seconds = cooldown_seconds
        self._last_logged_by_student_id: Dict[int, float] = {}

    def initialize(self) -> None:
        self.auth_service.initialize()

    def load_known_students(self):
        known_encodings, known_labels, known_ids = self.auth_service.load_known_students()
        if known_encodings:
            return known_encodings, known_labels, known_ids

        if self.pkl_repository is None:
            return known_encodings, known_labels, known_ids

        pkl_encodings, pkl_labels, pkl_ids = self.pkl_repository.load_student_biometrics()
        if not pkl_ids:
            pkl_ids = [0] * len(pkl_labels)
        return pkl_encodings, pkl_labels, pkl_ids

    def process_frame(
        self,
        encodings,
        known_encodings: List,
        known_labels: List[str],
        known_ids: List[int],
        *,
        tolerance: Optional[float] = None,
    ) -> LoginFrameResult:
        tol = self.tolerance if tolerance is None else float(tolerance)
        message = "ESPERANDO ROSTRO..."
        color = (255, 255, 255)
        match_index: Optional[int] = None

        for face_encoding in encodings:
            idx = -1
            if known_encodings and _is_face_encoding_vector(face_encoding) and all(
                _is_face_encoding_vector(k) for k in known_encodings
            ):
                best_i = -1
                best_d = tol + 1.0
                for i, k in enumerate(known_encodings):
                    d = float(face_recognition.face_distance([k], face_encoding)[0])
                    if d < best_d:
                        best_d = d
                        best_i = i
                if best_i >= 0 and best_d <= tol:
                    idx = best_i
            else:
                idx = self.matcher.find_first_match(known_encodings, face_encoding, tolerance=tol)

            if idx >= 0:
                student_label = known_labels[idx].upper()
                message = f"ACCESO CONCEDIDO: {student_label}"
                color = (0, 255, 0)
                match_index = idx
                self._log_access_with_cooldown(idx, known_ids)
            else:
                message = "ACCESO DENEGADO"
                color = (0, 0, 255)

        return LoginFrameResult(message=message, color=color, match_index=match_index)

    def _log_access_with_cooldown(self, idx: int, known_ids: List[int]) -> None:
        if idx >= len(known_ids):
            return

        student_id = known_ids[idx]
        if student_id <= 0:
            return

        now = monotonic()
        last = self._last_logged_by_student_id.get(student_id, 0.0)
        if now - last < self.cooldown_seconds:
            return

        self.auth_service.log_access(student_id, True)
        self._last_logged_by_student_id[student_id] = now
