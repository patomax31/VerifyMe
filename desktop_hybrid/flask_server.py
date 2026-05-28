from __future__ import annotations

import base64
import re
import sqlite3
import sys
import threading
import time
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, Response, jsonify, render_template, request, send_file, send_from_directory
from werkzeug.security import generate_password_hash

from deep_translator import GoogleTranslator

try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

ADMIN_PANEL_DIR = PROJECT_DIR / "admin_panel"
ADMIN_PANEL_DIST_DIR = ADMIN_PANEL_DIR / "dist"

from database.sqlite.access import close_access_session, get_active_session, start_access_session
from database.sqlite.connection import connect
from database.sqlite.migrations import initialize_database
from database.sqlite.reporting import (
    list_access_logs_detailed,
    list_access_logs_for_active_session,
)
from src.application.auth_service import AuthService
from src.application.login_use_case import LoginUseCase
from src.application.registration_service import RegistrationService
from src.application.registration_use_case import RegistrationUseCase
from src.core.config import RecognitionSettings, get_recognition_settings
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.pkl_repository import PklRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.hardware.hardware_integration import HardwareIntegration
from src.hardware import servomotor

RUNTIME_ERROR = None
try:
    from src.infrastructure.recognition.face_engine import (
        detect_face_encodings_from_frame,
        detect_face_encodings_from_frame_robust,
        extract_login_face_encoding,
    )
    from src.infrastructure.recognition.matcher_adapter import FaceMatcherAdapter
    from src.infrastructure.recognition.blink_liveness import (
        liveness_session_ready,
        push_liveness_frame,
        start_liveness_session,
    )
except Exception as exc:
    detect_face_encodings_from_frame = None
    detect_face_encodings_from_frame_robust = None
    extract_login_face_encoding = None
    FaceMatcherAdapter = None
    start_liveness_session = None
    push_liveness_frame = None
    liveness_session_ready = None
    RUNTIME_ERROR = str(exc)


class WebFaceEngine:
    def __init__(self, recognition_settings: RecognitionSettings) -> None:
        if RUNTIME_ERROR is not None:
            raise RuntimeError(RUNTIME_ERROR)
        if FaceMatcherAdapter is None:
            raise RuntimeError("Dependencias de reconocimiento no disponibles.")

        self.recognition_settings = recognition_settings
        self.login_use_case = LoginUseCase(
            auth_service=AuthService(SQLiteRepository()),
            matcher=FaceMatcherAdapter(),
            pkl_repository=PklRepository(),
            tolerance=recognition_settings.tolerance,
            cooldown_seconds=recognition_settings.access_cooldown_seconds,
        )
        self.login_use_case.initialize()

        self.registration_use_case = RegistrationUseCase(
            registration_service=RegistrationService(SQLiteRepository()),
            pkl_repository=PklRepository(),
        )
        self.registration_use_case.initialize()

        self.known_encodings = []
        self.known_labels = []
        self.known_ids = []
        self.refresh_known_students()

    def refresh_known_students(self) -> None:
        encodings, labels, ids = self.login_use_case.load_known_students()
        self.known_encodings = encodings
        self.known_labels = labels
        self.known_ids = ids

    def apply_model_config(self, scale: float, tolerance: float, cooldown_seconds: float) -> None:
        self.recognition_settings.scale = scale
        self.recognition_settings.tolerance = tolerance
        self.recognition_settings.access_cooldown_seconds = cooldown_seconds

        self.login_use_case.tolerance = tolerance
        self.login_use_case.cooldown_seconds = cooldown_seconds


def _resource_base() -> Path:
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        return Path(bundle_dir)
    return Path(__file__).resolve().parent


def _admin_panel_dist_ready() -> bool:
    return (ADMIN_PANEL_DIST_DIR / "index.html").exists()


def _runtime_check(engine_error: Optional[str], engine: Optional[WebFaceEngine]) -> Optional[str]:
    if cv2 is None or np is None:
        return "Faltan dependencias: instala opencv-python y numpy en el entorno activo."
    if RUNTIME_ERROR is not None:
        return f"Dependencias de reconocimiento no disponibles: {RUNTIME_ERROR}"
    if engine_error is not None:
        return f"No se pudo inicializar el motor facial: {engine_error}"
    if engine is None:
        return "Motor facial no inicializado."
    return None


