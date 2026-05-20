#!/usr/bin/env python3
"""
Test que open_camera() detecta la cámara correctamente
"""
import sys
import os
import signal

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def timeout_handler(signum, frame):
    print("\n[TIMEOUT] Operación tardó demasiado\n")
    sys.exit(1)

# Set 10 second timeout for entire script
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)

from src.infrastructure.camera.opencv_camera import open_camera

print("Tests de open_camera()...\n")

print("[1] Intentando abrir camara con open_camera()...")
try:
    cap = open_camera()
    
    if cap is None:
        print("    [FAIL] open_camera() retorno None\n")
        print("    Checklist:")
        print("    - Cable CSI conectado?")
        print("    - libcamera instalado?")
        print("    - Variables de entorno: CAMERA_PROFILE, CAMERA_INDEX")
        sys.exit(1)
    
    print("    [OK] Camara abierta\n")
    
    print("[2] Liberando camara...")
    cap.release()
    print("    [OK] Camara liberada\n")
    
    print("[OK] EXITO: open_camera() esta funcionando correctamente")
    print("\nAhora puedes ejecutar: python desktop_hybrid/main.py")
    signal.alarm(0)  # Cancel alarm
    
except Exception as e:
    print(f"    [ERROR] {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
