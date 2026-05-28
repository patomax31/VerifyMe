"""Prueba de modelo de deteccion y reconocimiento facial en tiempo real.

Este modulo esta pensado para pruebas locales y en Raspberry Pi.
- Usa OpenCV para camara y dibujo.
- Usa face_recognition para deteccion/encoding/matching.
- Carga rostros conocidos desde SQLite (si existe) o desde data/*.pkl.
"""

from __future__ import annotations

import os
import pickle
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
from src.infrastructure.camera.opencv_camera import open_camera as open_opencv_camera

try:
    import face_recognition
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "face_recognition no esta instalado. Instala dependencias antes de usar face_model.py"
    ) from exc

try:
    import tkinter as tk
except Exception:
    tk = None


@dataclass
class KnownFace:
    name: str
    encoding: List[float]


class FaceModelTester:
    """Ejecuta prueba de camara con deteccion/reconocimiento facial."""

    def __init__(self, tolerance: float = 0.5, scale: float = 0.25) -> None:
        self.tolerance = tolerance
        self.scale = scale
        self.known_names: List[str] = []
        self.known_encodings: List[List[float]] = []

    def _to_full_scale_box(self, box: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        inv_scale = int(1 / self.scale)
        top, right, bottom, left = box
        return top * inv_scale, right * inv_scale, bottom * inv_scale, left * inv_scale

    def is_face_well_positioned(
        self,
        frame_shape,
        face_location: Tuple[int, int, int, int],
    ) -> bool:
        """Evalua si el rostro detectado esta dentro de una zona guiada tipo ovalo."""
        full_top, full_right, full_bottom, full_left = self._to_full_scale_box(face_location)

        height, width = frame_shape[:2]
        cx = (full_left + full_right) / 2.0
        cy = (full_top + full_bottom) / 2.0

        oval_rx = width * 0.25
        oval_ry = height * 0.4
        oval_cx = width / 2.0
        oval_cy = height / 2.0

        # Ecuacion de elipse para comprobar que el centro facial quede dentro de la guia.
        normalized = ((cx - oval_cx) ** 2) / (oval_rx ** 2) + ((cy - oval_cy) ** 2) / (oval_ry ** 2)
        return normalized <= 1.0

    def load_known_faces(self) -> None:
        """Carga rostros conocidos desde SQLite y fallback a data/*.pkl."""
        names: List[str] = []
        encodings: List[List[float]] = []

        # Intento 1: SQLite manager del proyecto
        try:
            from database.sqlite_manager import load_student_biometrics

            db_encodings, db_names, _ids = load_student_biometrics()
            if db_encodings and db_names:
                encodings.extend(db_encodings)
                names.extend(db_names)
        except Exception as exc:
            print(f"[face_model] SQLite no disponible o sin datos: {exc}")

        # Intento 2: archivos PKL
        if not names:
            data_dir = "data"
            if os.path.isdir(data_dir):
                for filename in sorted(os.listdir(data_dir)):
                    if not filename.endswith(".pkl"):
                        continue
                    path = os.path.join(data_dir, filename)
                    try:
                        with open(path, "rb") as fh:
                            enc = pickle.load(fh)
                        encodings.append(enc)
                        names.append(filename.replace(".pkl", ""))
                    except Exception as exc:
                        print(f"[face_model] Error leyendo {path}: {exc}")

        self.known_names = names
        self.known_encodings = encodings
        print(f"[face_model] Rostros conocidos cargados: {len(self.known_names)}")

    def open_camera(self, camera_index: int = 0) -> Optional[cv2.VideoCapture]:
        """Abre la cámara delegando en la implementación de `opencv_camera.open_camera`.

        Acepta `camera_index` para pruebas locales.
        """
        try:
            return open_opencv_camera(camera_index=camera_index)
        except Exception as exc:
            print(f"[face_model] Error abriendo la camara: {exc}")
            return None

    def process_frame(self, frame) -> Tuple[List[Tuple[int, int, int, int]], List[str]]:
        """Detecta rostros y retorna labels por cada rostro detectado."""
        small_frame = cv2.resize(frame, (0, 0), fx=self.scale, fy=self.scale)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        labels: List[str] = []
        for encoding in face_encodings:
            name = "Desconocido"
            if self.known_encodings:
                matches = face_recognition.compare_faces(
                    self.known_encodings,
                    encoding,
                    tolerance=self.tolerance,
                )
                if True in matches:
                    idx = matches.index(True)
                    name = self.known_names[idx]
            labels.append(name)

        return face_locations, labels

    def draw_results(self, frame, face_locations, labels) -> None:
        """Dibuja bounding boxes y nombre detectado."""
        inv_scale = int(1 / self.scale)

        for (top, right, bottom, left), name in zip(face_locations, labels):
            top *= inv_scale
            right *= inv_scale
            bottom *= inv_scale
            left *= inv_scale

            color = (0, 180, 0) if name != "Desconocido" else (0, 0, 220)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 24), (right, bottom), color, cv2.FILLED)
            cv2.putText(
                frame,
                name,
                (left + 6, bottom - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )


class PopupBridge:
    """Adaptador para usar MessagePopup desde el loop de OpenCV sin bloquear."""

    def __init__(self) -> None:
        self.enabled = False
        self.popup = None
        self.root = None

        has_graphical_session = bool(os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))
        if tk is None or (os.name != "nt" and not has_graphical_session):
            return

        try:
            from UI.message_popup import MessagePopup

            self.root = tk.Tk()
            self.root.withdraw()
            self.popup = MessagePopup(self.root)
            self.enabled = True
        except Exception as exc:
            print(f"[face_model] Popup no disponible, se usara consola: {exc}")
            self.enabled = False

    def show(self, message: str, duration_ms: int = 5000) -> None:
        if self.enabled and self.popup is not None:
            self.popup.show(message, duration_ms=duration_ms)
            return
        print(f"[face_model] {message}")

    def pump(self) -> None:
        if self.enabled and self.root is not None:
            try:
                self.root.update_idletasks()
                self.root.update()
            except Exception:
                pass

    def close(self) -> None:
        if self.enabled and self.root is not None:
            try:
                self.root.destroy()
            except Exception:
                pass