def _decode_image_data_uri(image_data: str):
    if cv2 is None or np is None:
        return None
    if not image_data:
        return None

    payload = image_data
    if "," in image_data:
        payload = image_data.split(",", 1)[1]

    try:
        binary = base64.b64decode(payload)
    except (ValueError, TypeError):
        return None

    nparr = np.frombuffer(binary, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def _normalized_login_face_box(frame) -> Optional[Dict[str, float]]:
    if cv2 is None or frame is None:
        return None
    try:
        import face_recognition
    except Exception:
        return None

    h, w = frame.shape[:2]
    if h <= 0 or w <= 0:
        return None

    max_side = 720
    scale = min(1.0, max_side / float(max(h, w)))
    if scale < 1.0:
        small = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    else:
        small = frame

    sh, sw = small.shape[:2]
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    locs = face_recognition.face_locations(rgb, number_of_times_to_upsample=1, model="hog")
    if len(locs) != 1:
        return None
    top, right, bottom, left = locs[0]
    return {
        "x": max(0.0, min(1.0, left / float(sw))),
        "y": max(0.0, min(1.0, top / float(sh))),
        "width": max(0.0, min(1.0, (right - left) / float(sw))),
        "height": max(0.0, min(1.0, (bottom - top) / float(sh))),
    }


def _credential_jpeg_path(student_id: int) -> Optional[Path]:
    path = PROJECT_DIR / "data" / "credentials" / f"est_{student_id}.jpg"
    return path if path.is_file() else None

def _student_credential_path_from_db(student_id: int) -> Optional[Path]:
    try:
        with connect() as conn:
            row = conn.execute(
                """
                SELECT foto_credencial
                FROM datos_biometricos
                WHERE tipo_usuario = 'ESTUDIANTE' AND id_usuario_ref = ?
                ORDER BY rowid DESC
                LIMIT 1
                """,
                (student_id,),
            ).fetchone()
    except Exception:
        return None

    if not row:
        return None

    stored = str(row[0] or "").strip()
    if not stored:
        return None

    stored_path = Path(stored)
    if not stored_path.is_absolute():
        stored_path = PROJECT_DIR / stored_path
    return stored_path if stored_path.is_file() else None


def _resolve_credential_jpeg_path(student_id: int) -> Optional[Path]:
    direct_path = _credential_jpeg_path(student_id)
    if direct_path is not None:
        return direct_path
    return _student_credential_path_from_db(student_id)


def _persist_student_credential_jpeg(student_id: int, foto_bytes: Optional[bytes]) -> None:
    if not foto_bytes:
        return

    cred_dir = PROJECT_DIR / "data" / "credentials"
    cred_dir.mkdir(parents=True, exist_ok=True)
    out_path = cred_dir / f"est_{student_id}.jpg"
    out_path.write_bytes(foto_bytes)


def _jpeg_encode_frame(
    frame,
    max_width: int = 520,
    quality: int = 88,
    color_space: Optional[str] = None,
) -> Optional[bytes]:
    if cv2 is None or frame is None:
        return None
    h, w = frame.shape[:2]
    if w > max_width:
        scale = max_width / float(w)
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    if color_space and color_space.upper() == "RGB":
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        return None
    return bytes(buf)


_camera_stream_lock = threading.Lock()
_latest_frame_lock = threading.Lock()
_latest_frame_bgr = None


def _store_latest_frame(frame, color_space: Optional[str]) -> None:
    global _latest_frame_bgr
    if cv2 is None or frame is None:
        return
    try:
        if color_space and color_space.upper() == "RGB":
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        with _latest_frame_lock:
            _latest_frame_bgr = frame.copy()
    except Exception:
        return


def _get_latest_frame_bgr():
    with _latest_frame_lock:
        if _latest_frame_bgr is None:
            return None
        return _latest_frame_bgr.copy()


def _mjpeg_frame_stream(cap):
    try:
        color_space = getattr(cap, "color_space", None)
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            _store_latest_frame(frame, color_space)
            jpeg = _jpeg_encode_frame(frame, color_space=color_space)
            if not jpeg:
                continue
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
            )
    finally:
        try:
            cap.release()
        except Exception:
            pass


def _prime_camera(cap, timeout_seconds: float = 5.0, min_success: int = 1) -> bool:
    deadline = time.monotonic() + timeout_seconds
    successes = 0
    while time.monotonic() < deadline:
        ret, frame = cap.read()
        if ret and frame is not None:
            successes += 1
            if successes >= min_success:
                return True
        time.sleep(0.05)
    return False


def _parse_user_data(label: str, student_id: int) -> Dict[str, Any]:
    pattern = re.compile(
        r"^(?P<name>.+?)\s*\((?P<grado>\d)(?P<grupo>[A-Z])-(?P<turno>[^)]+)\)\s*#(?P<id>\d+)$"
    )
    match = pattern.match(label.strip())
    if match:
        sid = int(match.group("id"))
        grado = match.group("grado")
        grupo = match.group("grupo")
        turno = match.group("turno")
        salon = f"{grado}{grupo}-{turno}"
        foto_path = _credential_jpeg_path(sid)
        return {
            "nombre": match.group("name").strip(),
            "salon": salon,
            "grado": grado,
            "grupo": grupo,
            "turno": turno,
            "edad": "---",
            "id": sid,
            "foto_url": (f"/api/credencial/{sid}" if foto_path else None),
        }

    loose = re.compile(r"^(?P<name>.+?)\s*\((?P<classroom>.+?)\)\s*#(?P<id>\d+)$")
    m2 = loose.match(label.strip())
    if m2:
        sid = int(m2.group("id"))
        foto_path = _credential_jpeg_path(sid)
        return {
            "nombre": m2.group("name").strip(),
            "salon": m2.group("classroom"),
            "grado": "---",
            "grupo": "---",
            "turno": "---",
            "edad": "---",
            "id": sid,
            "foto_url": (f"/api/credencial/{sid}" if foto_path else None),
        }

    foto_path = _credential_jpeg_path(student_id)
    return {
        "nombre": label,
        "salon": "---",
        "grado": "---",
        "grupo": "---",
        "turno": "---",
        "edad": "---",
        "id": student_id,
        "foto_url": (f"/api/credencial/{student_id}" if foto_path else None),
    }


def _norm_shift(value: str) -> str:
    raw = value.strip().upper()
    if raw in {"MAT", "MATUTINO"}:
        return "MATUTINO"
    if raw in {"VESP", "VESPERTINO", "VERPERTINO"}:
        return "VESPERTINO"
    raise ValueError("Turno invalido")


def _ensure_grade(conn: sqlite3.Connection, grade: int) -> int:
    key = str(int(grade))
    row = conn.execute("SELECT id_grado FROM grados WHERE clave = ?", (key,)).fetchone()
    if row:
        return int(row[0])

    name_map = {"1": "PRIMERO", "2": "SEGUNDO", "3": "TERCERO"}
    conn.execute("INSERT INTO grados (clave, nombre) VALUES (?, ?)", (key, name_map.get(key, f"GRADO {key}")))
    return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])


def _ensure_group(conn: sqlite3.Connection, group_letter: str) -> int:
    key = group_letter.strip().upper()[:1]
    row = conn.execute("SELECT id_grupo FROM grupos WHERE clave = ?", (key,)).fetchone()
    if row:
        return int(row[0])

    conn.execute("INSERT INTO grupos (clave) VALUES (?)", (key,))
    return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])


