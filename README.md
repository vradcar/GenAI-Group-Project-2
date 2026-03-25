# GenAI-Group-Project-2

Template scaffold for a CLI coding assistant with provider abstraction, MCP integration, and a custom local RAG MCP server.

## Quick Start (Windows PowerShell)

1. Copy environment template:
	- `Copy-Item .env.example .env`
2. Bootstrap virtual environment:
	- `./scripts/bootstrap.ps1`
3. Run tests:
	- `./scripts/run_tests.ps1`
4. Run assistant template:
	- `./scripts/run_assistant.ps1 -Task "summarize this repository"`
5. Run local RAG ingestion + server template:
	- `./scripts/run_rag_ingest.ps1`
	- `./scripts/run_rag_server.ps1`
6. Run end-to-end local deployment checks:
  - `./scripts/deploy_local.ps1`

## Deployment

- Full local deployment guide: `DEPLOYMENT.md`
- Includes bootstrap, tests, RAG ingestion, and MCP invocation checks.

## Required Environment Templates

- `.env.example`: full environment variable template for all providers and MCP settings
- `.env.ollama.example`: local-model focused setup
- `.env.cloud.example`: cloud-provider focused setup
- `configs/mcp.servers.example.json`: MCP server definitions (filesystem, external, local RAG)
- `configs/providers.example.yaml`: provider examples
- `configs/tool_permissions.example.yaml`: confirm/auto execution policy template

## Scaffolded Project Structure

- `src/forgepilot/`
  - `cli.py`: REPL/entrypoint template
  - `agent.py`: agentic loop template
  - `providers.py`: provider abstraction template
  - `mcp_client.py`: dynamic MCP loading template
  - `local_tools.py`: local read/write/shell tool templates
  - `config.py`: pydantic settings
  - `types.py`: shared datatypes
- `rag_server/`
  - `server.py`: custom RAG MCP server template
  - `ingest.py`: one-time ingestion template
  - `retriever.py`: retrieval + advanced RAG hook points
  - `settings.py`: RAG settings
- `tests/`
  - `test_config.py`
  - `test_agent_template.py`
- `scripts/`
  - `bootstrap.ps1`
  - `deploy_local.ps1`
  - `run_assistant.ps1`
  - `run_rag_ingest.ps1`
  - `run_rag_server.ps1`
  - `run_tests.ps1`

## Planning Diagrams (Required)

- `docs/planning/STATE_DIAGRAM.mmd`
- `docs/planning/SEQUENCE_SCENARIO_1_DOC_RAG.mmd`
- `docs/planning/SEQUENCE_SCENARIO_2_READ_EDIT.mmd`
- `docs/planning/PLANNING_DELIVERABLES_CHECKLIST.md`

## Implementation Notes

- Non-MCP core now includes an autonomous multi-step local tool loop in `src/forgepilot/agent.py`.
- Provider abstraction now supports Ollama/OpenAI/Anthropic/Groq with safe fallback behavior.
- RAG ingestion and retrieval include persistent vectors and fusion-style multi-query ranking.
- MCP client includes dynamic tool loading, namespaced tool registration, and async tool invocation.
- Keep ingestion persistent so vector data is reused across sessions.

