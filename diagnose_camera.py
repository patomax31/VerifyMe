#!/usr/bin/env python3
"""
Script de diagnóstico para Raspberry Pi Camera 2 con Raspberry Pi 5
"""
import os
import sys
import subprocess
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_command(cmd, description):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        print(f"✓ {description}")
        if result.stdout:
            print(f"  {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"✗ {description}: {e}")
        return False

def main():
    print("\n🎥 DIAGNÓSTICO DE CÁMARA - RASPBERRY PI 5 + CAMERA 2\n")
    
    # 1. Check video devices
    print_section("1. Dispositivos de Video Disponibles")
    devices = list(Path("/dev").glob("video*"))
    if devices:
        print(f"✓ Encontrados {len(devices)} dispositivo(s):")
        for dev in sorted(devices):
            print(f"  - {dev}")
    else:
        print("✗ ¡No se encontraron dispositivos de video!")
        print("  → Verifica que la cámara esté habilitada en raspi-config")
    
    # 2. Check libcamera
    print_section("2. Verificar libcamera")
    check_command("dpkg -l | grep libcamera", "Libcamera instalado")
    check_command("libcamera-hello --version", "libcamera versión")
    
    # 3. Check V4L2
    print_section("3. Verificar V4L2")
    check_command("v4l2-ctl --list-devices", "Dispositivos V4L2")
    
    # 4. Check OpenCV
    print_section("4. Verificar OpenCV")
    try:
        import cv2
        print(f"✓ OpenCV versión: {cv2.__version__}")
    except ImportError:
        print("✗ OpenCV no está instalado")
    
    # 5. Test camera with libcamera
    print_section("5. Test Rápido con libcamera")
    check_command("timeout 2 libcamera-hello --preview off 2>&1 | head -5", 
                  "Prueba libcamera-hello")
    
    # 6. Test camera with OpenCV
    print_section("6. Test Rápido con OpenCV")
    try:
        import cv2
        for i in range(20):
            if Path(f"/dev/video{i}").exists():
                cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"✓ Cámara detectada en /dev/video{i}")
                        print(f"  Resolución: {frame.shape[1]}x{frame.shape[0]}")
                    cap.release()
                    break
    except Exception as e:
        print(f"✗ Error en test OpenCV: {e}")
    
    # 7. Recommendations
    print_section("7. Recomendaciones")
    print("""
Si NO ves dispositivos de video:
  1. ssh pi@raspberrypi.local
  2. sudo raspi-config
     → Interfacing Options → Camera → Enable
  3. sudo reboot

Si ves /dev/video* pero OpenCV no abre cámara:
  1. sudo apt install -y libcamera-dev python3-picamera2
  2. Edita /etc/libcamera/libcamera.conf:
     sudo nano /etc/libcamera/libcamera.conf
     Asegúrate de tener: use_libcamera=1
  3. sudo reboot

Para producción, usa:
  CAMERA_PROFILE=RASPBERRY_PI python desktop_hybrid/main.py
    """)

if __name__ == "__main__":
    main()
