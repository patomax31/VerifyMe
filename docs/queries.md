# Guia de consultas SQLite

## Objetivo

Este documento explica como funciona el modulo de consultas administrativas seguras y como usarlo en el proyecto.

Se implementaron tres piezas:

1. Vistas SQL de reporting.
2. Funciones Python seguras para consultar esas vistas.
3. Un script CLI para ejecutar consultas sin escribir SQL manual.

## Arquitectura de consultas

### 1) Vistas SQL

Las vistas se crean y mantienen en inicializacion y migraciones.

- vw_estudiantes
  - Muestra estudiantes con sus catalogos normalizados: grado, grupo y turno.
- vw_logs_acceso
  - Muestra logs de acceso con nombre de usuario resuelto para estudiante o personal.
- vw_intentos_fallidos
  - Filtra intentos con acceso_concedido = 0.

Estas vistas viven en el esquema y se regeneran de forma segura durante la migracion.

### 2) Funciones Python seguras

Archivo: database/sqlite/reporting.py

Funciones disponibles:

- list_students(...)
- list_access_logs(...)
- list_access_logs_for_active_session(...)
- list_access_logs_for_session_id(...)
- list_failed_attempts(...)
- list_sessions(...)

Principios de seguridad aplicados:

- Consultas parametrizadas con placeholders.
- Sin concatenacion de valores de usuario en SQL.
- Validacion de enums permitidos.
- Validacion de fechas en formato ISO-8601.
- Paginacion obligatoria con limit y offset.
- Limite maximo de registros por consulta para evitar abuso.

### 3) CLI de administracion

Archivo: scripts/db_queries.py

Comandos:

- students
- logs
- failed
- sessions

Formatos de salida:

- table (por defecto)
- json

## Uso rapido

## Requisito previo

Ejecutar en el entorno virtual del proyecto.

Ejemplo de ejecucion en Windows:

C:/Projects/face-recognition/.venv/Scripts/python.exe scripts/db_queries.py students --limit 20

## Consultar estudiantes

Parametros utiles:

- --active all|true|false
- --grado
- --grupo
- --turno
- --nombre
- --limit
- --offset
- --format table|json

Ejemplos:

C:/Projects/face-recognition/.venv/Scripts/python.exe scripts/db_queries.py students --active true --limit 50

C:/Projects/face-recognition/.venv/Scripts/python.exe scripts/db_queries.py students --grado 2 --grupo B --turno VESPERTINO --nombre Bruno --format json

## Consultar logs de acceso

Parametros utiles:

- --from-datetime
- --to-datetime
- --tipo-usuario ESTUDIANTE|PERSONAL
- --tipo-evento Entrada|Salida
- --acceso-concedido all|true|false
- --active-session
- --session-id
- --limit
- --offset
- --format table|json

Ejemplos:

C:/Projects/face-recognition/.venv/Scripts/python.exe scripts/db_queries.py logs --tipo-usuario ESTUDIANTE --acceso-concedido true --limit 100

C:/Projects/face-recognition/.venv/Scripts/python.exe scripts/db_queries.py logs --from-datetime 2026-04-01T00:00:00 --to-datetime 2026-04-30T23:59:59 --format json

Logs de la sesion activa (solo estudiantes):

C:/Projects/face-recognition/.venv/Scripts/python.exe scripts/db_queries.py logs --active-session --format table

Logs de una sesion historica por id (solo estudiantes):

C:/Projects/face-recognition/.venv/Scripts/python.exe scripts/db_queries.py logs --session-id 12 --format json

## Consultar intentos fallidos

Parametros utiles:

- --from-datetime
- --to-datetime
- --tipo-usuario ESTUDIANTE|PERSONAL
- --limit
- --offset
- --format table|json

Ejemplo:

C:/Projects/face-recognition/.venv/Scripts/python.exe scripts/db_queries.py failed --tipo-usuario ESTUDIANTE --limit 50

## Consultar sesiones de acceso

Parametros utiles:

- --active all|true|false
- --limit
- --offset
- --format table|json

Ejemplos:

C:/Projects/face-recognition/.venv/Scripts/python.exe scripts/db_queries.py sessions --active true

C:/Projects/face-recognition/.venv/Scripts/python.exe scripts/db_queries.py sessions --active false --format json

## Reglas de validacion

- Fechas invalidas devuelven error de validacion.
- Valores fuera de catalogo para tipo de usuario o tipo de evento devuelven error de validacion.
- limit debe estar entre 1 y 1000.
- offset no puede ser negativo.
- Los flags de sesion (--active-session, --session-id) no se combinan con --from-datetime/--to-datetime.
- Los logs por sesion solo aplican a ESTUDIANTE.

## Buenas practicas

1. Usar filtros por fecha en consultas grandes.
2. Evitar limit altos en tareas interactivas.
3. Preferir formato json cuando se integre con otras herramientas.
4. Mantener consultas administrativas en este script para no dispersar SQL en multiples archivos.

## Solucion de problemas

- Mensaje Sin resultados
  - La consulta es valida, pero no hay filas que cumplan los filtros.

- Error de validacion
  - Revisar formato de fecha, enums permitidos y rangos de limit u offset.

- Error inesperado
  - Verificar que la base este inicializada y que el entorno virtual correcto este activo.
