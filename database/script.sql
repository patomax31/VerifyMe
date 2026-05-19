-- ==============================================================================
-- PROYECTO: SISTEMA BIOMETRICO FACIAL BASADO EN RASPBERRY PI PARA CONTROL DE ACCESO
-- MOTOR: SQLite 3
-- DESCRIPCION: Esquema fisico local (sin internet, un solo dispositivo)
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- ==============================================================================
-- MODULO: CATALOGOS ESCOLARES
-- ==============================================================================

CREATE TABLE grados (
    id_grado INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE grupos (
    id_grupo INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL UNIQUE
);

CREATE TABLE turnos (
    id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL UNIQUE
);

-- ==============================================================================
-- MODULO: ENTORNO ESCOLAR Y USUARIOS
-- ==============================================================================

CREATE TABLE estudiantes (
    id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    id_grado INTEGER NOT NULL,
    id_grupo INTEGER NOT NULL,
    id_turno INTEGER NOT NULL,
    estado_activo INTEGER NOT NULL DEFAULT 1 CHECK (estado_activo IN (0, 1)),
    FOREIGN KEY (id_grado) REFERENCES grados(id_grado) ON DELETE RESTRICT,
    FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo) ON DELETE RESTRICT,
    FOREIGN KEY (id_turno) REFERENCES turnos(id_turno) ON DELETE RESTRICT
);

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

CREATE TABLE personal_administrativo (
    id_personal INTEGER PRIMARY KEY AUTOINCREMENT,
    num_empleado TEXT NOT NULL UNIQUE,
    nombre_completo TEXT NOT NULL,
    rol TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    estado_activo INTEGER NOT NULL DEFAULT 1 CHECK (estado_activo IN (0, 1))
);

-- ==============================================================================
-- MODULO: BIOMETRIA Y HARDWARE (TABLAS POLIMORFICAS)
-- ==============================================================================

CREATE TABLE datos_biometricos (
    id_biometria INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('ESTUDIANTE', 'PERSONAL')),
    id_usuario_ref INTEGER NOT NULL,
    vector_facial TEXT NOT NULL,
    foto_credencial TEXT,
    vector_perfil_izq TEXT,
    vector_perfil_der TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- MODULO: TRANSACCIONES
-- ==============================================================================

CREATE TABLE logs_acceso (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('ESTUDIANTE', 'PERSONAL')),
    id_usuario_ref INTEGER NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo_evento TEXT NOT NULL CHECK (tipo_evento IN ('Entrada', 'Salida')),
    acceso_concedido INTEGER NOT NULL CHECK (acceso_concedido IN (0, 1))
);

CREATE TABLE sesiones_escuela (
    id_sesion INTEGER PRIMARY KEY AUTOINCREMENT,
    inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fin DATETIME,
    estado_activa INTEGER NOT NULL DEFAULT 1 CHECK (estado_activa IN (0, 1))
);

-- ==============================================================================
-- CATALOGOS BASE
-- ==============================================================================

INSERT INTO grados (clave, nombre) VALUES
    ('1', 'PRIMERO'),
    ('2', 'SEGUNDO'),
    ('3', 'TERCERO');

INSERT INTO turnos (clave, nombre) VALUES
    ('MATUTINO', 'MATUTINO'),
    ('VESPERTINO', 'VESPERTINO');

-- ==============================================================================
-- INDICES
-- ==============================================================================

CREATE UNIQUE INDEX ux_datos_biometricos_usuario
ON datos_biometricos (tipo_usuario, id_usuario_ref);

CREATE INDEX ix_logs_acceso_usuario_fecha
ON logs_acceso (tipo_usuario, id_usuario_ref, fecha_hora DESC);

CREATE INDEX ix_sesiones_estado_inicio
ON sesiones_escuela (estado_activa, inicio DESC);

CREATE UNIQUE INDEX ux_sesion_activa
ON sesiones_escuela (estado_activa)
WHERE estado_activa = 1;

CREATE INDEX ix_estudiantes_catalogos
ON estudiantes (id_grado, id_grupo, id_turno, estado_activo);

-- ==============================================================================
-- VISTAS DE CONSULTA / REPORTING
-- ==============================================================================

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
JOIN turnos tr ON tr.id_turno = e.id_turno;

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
    AND p.id_personal = l.id_usuario_ref;

CREATE VIEW vw_intentos_fallidos AS
SELECT
    id_log,
    fecha_hora,
    tipo_usuario,
    id_usuario_ref,
    nombre_usuario,
    tipo_evento
FROM vw_logs_acceso
WHERE acceso_concedido = 0;