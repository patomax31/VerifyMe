#!/usr/bin/env python3
"""Prueba de LED, servomotor, buzzer y tira LED para Raspberry Pi 5.

Hace cuatro cosas:
- Enciende un LED durante 5 segundopython3 src/hardware/test_led_servo_raspberry.pys.
- Mueve un servomotor a una posicion de prueba y luego lo regresa.
- Suena un buzzer en sincronización.
- Controla brillo de una tira LED.

Pines por defecto:
- LED: GPIO 17
- Servo: GPIO 18
- Buzzer: GPIO 27
- Tira LED: GPIO 22

Usa gpiozero con lgpio backend (compatible con RPi 5).

Uso:
    sudo python test_led_servo_raspberry.py

Variables de entorno:
    GPIO_LED=17 GPIO_SERVO=18 GPIO_BUZZER=27 GPIO_STRIP_LED=22 sudo python test_led_servo_raspberry.py
"""

from __future__ import annotations

import os
import time
from gpiozero import LED, AngularServo, Buzzer, PWMLED, Device
from gpiozero.pins.lgpio import LGPIOFactory


LED_PIN = int(os.getenv("GPIO_LED", "17"))
SERVO_PIN = int(os.getenv("GPIO_SERVO", "18"))
BUZZER_PIN = int(os.getenv("GPIO_BUZZER", "27"))
STRIP_LED_PIN = int(os.getenv("GPIO_STRIP_LED", "22"))


def main() -> int:
    try:
        # Usar lgpio que es el backend recomendado para RPi 5
        Device.pin_factory = LGPIOFactory()
        
        print(f"Inicializando LED en GPIO {LED_PIN}...")
        led = LED(LED_PIN)
        
        print(f"Inicializando servomotor en GPIO {SERVO_PIN}...")
        servo = AngularServo(SERVO_PIN, min_angle=-90, max_angle=90)
        
        print(f"Inicializando buzzer en GPIO {BUZZER_PIN}...")
        buzzer = Buzzer(BUZZER_PIN)
        
        print(f"Inicializando tira LED en GPIO {STRIP_LED_PIN}...")
        strip_led = PWMLED(STRIP_LED_PIN)

        try:
            print("\n=== INICIANDO PRUEBA ===\n")
            
            # Fase 1: LED encendido + Tira LED a brillo máximo + Buzzer sonando
            print(f"Probando LED en GPIO {LED_PIN} durante 5 segundos...")
            print(f"Tira LED a brillo maximo...")
            print(f"Buzzer sonando...")
            led.on()
            strip_led.on()  # Brillo máximo
            buzzer.on()
            time.sleep(1)
            
            # Fase 2: Mover servo mientras continúa el LED y buzzer
            print(f"Moviendo servomotor a 90 grados...")
            servo.angle = 90
            time.sleep(0.8)
            
            # Fase 3: Buzzer intermitente + Tira LED con efecto de respiración
            print("Buzzer intermitente + Tira LED con efecto de respiracion...")
            for i in range(4):
                buzzer.off()
                strip_led.value = 0.3  # Brillo bajo
                time.sleep(0.3)
                buzzer.on()
                strip_led.value = 1.0  # Brillo máximo
                time.sleep(0.3)
            
            # Fase 4: Todo apagado y servo regresa
            print("Apagando LED, tira LED, buzzer y regresando servo a posicion inicial...")
            led.off()
            buzzer.off()
            strip_led.off()  # Apagar tira LED
            servo.angle = -90
            time.sleep(0.8)
            
            # Prueba final: Un beep de confirmación
            print("Beep de confirmacion...")
            buzzer.on()
            time.sleep(0.2)
            buzzer.off()
            time.sleep(0.2)
            buzzer.on()
            time.sleep(0.2)
            buzzer.off()
            
            print("\n=== PRUEBA COMPLETADA EXITOSAMENTE ===\n")
            return 0
        finally:
            led.off()
            buzzer.off()
            strip_led.off()
            servo.angle = 0
            led.close()
            buzzer.close()
            strip_led.close()
            servo.close()

    except Exception as exc:
        print(f"Error: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())