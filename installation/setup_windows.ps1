param(
    [string]$VenvName = ".venv",
    [string]$PythonCommand = "",
    [switch]$ForceRecreate
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[setup] $Message" -ForegroundColor Cyan
}

function Resolve-PythonCommand {
    param([string]$Requested)

    if ($Requested) {
        return $Requested
    }

    if (Get-Command py -ErrorAction SilentlyContinue) {
        return "py"
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        return "python"
    }

    throw "No se encontro Python en PATH. Instala Python 3 y vuelve a ejecutar."
}

function Invoke-Python {
    param(
        [string]$PythonCmd,
        [string[]]$Arguments
    )

    if ($PythonCmd -eq "py") {
        & py @Arguments
    }
    else {
        & $PythonCmd @Arguments
    }
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Step "Proyecto: $projectRoot"

$pythonCmd = Resolve-PythonCommand -Requested $PythonCommand
Write-Step "Python seleccionado: $pythonCmd"

if ($ForceRecreate -and (Test-Path $VenvName)) {
    Write-Step "Eliminando entorno virtual existente: $VenvName"
    Remove-Item -Recurse -Force $VenvName
}

if (-not (Test-Path $VenvName)) {
    Write-Step "Creando entorno virtual en $VenvName"
    Invoke-Python -PythonCmd $pythonCmd -Arguments @("-m", "venv", $VenvName)
}
else {
    Write-Step "Entorno virtual ya existe: $VenvName"
}

$venvPython = Join-Path $projectRoot "$VenvName\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "No se encontro el ejecutable del entorno virtual: $venvPython"
}

Write-Step "Actualizando pip y herramientas base"
& $venvPython -m pip install --upgrade pip wheel

# face_recognition_models depende de pkg_resources, removido en setuptools recientes.
Write-Step "Instalando setuptools compatible (<81)"
& $venvPython -m pip install "setuptools<81"

$requirementsFile = Join-Path $projectRoot "requirements.txt"

if (Test-Path $requirementsFile) {
    Write-Step "Instalando dependencias desde requirements.txt"
    & $venvPython -m pip install -r $requirementsFile
}
else {
    Write-Step "No existe requirements.txt; instalando dependencias base del proyecto"
    & $venvPython -m pip install opencv-python face_recognition dlib numpy
}

Write-Step "Validando imports principales"
& $venvPython -c "import cv2, face_recognition, dlib, numpy; print('OK - Dependencias instaladas correctamente')"

Write-Host "" 
Write-Host "Configuracion completada." -ForegroundColor Green
Write-Host "Para activar el entorno virtual en PowerShell:" -ForegroundColor Green
Write-Host ".\$VenvName\Scripts\Activate.ps1" -ForegroundColor Yellow
