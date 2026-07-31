from typing import List, Optional, Protocol, Tuple


class AuthRepositoryPort(Protocol):
    def initialize(self) -> None:
        ...

    def load_active_student_biometrics(self) -> Tuple[List, List[str], List[int]]:
        ...

    def log_student_access(self, id_estudiante: int, acceso_concedido: bool) -> None:
        ...


class PklBiometricRepositoryPort(Protocol):
    def load_student_biometrics(self) -> Tuple[List, List[str], List[int]]:
        ...

    def save_student_biometric(self, id_estudiante: int, encoding) -> None:
        ...


class FaceMatcherPort(Protocol):
    def find_first_match(self, known_encodings, candidate_encoding, tolerance: float) -> int:
        ...


class RegistrationRepositoryPort(Protocol):
    def initialize(self) -> None:
        ...

    def create_student(self, nombre: str, grado: int, letra: str, turno: str) -> int:
        ...

    def save_student_biometric(
        self,
        id_estudiante: int,
        encoding,
        *,
        encoding_izquierdo=None,
        encoding_derecho=None,
        foto_jpeg_bytes: Optional[bytes] = None,
    ) -> None:
        ...


class RegistrationResultPort(Protocol):
    success: bool
    message: str
    student_id: Optional[int]
