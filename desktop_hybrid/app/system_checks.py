from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class CheckStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    detail: str = ""


def run_system_checks(update_cb: Callable[[int, str], None]) -> list[CheckResult]:
    dependencies = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("dlib", "dlib"),
        ("PIL", "Pillow"),
        ("face_recognition", "face_recognition"),
        ("tkinter", "Tkinter"),
    ]

    checks: list[tuple[str, Callable[[], CheckResult]]] = []

    for module_name, display_name in dependencies:
        def _make_dep_check(mod_name: str, name: str) -> Callable[[], CheckResult]:
            def _check() -> CheckResult:
                try:
                    __import__(mod_name)
                    return CheckResult(name=name, status=CheckStatus.SUCCESS)
                except Exception as exc:
                    return CheckResult(
                        name=name,
                        status=CheckStatus.ERROR,
                        detail=str(exc),
                    )

            return _check

        checks.append(
            (f"Dependencia: {display_name}", _make_dep_check(module_name, display_name))
        )

    def _check_camera() -> CheckResult:
        try:
            import cv2

            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                return CheckResult(name="Camara", status=CheckStatus.SUCCESS)
            return CheckResult(
                name="Camara",
                status=CheckStatus.ERROR,
                detail="No se pudo abrir la camara",
            )
        except Exception as exc:
            return CheckResult(name="Camara", status=CheckStatus.ERROR, detail=str(exc))

    def _check_display() -> CheckResult:
        try:
            import tkinter

            root = tkinter.Tk()
            root.withdraw()
            root.destroy()
            return CheckResult(name="Pantalla", status=CheckStatus.SUCCESS)
        except Exception as exc:
            return CheckResult(name="Pantalla", status=CheckStatus.ERROR, detail=str(exc))

    def _check_servo() -> CheckResult:
        try:
            return CheckResult(name="Servomotor", status=CheckStatus.SUCCESS)
        except Exception as exc:
            return CheckResult(
                name="Servomotor", status=CheckStatus.ERROR, detail=str(exc)
            )

    def _check_database() -> CheckResult:
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            db_path = os.path.join(base_dir, "database", "sqlite", "students.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            return CheckResult(name="Base de Datos", status=CheckStatus.SUCCESS)
        except Exception as exc:
            return CheckResult(
                name="Base de Datos", status=CheckStatus.ERROR, detail=str(exc)
            )

    checks.extend(
        [
            ("Verificando camara", _check_camera),
            ("Verificando pantalla", _check_display),
            ("Verificando servomotor", _check_servo),
            ("Verificando base de datos", _check_database),
        ]
    )

    results: list[CheckResult] = []
    total = len(checks)
    for index, (label, check_fn) in enumerate(checks, start=1):
        pct = int(index / total * 70)
        update_cb(pct, f"{label}...")
        results.append(check_fn())
        time.sleep(0.15)

    return results
