import os
import sqlite3

from .connection import connect
from .paths import DB_PATH, SCHEMA_PATH


def initialize_database() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with connect() as conn:
        existe_grupos = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'grupos'"
        ).fetchone()

        if not existe_grupos:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
                conn.executescript(schema_file.read())
            ensure_reporting_views(conn)
            ensure_student_duplicate_trigger(conn)
            return

        migrate_local_schema(conn)


def ensure_reporting_views(conn: sqlite3.Connection) -> None:
    conn.execute("DROP VIEW IF EXISTS vw_intentos_fallidos")
    conn.execute("DROP VIEW IF EXISTS vw_logs_acceso")
    conn.execute("DROP VIEW IF EXISTS vw_estudiantes")

    conn.execute(
        """
        CREATE VIEW vw_estudiantes AS
        SELECT
            e.id_estudiante,
            e.nombre,
            gd.clave AS grado,
            gp.clave AS grupo,
            tr.clave AS turno,
            e.estado_activo
        FROM estudiantes e
        JOIN grados gd ON gd.id_grado = e.id_grado
        JOIN grupos gp ON gp.id_grupo = e.id_grupo
        JOIN turnos tr ON tr.id_turno = e.id_turno
        """
    )

    conn.execute(
        """
        CREATE VIEW vw_logs_acceso AS
        SELECT
            l.id_log,
            l.fecha_hora,
            l.tipo_usuario,
            l.id_usuario_ref,
            CASE
                WHEN l.tipo_usuario = 'ESTUDIANTE' THEN e.nombre
                WHEN l.tipo_usuario = 'PERSONAL' THEN p.nombre_completo
                ELSE NULL
            END AS nombre_usuario,
            l.tipo_evento,
            l.acceso_concedido
        FROM logs_acceso l
        LEFT JOIN estudiantes e
            ON l.tipo_usuario = 'ESTUDIANTE'
            AND e.id_estudiante = l.id_usuario_ref
        LEFT JOIN personal_administrativo p
            ON l.tipo_usuario = 'PERSONAL'
            AND p.id_personal = l.id_usuario_ref
        """
    )

    conn.execute(
        """
        CREATE VIEW vw_intentos_fallidos AS
        SELECT
            id_log,
            fecha_hora,
            tipo_usuario,
            id_usuario_ref,
            nombre_usuario,
            tipo_evento
        FROM vw_logs_acceso
        WHERE acceso_concedido = 0
        """
    )


