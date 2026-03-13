# Group Project 2 Team Execution Template

Use this document as the working plan for a 5-person team building the CLI coding assistant.

## 1) Team Identity
- Assistant Name: `<choose a unique product name>`
- Team Name: `<optional>`
- Repository: `<github link>`
- Due Date: `Mar 20, 11:59 PM`

## 2) Team Roles (5 People)

### Person 1 — Integration Lead (You)
**Owner:** `<name>`
**Primary responsibilities:**
- Own architecture and interface contracts
- Merge and integration management
- End-to-end wiring and smoke tests
- Daily sync + blocker resolution
- Demo reliability and final packaging

**Definition of done:**
- Main branch passes smoke test scenario
- All required MCP servers connected and invocable
- Rubric tracker is green or has action items assigned

### Person 2 — Agentic Loop + Reasoning
**Owner:** `<name>`
**Primary responsibilities:**
- Implement loop: plan -> tool selection -> execution -> observation -> continue/stop
- Tool call decision schema + stopping conditions
- Error recovery and retry policy

**Definition of done:**
- Agent completes at least 2 non-trivial tasks without manual intervention

### Person 3 — CLI + Tool Runtime
**Owner:** `<name>`
**Primary responsibilities:**
- REPL interface
- Streaming model output
- Tool call visibility/status indicators
- Confirm mode and auto-execute mode

**Definition of done:**
- User can switch between `confirm` and `auto` mode
- Tool calls are visibly printed with clear start/finish status

### Person 4 — MCP Integrations
**Owner:** `<name>`
**Primary responsibilities:**
- MCP client implementation
- Dynamic tool loading from connected servers
- Filesystem server + 1 external server integration

**Definition of done:**
- Filesystem and external MCP tools load dynamically and run successfully

### Person 5 — Custom RAG MCP Server
**Owner:** `<name>`
**Primary responsibilities:**
- Build local documentation RAG server
- Implement ingestion/chunking/embedding/vector store
- Implement one advanced RAG technique (HyDE/Fusion/Semantic Chunking)
- Ensure persistent vector DB for reuse across sessions

**Definition of done:**
- RAG server answers documentation queries with relevant chunks
- No full re-index required on every run

## 3) Architecture Contracts (fill these first)

### A) Agent <-> Tool Executor
- Input schema: `<json schema / pydantic model>`
- Output schema: `<tool_result schema>`
- Error format: `<standardized error object>`

### B) Agent <-> Provider Layer
- `generate(messages, tools, stream)` contract
- Supported providers: `ollama`, `<cloud provider>`
- Provider selection config: `<env/config field>`

### C) Agent <-> MCP Client
- `list_tools()` returns normalized tool metadata
- `call_tool(name, args)` returns normalized response

### D) Agent <-> RAG MCP Server
- Query endpoint/tool: `<name>`
- Response fields: `answer`, `citations/chunks`, `confidence(optional)`

## 4) Delivery Timeline (Mar 13 -> Mar 20)

### Day 1 (Planning)
- Finalize architecture + interfaces
- Create planning docs and diagrams
- Create issues and assign owners

### Day 2-3 (Parallel build)
- P2: agent loop baseline
- P3: CLI streaming + tool visibility
- P4: filesystem + external MCP
- P5: ingestion + vector DB baseline
- You: integration branch + shared test harness

### Day 4-5 (Integration)
- Wire provider abstraction
- Wire MCP dynamic tool loading
- Wire custom RAG server into agent loop

### Day 6 (Stabilization)
- Fix reliability bugs and edge cases
- Prepare demo scripts for two non-trivial tasks

### Day 7 (Submission assets)
- Record demo video
- Finalize reflection + LLM comparison + architecture diagrams
- Final rubric pass

## 5) Required Feature Checklist
- [ ] Autonomous agentic loop
- [ ] Provider abstraction (Ollama + cloud)
- [ ] CLI streaming output
- [ ] Visible tool call logs/status
- [ ] Confirm mode
- [ ] Auto-execute mode
- [ ] MCP dynamic tool loading
- [ ] Filesystem MCP server integrated
- [ ] External MCP server integrated
- [ ] Custom RAG MCP server integrated
- [ ] Advanced RAG technique implemented
- [ ] Persistent vector DB reuse

## 6) Risk Register
| Risk | Owner | Mitigation | Trigger | Status |
|---|---|---|---|---|
| API/provider outages | `<name>` | Add provider fallback and retries | Failing cloud calls | Open |
| MCP server startup friction | `<name>` | Add startup script + health checks | Tool loading failures | Open |
| RAG quality too low | `<name>` | Tune chunking + reranking/fusion | Irrelevant retrieval | Open |
| Integration conflicts | `<name>` | Interface contracts + frequent merges | Merge failures | Open |

## 7) Daily Standup Log
| Date | Yesterday | Today | Blockers | Needs from Lead |
|---|---|---|---|---|
| `<date>` |  |  |  |  |

## 8) Demo Acceptance Gate
- [ ] Demo task #1 completes end-to-end
- [ ] Demo task #2 completes end-to-end
- [ ] Filesystem MCP visibly invoked
- [ ] External MCP visibly invoked
- [ ] Custom RAG MCP visibly invoked
- [ ] Tool calls visibly shown in terminal
- [ ] Recording quality and pace are clear
