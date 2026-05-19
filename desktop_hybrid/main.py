from __future__ import annotations

import html
import json
import os
import socket
import sqlite3
import sys
import threading
import time
from contextlib import closing
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Protocol
from urllib.request import Request, urlopen

import webview
from webview.errors import WebViewException
from werkzeug.serving import make_server

from flask_server import _admin_panel_dist_ready, create_app
from src.hardware.hardware_integration import HardwareIntegration


# ── Configuración de ventana ──────────────────────────────────────────────
HOST         = "127.0.0.1"
PORT         = 5000
WIN_WIDTH    = 420
WIN_HEIGHT   = 800
WIN_TITLE    = "IdentifyMe"

# ── HTML del splash (logo + texto + barra de progreso) ───────────────────
SPLASH_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0D1B2A;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-family: 'Inter', system-ui, sans-serif;
    color: #fff;
    user-select: none;
  }

  .logo-wrap {
    width: 88px;
    height: 88px;
    border-radius: 24px;
    background: linear-gradient(135deg, #1A56DB, #0EA5E9);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 22px;
    box-shadow: 0 8px 32px rgba(26,86,219,0.45);
  }

  .logo-wrap svg {
    width: 48px;
    height: 48px;
    fill: none;
    stroke: #fff;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  h1 {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
  }

  .subtitle {
    font-size: 13px;
    color: rgba(255,255,255,0.55);
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 48px;
  }

  .bar-track {
    width: 240px;
    height: 5px;
    background: rgba(255,255,255,0.12);
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 14px;
  }

  .bar-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #1A56DB, #0EA5E9);
    border-radius: 999px;
    transition: width 0.3s ease;
  }

  .status-text {
    font-size: 12px;
    color: rgba(255,255,255,0.45);
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    min-height: 18px;
  }
</style>
</head>
<body>
  <div class="logo-wrap">
    <!-- ícono: scan-face estilo Lucide -->
    <svg viewBox="0 0 24 24">
      <path d="M3 7V5a2 2 0 0 1 2-2h2"/>
      <path d="M17 3h2a2 2 0 0 1 2 2v2"/>
      <path d="M21 17v2a2 2 0 0 1-2 2h-2"/>
      <path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
      <circle cx="12" cy="10" r="3"/>
      <path d="M7 16.8A6 6 0 0 1 12 14a6 6 0 0 1 5 2.8"/>
    </svg>
  </div>

  <h1>IdentifyMe</h1>
  <p class="subtitle">Sistema biométrico escolar</p>

  <div class="bar-track">
    <div class="bar-fill" id="bar"></div>
  </div>
  <p class="status-text" id="status">Iniciando...</p>

  <script>
    const bar    = document.getElementById('bar');
    const status = document.getElementById('status');

    window.updateProgress = (pct, msg) => {
      if (typeof pct === 'number') {
        bar.style.width = pct + '%';
      }
      if (msg) {
        status.textContent = msg;
      }
    };

    window.updateProgress(5, 'Iniciando...');
  </script>
</body>
</html>"""

# ── HTML de error visual ──────────────────────────────────────────────────
def error_html(title: str, detail: str, hint: str = "") -> str:
    hint_block = f'<p class="hint">{hint}</p>' if hint else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0D1B2A;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-family: 'Inter', system-ui, sans-serif;
    color: #fff;
    padding: 32px;
    text-align: center;
  }}
  .icon {{
    width: 72px; height: 72px;
    border-radius: 50%;
    background: rgba(185,28,28,0.18);
    border: 2px solid rgba(185,28,28,0.5);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 24px;
  }}
  .icon svg {{
    width: 36px; height: 36px;
    stroke: #FCA5A5; stroke-width: 2;
    stroke-linecap: round; stroke-linejoin: round; fill: none;
  }}
  h2 {{
    font-size: 20px; font-weight: 800;
    color: #FCA5A5; margin-bottom: 10px;
  }}
  .detail {{
    font-size: 13px; color: rgba(255,255,255,0.55);
    line-height: 1.6; margin-bottom: 16px;
    max-width: 320px;
  }}
  .hint {{
    font-size: 12px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 10px 16px;
    color: rgba(255,255,255,0.45);
    line-height: 1.6;
    max-width: 320px;
  }}
</style>
</head>
<body>
  <div class="icon">
    <svg viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  </div>
  <h2>{title}</h2>
  <p class="detail">{detail}</p>
  {hint_block}
</body>
</html>"""


