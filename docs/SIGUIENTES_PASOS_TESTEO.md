# Siguientes pasos para testeo

Este documento lista pruebas recomendadas para validar el log de acceso por sesion activa e historica.

## 1) Preparacion

- Asegurar entorno virtual activo.
- Verificar que la base esta inicializada.
- Confirmar que no exista una sesion activa si se desea probar inicio de sesion.

## 2) Pruebas de sesion activa

- Iniciar sesion activa (flujo del sistema).
- Registrar accesos de estudiantes (entrada/salida, concedido/denegado).
- Consultar logs de sesion activa via CLI:
  - scripts/db_queries.py logs --active-session --format table
- Verificar que los resultados solo incluyan estudiantes y esten dentro del rango de la sesion.

## 3) Pruebas de sesion historica

- Cerrar sesion activa (cierre manual).
- Consultar sesiones historicas:
  - scripts/db_queries.py sessions --active false --format table
- Tomar un id de sesion y consultar logs:
  - scripts/db_queries.py logs --session-id <id> --format json
- Verificar que el rango de fechas coincida con inicio/fin guardados en la sesion.

## 4) Pruebas de validacion

- Intentar usar --active-session con --session-id y validar error.
- Intentar usar --active-session junto a --from-datetime/--to-datetime y validar error.
- Intentar usar --session-id con tipo_usuario PERSONAL y validar error.
- Probar limites fuera de rango para confirmar validaciones (limit <= 0, limit > 1000).

## 5) Pruebas de consistencia de datos

- Abrir y cerrar varias sesiones (no simultaneas).
- Confirmar que solo una sesion activa es posible.
- Verificar que la sesion activa siempre tenga estado_activa = 1.

## 6) Pruebas de rendimiento basicas

- Insertar un volumen representativo de logs.
- Consultar logs por sesion activa y por sesion historica con limit 100/500/1000.
- Confirmar tiempos aceptables para uso diario.

## 7) Evidencias recomendadas

- Capturas de salida CLI (tabla y json).
- Registro de tiempos de consulta.
- Lista de sesiones creadas durante la prueba.
