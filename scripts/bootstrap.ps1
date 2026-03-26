param(
  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

& $Python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
& .\.venv\Scripts\python.exe -m pip install -e .
Write-Host "Bootstrap complete. Activate with: .\.venv\Scripts\Activate.ps1"
