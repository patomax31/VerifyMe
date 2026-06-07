#!/usr/bin/env python3
"""Prueba de LED, servomotor, buzzer y tira LED para Raspberry Pi 5.

Hace cuatro cosas:
- Enciende un LED durante 5 segundos.
- Mueve un servomotor a una posicion de prueba y luego lo regresa.
- Suena un buzzer en sincronización.
- Controla brillo de una tira LED.

Pines por defecto:
- LED: GPIO 17
- Servo: GPIO 18
- Buzzer: GPIO 27
- Tira LED: GPIO 22

Uso:
    sudo python test_led_servo_raspberry.py
"""

from __future__ import annotations

import os
import time

from gpiozero import (
    LED,
    AngularServo,
    Buzzer,
    PWMLED,
    Device
)
from gpiozero.pins.lgpio import LGPIOFactory


LED_PIN = int(os.getenv("GPIO_LED", "17"))
SERVO_PIN = int(os.getenv("GPIO_SERVO", "18"))
BUZZER_PIN = int(os.getenv("GPIO_BUZZER", "27"))
STRIP_LED_PIN = int(os.getenv("GPIO_STRIP_LED", "22"))


def main() -> int:
    try:
        # Backend recomendado para Raspberry Pi 5
        Device.pin_factory = LGPIOFactory()

        print(f"Inicializando LED en GPIO {LED_PIN}...")
        led = LED(LED_PIN)

        print(f"Inicializando servomotor en GPIO {SERVO_PIN}...")

        # Configuración similar a Arduino Servo.h
        servo = AngularServo(
            SERVO_PIN,
            min_angle=0,
            max_angle=120,
            min_pulse_width=0.000544,  # 544 µs
            max_pulse_width=0.0024,    # 2400 µs
            frame_width=0.02           # 20 ms (50 Hz)
        )

        print(f"Inicializando buzzer en GPIO {BUZZER_PIN}...")
        buzzer = Buzzer(BUZZER_PIN)

        print(f"Inicializando tira LED en GPIO {STRIP_LED_PIN}...")
        strip_led = PWMLED(STRIP_LED_PIN)

        try:
            print("\n=== INICIANDO PRUEBA ===\n")

            # Posición inicial
            servo.angle = 0
            time.sleep(1)

            # Fase 1
            print(f"Probando LED en GPIO {LED_PIN}...")
            print("Tira LED a brillo maximo...")
            print("Buzzer sonando...")

            led.on()
            strip_led.on()
            buzzer.on()

            time.sleep(1)

            # Fase 2
            print("Moviendo servomotor a 100 grados...")
            servo.angle = 100
            time.sleep(1.5)

            # Fase 3
            print("Buzzer intermitente + efecto respiracion...")

            for _ in range(4):
                buzzer.off()
                strip_led.value = 0.3
                time.sleep(0.3)

                buzzer.on()
                strip_led.value = 1.0
                time.sleep(0.3)

            # Fase 4
            print("Regresando servomotor a 0 grados...")

            led.off()
            buzzer.off()
            strip_led.off()

            servo.angle = 0
            time.sleep(1.5)

            # Confirmación
            print("Beep de confirmacion...")

            for _ in range(2):
                buzzer.on()
                time.sleep(0.2)
                buzzer.off()
                time.sleep(0.2)

            print("\n=== PRUEBA COMPLETADA EXITOSAMENTE ===\n")
            return 0

        finally:
            try:
                led.off()
                buzzer.off()
                strip_led.off()

                servo.angle = 0
                time.sleep(0.5)

                led.close()
                buzzer.close()
                strip_led.close()
                servo.close()

            except Exception:
                pass

    except Exception as exc:
        print(f"Error: {exc}")

        import traceback
        traceback.print_exc()

        return 1


if __name__ == "__main__":
    raise SystemExit(main())