# How to Use ForgePilot

ForgePilot is a CLI coding assistant with MCP integration and a local RAG pipeline.
This guide covers macOS/Linux and Windows. Use the scripts in `scripts/mac/` for macOS/Linux or `scripts/windows/` for Windows.

## Prerequisites

- Python 3.11+
- Node.js (for MCP filesystem server via `npx`)

## Setup

### 1) Create `.env`

```bash
cp .env.example .env
```

Fill provider keys/models you plan to use (for example `GROQ_API_KEY`, `GROQ_MODEL`, `CONTEXT7_API_KEY`).

### 2) Bootstrap environment

macOS/Linux:
```bash
./scripts/mac/bootstrap.sh
```

Windows:
```powershell
.\scripts\windows\bootstrap.ps1
```

This creates `.venv`, installs dependencies, and installs this project in editable mode (`pip install -e .`).

## Run ForgePilot

If your prompt already shows `(.venv)`, you can run `python` commands directly without re-activating.

### Single-task mode

```bash
python3 -m forgepilot.cli run "summarize this repository"
```

Wrapper script option:

macOS/Linux:
```bash
./scripts/mac/run_assistant.sh "summarize this repository"
```

Windows:
```powershell
.\scripts\windows\run_assistant.ps1 -Task "summarize this repository"
```

Interpreter-explicit option (works even if venv is not activated):

```bash
./.venv/bin/python -m forgepilot.cli run "summarize this repository"
```

### REPL mode

```bash
python3 -m forgepilot.cli repl
```

Interpreter-explicit option:

```bash
./.venv/bin/python -m forgepilot.cli repl
```

Inside REPL:
- `/mode` toggles confirm/auto execution mode for the current session
- `exit` or `quit` ends the session

## Confirm vs Auto Mode

ForgePilot uses `EXECUTION_MODE` from `.env`:

- `EXECUTION_MODE=confirm` (default): asks before tool execution
- `EXECUTION_MODE=auto`: executes tool calls without prompt

You can also override per command:

macOS/Linux:
```bash
EXECUTION_MODE=auto ./scripts/mac/run_assistant.sh "create NOTES.md"
```

Windows:
```powershell
$env:EXECUTION_MODE='auto'; .\scripts\windows\run_assistant.ps1 -Task "create NOTES.md"; $env:EXECUTION_MODE='confirm'
```

## Common Commands

macOS/Linux:
```bash
./scripts/mac/run_tests.sh
./scripts/mac/run_rag_ingest.sh
./scripts/mac/run_rag_server.sh
./scripts/mac/deploy_local.sh
```

Windows:
```powershell
.\scripts\windows\run_tests.ps1
.\scripts\windows\run_rag_ingest.ps1
.\scripts\windows\run_rag_server.ps1
.\scripts\windows\deploy_local.ps1
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'forgepilot'`

```bash
./.venv/bin/python -m pip install -e .
```

### REPL does not start

Use the exact command below (note `repl` subcommand):

```bash
python3 -m forgepilot.cli repl
```

If that fails because the active interpreter is not the project venv, use:

```bash
./.venv/bin/python -m forgepilot.cli repl
```

### MCP tools not available

- Ensure `npx` works
- Verify `.env` keys used by MCP servers (for example `CONTEXT7_API_KEY`)
- Confirm `MCP_CONFIG_PATH` points to `configs/mcp.servers.example.json` (default)

### RAG results missing

macOS/Linux:
```bash
./scripts/mac/run_rag_ingest.sh
```

Windows:
```powershell
.\scripts\windows\run_rag_ingest.ps1
```

Also verify `docs/source_docs` contains source files and `.vectorstore` is writable.

## Where to look next

- [README.md](README.md): quick-start and project overview
- [DEPLOYMENT.md](DEPLOYMENT.md): deployment workflow and checks
- [rag_server/README.md](rag_server/README.md): RAG-specific details