#!/usr/bin/env bash
set -euo pipefail

PYTHON="${1:-python3}"

"$PYTHON" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip install -e .
echo "Bootstrap complete. Activate with: source .venv/bin/activate"
