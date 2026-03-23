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
  - `run_assistant.ps1`
  - `run_rag_ingest.ps1`
  - `run_rag_server.ps1`
  - `run_tests.ps1`

## Team Execution Templates

## Project Templates

Use these templates to organize Group Project 2 execution:

- `docs/templates/TEAM_EXECUTION_TEMPLATE.md` — 5-person role split + day-by-day plan (integration lead included)
- `docs/templates/SPRINT_BOARD_TEMPLATE.md` — issue/milestone/label setup for GitHub Projects
- `docs/templates/RUBRIC_TRACKER_TEMPLATE.md` — grading rubric tracker with evidence mapping
- `docs/templates/DEMO_REFLECTION_TEMPLATE.md` — demo script and written reflection template

## Suggested Order

1. Fill `TEAM_EXECUTION_TEMPLATE.md`
2. Create issues from `SPRINT_BOARD_TEMPLATE.md`
3. Track score gaps with `RUBRIC_TRACKER_TEMPLATE.md`
4. Prepare submission using `DEMO_REFLECTION_TEMPLATE.md`

## Implementation Notes

- Non-MCP core now includes an autonomous multi-step local tool loop in `src/forgepilot/agent.py`.
- Provider abstraction now supports Ollama/OpenAI/Anthropic/Groq with safe fallback behavior.
- RAG ingestion and retrieval include persistent vectors and fusion-style multi-query ranking.
- MCP client is still a placeholder and should be replaced with MCP Python SDK session/tool calls.
- Keep ingestion persistent so vector data is reused across sessions.

