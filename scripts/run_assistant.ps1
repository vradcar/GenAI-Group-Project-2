param(
  [Parameter(Mandatory=$true)]
  [string]$Task,
  [int]$MaxSteps = 5
)

$ErrorActionPreference = "Stop"

if (Test-Path .\.venv\Scripts\python.exe) {
  & .\.venv\Scripts\python.exe -m forgepilot.cli run --task "$Task" --max-steps $MaxSteps
} else {
  python -m forgepilot.cli run --task "$Task" --max-steps $MaxSteps
}