def _ensure_shift(conn: sqlite3.Connection, shift: str) -> int:
    key = _norm_shift(shift)
    row = conn.execute("SELECT id_turno FROM turnos WHERE clave = ?", (key,)).fetchone()
    if row:
        return int(row[0])

    conn.execute("INSERT INTO turnos (clave, nombre) VALUES (?, ?)", (key, key))
    return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])


def _ensure_settings_table() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS model_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                scale REAL NOT NULL,
                tolerance REAL NOT NULL,
                cooldown_seconds REAL NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def _load_model_settings(defaults: RecognitionSettings) -> Dict[str, float]:
    _ensure_settings_table()

    with connect() as conn:
        row = conn.execute(
            "SELECT scale, tolerance, cooldown_seconds FROM model_settings WHERE id = 1"
        ).fetchone()

    if row:
        return {
            "scale": float(row[0]),
            "tolerance": float(row[1]),
            "cooldown_seconds": float(row[2]),
        }

    return {
        "scale": float(defaults.scale),
        "tolerance": float(defaults.tolerance),
        "cooldown_seconds": float(defaults.access_cooldown_seconds),
    }


def _save_model_settings(scale: float, tolerance: float, cooldown_seconds: float) -> None:
    _ensure_settings_table()

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO model_settings (id, scale, tolerance, cooldown_seconds)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                scale = excluded.scale,
                tolerance = excluded.tolerance,
                cooldown_seconds = excluded.cooldown_seconds,
                updated_at = CURRENT_TIMESTAMP
            """,
            (scale, tolerance, cooldown_seconds),
        )


def _ensure_servo_settings_table() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS servo_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                hold_seconds REAL NOT NULL,
                always_active INTEGER NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def _load_servo_settings() -> Dict[str, float | bool]:
    _ensure_servo_settings_table()
    defaults = servomotor.get_servo_settings()

    with connect() as conn:
        row = conn.execute(
            "SELECT hold_seconds, always_active FROM servo_settings WHERE id = 1"
        ).fetchone()

    if row:
        return {
            "hold_seconds": float(row[0]),
            "always_active": bool(int(row[1])),
        }

    return {
        "hold_seconds": float(defaults["hold_seconds"]),
        "always_active": bool(defaults["always_active"]),
    }


def _save_servo_settings(*, hold_seconds: float, always_active: bool) -> None:
    _ensure_servo_settings_table()

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO servo_settings (id, hold_seconds, always_active)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                hold_seconds = excluded.hold_seconds,
                always_active = excluded.always_active,
                updated_at = CURRENT_TIMESTAMP
            """,
            (float(hold_seconds), 1 if always_active else 0),
        )


def _parse_optional_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None

    raw = value.strip().lower()
    if not raw or raw == "all":
        return None
    if raw in {"true", "1", "yes"}:
        return True
    if raw in {"false", "0", "no"}:
        return False

    raise ValueError("acceso_concedido debe ser true, false o all")


