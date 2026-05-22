import sqlite3
from datetime import datetime, timezone
from typing import Dict, Optional

from .connection import connect
from .migrations import initialize_database


def log_access(
    id_usuario_ref: int,
    acceso_concedido: bool,
    tipo_evento: str = "Entrada",
    tipo_usuario: str = "ESTUDIANTE",
) -> None:
    initialize_database()

    tipo_usuario_norm = tipo_usuario.upper()
    if tipo_usuario_norm not in {"ESTUDIANTE", "PERSONAL"}:
        raise ValueError("tipo_usuario debe ser 'ESTUDIANTE' o 'PERSONAL'")

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO logs_acceso (
                tipo_usuario, id_usuario_ref, tipo_evento, acceso_concedido
            ) VALUES (?, ?, ?, ?)
            """,
            (tipo_usuario_norm, id_usuario_ref, tipo_evento, 1 if acceso_concedido else 0),
        )


def _normalize_iso_datetime(value: Optional[str], field_name: str) -> Optional[str]:
    if value is None:
        return None

    raw = value.strip()
    if not raw:
        return None

    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} debe estar en formato ISO-8601") from exc

    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def start_access_session(*, inicio: Optional[str] = None) -> int:
    initialize_database()

    inicio_value = _normalize_iso_datetime(inicio, "inicio")

    with connect() as conn:
        try:
            if inicio_value:
                conn.execute(
                    """
                    INSERT INTO sesiones_escuela (inicio, estado_activa)
                    VALUES (?, 1)
                    """,
                    (inicio_value,),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO sesiones_escuela (estado_activa)
                    VALUES (1)
                    """
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError("Ya existe una sesion activa") from exc

        session_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()[0]

    return int(session_id)


def close_access_session(
    *, session_id: Optional[int] = None, fin: Optional[str] = None
) -> None:
    initialize_database()

    fin_value = _normalize_iso_datetime(fin, "fin")

    with connect() as conn:
        if session_id is None:
            row = conn.execute(
                """
                SELECT id_sesion
                FROM sesiones_escuela
                WHERE estado_activa = 1
                ORDER BY inicio DESC, id_sesion DESC
                LIMIT 1
                """
            ).fetchone()
            if not row:
                raise ValueError("No hay sesion activa")
            session_id = row[0]

        if fin_value:
            cursor = conn.execute(
                """
                UPDATE sesiones_escuela
                SET fin = ?, estado_activa = 0
                WHERE id_sesion = ?
                """,
                (fin_value, session_id),
            )
        else:
            cursor = conn.execute(
                """
                UPDATE sesiones_escuela
                SET fin = COALESCE(fin, CURRENT_TIMESTAMP), estado_activa = 0
                WHERE id_sesion = ?
                """,
                (session_id,),
            )

    if cursor.rowcount == 0:
        raise ValueError("Sesion no encontrada")


def get_active_session() -> Optional[Dict]:
    initialize_database()

    with connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT id_sesion, inicio, fin, estado_activa
            FROM sesiones_escuela
            WHERE estado_activa = 1
            ORDER BY inicio DESC, id_sesion DESC
            LIMIT 1
            """
        ).fetchone()

    return dict(row) if row else None
