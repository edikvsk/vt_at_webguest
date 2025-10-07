#Requires -Version 5.1

param(
    [string]$TestPath = "-q"  # путь к тесту или параметры pytest
)

$ErrorActionPreference = "Stop"

# Активируем venv, если есть
if (Test-Path "$PSScriptRoot/../.venv/Scripts/Activate.ps1") {
    . "$PSScriptRoot/../.venv/Scripts/Activate.ps1"
}

# Запускаем pytest с переданными аргументами
Write-Host "[Run] pytest $TestPath" -ForegroundColor Cyan
py -3 -m pytest $TestPath


