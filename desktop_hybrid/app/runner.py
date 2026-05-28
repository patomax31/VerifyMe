from __future__ import annotations

import html
import sys
import threading
import time
import webbrowser
from typing import Optional

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

    def _startup_sequence(splash: Optional[webview.Window] = None) -> bool:
        """Run startup sequence: hardware, checks, start server and load UI.

        If `splash` is None the function will print progress and open the system
        browser instead of loading a webview window.
        Returns True on success, False on failure.
        """
        hardware.startup()
        if splash:
            update_splash(splash, 8, "Verificando sistema...")
        else:
            print("[INFO] Verificando sistema...")

        results = run_system_checks(lambda pct, msg: update_splash(splash, pct, msg) if splash else print(f"[CHECK] {pct}% {msg}"))
        errors = [r for r in results if r.status == CheckStatus.ERROR]

        if errors:
            hardware.error()
            detail_lines = [f"- {r.name}: {r.detail}" for r in errors if r.detail]
            detail = format_error_details(detail_lines)
            if splash:
                splash.load_html(
                    error_html(
                        title="Verificacion fallida",
                        detail=detail or "Se encontraron errores durante las verificaciones.",
                        hint="Instala las dependencias faltantes y vuelve a abrir la aplicacion.",
                    )
                )
            else:
                print("[ERROR] Verificacion fallida:")
                print(detail or "Se encontraron errores durante las verificaciones.")
            return False

        if splash:
            update_splash(splash, 80, "Iniciando servidor...")
        else:
            print("[INFO] Iniciando servidor...")

        state.thread.start()
        ready = wait_for_server()

        if not ready:
            hardware.error()
            detail = html.escape(state.startup_error or "Tiempo de espera agotado al iniciar Flask.")
            if splash:
                splash.load_html(
                    error_html(
                        title="No se pudo iniciar",
                        detail=detail,
                        hint="Revisa la consola para mas detalles del error.",
                    )
                )
            else:
                print(f"[ERROR] No se pudo iniciar el servidor: {detail}")
            return False

        if splash:
            update_splash(splash, 96, "Preparando interfaz...")
            target_path = "/admin-panel/" if _admin_panel_dist_ready() else "/"
            splash.load_url(f"http://{HOST}:{PORT}{target_path}")
        else:
            target_path = "/admin-panel/" if _admin_panel_dist_ready() else "/"
            print(f"[INFO] Servidor listo en http://{HOST}:{PORT}{target_path}")
        hardware.success()
        return True

    def _on_splash_shown() -> None:
        _startup_sequence(splash)

    splash.events.shown += _on_splash_shown

    try:
        webview.start(gui="qt", debug=False)
    except WebViewException as exc:
        print("[ERROR] No se pudo iniciar PyWebview con backend Qt.")
        print(f"[ERROR] Detalle: {exc}")
        print("[HINT] Instala dependencias: pip install qtpy PyQt6 PyQt6-WebEngine")
        # Fallback: iniciar servidor en modo headless y abrir navegador por defecto
        print("[INFO] Iniciando servidor en modo headless y abriendo navegador por defecto...")
        ok = _startup_sequence(None)
        if not ok:
            return 1
        target_path = "/admin-panel/" if _admin_panel_dist_ready() else "/"
        try:
            webbrowser.open(f"http://{HOST}:{PORT}{target_path}")
        except Exception:
            print(f"[WARN] No se pudo abrir el navegador automaticamente. Abre: http://{HOST}:{PORT}{target_path}")
        try:
            while state.thread.is_alive():
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    finally:
        hardware.cleanup()
        stop_server(state)

    return 0


if __name__ == "__main__":
    sys.exit(run_desktop_app())
