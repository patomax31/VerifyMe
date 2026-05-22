import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.sqlite.reporting import (
    list_access_logs,
    list_access_logs_for_active_session,
    list_access_logs_for_session_id,
    list_failed_attempts,
    list_sessions,
    list_students,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Consultas administrativas seguras para SQLite (estudiantes y logs)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    students = subparsers.add_parser("students", help="Listar estudiantes desde la vista vw_estudiantes")
    students.add_argument("--active", choices=["all", "true", "false"], default="all")
    students.add_argument("--grado")
    students.add_argument("--grupo")
    students.add_argument("--turno")
    students.add_argument("--nombre")
    students.add_argument("--limit", type=int, default=100)
    students.add_argument("--offset", type=int, default=0)
    students.add_argument("--format", choices=["json", "table"], default="table")

    logs = subparsers.add_parser("logs", help="Listar logs desde la vista vw_logs_acceso")
    logs.add_argument("--from-datetime")
    logs.add_argument("--to-datetime")
    logs.add_argument("--tipo-usuario", choices=["ESTUDIANTE", "PERSONAL"])
    logs.add_argument("--tipo-evento", choices=["Entrada", "Salida"])
    logs.add_argument("--acceso-concedido", choices=["all", "true", "false"], default="all")
    logs.add_argument("--active-session", action="store_true")
    logs.add_argument("--session-id", type=int)
    logs.add_argument("--limit", type=int, default=100)
    logs.add_argument("--offset", type=int, default=0)
    logs.add_argument("--format", choices=["json", "table"], default="table")

    failed = subparsers.add_parser("failed", help="Listar intentos fallidos desde vw_intentos_fallidos")
    failed.add_argument("--from-datetime")
    failed.add_argument("--to-datetime")
    failed.add_argument("--tipo-usuario", choices=["ESTUDIANTE", "PERSONAL"])
    failed.add_argument("--limit", type=int, default=100)
    failed.add_argument("--offset", type=int, default=0)
    failed.add_argument("--format", choices=["json", "table"], default="table")

    sessions = subparsers.add_parser(
        "sessions", help="Listar sesiones de acceso (actual e historicas)"
    )
    sessions.add_argument("--active", choices=["all", "true", "false"], default="all")
    sessions.add_argument("--limit", type=int, default=100)
    sessions.add_argument("--offset", type=int, default=0)
    sessions.add_argument("--format", choices=["json", "table"], default="table")

    return parser


def _to_bool_or_none(value: str) -> Optional[bool]:
    if value == "all":
        return None
    return value == "true"


def _print_json(rows: List[Dict[str, Any]]) -> None:
    print(json.dumps(rows, ensure_ascii=True, indent=2))


def _print_table(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        print("Sin resultados.")
        return

    columns = list(rows[0].keys())
    widths = {col: len(col) for col in columns}

    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row.get(col, ""))))

    header = " | ".join(col.ljust(widths[col]) for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)
    print(header)
    print(separator)

    for row in rows:
        line = " | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns)
        print(line)


def _emit(rows: List[Dict[str, Any]], output_format: str) -> None:
    if output_format == "json":
        _print_json(rows)
        return
    _print_table(rows)


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "students":
            rows = list_students(
                active_only=_to_bool_or_none(args.active),
                grado=args.grado,
                grupo=args.grupo,
                turno=args.turno,
                nombre_contains=args.nombre,
                limit=args.limit,
                offset=args.offset,
            )
            _emit(rows, args.format)
            return 0

        if args.command == "logs":
            if args.active_session and args.session_id is not None:
                raise ValueError("No se puede combinar --active-session con --session-id")

            if args.active_session or args.session_id is not None:
                if args.from_datetime or args.to_datetime:
                    raise ValueError("No use --from-datetime/--to-datetime con sesiones")
                if args.tipo_usuario and args.tipo_usuario != "ESTUDIANTE":
                    raise ValueError("Las sesiones solo aplican a ESTUDIANTE")

                if args.active_session:
                    rows = list_access_logs_for_active_session(
                        tipo_evento=args.tipo_evento,
                        acceso_concedido=_to_bool_or_none(args.acceso_concedido),
                        limit=args.limit,
                        offset=args.offset,
                    )
                else:
                    rows = list_access_logs_for_session_id(
                        session_id=args.session_id,
                        tipo_evento=args.tipo_evento,
                        acceso_concedido=_to_bool_or_none(args.acceso_concedido),
                        limit=args.limit,
                        offset=args.offset,
                    )
            else:
                rows = list_access_logs(
                    from_datetime=args.from_datetime,
                    to_datetime=args.to_datetime,
                    tipo_usuario=args.tipo_usuario,
                    tipo_evento=args.tipo_evento,
                    acceso_concedido=_to_bool_or_none(args.acceso_concedido),
                    limit=args.limit,
                    offset=args.offset,
                )
            _emit(rows, args.format)
            return 0

        if args.command == "failed":
            rows = list_failed_attempts(
                from_datetime=args.from_datetime,
                to_datetime=args.to_datetime,
                tipo_usuario=args.tipo_usuario,
                limit=args.limit,
                offset=args.offset,
            )
            _emit(rows, args.format)
            return 0

        if args.command == "sessions":
            rows = list_sessions(
                active_only=_to_bool_or_none(args.active),
                limit=args.limit,
                offset=args.offset,
            )
            _emit(rows, args.format)
            return 0

        parser.print_help()
        return 2
    except ValueError as exc:
        print(f"Error de validacion: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Error inesperado: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
