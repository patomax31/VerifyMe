"""Control de servomotor para torniquete.

Permite abrir en acceso exitoso, esperar y volver a bloqueo.
Soporta fallback simulado cuando GPIO no esta disponible.
"""

from __future__ import annotations

import os
import threading
import time
from typing import Optional


class _MockPWM:
    def __init__(self, pin: int, freq: float) -> None:
        self.pin = pin
        self.freq = freq

    def start(self, duty_cycle: float) -> None:
        print(f"[servo:MOCK] PWM start pin={self.pin}, duty={duty_cycle}, freq={self.freq}")

    def ChangeDutyCycle(self, duty_cycle: float) -> None:
        print(f"[servo:MOCK] PWM duty -> {duty_cycle}")

    def stop(self) -> None:
        print("[servo:MOCK] PWM stop")


class _MockGPIO:
    BCM = "BCM"
    OUT = "OUT"

    def setwarnings(self, _state: bool) -> None:
        pass

    def setmode(self, mode) -> None:
        print(f"[servo:MOCK] setmode({mode})")

    def setup(self, pin: int, mode) -> None:
        print(f"[servo:MOCK] setup(pin={pin}, mode={mode})")

    def PWM(self, pin: int, freq: float) -> _MockPWM:
        return _MockPWM(pin, freq)

    def cleanup(self, pin: Optional[int] = None) -> None:
        print(f"[servo:MOCK] cleanup(pin={pin})")


class ServoMotorController:
    """Controla un servo SG90 usando PWM en GPIO."""

    def __init__(self) -> None:
        self.pin = int(os.getenv("GPIO_SERVO_PIN", "17"))
        self.frequency = float(os.getenv("GPIO_SERVO_FREQUENCY", "50"))
        self.lock_angle = float(os.getenv("SERVO_LOCK_ANGLE", "0"))
        self.unlock_angle = float(os.getenv("SERVO_UNLOCK_ANGLE", "90"))
        self.settle_delay = float(os.getenv("SERVO_SETTLE_DELAY", "0.5"))
        self.enabled = os.getenv("HARDWARE_ENABLED", "1").strip() != "0"

        self._gpio = self._load_gpio_backend()
        self._pwm = None
        self._setup_done = False
        self._lock = threading.Lock()

    def _load_gpio_backend(self):
        if not self.enabled:
            return _MockGPIO()

        try:
            import RPi.GPIO as GPIO  # type: ignore

            return GPIO
        except Exception as exc:
            print(f"[servo] GPIO no disponible, modo simulado: {exc}")
            return _MockGPIO()

    def setup(self) -> None:
        if self._setup_done:
            return

        self._gpio.setwarnings(False)
        self._gpio.setmode(self._gpio.BCM)
        self._gpio.setup(self.pin, self._gpio.OUT)
        self._pwm = self._gpio.PWM(self.pin, self.frequency)
        self._pwm.start(0)
        self.move_to_angle(self.lock_angle)
        self._setup_done = True

    @staticmethod
    def _angle_to_duty_cycle(angle: float) -> float:
        # Formula estandar para SG90 en 50 Hz: 2.5 a 12.5 aprox.
        angle = max(0.0, min(180.0, angle))
        return 2.5 + (angle / 180.0) * 10.0

    def move_to_angle(self, angle: float) -> None:
        if self._pwm is None:
            raise RuntimeError("PWM no inicializado")

        duty = self._angle_to_duty_cycle(angle)
        self._pwm.ChangeDutyCycle(duty)
        time.sleep(self.settle_delay)
        # Evita jitter continuo en algunos servos.
        self._pwm.ChangeDutyCycle(0)

    def open_then_close(self, hold_seconds: float = 10.0) -> None:
        self.setup()
        with self._lock:
            self.move_to_angle(self.unlock_angle)
            time.sleep(max(0.0, hold_seconds))
            self.move_to_angle(self.lock_angle)

    def cleanup(self) -> None:
        try:
            if self._pwm is not None:
                self._pwm.stop()
        except Exception as exc:
            print(f"[servo] Error al detener PWM: {exc}")
        finally:
            self._pwm = None

        try:
            self._gpio.cleanup()
        except Exception as exc:
            print(f"[servo] Error en cleanup GPIO: {exc}")
        finally:
            self._setup_done = False


_controller = ServoMotorController()

_DEFAULT_HOLD_SECONDS = float(os.getenv("SERVO_HOLD_SECONDS", "10"))
_ALWAYS_ACTIVE_DEFAULT = os.getenv("SERVO_ALWAYS_ACTIVE", "0").strip().lower() in {"1", "true", "yes", "on"}
_hold_seconds = _DEFAULT_HOLD_SECONDS
_always_active = _ALWAYS_ACTIVE_DEFAULT


def get_servo_settings() -> dict:
    return {
        "hold_seconds": float(_hold_seconds),
        "always_active": bool(_always_active),
    }


def update_servo_settings(*, hold_seconds: float, always_active: bool) -> None:
    global _hold_seconds, _always_active

    _hold_seconds = max(0.0, float(hold_seconds))
    _always_active = bool(always_active)

    try:
        _controller.setup()
        if _always_active:
            _controller.move_to_angle(_controller.unlock_angle)
        else:
            _controller.move_to_angle(_controller.lock_angle)
    except Exception as exc:
        print(f"[servo] Error al aplicar configuracion: {exc}")


def access_successful(wait_seconds: float | None = None, non_blocking: bool = True) -> None:
    """Secuencia de torniquete para acceso concedido.

    Gira a posicion de apertura, espera y vuelve a bloqueo.
    """

    if _always_active:
        try:
            _controller.setup()
            _controller.move_to_angle(_controller.unlock_angle)
        except Exception as exc:
            print(f"[servo] Error al mantener activo: {exc}")
        return

    hold_seconds = _hold_seconds if wait_seconds is None else float(wait_seconds)

    def _job() -> None:
        try:
            _controller.open_then_close(hold_seconds=hold_seconds)
        except Exception as exc:
            print(f"[servo] Error en secuencia de acceso: {exc}")

    if non_blocking:
        threading.Thread(target=_job, daemon=True).start()
    else:
        _job()


def cleanup() -> None:
    """Limpia recursos de PWM/GPIO."""
    _controller.cleanup()
