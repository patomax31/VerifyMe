from .ports import AuthRepositoryPort


class AuthService:
    def __init__(self, repository: AuthRepositoryPort) -> None:
        self.repository = repository

    def initialize(self) -> None:
        self.repository.initialize()

    def load_known_students(self):
        return self.repository.load_active_student_biometrics()

    def log_access(self, student_id: int, granted: bool) -> None:
        self.repository.log_student_access(student_id, granted)
