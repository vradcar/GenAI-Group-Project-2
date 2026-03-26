# Project Architecture

This document summarizes the runtime architecture of ForgePilot and the interaction between the core assistant, provider layer, MCP tools, and local RAG pipeline.

## Agent Loop

The agent loop is implemented in `src/forgepilot/agent.py` (`CodingAgent`).

1. CLI command (`forgepilot run` or `forgepilot repl`) builds the agent and runtime in `src/forgepilot/cli.py`.
2. Agent opens MCP connections (`async with self.mcp_client`) and records available MCP tools.
3. For each step (bounded by `max_steps`), the agent sends:
	 - task,
	 - step number,
	 - recent observations/history,
	 - strict JSON schema instructions.
4. Provider response is parsed into:
	 - `thought`: reasoning summary,
	 - `action`: single tool call (`tool`, `args`) or `null`,
	 - `final`: final response or `null`.
5. If `action` exists, the call is dispatched through `ToolRuntime` (never directly), preserving execution mode controls and MCP dispatch compatibility.
6. Loop ends when `final` is returned, or when step budget is exhausted.

### Robustness behavior

- The parser handles strict JSON, fenced JSON blocks, and extracted balanced JSON objects.
- If output is still unstructured, the agent attempts one repair pass to coerce it into the required schema.
- If coercion fails, a fallback status summary is returned instead of raising.

## Provider Abstraction

Provider logic lives in `src/forgepilot/providers.py`.

- Interface: `LLMProvider` with `complete()` and `stream()`.
- Implementations:
	- `LangChainChatProvider` (real model invocation via LangChain adapters),
	- `TemplateProvider` (safe placeholder fallback when provider setup is unavailable).
- Supported providers:
	- Ollama (`langchain_ollama`),
	- OpenAI (`langchain_openai`),
	- Anthropic (`langchain_anthropic`),
	- Groq (`langchain_groq`).

### Selection and fallback

- Primary provider is selected by `DEFAULT_PROVIDER` in `.env`.
- If selected provider cannot initialize, fallback attempts proceed through cloud/local alternatives.
- If no real provider is available, `TemplateProvider` is used to keep CLI operational.
- Runtime provider invocation errors are caught and surfaced as readable provider-error text to avoid hard crashes.

## MCP Integration (filesystem / context7 / rag)

MCP orchestration is implemented in `src/forgepilot/mcp_client.py`.

- Server config source: `MCP_CONFIG_PATH` (default `configs/mcp.servers.example.json`).
- Lifecycle:
	1. load server definitions,
	2. connect stdio transports,
	3. discover tools per server,
	4. expose tools as namespaced names (`server__tool`),
	5. execute calls and return normalized output.

### Configured servers

- `filesystem`: local file operations through MCP filesystem server.
- `context7`: external documentation/context retrieval via MCP.
- `rag`: local RAG MCP server (`python -m rag_server.mcp_server`) exposing RAG query/health tools.

### Env handling

- MCP env placeholders support `${VAR}`, `$VAR`, and `%VAR%` styles for cross-platform compatibility (including Windows shell behavior).

## Tool Runtime Modes (confirm / auto)

Execution gating is implemented in `src/forgepilot/tool_runtime.py` and surfaced in CLI.

- `confirm` mode (default): each tool call is shown and requires explicit approval.
- `auto` mode: tool calls are executed without prompt.

All local and MCP tool calls pass through this runtime, ensuring one consistent control point for:

- user approvals,
- tool-call logging/output,
- local tool dispatch (`read_file`, `write_file`, `run_shell`),
- MCP tool dispatch (`server__tool`).

## RAG Pipeline

RAG components are in the `rag_server/` package.

### Ingestion

- `rag_server/ingest.py` reads docs from `RAG_DOCS_DIR`.
- Text is chunked and embedded using Sentence Transformers.
- Vectors are persisted in Chroma under `RAG_VECTOR_DIR`.
- Stable identifiers make ingestion idempotent across reruns.

### Retrieval

- `rag_server/retriever.py` performs retrieval (fusion-style ranking strategy).
- Query returns top-k chunks (`RAG_TOP_K`) with source context.

### MCP exposure

- `rag_server/mcp_server.py` wraps retrieval as MCP tools:
	- `rag_query_docs`
	- `rag_health`
- This allows the agent to query project knowledge through the same MCP mechanism used for other tools.

## End-to-end Flow

1. User submits task via CLI.
2. Agent plans one step and emits a structured action.
3. ToolRuntime enforces mode (`confirm`/`auto`) and dispatches tool call.
4. Tool result is added to history.
5. Agent iterates until `final` response.
6. If needed, agent uses MCP RAG tools to fetch context before writing or editing files.