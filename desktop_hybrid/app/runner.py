from __future__ import annotations

import html
import sys
import threading

import webview
from webview.errors import WebViewException

from flask_server import _admin_panel_dist_ready
from src.hardware.hardware_integration import HardwareIntegration

from .config import HOST, PORT, WIN_HEIGHT, WIN_TITLE, WIN_WIDTH
from .network import is_port_available
from .server import ServerState, start_flask_server, stop_server, wait_for_server
from .system_checks import CheckStatus, run_system_checks
from .ui import SPLASH_HTML, error_html, format_error_details, update_splash


def run_desktop_app() -> int:
    if not is_port_available(HOST, PORT):
        webview.create_window(
            title=WIN_TITLE,
            html=error_html(
                title="Puerto ocupado",
                detail=(
                    f"El puerto {PORT} ya esta en uso. Cierra la aplicacion que lo "
                    "ocupa e intenta de nuevo."
                ),
                hint=(
                    f"Puedes identificar el proceso con: lsof -i :{PORT}  "
                    "(macOS/Linux)  o  netstat -ano | findstr :{PORT}  (Windows)"
                ),
            ),
            width=WIN_WIDTH,
            height=WIN_HEIGHT,
            resizable=False,
        )
        webview.start(gui="qt", debug=False)
        return 1

    splash = webview.create_window(
        title=WIN_TITLE,
        html=SPLASH_HTML,
        width=WIN_WIDTH,
        height=WIN_HEIGHT,
        resizable=False,
    )

    hardware = HardwareIntegration()
    state = ServerState()
    state.thread = threading.Thread(
        target=start_flask_server, args=(state,), daemon=True
    )

    def _on_splash_shown() -> None:
        hardware.startup()
        update_splash(splash, 8, "Verificando sistema...")
        results = run_system_checks(
            lambda pct, msg: update_splash(splash, pct, msg)
        )
        errors = [r for r in results if r.status == CheckStatus.ERROR]

        if errors:
            hardware.error()
            detail_lines = [f"- {r.name}: {r.detail}" for r in errors if r.detail]
            detail = format_error_details(detail_lines)
            splash.load_html(
                error_html(
                    title="Verificacion fallida",
                    detail=detail
                    or "Se encontraron errores durante las verificaciones.",
                    hint="Instala las dependencias faltantes y vuelve a abrir la aplicacion.",
                )
            )
            return

        update_splash(splash, 80, "Iniciando servidor...")
        state.thread.start()
        ready = wait_for_server()

        if not ready:
            hardware.error()
            detail = html.escape(state.startup_error or "Tiempo de espera agotado al iniciar Flask.")
            splash.load_html(
                error_html(
                    title="No se pudo iniciar",
                    detail=detail,
                    hint="Revisa la consola para mas detalles del error.",
                )
            )
            return

        update_splash(splash, 96, "Preparando interfaz...")
        target_path = "/admin-panel/" if _admin_panel_dist_ready() else "/"
        splash.load_url(f"http://{HOST}:{PORT}{target_path}")
        hardware.success()

    splash.events.shown += _on_splash_shown

    try:
        webview.start(gui="qt", debug=False)
    except WebViewException as exc:
        print("[ERROR] No se pudo iniciar PyWebview con backend Qt.")
        print(f"[ERROR] Detalle: {exc}")
        print("[HINT] Instala dependencias: pip install qtpy PyQt6 PyQt6-WebEngine")
        return 1
    finally:
        hardware.cleanup()
        stop_server(state)

    return 0


if __name__ == "__main__":
    sys.exit(run_desktop_app())