def run_test_camera(camera_index: int = 0) -> None:
    """Ejecuta la prueba de camara de forma independiente.

    Tecla q o ESC para salir.
    """
    tester = FaceModelTester(
        tolerance=float(os.getenv("RECOGNITION_TOLERANCE", "0.5")),
        scale=float(os.getenv("RECOGNITION_SCALE", "0.25")),
    )
    tester.load_known_faces()

    cap = tester.open_camera(camera_index=camera_index)
    if cap is None:
        print("[face_model] No se pudo abrir la camara.")
        return

    print("[face_model] Prueba iniciada. Presiona q o ESC para salir.")
    prev_t = time.time()
    popup = PopupBridge()
    last_popup_time = 0.0
    popup_cooldown = 2.5
    no_face_timeout_seconds = 10.0
    no_face_since = time.time()
    popup.show("Iniciando camara...", duration_ms=2500)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[face_model] Frame invalido, cerrando prueba.")
                break

            popup.pump()

            locations, labels = tester.process_frame(frame)
            tester.draw_results(frame, locations, labels)

            if len(locations) == 0:
                if time.time() - no_face_since >= no_face_timeout_seconds:
                    now_t = time.time()
                    if now_t - last_popup_time >= popup_cooldown:
                        popup.show("No se detecta rostro desde hace 10 segundos", duration_ms=5000)
                        last_popup_time = now_t
                    no_face_since = now_t
            else:
                no_face_since = time.time()

            # Aviso de posicionamiento: un rostro fuera de la zona guiada.
            if len(locations) == 1 and not tester.is_face_well_positioned(frame.shape, locations[0]):
                now_t = time.time()
                if now_t - last_popup_time >= popup_cooldown:
                    popup.show("Ajusta tu rostro dentro del ovalo para continuar", duration_ms=5000)
                    last_popup_time = now_t
            elif len(locations) > 1:
                now_t = time.time()
                if now_t - last_popup_time >= popup_cooldown:
                    popup.show("Solo una persona frente a camara", duration_ms=5000)
                    last_popup_time = now_t

            now = time.time()
            fps = 1.0 / (now - prev_t) if now > prev_t else 0.0
            prev_t = now
            cv2.putText(
                frame,
                f"FPS: {fps:.1f} | Rostros: {len(locations)}",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow("Face Model Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break
    finally:
        popup.close()
        cap.release()
        cv2.destroyAllWindows()
        print("[face_model] Prueba finalizada.")


if __name__ == "__main__":
    run_test_camera()