def ensure_student_duplicate_trigger(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TRIGGER IF EXISTS trg_estudiantes_bloquear_duplicados")
    conn.execute(
        """
        CREATE TRIGGER trg_estudiantes_bloquear_duplicados
        BEFORE INSERT ON estudiantes
        BEGIN
            SELECT CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM estudiantes e
                    WHERE UPPER(TRIM(e.nombre)) = UPPER(TRIM(NEW.nombre))
                      AND e.id_grado = NEW.id_grado
                      AND e.id_grupo = NEW.id_grupo
                      AND e.id_turno = NEW.id_turno
                )
                THEN RAISE(ABORT, 'El estudiante ya existe en la base de datos.')
            END;
        END;
        """
    )


def migrate_local_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS grados (
            id_grado INTEGER PRIMARY KEY AUTOINCREMENT,
            clave TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS turnos (
            id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
            clave TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.execute("INSERT OR IGNORE INTO grados (clave, nombre) VALUES ('1', 'PRIMERO')")
    conn.execute("INSERT OR IGNORE INTO grados (clave, nombre) VALUES ('2', 'SEGUNDO')")
    conn.execute("INSERT OR IGNORE INTO grados (clave, nombre) VALUES ('3', 'TERCERO')")
    conn.execute("INSERT OR IGNORE INTO turnos (clave, nombre) VALUES ('MATUTINO', 'MATUTINO')")
    conn.execute("INSERT OR IGNORE INTO turnos (clave, nombre) VALUES ('VESPERTINO', 'VESPERTINO')")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS personal_administrativo (
            id_personal INTEGER PRIMARY KEY AUTOINCREMENT,
            num_empleado TEXT NOT NULL UNIQUE,
            nombre_completo TEXT NOT NULL,
            rol TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            estado_activo INTEGER NOT NULL DEFAULT 1 CHECK (estado_activo IN (0, 1))
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sesiones_escuela (
            id_sesion INTEGER PRIMARY KEY AUTOINCREMENT,
            inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            fin DATETIME,
            estado_activa INTEGER NOT NULL DEFAULT 1 CHECK (estado_activa IN (0, 1))
        )
        """
    )

    grupos_info = conn.execute("PRAGMA table_info(grupos)").fetchall()
    grupos_columns = {row[1] for row in grupos_info}
    is_legacy_grupos = {"grado", "letra", "turno"}.issubset(grupos_columns)

    if is_legacy_grupos:
        conn.execute("ALTER TABLE grupos RENAME TO grupos_legacy")
        conn.execute(
            """
            CREATE TABLE grupos (
                id_grupo INTEGER PRIMARY KEY AUTOINCREMENT,
                clave TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO grupos (clave)
            SELECT DISTINCT UPPER(SUBSTR(TRIM(letra), 1, 1))
            FROM grupos_legacy
            WHERE TRIM(letra) <> ''
            """
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO grados (clave, nombre)
            SELECT DISTINCT
                CAST(grado AS TEXT) AS clave,
                CASE CAST(grado AS TEXT)
                    WHEN '1' THEN 'PRIMERO'
                    WHEN '2' THEN 'SEGUNDO'
                    WHEN '3' THEN 'TERCERO'
                    ELSE 'GRADO ' || CAST(grado AS TEXT)
                END AS nombre
            FROM grupos_legacy
            """
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO turnos (clave, nombre)
            SELECT DISTINCT
                CASE
                    WHEN UPPER(TRIM(turno)) IN ('MATUTINO', 'MAT') THEN 'MATUTINO'
                    WHEN UPPER(TRIM(turno)) IN ('VESPERTINO', 'VERPERTINO', 'VESP', 'VESP') THEN 'VESPERTINO'
                    ELSE 'MATUTINO'
                END AS clave,
                CASE
                    WHEN UPPER(TRIM(turno)) IN ('MATUTINO', 'MAT') THEN 'MATUTINO'
                    WHEN UPPER(TRIM(turno)) IN ('VESPERTINO', 'VERPERTINO', 'VESP', 'VESP') THEN 'VESPERTINO'
                    ELSE 'MATUTINO'
                END AS nombre
            FROM grupos_legacy
            """
        )

    conn.execute("DROP TABLE IF EXISTS estudiante_tutor")
    conn.execute("DROP TABLE IF EXISTS tutores")

    estudiantes_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(estudiantes)").fetchall()
    }
    needs_estudiantes_migration = {
        "nombre",
        "id_grado",
        "id_grupo",
        "id_turno",
        "estado_activo",
    } - estudiantes_columns

    if {"matricula", "nombre", "apellidos"}.issubset(estudiantes_columns) or needs_estudiantes_migration:
        conn.execute(
            """
            CREATE TABLE estudiantes_new (
                id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                id_grado INTEGER NOT NULL,
                id_grupo INTEGER NOT NULL,
                id_turno INTEGER NOT NULL,
                estado_activo INTEGER NOT NULL DEFAULT 1 CHECK (estado_activo IN (0, 1)),
                FOREIGN KEY (id_grado) REFERENCES grados(id_grado) ON DELETE RESTRICT,
                FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo) ON DELETE RESTRICT,
                FOREIGN KEY (id_turno) REFERENCES turnos(id_turno) ON DELETE RESTRICT
            )
            """
        )

        if is_legacy_grupos:
            if "nombre" in estudiantes_columns:
                conn.execute(
                    """
                    INSERT INTO estudiantes_new (id_estudiante, nombre, id_grado, id_grupo, id_turno, estado_activo)
                    SELECT
                        s.id_estudiante,
                        COALESCE(NULLIF(TRIM(s.nombre), ''), 'ESTUDIANTE #' || s.id_estudiante),
                        gd.id_grado,
                        gp.id_grupo,
                        tr.id_turno,
                        COALESCE(s.estado_activo, 1)
                    FROM estudiantes s
                    JOIN grupos_legacy gl ON gl.id_grupo = s.id_grupo
                    JOIN grados gd ON gd.clave = CAST(gl.grado AS TEXT)
                    JOIN grupos gp ON gp.clave = UPPER(SUBSTR(TRIM(gl.letra), 1, 1))
                    JOIN turnos tr ON tr.clave = CASE
                        WHEN UPPER(TRIM(gl.turno)) IN ('MATUTINO', 'MAT') THEN 'MATUTINO'
                        WHEN UPPER(TRIM(gl.turno)) IN ('VESPERTINO', 'VERPERTINO', 'VESP') THEN 'VESPERTINO'
                        ELSE 'MATUTINO'
                    END
                    """
                )
            else:
                conn.execute(
                    """
                    INSERT INTO estudiantes_new (id_estudiante, nombre, id_grado, id_grupo, id_turno, estado_activo)
                    SELECT
                        s.id_estudiante,
                        'ESTUDIANTE #' || s.id_estudiante,
                        gd.id_grado,
                        gp.id_grupo,
                        tr.id_turno,
                        COALESCE(s.estado_activo, 1)
                    FROM estudiantes s
                    JOIN grupos_legacy gl ON gl.id_grupo = s.id_grupo
                    JOIN grados gd ON gd.clave = CAST(gl.grado AS TEXT)
                    JOIN grupos gp ON gp.clave = UPPER(SUBSTR(TRIM(gl.letra), 1, 1))
                    JOIN turnos tr ON tr.clave = CASE
                        WHEN UPPER(TRIM(gl.turno)) IN ('MATUTINO', 'MAT') THEN 'MATUTINO'
                        WHEN UPPER(TRIM(gl.turno)) IN ('VESPERTINO', 'VERPERTINO', 'VESP') THEN 'VESPERTINO'
                        ELSE 'MATUTINO'
                    END
                    """
                )
        else:
            conn.execute(
                """
                INSERT INTO estudiantes_new (id_estudiante, nombre, id_grado, id_grupo, id_turno, estado_activo)
                SELECT
                    id_estudiante,
                    COALESCE(NULLIF(TRIM(nombre), ''), 'ESTUDIANTE #' || id_estudiante),
                    id_grado,
                    id_grupo,
                    id_turno,
                    COALESCE(estado_activo, 1)
                FROM estudiantes
                """
            )

        conn.execute("DROP TABLE estudiantes")
        conn.execute("ALTER TABLE estudiantes_new RENAME TO estudiantes")

    if is_legacy_grupos:
        conn.execute("DROP TABLE grupos_legacy")

    log_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(logs_acceso)").fetchall()
    }
    if "id_dispositivo" in log_columns:
        conn.execute(
            """
            CREATE TABLE logs_acceso_new (
                id_log INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('ESTUDIANTE', 'PERSONAL')),
                id_usuario_ref INTEGER NOT NULL,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo_evento TEXT NOT NULL CHECK (tipo_evento IN ('Entrada', 'Salida')),
                acceso_concedido INTEGER NOT NULL CHECK (acceso_concedido IN (0, 1))
            )
            """
        )
        conn.execute(
            """
            INSERT INTO logs_acceso_new (
                id_log, tipo_usuario, id_usuario_ref, fecha_hora, tipo_evento, acceso_concedido
            )
            SELECT id_log, tipo_usuario, id_usuario_ref, fecha_hora, tipo_evento, acceso_concedido
            FROM logs_acceso
            """
        )
        conn.execute("DROP TABLE logs_acceso")
        conn.execute("ALTER TABLE logs_acceso_new RENAME TO logs_acceso")

    conn.execute("DROP TABLE IF EXISTS dispositivos_raspberry")

    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_datos_biometricos_usuario
        ON datos_biometricos (tipo_usuario, id_usuario_ref)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_logs_acceso_usuario_fecha
        ON logs_acceso (tipo_usuario, id_usuario_ref, fecha_hora DESC)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_sesiones_estado_inicio
        ON sesiones_escuela (estado_activa, inicio DESC)
        """
    )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_sesion_activa
        ON sesiones_escuela (estado_activa)
        WHERE estado_activa = 1
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_estudiantes_catalogos
        ON estudiantes (id_grado, id_grupo, id_turno, estado_activo)
        """
    )
    ensure_student_duplicate_trigger(conn)
    _ensure_datos_biometricos_extra_columns(conn)
    ensure_reporting_views(conn)


def _ensure_datos_biometricos_extra_columns(conn: sqlite3.Connection) -> None:
    """Añade columnas para foto de credencial y encodings de perfiles (migraciones locales)."""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(datos_biometricos)").fetchall()}
    if "foto_credencial" not in cols:
        conn.execute("ALTER TABLE datos_biometricos ADD COLUMN foto_credencial TEXT")
    if "vector_perfil_izq" not in cols:
        conn.execute("ALTER TABLE datos_biometricos ADD COLUMN vector_perfil_izq TEXT")
    if "vector_perfil_der" not in cols:
        conn.execute("ALTER TABLE datos_biometricos ADD COLUMN vector_perfil_der TEXT")