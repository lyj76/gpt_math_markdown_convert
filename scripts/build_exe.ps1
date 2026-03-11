param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & $Python -m PyInstaller --onefile tr.py
    Write-Host "Build done. Output: dist\tr.exe"
}
finally {
    Pop-Location
}
