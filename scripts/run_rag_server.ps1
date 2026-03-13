$ErrorActionPreference = "Stop"

if (Test-Path .\.venv\Scripts\python.exe) {
  & .\.venv\Scripts\python.exe -m rag_server.server serve
} else {
  python -m rag_server.server serve
}
