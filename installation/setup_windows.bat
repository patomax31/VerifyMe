@echo off
setlocal

set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%setup_windows.ps1" %*

if errorlevel 1 (
  echo.
  echo [setup] Ocurrio un error durante la configuracion.
  exit /b 1
)

echo.
echo [setup] Configuracion finalizada correctamente.
exit /b 0
