#!/usr/bin/env python3
"""
Simple camera test for Raspberry Pi 5
"""
import cv2
import sys
import signal
import threading
import time

def timeout_handler(signum, frame):
    print("\n[TIMEOUT] Ningún dispositivo de video responde en 5 segundos")
    sys.exit(1)

print("TEST DE CAMARA - Raspberry Pi 5\n")
print("Dispositivos disponibles:")

import subprocess
result = subprocess.run("v4l2-ctl --list-devices", shell=True, capture_output=True, text=True)
print(result.stdout)

print("\nIntentando abrir cada dispositivo (5 segundos timeout)...\n")

found = False
for i in range(0, 36):
    cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
    if not cap.isOpened():
        continue
    
    print(f"[{i}] Abierto. Intentando leer frame...")
    
    # Timeout de 3 segundos para cada lectura
    def read_frame():
        global found
        ret, frame = cap.read()
        if ret:
            print(f"    [OK] Frame leido! {frame.shape}")
            found = True
    
    thread = threading.Thread(target=read_frame)
    thread.daemon = True
    thread.start()
    thread.join(timeout=3)
    
    cap.release()
    
    if found:
        print("\n[EXITO] Camara detectada en /dev/video" + str(i))
        sys.exit(0)

print("\n[FALLO] No se pudo leer ninguna camara")
print("\nChecklist:")
print("  [ ] Verificaste que el cable este en puerto CSI (no HDMI)?")
print("  [ ] Verificaste que el ribbon cable este correctamente conectado?")
print("  [ ] Ejecutaste: sudo raspi-config nonint set_camera 1")
print("  [ ] Ejecutaste: sudo rpi-update")
print("  [ ] Hiciste reboot?")
