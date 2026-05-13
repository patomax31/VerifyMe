# IdentifyMe

IdentifyMe es un sistema de control de acceso mediante datos biométricos faciales en una Raspberry Pi 5

## 📌 Estructura del proyecto

- `login.py` – Módulo de ejecución para iniciar el sistema de login por reconocimiento facial.
- `registrar.py` – Script para registrar un nuevo estudiante (grupo + biometria facial).
- `src/` – Nueva arquitectura modular (en adopcion progresiva):
	- `src/core/` – Configuracion compartida.
	- `src/domain/` – Puertos (interfaces) del dominio para desacoplar servicios de la infraestructura.
	- `src/application/` – Servicios/casos de uso de alto nivel.
	- `src/infrastructure/camera/` – Adaptadores de camara OpenCV.
	- `src/infrastructure/recognition/` – Motor de reconocimiento facial.
	- `src/infrastructure/persistence/` – Repositorio de persistencia (SQLite adapter).
- `data/` – Carpeta de respaldo con archivos `.pkl` (formato `est_<id>.pkl`).
- `database/script.sql` – Esquema SQLite del sistema.
- `database/face_recognition.db` – Base de datos SQLite generada automaticamente al ejecutar el sistema.
- `test.py` – Verifica que las librerías necesarias (OpenCV, dlib, numpy) estén instaladas.

### Estado actual de modularizacion

- `login.py` y `registrar.py` ya delegan en modulos de `src/` para camara, reconocimiento y servicios de aplicacion.
- Los flujos de negocio de login/registro viven en casos de uso:
	- `src/application/login_use_case.py`
	- `src/application/registration_use_case.py`
- `database/sqlite_manager.py` funciona como fachada de compatibilidad.
- La implementacion SQLite se separo por responsabilidad en `database/sqlite/`:
	- `connection.py` (conexion),
	- `migrations.py` (inicializacion/migracion),
	- `students.py` (consultas de estudiantes y biometria),
	- `access.py` (bitacora de accesos),
	- `encoding.py` (serializacion de vectores faciales),
	- `paths.py` (rutas del motor local).
- `src/infrastructure/persistence/sqlite_repository.py` permanece como adaptador usado por servicios de aplicacion.

### Diagrama de capas (resumen textual)

- `domain`: define puertos (`src/domain/ports.py`) y reglas de dependencia.
- `application`: coordina casos de uso y flujo funcional sin depender de implementaciones concretas.
- `infrastructure`: implementa puertos para camara, reconocimiento y persistencia (SQLite y PKL).
- `entrypoints` (`login.py`, `registrar.py`): UI/IO y orquestacion ligera.

## ✅ Requisitos (dependencias)

Este proyecto funciona mejor dentro de un entorno virtual de Python para evitar conflictos con otras librerías del sistema.

### Configuración automática en Windows (recomendada)

Puedes configurar todo el entorno en un solo paso (crea `.venv`, instala dependencias y valida imports):

```powershell
.\setup_windows.ps1
```

También puedes usar el lanzador para CMD o doble clic:

```cmd
setup_windows.bat
```

Opcionalmente, para recrear el entorno desde cero:

```powershell
.\setup_windows.ps1 -ForceRecreate
```

### 1) Crear y activar un entorno virtual (recomendado)

#### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### En Windows (CMD):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### En macOS:
```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

> ⚠️ **Importante:** El flag `--system-site-packages` es CRÍTICO en Raspberry Pi porque permite acceso a librerías del sistema operativo (libcamera, libpicamera2) que no están disponibles en PyPI.

### Paso 3: Instalar dependencias

```bash
pip install --upgrade pip
pip install opencv-python face-recognition dlib numpy pygame
pip install -r requirements.txt
pip install deep_translator
```

> 📌 `face-recognition` depende de `dlib`, que requiere compilación. En Raspberry Pi esto puede tomar 10-20 minutos. Sea paciente.

**Si la compilación de dlib falla en Raspberry Pi**, intente usar piwheels:
```bash
pip install --upgrade pip
pip install --index-url https://www.piwheels.org/simple opencv-python face-recognition numpy
```

### Paso 4: Instalar dependencias del sistema (Raspberry Pi)

Si está en Raspberry Pi, instale también las librerías de cámara:

```bash
sudo apt-get update
sudo apt-get install -y python3-libcamera python3-picamera2
```

### Paso 5: Verificar la instalación

```bash
pip install opencv-python face_recognition dlib numpy

// Instalar setuptools para poder instalar los modelos de face_recognition

venv/bin/python -m pip install "setuptools<81"

// Instalar modelos de face_recognition

