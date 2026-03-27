#!/usr/bin/env bash
set -euo pipefail

if [ -x .venv/bin/python ]; then
  .venv/bin/python -m rag_server.ingest
else
  python3 -m rag_server.ingest
fi
