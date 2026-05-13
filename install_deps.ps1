param()
$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$root = Split-Path $here -Parent

$pip = $null
if ($env:VIRTUAL_ENV) {
    $candidate = Join-Path $env:VIRTUAL_ENV "Scripts\pip.exe"
    if (Test-Path $candidate) { $pip = $candidate }
}
if (-not $pip) {
    $candidate = Join-Path $root ".venv\Scripts\pip.exe"
    if (Test-Path $candidate) { $pip = $candidate }
}
if (-not $pip) {
    throw "No se encontro pip en .venv ni VIRTUAL_ENV. Activa el entorno o crea .venv con setup_windows.ps1 en la raiz del repo."
}

Write-Host "[install] pip: $pip" -ForegroundColor Cyan
& $pip install -r (Join-Path $here "requirements.txt")
& $pip install --no-deps "pywebview>=5.0,<6.0"
Write-Host "[install] Completado." -ForegroundColor Green