def create_app() -> Flask:
    initialize_database()

    base_dir = _resource_base()
    templates_dir = base_dir / "templates"
    static_dir = base_dir / "static"

    app = Flask(
        __name__,
        template_folder=str(templates_dir),
        static_folder=str(static_dir),
    )

    admin_panel_ready = _admin_panel_dist_ready()

    recognition_settings = get_recognition_settings()
    cfg = _load_model_settings(recognition_settings)
    recognition_settings.scale = cfg["scale"]
    recognition_settings.tolerance = cfg["tolerance"]
    recognition_settings.access_cooldown_seconds = cfg["cooldown_seconds"]

    servo_cfg = _load_servo_settings()
    servomotor.update_servo_settings(
        hold_seconds=float(servo_cfg["hold_seconds"]),
        always_active=bool(servo_cfg["always_active"]),
    )

    hardware = HardwareIntegration()

    engine = None
    engine_error = None
    try:
        engine = WebFaceEngine(recognition_settings)
    except Exception as exc:
        engine_error = str(exc)

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/admin-panel/")
    @app.get("/admin-panel/<path:requested_path>")
    def admin_panel(requested_path: str = ""):
        if not admin_panel_ready:
            return (
                jsonify(
                    {
                        "ok": False,
                        "message": "El build de admin_panel no esta disponible. Ejecuta npm run build dentro de admin_panel.",
                    }
                ),
                404,
            )

        rel_path = requested_path.strip("/")
        candidate = ADMIN_PANEL_DIST_DIR / rel_path if rel_path else ADMIN_PANEL_DIST_DIR / "index.html"

        if rel_path and candidate.is_file():
            return send_from_directory(ADMIN_PANEL_DIST_DIR, rel_path)

        if rel_path and "." in Path(rel_path).name:
            return jsonify({"ok": False, "message": "Asset no encontrado en admin_panel"}), 404

        return send_from_directory(ADMIN_PANEL_DIST_DIR, "index.html")

    @app.get("/status")
    def status():
        runtime_issue = _runtime_check(engine_error, engine)
        return jsonify(
            {
                "ok": runtime_issue is None,
                "service": "VerifyMe",
                "message": runtime_issue or "",
            }
        )

    @app.get("/api/camera/stream")
    def camera_stream():
        if cv2 is None:
            return jsonify({"ok": False, "message": "OpenCV no disponible."}), 500

        acquired = _camera_stream_lock.acquire(blocking=False)
        if not acquired:
            return jsonify({"ok": False, "message": "Camara en uso."}), 409

        cap = open_camera()
        if cap is None:
            _camera_stream_lock.release()
            return jsonify({"ok": False, "message": "No se pudo abrir la camara."}), 503

        if not _prime_camera(cap):
            try:
                cap.release()
            except Exception:
                pass
            _camera_stream_lock.release()
            return jsonify({"ok": False, "message": "La camara no entrega frames."}), 503

        def _generate():
            try:
                yield from _mjpeg_frame_stream(cap)
            finally:
                _camera_stream_lock.release()

        response = Response(_generate(), mimetype="multipart/x-mixed-replace; boundary=frame")
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    @app.get("/api/login/status")
    def login_status():
        runtime_issue = _runtime_check(engine_error, engine)
        if runtime_issue is not None:
            return jsonify({"users_count": 0, "ready": False, "message": runtime_issue})

        assert engine is not None

        engine.refresh_known_students()
        return jsonify(
            {
                "users_count": len(engine.known_ids),
                "ready": len(engine.known_ids) > 0,
                "message": "Listo" if engine.known_ids else "No hay usuarios registrados",
            }
        )

    @app.get("/api/credencial/<int:student_id>")
    def credencial_foto(student_id: int):
        path = _resolve_credential_jpeg_path(student_id)
        if path is None:
            return jsonify({"ok": False, "message": "Sin fotografia de credencial"}), 404
        return send_file(path, mimetype="image/jpeg")

    @app.post("/api/login/liveness/start")
    def liveness_start():
        runtime_issue = _runtime_check(engine_error, engine)
        if runtime_issue is not None:
            return jsonify({"ok": False, "message": runtime_issue}), 500
        if start_liveness_session is None:
            return jsonify({"ok": False, "message": "Liveness no disponible en este entorno."}), 500
        session_id = start_liveness_session()
        return jsonify({"ok": True, "session_id": session_id})

    @app.post("/api/login/liveness/frame")
    def liveness_frame():
        runtime_issue = _runtime_check(engine_error, engine)
        if runtime_issue is not None:
            return jsonify({"ok": False, "state": "error", "message": runtime_issue}), 500
        if push_liveness_frame is None:
            return jsonify({"ok": False, "state": "error", "message": "Liveness no disponible"}), 500

        payload = request.get_json(silent=True) or {}
        session_id = str(payload.get("session_id", "")).strip()
        use_latest = bool(payload.get("use_latest"))
        frame = None if use_latest else _decode_image_data_uri(payload.get("image", ""))
        if not session_id:
            return jsonify({"ok": False, "state": "error", "message": "Falta session_id"}), 400
        if frame is None:
            frame = _get_latest_frame_bgr()
        if frame is None:
            return jsonify({"ok": True, "state": "no_face", "message": "Imagen invalida"})

        state, message, face_box = push_liveness_frame(session_id, frame)
        return jsonify({"ok": True, "state": state, "message": message, "face_box": face_box})

    @app.post("/api/login/verify")
    def verify_face():
        runtime_issue = _runtime_check(engine_error, engine)
        if runtime_issue is not None:
            return jsonify({"ok": False, "state": "error", "message": runtime_issue}), 500

        assert engine is not None

        payload = request.get_json(silent=True) or {}
        use_latest = bool(payload.get("use_latest"))
        frame = None if use_latest else _decode_image_data_uri(payload.get("image", ""))
        if frame is None:
            frame = _get_latest_frame_bgr()
        if frame is None:
            return jsonify({"ok": False, "state": "error", "message": "Imagen invalida"}), 400

        face_box = _normalized_login_face_box(frame)
        liveness_sid = str(payload.get("liveness_session_id") or payload.get("liveness_session") or "").strip()
        if not liveness_sid or liveness_session_ready is None or not liveness_session_ready(liveness_sid):
            return jsonify(
                {
                    "ok": True,
                    "state": "liveness_required",
                    "message": "Primero completa la verificación: parpadea cuando el sistema te lo pida.",
                    "user": None,
                    "face_box": face_box,
                }
            )

        engine.refresh_known_students()
        if not engine.known_encodings:
            return jsonify(
                {
                    "ok": False,
                    "state": "error",
                    "message": "ERROR: No hay usuarios registrados",
                    "face_box": face_box,
                }
            ), 400

        base_scale = engine.recognition_settings.scale
        if extract_login_face_encoding is not None:
            enc_live = extract_login_face_encoding(frame, base_scale=base_scale)
        else:
            enc_live = None
        if enc_live is None:
            assert detect_face_encodings_from_frame is not None
            _, enc_list = detect_face_encodings_from_frame(frame, scale=base_scale)
            if len(enc_list) > 1:
                return jsonify(
                    {
                        "ok": True,
                        "state": "positioning",
                        "message": "CENTRA TU ROSTRO",
                        "user": None,
                        "face_box": None,
                    }
                )
            enc_live = enc_list[0] if len(enc_list) == 1 else None

        if enc_live is None:
            return jsonify(
                {
                    "ok": True,
                    "state": "waiting",
                    "message": "ESPERANDO ROSTRO...",
                    "user": None,
                    "face_box": None,
                }
            )

        web_tol = min(0.6, float(engine.recognition_settings.tolerance) + 0.08)

        result = engine.login_use_case.process_frame(
            [enc_live],
            engine.known_encodings,
            engine.known_labels,
            engine.known_ids,
            tolerance=web_tol,
        )

        if "ACCESO CONCEDIDO" in result.message:
            idx = result.match_index
            if idx is None or idx < 0:
                idx = engine.login_use_case.matcher.find_first_match(
                    engine.known_encodings,
                    enc_live,
                    tolerance=web_tol,
                )
            user_data = None
            if 0 <= idx < len(engine.known_labels):
                user_data = _parse_user_data(engine.known_labels[idx], engine.known_ids[idx])

            return jsonify(
                {
                    "ok": True,
                    "state": "granted",
                    "message": result.message,
                    "user": user_data,
                    "face_box": face_box,
                }
            )

        return jsonify(
            {
                "ok": True,
                "state": "denied",
                "message": result.message,
                "user": None,
                "face_box": face_box,
            }
        )

    @app.post("/api/hardware/access-success")
    def hardware_access_success():
        hardware.success()
        return jsonify({"ok": True, "message": "Hardware de acceso activado."})

    @app.post("/api/registro-admin")
    def register_admin_face():
        runtime_issue = _runtime_check(engine_error, engine)
        if runtime_issue is not None:
            return jsonify({"ok": False, "message": runtime_issue}), 500

        assert engine is not None

        payload = request.get_json(silent=True) or {}

        num_empleado = str(payload.get("num_empleado") or payload.get("numero_empleado") or "").strip()
        nombre = str(payload.get("nombre", "")).strip()
        rol = str(payload.get("rol", "")).strip() or "ADMIN"
        correo = str(payload.get("correo", "")).strip().lower()
        password = str(payload.get("password", ""))

        if not all([num_empleado, nombre, correo, password]):
            return jsonify({"ok": False, "message": "Todos los campos de administrador son obligatorios."}), 400

        frame_f = _decode_image_data_uri(str(payload.get("image_front", "") or ""))
        frame_l = _decode_image_data_uri(str(payload.get("image_left", "") or ""))
        frame_r = _decode_image_data_uri(str(payload.get("image_right", "") or ""))

        if not (frame_f is not None and frame_l is not None and frame_r is not None):
            return jsonify({"ok": False, "message": "Faltan imagenes para el registro biometrico."}), 400

        scale = engine.recognition_settings.scale

        def _encode_registration_frame(fr):
            if detect_face_encodings_from_frame_robust is not None:
                return detect_face_encodings_from_frame_robust(fr, base_scale=scale)
            return detect_face_encodings_from_frame(fr, scale=scale)

        encodings_f = _encode_registration_frame(frame_f)[1]
        encodings_l = _encode_registration_frame(frame_l)[1]
        encodings_r = _encode_registration_frame(frame_r)[1]

        for tag, encs in (
            ("frente", encodings_f),
            ("perfil izquierdo", encodings_l),
            ("perfil derecho", encodings_r),
        ):
            if len(encs) == 0:
                return jsonify({"ok": False, "message": f"No se detecto rostro en {tag}."}), 400
            if len(encs) > 1:
                return jsonify({"ok": False, "message": f"Varios rostros en {tag}. Debe haber solo uno."}), 400

        foto_bytes = _jpeg_encode_frame(frame_f)
        if not foto_bytes:
            return jsonify({"ok": False, "message": "No se pudo guardar la foto de credencial."}), 400

        password_hash = generate_password_hash(password)

        try:
            with closing(connect()) as conn:
                cur = conn.execute(
                    """
                    INSERT INTO personal_administrativo
                    (num_empleado, nombre_completo, rol, correo, password_hash, estado_activo)
                    VALUES (?, ?, ?, ?, ?, 1)
                    """,
                    (num_empleado, nombre, rol, correo, password_hash),
                )
                admin_id = cur.lastrowid
                
                import json
                conn.execute(
                    """
                    INSERT INTO datos_biometricos 
                    (tipo_usuario, id_usuario_ref, vector_facial, vector_perfil_izq, vector_perfil_der, foto_credencial)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "PERSONAL",
                        admin_id,
                        json.dumps(encodings_f[0].tolist()),
                        json.dumps(encodings_l[0].tolist()),
                        json.dumps(encodings_r[0].tolist()),
                        foto_bytes
                    )
                )
                conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({"ok": False, "message": "El numero de empleado o correo ya esta registrado."}), 400
        except Exception as e:
            return jsonify({"ok": False, "message": f"Error en base de datos: {str(e)}"}), 500

        engine.refresh_known_students() # It also refreshes staff
        return jsonify({"ok": True, "message": "Administrador y datos biometricos registrados correctamene."})

    @app.post("/api/registro")
    def register_face():
        runtime_issue = _runtime_check(engine_error, engine)
        if runtime_issue is not None:
            return jsonify({"ok": False, "message": runtime_issue}), 500

        assert engine is not None

        payload = request.get_json(silent=True) or {}

        nombre = str(payload.get("nombre", "")).strip()
        grado_raw = str(payload.get("grado", "")).strip()
        letra = str(payload.get("letra", "")).strip().upper()
        turno = str(payload.get("turno", "")).strip().upper()

        if not nombre:
            return jsonify({"ok": False, "message": "Dato invalido. El nombre es obligatorio."}), 400
        if grado_raw not in {"1", "2", "3"}:
            return jsonify({"ok": False, "message": "Dato invalido. El grado debe ser 1, 2 o 3."}), 400
        if len(letra) != 1 or not letra.isalpha():
            return jsonify({"ok": False, "message": "Dato invalido. Ingresa una sola letra (A-Z)."}), 400
        if turno not in {"MATUTINO", "VESPERTINO"}:
            return jsonify({"ok": False, "message": "Dato invalido. Usa MATUTINO o VESPERTINO."}), 400

        frame_f = _decode_image_data_uri(str(payload.get("image_front", "") or ""))
        frame_l = _decode_image_data_uri(str(payload.get("image_left", "") or ""))
        frame_r = _decode_image_data_uri(str(payload.get("image_right", "") or ""))
        legacy = _decode_image_data_uri(str(payload.get("image", "") or ""))

        scale = engine.recognition_settings.scale

        def _encode_registration_frame(fr):
            if detect_face_encodings_from_frame_robust is not None:
                return detect_face_encodings_from_frame_robust(fr, base_scale=scale)
            assert detect_face_encodings_from_frame is not None
            return detect_face_encodings_from_frame(fr, scale=scale)

        if frame_f is not None and frame_l is not None and frame_r is not None:
            encodings_f = _encode_registration_frame(frame_f)[1]
            encodings_l = _encode_registration_frame(frame_l)[1]
            encodings_r = _encode_registration_frame(frame_r)[1]
            for tag, encs in (
                ("frente", encodings_f),
                ("perfil izquierdo", encodings_l),
                ("perfil derecho", encodings_r),
            ):
                if len(encs) == 0:
                    return jsonify(
                        {
                            "ok": False,
                            "message": (
                                f"No se detecto rostro en {tag}. "
                                "Prueba con mas luz, acerca el rostro o un giro mas leve (debe verse parte del rostro)."
                            ),
                        },
                    ), 400
                if len(encs) > 1:
                    return jsonify(
                        {"ok": False, "message": f"Varios rostros en {tag}. Debe haber solo uno."},
                    ), 400

            foto_bytes = _jpeg_encode_frame(frame_f)
            if not foto_bytes:
                return jsonify({"ok": False, "message": "No se pudo guardar la foto de credencial."}), 400

            result = engine.registration_use_case.register_from_three_encodings(
                nombre,
                int(grado_raw),
                letra,
                turno,
                encodings_f[0],
                encodings_l[0],
                encodings_r[0],
                foto_bytes,
            )
        elif legacy is not None:
            _, encodings = _encode_registration_frame(legacy)
            result = engine.registration_use_case.register_from_detected_faces(
                nombre,
                int(grado_raw),
                letra,
                turno,
                encodings,
            )
        else:
            return jsonify(
                {
                    "ok": False,
                    "message": "Faltan imagenes. Usa image_front, image_left e image_right (registro completo).",
                }
            ), 400

        if not result.success:
            return jsonify({"ok": False, "message": result.message}), 400

        if result.student_id is not None and foto_bytes:
            _persist_student_credential_jpeg(result.student_id, foto_bytes)

        engine.refresh_known_students()
        return jsonify({"ok": True, "message": result.message, "student_id": result.student_id})

    @app.get("/api/admin/students")
    def list_students():
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT id_estudiante, nombre, grado, grupo, turno, estado_activo
                FROM vw_estudiantes
                ORDER BY id_estudiante DESC
                """
            ).fetchall()

        students = [
            {
                "id": int(row[0]),
                "nombre": row[1],
                "grado": row[2],
                "grupo": row[3],
                "turno": row[4],
                "estado_activo": int(row[5]),
                "foto_url": (f"/api/credencial/{int(row[0])}" if _resolve_credential_jpeg_path(int(row[0])) else None),
            }
            for row in rows
        ]
        return jsonify({"ok": True, "students": students})

    @app.post("/api/admin/students")
    def create_student_admin():
        payload = request.get_json(silent=True) or {}
        nombre = str(payload.get("nombre", "")).strip()
        grado = str(payload.get("grado", "")).strip()
        grupo = str(payload.get("grupo", "")).strip().upper()
        turno = str(payload.get("turno", "")).strip().upper()

        if not nombre:
            return jsonify({"ok": False, "message": "Nombre es obligatorio."}), 400
        if grado not in {"1", "2", "3"}:
            return jsonify({"ok": False, "message": "Grado invalido."}), 400
        if len(grupo) != 1 or not grupo.isalpha():
            return jsonify({"ok": False, "message": "Grupo invalido (usa una letra)."}), 400

        try:
            shift = _norm_shift(turno)
            with connect() as conn:
                id_grado = _ensure_grade(conn, int(grado))
                id_grupo = _ensure_group(conn, grupo)
                id_turno = _ensure_shift(conn, shift)
                conn.execute(
                    """
                    INSERT INTO estudiantes (nombre, id_grado, id_grupo, id_turno, estado_activo)
                    VALUES (?, ?, ?, ?, 1)
                    """,
                    (nombre, id_grado, id_grupo, id_turno),
                )
                student_id = int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])
        except ValueError:
            return jsonify({"ok": False, "message": "Turno invalido."}), 400

        return jsonify({"ok": True, "student_id": student_id, "message": "Estudiante creado."})

    @app.get("/api/admin/access-session")
    def get_access_session():
        session = get_active_session()
        return jsonify({"ok": True, "active": session is not None, "session": session})

    @app.post("/api/admin/access-session/start")
    def start_access_session_admin():
        payload = request.get_json(silent=True) or {}
        inicio = payload.get("inicio")

        try:
            session_id = start_access_session(inicio=str(inicio) if inicio else None)
        except ValueError as exc:
            message = str(exc)
            status = 409 if "Ya existe" in message else 400
            return jsonify({"ok": False, "message": message}), status

        return jsonify({"ok": True, "session_id": session_id, "message": "Sesion iniciada."})

    @app.post("/api/admin/access-session/close")
    def close_access_session_admin():
        payload = request.get_json(silent=True) or {}
        session_id = payload.get("session_id")
        fin = payload.get("fin")

        try:
            session_id_value = int(session_id) if session_id is not None else None
        except (TypeError, ValueError):
            return jsonify({"ok": False, "message": "session_id invalido."}), 400

        try:
            close_access_session(
                session_id=session_id_value,
                fin=str(fin) if fin else None,
            )
        except ValueError as exc:
            return jsonify({"ok": False, "message": str(exc)}), 400

        return jsonify({"ok": True, "message": "Sesion cerrada."})

    @app.get("/api/admin/access-logs/active-session")
    def list_access_logs_active_session():
        tipo_evento = request.args.get("tipo_evento")
        acceso_concedido_raw = request.args.get("acceso_concedido")
        limit_raw = request.args.get("limit", "100")
        offset_raw = request.args.get("offset", "0")

        try:
            limit = int(limit_raw)
            offset = int(offset_raw)
        except (TypeError, ValueError):
            return jsonify({"ok": False, "message": "limit/offset deben ser enteros."}), 400

        try:
            acceso_concedido = _parse_optional_bool(acceso_concedido_raw)
            rows = list_access_logs_for_active_session(
                tipo_evento=tipo_evento,
                acceso_concedido=acceso_concedido,
                limit=limit,
                offset=offset,
            )
        except ValueError as exc:
            return jsonify({"ok": False, "message": str(exc)}), 400

        return jsonify({"ok": True, "logs": rows})

    @app.get("/api/admin/access-logs")
    def list_access_logs_admin():
        grado = request.args.get("grado")
        grupo = request.args.get("grupo")
        turno = request.args.get("turno")
        tipo_evento = request.args.get("tipo_evento")
        acceso_concedido_raw = request.args.get("acceso_concedido")
        nombre_contains = request.args.get("nombre")
        from_datetime = request.args.get("from_datetime")
        to_datetime = request.args.get("to_datetime")
        limit_raw = request.args.get("limit", "10")
        offset_raw = request.args.get("offset", "0")

        try:
            limit = int(limit_raw)
            offset = int(offset_raw)
        except (TypeError, ValueError):
            return jsonify({"ok": False, "message": "limit/offset deben ser enteros."}), 400

        try:
            acceso_concedido = _parse_optional_bool(acceso_concedido_raw)
            rows = list_access_logs_detailed(
                from_datetime=str(from_datetime) if from_datetime else None,
                to_datetime=str(to_datetime) if to_datetime else None,
                tipo_evento=tipo_evento,
                acceso_concedido=acceso_concedido,
                grado=grado,
                grupo=grupo,
                turno=turno,
                nombre_contains=nombre_contains,
                limit=limit,
                offset=offset,
            )
        except ValueError as exc:
            return jsonify({"ok": False, "message": str(exc)}), 400

        return jsonify({"ok": True, "logs": rows})

    @app.put("/api/admin/students/<int:student_id>")
    def update_student_admin(student_id: int):
        payload = request.get_json(silent=True) or {}
        nombre = str(payload.get("nombre", "")).strip()
        grado = str(payload.get("grado", "")).strip()
        grupo = str(payload.get("grupo", "")).strip().upper()
        turno = str(payload.get("turno", "")).strip().upper()
        estado = int(payload.get("estado_activo", 1))

        if not nombre:
            return jsonify({"ok": False, "message": "Nombre es obligatorio."}), 400
        if grado not in {"1", "2", "3"}:
            return jsonify({"ok": False, "message": "Grado invalido."}), 400
        if len(grupo) != 1 or not grupo.isalpha():
            return jsonify({"ok": False, "message": "Grupo invalido (usa una letra)."}), 400

        try:
            shift = _norm_shift(turno)
            with connect() as conn:
                id_grado = _ensure_grade(conn, int(grado))
                id_grupo = _ensure_group(conn, grupo)
                id_turno = _ensure_shift(conn, shift)
                cur = conn.execute(
                    """
                    UPDATE estudiantes
                    SET nombre = ?, id_grado = ?, id_grupo = ?, id_turno = ?, estado_activo = ?
                    WHERE id_estudiante = ?
                    """,
                    (nombre, id_grado, id_grupo, id_turno, 1 if estado else 0, student_id),
                )
                if cur.rowcount == 0:
                    return jsonify({"ok": False, "message": "Estudiante no encontrado."}), 404
        except ValueError:
            return jsonify({"ok": False, "message": "Turno invalido."}), 400

        return jsonify({"ok": True, "message": "Estudiante actualizado."})

    @app.delete("/api/admin/students/<int:student_id>")
    def deactivate_student_admin(student_id: int):
        with connect() as conn:
            cur = conn.execute(
                "UPDATE estudiantes SET estado_activo = 0 WHERE id_estudiante = ?",
                (student_id,),
            )
            if cur.rowcount == 0:
                return jsonify({"ok": False, "message": "Estudiante no encontrado."}), 404

        cred_path = PROJECT_DIR / "data" / "credentials" / f"est_{student_id}.jpg"
        pkl_path = PROJECT_DIR / "data" / f"est_{student_id}.pkl"
        try:
            if cred_path.exists():
                cred_path.unlink()
        except Exception as exc:
            print(f"[WARN] No se pudo borrar credencial: {exc}")

        try:
            if pkl_path.exists():
                pkl_path.unlink()
        except Exception as exc:
            print(f"[WARN] No se pudo borrar pkl: {exc}")

        return jsonify({"ok": True, "message": "Estudiante desactivado."})

    @app.get("/api/admin/model-config")
    def get_model_config():
        cfg_local = _load_model_settings(recognition_settings)
        return jsonify({"ok": True, "config": cfg_local})

    @app.put("/api/admin/model-config")
    def update_model_config():
        payload = request.get_json(silent=True) or {}

        try:
            scale = float(payload.get("scale", recognition_settings.scale))
            tolerance = float(payload.get("tolerance", recognition_settings.tolerance))
            cooldown_seconds = float(
                payload.get("cooldown_seconds", recognition_settings.access_cooldown_seconds)
            )
        except (TypeError, ValueError):
            return jsonify({"ok": False, "message": "Valores invalidos para configuracion."}), 400

        if not (0.05 <= scale <= 1.0):
            return jsonify({"ok": False, "message": "scale debe estar entre 0.05 y 1.0"}), 400
        if not (0.2 <= tolerance <= 1.0):
            return jsonify({"ok": False, "message": "tolerance debe estar entre 0.2 y 1.0"}), 400
        if cooldown_seconds < 0:
            return jsonify({"ok": False, "message": "cooldown_seconds no puede ser negativo"}), 400

        _save_model_settings(scale, tolerance, cooldown_seconds)
        if engine is not None:
            engine.apply_model_config(scale, tolerance, cooldown_seconds)

        return jsonify(
            {
                "ok": True,
                "message": "Configuracion del modelo actualizada.",
                "config": {
                    "scale": scale,
                    "tolerance": tolerance,
                    "cooldown_seconds": cooldown_seconds,
                },
            }
        )

    @app.get("/api/admin/servo-settings")
    def get_servo_settings():
        cfg_local = _load_servo_settings()
        return jsonify({"ok": True, "config": cfg_local})

    @app.put("/api/admin/servo-settings")
    def update_servo_settings():
        payload = request.get_json(silent=True) or {}
        current = _load_servo_settings()
        hold_raw = payload.get("hold_seconds", current["hold_seconds"])
        always_raw = payload.get("always_active", current["always_active"])

        try:
            hold_seconds = float(hold_raw)
        except (TypeError, ValueError):
            return jsonify({"ok": False, "message": "hold_seconds debe ser numerico."}), 400

        if hold_seconds < 0 or hold_seconds > 120:
            return jsonify({"ok": False, "message": "hold_seconds debe estar entre 0 y 120."}), 400

        if isinstance(always_raw, bool):
            always_active = always_raw
        elif isinstance(always_raw, (int, float)):
            always_active = bool(always_raw)
        elif isinstance(always_raw, str):
            always_active = always_raw.strip().lower() in {"1", "true", "yes", "on"}
        else:
            always_active = False

        _save_servo_settings(hold_seconds=hold_seconds, always_active=always_active)
        servomotor.update_servo_settings(
            hold_seconds=hold_seconds,
            always_active=always_active,
        )

        return jsonify(
            {
                "ok": True,
                "message": "Configuracion del servomotor actualizada.",
                "config": {
                    "hold_seconds": hold_seconds,
                    "always_active": always_active,
                },
            }
        )

    @app.get("/api/admin/admins")
    def list_admins():
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT id_personal, num_empleado, nombre_completo, rol, correo, estado_activo
                FROM personal_administrativo
                ORDER BY id_personal DESC
                """
            ).fetchall()

        admins = [
            {
                "id": int(row[0]),
                "num_empleado": row[1],
                "numero_empleado": row[1],
                "nombre_completo": row[2],
                "nombre": row[2],
                "rol": row[3],
                "correo": row[4],
                "estado_activo": int(row[5]),
            }
            for row in rows
        ]
        return jsonify({"ok": True, "admins": admins})

    @app.post("/api/admin/admins")
    def create_admin():
        payload = request.get_json(silent=True) or {}
        num_empleado = str(payload.get("num_empleado") or payload.get("numero_empleado") or "").strip()
        nombre_completo = str(payload.get("nombre_completo") or payload.get("nombre") or "").strip()
        rol = str(payload.get("rol", "")).strip() or "ADMIN"
        correo = str(payload.get("correo", "")).strip().lower()
        password = str(payload.get("password", ""))

        if not all([num_empleado, nombre_completo, correo, password]):
            return jsonify({"ok": False, "message": "Todos los campos son obligatorios."}), 400

        password_hash = generate_password_hash(password)

        try:
            with closing(connect()) as conn:
                conn.execute(
                    """
                    INSERT INTO personal_administrativo
                    (num_empleado, nombre_completo, rol, correo, password_hash, estado_activo)
                    VALUES (?, ?, ?, ?, ?, 1)
                    """,
                    (num_empleado, nombre_completo, rol, correo, password_hash),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({"ok": False, "message": "num_empleado o correo ya existe."}), 409

        return jsonify({"ok": True, "message": "Administrador registrado correctamente."})

    @app.put("/api/admin/admins/<int:admin_id>")
    def update_admin(admin_id: int):
        payload = request.get_json(silent=True) or {}
        num_empleado = str(payload.get("num_empleado") or payload.get("numero_empleado") or "").strip()
        nombre_completo = str(payload.get("nombre_completo") or payload.get("nombre") or "").strip()
        rol = str(payload.get("rol", "")).strip() or "ADMIN"
        correo = str(payload.get("correo", "")).strip().lower()
        estado_activo = int(payload.get("estado_activo", 1))
        password = str(payload.get("password") or "").strip()

        if not nombre_completo or not correo:
            return jsonify({"ok": False, "message": "Nombre y correo son obligatorios."}), 400

        updates = ["nombre_completo = ?", "rol = ?", "correo = ?", "estado_activo = ?"]
        params = [nombre_completo, rol, correo, 1 if estado_activo else 0]

        if num_empleado:
            updates.append("num_empleado = ?")
            params.append(num_empleado)

        if password:
            password_hash = generate_password_hash(password)
            updates.append("password_hash = ?")
            params.append(password_hash)

        params.append(admin_id)

        with closing(connect()) as conn:
            cur = conn.execute(
                f"UPDATE personal_administrativo SET {', '.join(updates)} WHERE id_personal = ?",
                params,
            )
            if cur.rowcount == 0:
                return jsonify({"ok": False, "message": "Administrador no encontrado."}), 404
            conn.commit()

        return jsonify({"ok": True, "message": "Administrador actualizado."})

    @app.delete("/api/admin/admins/<int:admin_id>")
    def deactivate_admin(admin_id: int):
        with closing(connect()) as conn:
            cur = conn.execute(
                "UPDATE personal_administrativo SET estado_activo = 0 WHERE id_personal = ?",
                (admin_id,),
            )
            if cur.rowcount == 0:
                return jsonify({"ok": False, "message": "Administrador no encontrado."}), 404
            conn.commit()

        return jsonify({"ok": True, "message": "Administrador desactivado."})

    @app.post("/api/admin/register")
    def register_admin():
        payload = request.get_json(silent=True) or {}
        num_empleado = str(payload.get("num_empleado") or payload.get("numero_empleado") or "").strip()
        nombre_completo = str(payload.get("nombre_completo") or payload.get("nombre") or "").strip()
        rol = str(payload.get("rol", "")).strip() or "ADMIN"
        correo = str(payload.get("correo", "")).strip().lower()
        password = str(payload.get("password", ""))

        if not all([num_empleado, nombre_completo, correo, password]):
            return jsonify({"ok": False, "message": "Todos los campos son obligatorios."}), 400

        password_hash = generate_password_hash(password)

        try:
            with closing(connect()) as conn:
                conn.execute(
                    """
                    INSERT INTO personal_administrativo
                    (num_empleado, nombre_completo, rol, correo, password_hash, estado_activo)
                    VALUES (?, ?, ?, ?, ?, 1)
                    """,
                    (num_empleado, nombre_completo, rol, correo, password_hash),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({"ok": False, "message": "num_empleado o correo ya existe."}), 409

        return jsonify({"ok": True, "message": "Administrador registrado correctamente."})
    
    @app.route("/translate", methods=["POST"])
    def translate_text():

        data = request.get_json()

        text = data.get("text", "")
        target = data.get("target", "en")

        try:

            translated = GoogleTranslator(
                source="auto",
                target=target
            ).translate(text)

            return jsonify({
                "success": True,
                "translated": translated
            })

        except Exception:

            return jsonify({
                "success": False,
                "error": "Translation service unavailable."
            }), 500
        
    
    return app
