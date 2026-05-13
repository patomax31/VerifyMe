from __future__ import annotations

import base64
import re
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory
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

from database.sqlite.connection import connect
from database.sqlite.migrations import initialize_database
from src.application.auth_service import AuthService
from src.application.login_use_case import LoginUseCase
from src.application.registration_service import RegistrationService
from src.application.registration_use_case import RegistrationUseCase
from src.core.config import RecognitionSettings, get_recognition_settings
from src.infrastructure.persistence.pkl_repository import PklRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

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
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
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


def _credential_jpeg_path(student_id: int) -> Optional[Path]:
    path = PROJECT_DIR / "data" / "credentials" / f"est_{student_id}.jpg"
    return path if path.is_file() else None


def _jpeg_encode_frame(frame, max_width: int = 520, quality: int = 88) -> Optional[bytes]:
    if cv2 is None or frame is None:
        return None
    h, w = frame.shape[:2]
    if w > max_width:
        scale = max_width / float(w)
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        return None
    return bytes(buf)


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
                "service": "IdentifyMe Desktop",
                "message": runtime_issue or "Servidor Flask activo",
            }
        )

    @app.get("/api/login/status")
    def login_status():
        runtime_issue = _runtime_check(engine_error, engine)
        if runtime_issue is not None:
            return jsonify({"users_count": 0, "ready": False, "message": runtime_issue})

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
        path = _credential_jpeg_path(student_id)
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
        frame = _decode_image_data_uri(payload.get("image", ""))
        if not session_id:
            return jsonify({"ok": False, "state": "error", "message": "Falta session_id"}), 400
        if frame is None:
            return jsonify({"ok": True, "state": "no_face", "message": "Imagen invalida"})

        state, message = push_liveness_frame(session_id, frame)
        return jsonify({"ok": True, "state": state, "message": message})

    @app.post("/api/login/verify")
    def verify_face():
        runtime_issue = _runtime_check(engine_error, engine)
        if runtime_issue is not None:
            return jsonify({"ok": False, "state": "error", "message": runtime_issue}), 500

        payload = request.get_json(silent=True) or {}
        frame = _decode_image_data_uri(payload.get("image", ""))
        if frame is None:
            return jsonify({"ok": False, "state": "error", "message": "Imagen invalida"}), 400

        liveness_sid = str(payload.get("liveness_session_id") or payload.get("liveness_session") or "").strip()
        if not liveness_sid or liveness_session_ready is None or not liveness_session_ready(liveness_sid):
            return jsonify(
                {
                    "ok": True,
                    "state": "liveness_required",
                    "message": "Primero completa la verificación: parpadea cuando el sistema te lo pida.",
                    "user": None,
                }
            )

        engine.refresh_known_students()
        if not engine.known_encodings:
            return jsonify(
                {
                    "ok": False,
                    "state": "error",
                    "message": "ERROR: No hay usuarios registrados",
                }
            ), 400

        base_scale = engine.recognition_settings.scale
        if extract_login_face_encoding is not None:
            enc_live = extract_login_face_encoding(frame, base_scale=base_scale)
        else:
            enc_live = None
        if enc_live is None:
            _, enc_list = detect_face_encodings_from_frame(frame, scale=base_scale)
            if len(enc_list) > 1:
                return jsonify(
                    {
                        "ok": True,
                        "state": "positioning",
                        "message": "CENTRA TU ROSTRO",
                        "user": None,
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
                }
            )

        return jsonify(
            {
                "ok": True,
                "state": "denied",
                "message": result.message,
                "user": None,
            }
        )

    @app.post("/api/registro")
    def register_face():
        runtime_issue = _runtime_check(engine_error, engine)
        if runtime_issue is not None:
            return jsonify({"ok": False, "message": runtime_issue}), 500

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
                "nombre_completo": row[2],
                "rol": row[3],
                "correo": row[4],
                "estado_activo": int(row[5]),
            }
            for row in rows
        ]
        return jsonify({"ok": True, "admins": admins})

    @app.post("/api/admin/register")
    def register_admin():
        payload = request.get_json(silent=True) or {}
        num_empleado = str(payload.get("num_empleado", "")).strip()
        nombre_completo = str(payload.get("nombre_completo", "")).strip()
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

        except Exception as e:

            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
        
    
    return app
