#!/usr/bin/env bash
set -euo pipefail

TASK="${1:?Usage: $0 \"<task>\" [max_steps]}"
MAX_STEPS="${2:-5}"

if [ -x .venv/bin/python ]; then
  .venv/bin/python -m forgepilot.cli run "$TASK" --max-steps "$MAX_STEPS"
else
  python3 -m forgepilot.cli run "$TASK" --max-steps "$MAX_STEPS"
fi
