# How to Use ForgePilot

ForgePilot is a CLI coding assistant with MCP integration and a local RAG pipeline.
This guide is accurate for this repository on Windows PowerShell.

## Prerequisites

- Python 3.11+
- Node.js (for MCP filesystem server via `npx`)
- PowerShell with script execution enabled for local scripts

Check script policy if needed:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Setup

### 1) Create `.env`

```powershell
Copy-Item .env.example .env
notepad .env
```

Fill provider keys/models you plan to use (for example `GROQ_API_KEY`, `GROQ_MODEL`, `CONTEXT7_API_KEY`).

### 2) Bootstrap environment

```powershell
./scripts/bootstrap.ps1
```

This creates `.venv`, installs dependencies, and installs this project in editable mode (`pip install -e .`).

## Run ForgePilot

If your prompt already shows `(.venv)`, you can run `python` commands directly without re-activating.

### Single-task mode

```powershell
python -m forgepilot.cli run "summarize this repository"
```

Wrapper script option:

```powershell
./scripts/run_assistant.ps1 -Task "summarize this repository"
```

Interpreter-explicit option (works even if venv is not activated):

```powershell
./.venv/Scripts/python.exe -m forgepilot.cli run "summarize this repository"
```

### REPL mode

```powershell
python -m forgepilot.cli repl
```

Interpreter-explicit option:

```powershell
./.venv/Scripts/python.exe -m forgepilot.cli repl
```

Inside REPL:
- `/mode` toggles confirm/auto execution mode for the current session
- `exit` or `quit` ends the session

## Confirm vs Auto Mode

ForgePilot uses `EXECUTION_MODE` from `.env`:

- `EXECUTION_MODE=confirm` (default): asks before tool execution
- `EXECUTION_MODE=auto`: executes tool calls without prompt

You can also override per command:

```powershell
$env:EXECUTION_MODE='auto'; ./scripts/run_assistant.ps1 -Task "create NOTES.md"; $env:EXECUTION_MODE='confirm'
```

## Common Commands

```powershell
# Run tests
./scripts/run_tests.ps1

# Ingest RAG docs
./scripts/run_rag_ingest.ps1

# Start RAG service CLI helper
./scripts/run_rag_server.ps1

# Local end-to-end deployment checks
./scripts/deploy_local.ps1
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'forgepilot'`

```powershell
./.venv/Scripts/python.exe -m pip install -e .
```

### REPL does not start

Use the exact command below (note `repl` subcommand):

```powershell
python -m forgepilot.cli repl
```

If that fails because the active interpreter is not the project venv, use:

```powershell
./.venv/Scripts/python.exe -m forgepilot.cli repl
```

### MCP tools not available

- Ensure `npx` works
- Verify `.env` keys used by MCP servers (for example `CONTEXT7_API_KEY`)
- Confirm `MCP_CONFIG_PATH` points to `configs/mcp.servers.example.json` (default)

### RAG results missing

```powershell
./scripts/run_rag_ingest.ps1
```

Also verify `docs/source_docs` contains source files and `.vectorstore` is writable.

## Where to look next

- [README.md](README.md): quick-start and project overview
- [DEPLOYMENT.md](DEPLOYMENT.md): deployment workflow and checks
- [rag_server/README.md](rag_server/README.md): RAG-specific details