# ── Estado del servidor ───────────────────────────────────────────────────
class ShutdownableServer(Protocol):
    def shutdown(self) -> None:
        ...


@dataclass
class ServerState:
    server: Optional[ShutdownableServer] = None
    thread: Optional[threading.Thread] = None
    startup_error: Optional[str] = None


# ── Validaciones de sistema ───────────────────────────────────────────────
class CheckStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    detail: str = ""


def _update_splash(splash: webview.Window, pct: int, message: str) -> None:
    try:
        splash.evaluate_js(
            "window.updateProgress(%s, %s);" % (pct, json.dumps(message))
        )
    except Exception:
        pass


def run_system_checks(update_cb: Callable[[int, str], None]) -> list[CheckResult]:
    dependencies = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("dlib", "dlib"),
        ("PIL", "Pillow"),
        ("face_recognition", "face_recognition"),
        ("tkinter", "Tkinter"),
    ]

    checks: list[tuple[str, Callable[[], CheckResult]]] = []

    for module_name, display_name in dependencies:
        def _make_dep_check(mod_name: str, name: str) -> Callable[[], CheckResult]:
            def _check() -> CheckResult:
                try:
                    __import__(mod_name)
                    return CheckResult(name=name, status=CheckStatus.SUCCESS)
                except Exception as exc:
                    return CheckResult(
                        name=name,
                        status=CheckStatus.ERROR,
                        detail=str(exc),
                    )

            return _check

        checks.append(
            (f"Dependencia: {display_name}", _make_dep_check(module_name, display_name))
        )

    def _check_camera() -> CheckResult:
        try:
            import cv2

            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                return CheckResult(name="Camara", status=CheckStatus.SUCCESS)
            return CheckResult(
                name="Camara",
                status=CheckStatus.ERROR,
                detail="No se pudo abrir la camara",
            )
        except Exception as exc:
            return CheckResult(name="Camara", status=CheckStatus.ERROR, detail=str(exc))

    def _check_display() -> CheckResult:
        try:
            import tkinter

            root = tkinter.Tk()
            root.withdraw()
            root.destroy()
            return CheckResult(name="Pantalla", status=CheckStatus.SUCCESS)
        except Exception as exc:
            return CheckResult(name="Pantalla", status=CheckStatus.ERROR, detail=str(exc))

    def _check_servo() -> CheckResult:
        try:
            return CheckResult(name="Servomotor", status=CheckStatus.SUCCESS)
        except Exception as exc:
            return CheckResult(
                name="Servomotor", status=CheckStatus.ERROR, detail=str(exc)
            )

    def _check_database() -> CheckResult:
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            db_path = os.path.join(base_dir, "database", "sqlite", "students.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            return CheckResult(name="Base de Datos", status=CheckStatus.SUCCESS)
        except Exception as exc:
            return CheckResult(
                name="Base de Datos", status=CheckStatus.ERROR, detail=str(exc)
            )

    checks.extend(
        [
            ("Verificando camara", _check_camera),
            ("Verificando pantalla", _check_display),
            ("Verificando servomotor", _check_servo),
            ("Verificando base de datos", _check_database),
        ]
    )

    results: list[CheckResult] = []
    total = len(checks)
    for index, (label, check_fn) in enumerate(checks, start=1):
        pct = int(index / total * 70)
        update_cb(pct, f"{label}...")
        results.append(check_fn())
        time.sleep(0.15)

    return results


# ── Utilidades de red ─────────────────────────────────────────────────────
def is_port_available(host: str, port: int) -> bool:
    """Devuelve True si el puerto TCP está libre."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def start_flask_server(state: ServerState) -> None:
    """Ejecuta Flask en hilo dedicado con servidor WSGI controlable."""
    try:
        app = create_app()
        http_server = make_server(HOST, PORT, app)
        state.server = http_server
        http_server.serve_forever()
    except Exception as exc:
        state.startup_error = str(exc)
        print(f"[ERROR] Flask no pudo iniciar: {exc}")


def wait_for_server(timeout_seconds: float = 12.0) -> bool:
    """Hace polling a /status hasta que el servidor responde o expira."""
    url      = f"http://{HOST}:{PORT}/status"
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        try:
            req = Request(url, method="GET")
            with urlopen(req, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.25)

    return False


def stop_server(state: ServerState) -> None:
    """Detiene Flask y espera a que el hilo termine."""
    if state.server is not None:
        try:
            state.server.shutdown()
        except Exception as exc:
            print(f"[WARN] Error al detener servidor Flask: {exc}")

    if state.thread is not None and state.thread.is_alive():
        state.thread.join(timeout=3)


# ── Punto de entrada principal ────────────────────────────────────────────
def run_desktop_app() -> int:

    # 1. Verificar puerto disponible
    if not is_port_available(HOST, PORT):
        win = webview.create_window(
            title=WIN_TITLE,
            html=error_html(
                title="Puerto ocupado",
                detail=f"El puerto {PORT} ya está en uso. Cierra la aplicación que lo ocupa e intenta de nuevo.",
                hint=f"Puedes identificar el proceso con: lsof -i :{PORT}  (macOS/Linux)  o  netstat -ano | findstr :{PORT}  (Windows)",
            ),
            width=WIN_WIDTH,
            height=WIN_HEIGHT,
            resizable=False,
        )
        webview.start(gui="qt", debug=False)
        return 1

    # 2. Mostrar splash mientras arranca Flask
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

    def _on_splash_shown():
        hardware.startup()
        _update_splash(splash, 8, "Verificando sistema...")
        results = run_system_checks(
            lambda pct, msg: _update_splash(splash, pct, msg)
        )
        errors = [r for r in results if r.status == CheckStatus.ERROR]

        if errors:
            hardware.error()
            detail_lines = [f"- {r.name}: {r.detail}" for r in errors if r.detail]
            detail = "<br>".join(html.escape(line) for line in detail_lines)
            splash.load_html(
                error_html(
                    title="Verificacion fallida",
                    detail=detail
                    or "Se encontraron errores durante las verificaciones.",
                    hint="Instala las dependencias faltantes y vuelve a abrir la aplicacion.",
                )
            )
            return

        _update_splash(splash, 80, "Iniciando servidor...")
        thread = state.thread
        if thread is None:
            hardware.error()
            splash.load_html(
                error_html(
                    title="No se pudo iniciar",
                    detail="No se pudo crear el hilo del servidor Flask.",
                    hint="Revisa la consola y vuelve a abrir la aplicacion.",
                )
            )
            return

        thread.start()
        ready = wait_for_server()

        if not ready:
            hardware.error()
            detail = state.startup_error or "Tiempo de espera agotado al iniciar Flask."
            splash.load_html(
                error_html(
                    title="No se pudo iniciar",
                    detail=detail,
                    hint="Revisa la consola para más detalles del error.",
                )
            )
            return

        # 3. Flask listo → cargar la app real en la misma ventana
        _update_splash(splash, 96, "Preparando interfaz...")
        target_path = "/admin-panel/" if _admin_panel_dist_ready() else "/"
        splash.load_url(f"http://{HOST}:{PORT}{target_path}")
        hardware.success()

    # El evento `shown` dispara _on_splash_shown en un hilo separado
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