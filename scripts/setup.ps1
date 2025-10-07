#Requires -Version 5.1

param(
	[string]$Python = "py",
	[string]$VenvDir = ".venv"
)

$ErrorActionPreference = "Stop"

Write-Host '[1/5] Checking Python...' -ForegroundColor Cyan
$pythonVersion = & $Python -3 -c "import sys; print(sys.version.split()[0])" 2>$null
if (-not $pythonVersion) {
	Write-Error 'Python 3 not found. Please install Python 3 and retry.'
}
Write-Host "Python $pythonVersion detected" -ForegroundColor Green

Write-Host "[2/5] Creating virtual environment $VenvDir..." -ForegroundColor Cyan
if (-not (Test-Path $VenvDir)) {
	& $Python -3 -m venv $VenvDir
}

$activate = Join-Path $VenvDir 'Scripts/Activate.ps1'
. $activate

Write-Host '[3/5] Upgrading pip...' -ForegroundColor Cyan
python -m pip install --upgrade pip

Write-Host '[4/5] Installing dependencies from requirements.txt...' -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host '[5/5] Done. Virtual environment is active.' -ForegroundColor Green
Write-Host 'Example: py -3 -m pytest --collect-only -q' -ForegroundColor Yellow
