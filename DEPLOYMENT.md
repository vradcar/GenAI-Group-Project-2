# Deployment Guide (Local)

This project deploys locally for grading/demo.

## Prerequisites
- Python 3.11+
- Node.js + `npx`
- `.env` configured from `.env.example`
- Valid `CONTEXT7_API_KEY`

## One-Command Deployment Check
From repo root:

```powershell
./scripts/deploy_local.ps1
```

This command performs:
1. Environment bootstrap
2. Test run
3. RAG ingestion
4. MCP discovery + runtime tool calls for:
   - filesystem
   - rag
   - context7

## Optional Flags
- `-SkipBootstrap`
- `-SkipTests`
- `-SkipRagIngest`
- `-SkipMcpCheck`

Example:

```powershell
./scripts/deploy_local.ps1 -SkipBootstrap
```

## Manual Runtime Start
After deployment checks:

```powershell
python -m forgepilot.cli repl
```

For RAG ingestion only:

```powershell
python -m rag_server.ingest
```

## Troubleshooting
- If external MCP fails, verify `CONTEXT7_API_KEY` in `.env`.
- If filesystem server fails, verify `npx` is available.
- If RAG fails, verify `docs/source_docs` exists and `.vectorstore` is writable.
