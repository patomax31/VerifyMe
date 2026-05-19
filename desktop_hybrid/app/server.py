from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional
from urllib.request import Request, urlopen

from werkzeug.serving import make_server

from flask_server import create_app
from .config import HOST, PORT


@dataclass
class ServerState:
    server: Optional[object] = None
    thread: Optional[threading.Thread] = None
    startup_error: Optional[str] = None


def start_flask_server(state: ServerState) -> None:
    try:
        app = create_app()
        http_server = make_server(HOST, PORT, app)
        state.server = http_server
        http_server.serve_forever()
    except Exception as exc:
        state.startup_error = str(exc)
        print(f"[ERROR] Flask no pudo iniciar: {exc}")


def wait_for_server(timeout_seconds: float = 12.0) -> bool:
    url = f"http://{HOST}:{PORT}/status"
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
    if state.server is not None:
        try:
            state.server.shutdown()
        except Exception as exc:
            print(f"[WARN] Error al detener servidor Flask: {exc}")

    if state.thread is not None and state.thread.is_alive():
        state.thread.join(timeout=3)