pip install git+https://github.com/ageitgey/face_recognition_models
```

> 🔍 `face_recognition` depende de `dlib`, que a su vez requiere compilación en algunos sistemas. Si tienes problemas en Windows, busca instalación de `dlib` con ruedas precompiladas.

## 🗄️ Base de datos SQLite

- El sistema inicializa automaticamente la base de datos desde `database/script.sql`.
- El registro guarda biometria en SQLite (tabla `datos_biometricos`) para `ESTUDIANTE` y conserva un respaldo en `data/*.pkl`.
- En la version local, el login usa SQLite como fuente principal y solo usa `.pkl` como compatibilidad si aun no hay biometria en BD.

## ⚙️ Configuracion por entorno

Variables soportadas:

- `CAMERA_INDEX` (default: `0`)
- `CAMERA_PROFILE` (default: `AUTO`, opciones comunes: `WINDOWS_STABLE`, `RASPBERRY_PI`)
- `CAMERA_WIDTH` (default: `640`)
- `CAMERA_HEIGHT` (default: `480`)
- `CAMERA_FPS` (default: `20`)
- `RECOGNITION_SCALE` (default: `0.25`)
- `RECOGNITION_TOLERANCE` (default: `0.5`)
- `ACCESS_COOLDOWN_SECONDS` (default: `8.0`)

Ejemplo en PowerShell:

```powershell
$env:RECOGNITION_TOLERANCE = "0.48"
$env:ACCESS_COOLDOWN_SECONDS = "10"
python login.py
```

## 🚀 Uso

### 1) Registrar un estudiante

Ejecuta el script de registro y sigue las instrucciones en pantalla:

```bash
python registrar.py
```

- Se abrirá la cámara y verás un óvalo guía.
- Captura primero los datos del grupo: grado, letra y turno.
- Coloca tu rostro dentro del óvalo.
- Presiona `S` para capturar y guardar el encoding.
- El encoding se guardará en SQLite y en `data/est_<id>.pkl` como respaldo.

### 2) Iniciar la sesión (login)

Ejecuta el script de login:

```bash
python login.py
```

- El sistema buscará el rostro en SQLite (estudiantes activos).
- Si encuentra una coincidencia, mostrará `ACCESO CONCEDIDO` con grupo e identificador interno.
- Si no, mostrará `ACCESO DENEGADO`.
- Presiona `q` para cerrar la ventana.

## 🧪 Verificar la instalación

Puedes verificar que las librerías estén correctamente instaladas ejecutando:

```bash
# Ver rama actual
git branch

# Cambiar de rama (el venv se mantiene)
git checkout VictorRama
git checkout kevin

# Activar venv (igual para todas las ramas)
source venv/bin/activate

# Ejecutar
python login.py
```

## ✅ Pruebas unitarias (arquitectura modular)

Se incluyeron pruebas unitarias para los servicios de aplicacion en `tests/`.

Ejecuta:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Cobertura actual de pruebas:

- Delegacion de inicializacion de servicios hacia el repositorio.
- Carga de estudiantes conocidos en autenticacion.
- Registro de bitacora de acceso en autenticacion.
- Flujo de registro de estudiante + persistencia de biometria.
- Integracion SQLite para `students.py` (crear/cargar biometria).
- Integracion SQLite para `access.py` (persistencia y validacion de tipo de usuario).
- Integracion SQLite para vistas/reporting (`vw_estudiantes`, `vw_logs_acceso`, `vw_intentos_fallidos`).

## Consultas administrativas seguras (SQLite)

Se agregaron vistas y utilidades para reporting sin exponer SQL dinamico inseguro:

- `vw_estudiantes`
- `vw_logs_acceso`
- `vw_intentos_fallidos`

Script CLI:

```bash
python scripts/db_queries.py students --active true --limit 50
python scripts/db_queries.py logs --tipo-usuario ESTUDIANTE --acceso-concedido true --limit 100
python scripts/db_queries.py failed --from-datetime 2026-04-01T00:00:00 --to-datetime 2026-04-30T23:59:59
```

Opciones de salida:

- `--format table` (default)
- `--format json`

## 📌 Notas generales de uso

- Usa buena iluminación para mejorar la detección facial.
- Asegúrate de que solo haya un rostro en el cuadro al capturar el encoding.
- Si tienes problemas con la cámara, prueba con otro dispositivo o controla que no esté siendo utilizada por otra aplicación.
<<<<<<< HEAD
- Si tienes más de una cámara, puedes seleccionar índice con variable de entorno: `set CAMERA_INDEX=1` (Windows CMD) o `$env:CAMERA_INDEX=1` (PowerShell).
- Perfil de cámara dual con `CAMERA_PROFILE`:
	- `WINDOWS_STABLE` para desarrollo en Windows (DirectShow).
	- `RASPBERRY_PI` para despliegue en Linux/Raspberry Pi (V4L2).
	- `AUTO` (valor por defecto) detecta por sistema operativo.
- Variables opcionales de rendimiento: `CAMERA_WIDTH`, `CAMERA_HEIGHT`, `CAMERA_FPS`.
=======

### Troubleshooting rápido (Windows)

- Si aparece `Please install face_recognition_models...`, instala siempre con el Python del entorno virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install face_recognition_models
```

- Si luego aparece error de `pkg_resources`, fija `setuptools` a una versión compatible:

```powershell
.\.venv\Scripts\python.exe -m pip install "setuptools<81"
```
>>>>>>> 8461d2d623db31dab5f72fded4d377749a53703e
