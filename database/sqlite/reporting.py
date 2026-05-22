from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .access import get_active_session
from .connection import connect
from .migrations import initialize_database

_MAX_LIMIT = 1000
_VALID_TIPO_USUARIO = {"ESTUDIANTE", "PERSONAL"}
_VALID_TIPO_EVENTO = {"Entrada", "Salida"}


def _validate_limit_offset(limit: int, offset: int) -> None:
    if limit <= 0 or limit > _MAX_LIMIT:
        raise ValueError(f"limit debe estar entre 1 y {_MAX_LIMIT}")
    if offset < 0:
        raise ValueError("offset no puede ser negativo")


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


def _rows_to_dicts(rows) -> List[Dict]:
    return [dict(row) for row in rows]


def list_students(
    *,
    active_only: Optional[bool] = None,
    grado: Optional[str] = None,
    grupo: Optional[str] = None,
    turno: Optional[str] = None,
    nombre_contains: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict]:
    initialize_database()
    _validate_limit_offset(limit, offset)

    conditions = []
    params = []

    if active_only is True:
        conditions.append("estado_activo = 1")
    elif active_only is False:
        conditions.append("estado_activo = 0")

    if grado:
        conditions.append("grado = ?")
        params.append(str(grado).strip())

    if grupo:
        conditions.append("grupo = ?")
        params.append(str(grupo).strip().upper())

    if turno:
        conditions.append("turno = ?")
        params.append(str(turno).strip().upper())

    if nombre_contains:
        conditions.append("UPPER(nombre) LIKE UPPER(?)")
        params.append(f"%{nombre_contains.strip()}%")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT
            id_estudiante,
            nombre,
            grado,
            grupo,
            turno,
            estado_activo
        FROM vw_estudiantes
        {where_clause}
        ORDER BY id_estudiante ASC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    with connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()

    return _rows_to_dicts(rows)


def list_access_logs(
    *,
    from_datetime: Optional[str] = None,
    to_datetime: Optional[str] = None,
    tipo_usuario: Optional[str] = None,
    tipo_evento: Optional[str] = None,
    acceso_concedido: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict]:
    initialize_database()
    _validate_limit_offset(limit, offset)

    from_iso = _normalize_iso_datetime(from_datetime, "from_datetime")
    to_iso = _normalize_iso_datetime(to_datetime, "to_datetime")

    conditions = []
    params = []

    if from_iso:
        conditions.append("fecha_hora >= ?")
        params.append(from_iso)

    if to_iso:
        conditions.append("fecha_hora <= ?")
        params.append(to_iso)

    if tipo_usuario:
        tipo_usuario_norm = tipo_usuario.strip().upper()
        if tipo_usuario_norm not in _VALID_TIPO_USUARIO:
            raise ValueError("tipo_usuario debe ser ESTUDIANTE o PERSONAL")
        conditions.append("tipo_usuario = ?")
        params.append(tipo_usuario_norm)

    if tipo_evento:
        tipo_evento_norm = tipo_evento.strip().capitalize()
        if tipo_evento_norm not in _VALID_TIPO_EVENTO:
            raise ValueError("tipo_evento debe ser Entrada o Salida")
        conditions.append("tipo_evento = ?")
        params.append(tipo_evento_norm)

    if acceso_concedido is not None:
        conditions.append("acceso_concedido = ?")
        params.append(1 if acceso_concedido else 0)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT
            id_log,
            fecha_hora,
            tipo_usuario,
            id_usuario_ref,
            nombre_usuario,
            tipo_evento,
            acceso_concedido
        FROM vw_logs_acceso
        {where_clause}
        ORDER BY fecha_hora DESC, id_log DESC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    with connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()

    return _rows_to_dicts(rows)


def list_access_logs_for_active_session(
    *,
    tipo_evento: Optional[str] = None,
    acceso_concedido: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict]:
    session = get_active_session()
    if not session:
        raise ValueError("No hay sesion activa")

    return list_access_logs(
        from_datetime=session["inicio"],
        to_datetime=session["fin"],
        tipo_usuario="ESTUDIANTE",
        tipo_evento=tipo_evento,
        acceso_concedido=acceso_concedido,
        limit=limit,
        offset=offset,
    )


def list_access_logs_for_session_id(
    *,
    session_id: int,
    tipo_evento: Optional[str] = None,
    acceso_concedido: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict]:
    initialize_database()

    with connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT inicio, fin
            FROM sesiones_escuela
            WHERE id_sesion = ?
            """,
            (session_id,),
        ).fetchone()

    if not row:
        raise ValueError("Sesion no encontrada")

    return list_access_logs(
        from_datetime=row["inicio"],
        to_datetime=row["fin"],
        tipo_usuario="ESTUDIANTE",
        tipo_evento=tipo_evento,
        acceso_concedido=acceso_concedido,
        limit=limit,
        offset=offset,
    )


def list_sessions(
    *,
    active_only: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict]:
    initialize_database()
    _validate_limit_offset(limit, offset)

    conditions = []
    params = []

    if active_only is True:
        conditions.append("estado_activa = 1")
    elif active_only is False:
        conditions.append("estado_activa = 0")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT
            id_sesion,
            inicio,
            fin,
            estado_activa
        FROM sesiones_escuela
        {where_clause}
        ORDER BY inicio DESC, id_sesion DESC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    with connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()

    return _rows_to_dicts(rows)


def list_failed_attempts(
    *,
    from_datetime: Optional[str] = None,
    to_datetime: Optional[str] = None,
    tipo_usuario: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict]:
    initialize_database()
    _validate_limit_offset(limit, offset)

    from_iso = _normalize_iso_datetime(from_datetime, "from_datetime")
    to_iso = _normalize_iso_datetime(to_datetime, "to_datetime")

    conditions = []
    params = []

    if from_iso:
        conditions.append("fecha_hora >= ?")
        params.append(from_iso)

    if to_iso:
        conditions.append("fecha_hora <= ?")
        params.append(to_iso)

    if tipo_usuario:
        tipo_usuario_norm = tipo_usuario.strip().upper()
        if tipo_usuario_norm not in _VALID_TIPO_USUARIO:
            raise ValueError("tipo_usuario debe ser ESTUDIANTE o PERSONAL")
        conditions.append("tipo_usuario = ?")
        params.append(tipo_usuario_norm)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT
            id_log,
            fecha_hora,
            tipo_usuario,
            id_usuario_ref,
            nombre_usuario,
            tipo_evento
        FROM vw_intentos_fallidos
        {where_clause}
        ORDER BY fecha_hora DESC, id_log DESC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    with connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()

    return _rows_to_dicts(rows)
