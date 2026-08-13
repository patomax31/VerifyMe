from dataclasses import dataclass
from typing import Optional

from src.application.registration_service import RegistrationService
from .ports import PklBiometricRepositoryPort


@dataclass
class RegistrationResult:
    success: bool
    message: str
    student_id: Optional[int] = None


class RegistrationUseCase:
    def __init__(
        self,
        registration_service: RegistrationService,
        pkl_repository: PklBiometricRepositoryPort,
    ) -> None:
        self.registration_service = registration_service
        self.pkl_repository = pkl_repository

    def initialize(self) -> None:
        self.registration_service.initialize()

    def register_from_detected_faces(self, nombre: str, grado: int, letra: str, turno: str, encodings) -> RegistrationResult:
        if len(encodings) == 0:
            return RegistrationResult(
                success=False,
                message="Error: No se detecto ningun rostro. Intenta de nuevo.",
            )

        if len(encodings) > 1:
            return RegistrationResult(
                success=False,
                message="Error: Se detectaron multiples rostros. Debe haber solo uno.",
            )

        encoding = encodings[0]
        try:
            student_id = self.registration_service.register_student_with_encoding(nombre, grado, letra, turno, encoding)
        except ValueError as exc:
            return RegistrationResult(
                success=False,
                message=str(exc),
            )

        self.pkl_repository.save_student_biometric(student_id, encoding)

        return RegistrationResult(
            success=True,
            student_id=student_id,
            message=f"Registro exitoso. {nombre} #{student_id} ({grado}{letra}-{turno}).",
        )

    def register_from_three_encodings(
        self,
        nombre: str,
        grado: int,
        letra: str,
        turno: str,
        enc_front,
        enc_left,
        enc_right,
        foto_jpeg_bytes: bytes,
    ) -> RegistrationResult:
        try:
            student_id = self.registration_service.register_student_with_encoding(
                nombre,
                grado,
                letra,
                turno,
                enc_front,
                encoding_izquierdo=enc_left,
                encoding_derecho=enc_right,
                foto_jpeg_bytes=foto_jpeg_bytes,
            )
        except ValueError as exc:
            return RegistrationResult(success=False, message=str(exc), student_id=None)

        self.pkl_repository.save_student_biometric(student_id, enc_front)

        return RegistrationResult(
            success=True,
            student_id=student_id,
            message=f"Registro exitoso (3 ángulos + foto). {nombre} #{student_id} ({grado}{letra}-{turno}).",
        )
