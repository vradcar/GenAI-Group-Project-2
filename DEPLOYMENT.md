# Deployment Guide (Local)

This project deploys locally for grading/demo.

## Prerequisites
- Python 3.11+
- Node.js + `npx`
- `.env` configured from `.env.example`
- Valid `CONTEXT7_API_KEY`

## One-Command Deployment Check
From repo root:

macOS/Linux:
```bash
./scripts/mac/deploy_local.sh
```

Windows:
```powershell
.\scripts\windows\deploy_local.ps1
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
- `--skip-bootstrap`
- `--skip-tests`
- `--skip-rag-ingest`
- `--skip-mcp-check`

Example:

macOS/Linux:
```bash
./scripts/mac/deploy_local.sh --skip-bootstrap
```

Windows:
```powershell
.\scripts\windows\deploy_local.ps1 -SkipBootstrap
```

## Manual Runtime Start
After deployment checks:

```bash
python3 -m forgepilot.cli repl
```

For RAG ingestion only:

```bash
python3 -m rag_server.ingest
```

## Troubleshooting
- If external MCP fails, verify `CONTEXT7_API_KEY` in `.env`.
- If filesystem server fails, verify `npx` is available.
- If RAG fails, verify `docs/source_docs` exists and `.vectorstore` is writable.

## Extra Notes
- Always verify environment variables are loaded before starting (`cat .env`)
- Double-check API keys are valid and not expired - test with a simple API call first
- Run `mcp list` to verify all MCP servers are discoverable and responding
- Model fallback behavior: if primary model fails, system will attempt to use backup models in order: gpt-4, gpt-3.5-turbo, claude-3-sonnet
- Quick rollback: keep previous `.vectorstore` backup and restore if ingestion fails

## Post-Deploy Verification Checklist

- [ ] Tests passed successfully
- [ ] RAG ingestion completed
- [ ] MCP servers discovered and responding
- [ ] Assistant CLI starts without errors
- [ ] Context7 access works properly