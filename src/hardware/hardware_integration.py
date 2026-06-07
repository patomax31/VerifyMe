"""Orquesta audio, leds y servomotor para eventos del sistema."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

from . import audio, leds, servomotor


def _run_led_servo_test() -> None:
    """Ejecuta el script de prueba LED/servo cuando se detecta acceso concedido."""
    try:
        # Ruta del script relativa al directorio de hardware
        script_path = Path(__file__).parent / "test_led_servo_raspberry.py"
        
        if not script_path.exists():
            print(f"[hardware] Advertencia: No se encontró {script_path}")
            return
        
        print(f"[hardware] Ejecutando script LED/servo: {script_path}")
        
        # Ejecutar con sudo para acceso a GPIO
        subprocess.run(
            ["sudo", "python3", str(script_path)],
            timeout=30,
            capture_output=True,
            text=True,
            check=False
        )
    except subprocess.TimeoutExpired:
        print("[hardware] Timeout ejecutando script LED/servo")
    except Exception as exc:
        print(f"[hardware] Error ejecutando script LED/servo: {exc}")


class HardwareIntegration:
    """Fachada de hardware para eventos de la app."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def startup(self) -> None:
        self._safe_call(audio.start_up)

    def success(self) -> None:
        self._safe_call(audio.access_successful)
        self._safe_call(lambda: leds.leds_turnon(success=True))
        self._safe_call(servomotor.access_successful)
        self._safe_call(_run_led_servo_test)

    def error(self) -> None:
        self._safe_call(audio.access_invalid)
        self._safe_call(lambda: leds.leds_turnon(success=False))

    def access_successful(self) -> None:
        self.success()

    def access_invalid(self) -> None:
        self.error()

    def registration(self) -> None:
        self._safe_call(audio.registration)
        self._safe_call(lambda: leds.leds_turnon(success=True))

    def open_door(self) -> None:
        """Ejecuta solo el script LED/servo para abrir la puerta manualmente."""
        self._safe_call(_run_led_servo_test)

    def cleanup(self) -> None:
        self._safe_call(audio.cleanup)
        self._safe_call(leds.cleanup)
        self._safe_call(servomotor.cleanup)

    def _safe_call(self, fn: Callable[[], None]) -> None:
        if not self.enabled:
            return
        try:
            fn()
        except Exception as exc:
            print(f"[hardware] Error en evento: {exc}")
