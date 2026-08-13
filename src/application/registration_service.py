from .ports import RegistrationRepositoryPort


class RegistrationService:
    def __init__(self, repository: RegistrationRepositoryPort) -> None:
        self.repository = repository

    def initialize(self) -> None:
        self.repository.initialize()

    def register_student_with_encoding(
        self,
        nombre: str,
        grado: int,
        letra: str,
        turno: str,
        encoding,
        *,
        encoding_izquierdo=None,
        encoding_derecho=None,
        foto_jpeg_bytes=None,
    ) -> int:
        student_id = self.repository.create_student(nombre, grado, letra, turno)
        self.repository.save_student_biometric(
            student_id,
            encoding,
            encoding_izquierdo=encoding_izquierdo,
            encoding_derecho=encoding_derecho,
            foto_jpeg_bytes=foto_jpeg_bytes,
        )
        return student_id
