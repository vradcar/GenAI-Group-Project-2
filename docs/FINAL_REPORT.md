# Final Report — ForgePilot CLI Coding Assistant

## Project Summary

ForgePilot is a CLI coding assistant that supports:

- Multi-step agentic task execution
- Provider abstraction across Ollama/OpenAI/Anthropic/Groq
- MCP tool integration (filesystem, context7, local RAG)
- Confirm/auto execution modes
- Local RAG ingestion and retrieval pipeline

The implementation focuses on practical coding workflows: reading files, writing edits, running shell commands, and grounding responses with repository context.

## System Architecture

### Runtime Architecture (Components)

```mermaid
flowchart LR
    U[User] --> C[CLI\nsrc/forgepilot/cli.py]
    C --> A[Agentic Loop\nsrc/forgepilot/agent.py]
    A --> P[LLM Provider\nsrc/forgepilot/providers.py]
    A --> T[Tool Runtime\nsrc/forgepilot/tool_runtime.py]
    T --> L[Local Tools\nread_file/write_file/run_shell]
    T --> M[MCP Client\nsrc/forgepilot/mcp_client.py]
    M --> FS[Filesystem MCP]
    M --> CX[Context7 MCP]
    M --> RAG[Local RAG MCP\nrag_server/mcp_server.py]
    RAG --> RET[Retriever\nrag_server/retriever.py]
    RET --> VDB[Chroma Vector Store\n.vectorstore]
    ING[Ingestion\nrag_server/ingest.py] --> VDB
```

Source architecture narrative: [ARCHITECTURE.md](../ARCHITECTURE.md).

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> ParseTask: User enters task in CLI
    ParseTask --> BuildContext: Gather workspace/tool context

    BuildContext --> SelectProvider: Choose Ollama/Groq/OpenAI/Anthropic
    SelectProvider --> LoadTools: Load local + MCP tools

    LoadTools --> PlanAction: Agent asks LLM for next step

    PlanAction --> AwaitConfirm: Tool requires approval in confirm mode
    AwaitConfirm --> ExecuteTool: User approves
    AwaitConfirm --> PlanAction: User rejects / replan

    PlanAction --> ExecuteTool: Auto mode

    ExecuteTool --> ObserveResult: Tool output captured
    ObserveResult --> PlanAction: More work remains
    ObserveResult --> Finalize: Task complete

    PlanAction --> Finalize: No further tools needed

    Finalize --> Idle: Show result and wait for next prompt
    Finalize --> Error: Unhandled exception path
    Error --> Idle: Recovery
```

Source file: [STATE_DIAGRAM.mmd](planning/STATE_DIAGRAM.mmd).

## Sequence Diagram — Scenario 1 (Documentation Query with RAG)

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant C as CLI
    participant A as Agentic Loop
    participant P as LLM Provider
    participant M as MCP Client
    participant R as Local RAG MCP Server

    U->>C: Ask docs question (e.g., Fusion Retrieval)
    C->>A: Forward task
    A->>M: list_tools()
    M-->>A: Filesystem + External + RAG tools
    A->>P: Decide next action
    P-->>A: Select rag__query_docs

    alt confirm mode
        A->>C: Show tool call + prompt
        U-->>C: Approve
    end

    A->>M: call_tool(rag__query_docs, question)
    M->>R: Query vector DB
    R-->>M: chunks + answer
    M-->>A: tool result

    A->>P: Produce grounded final response
    P-->>A: Final answer
    A-->>C: Stream output + tool logs
    C-->>U: Display completion
```

Source file: [SEQUENCE_SCENARIO_1_DOC_RAG.mmd](planning/SEQUENCE_SCENARIO_1_DOC_RAG.mmd).

## Sequence Diagram — Scenario 2 (Read/Edit File Flow)

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant C as CLI
    participant A as Agentic Loop
    participant P as LLM Provider
    participant T as Tool Runtime
    participant F as Filesystem MCP Server

    U->>C: "Read file and make edits"
    C->>A: Task
    A->>P: Plan first action
    P-->>A: filesystem__read_file

    alt confirm mode
        A->>C: Ask permission
        U-->>C: Approve
    end

    A->>T: dispatch(read_file)
    T->>F: call_tool(read_file)
    F-->>T: file content
    T-->>A: result

    A->>P: Plan next action
    P-->>A: filesystem__write_file

    alt confirm mode
        A->>C: Ask permission
        U-->>C: Approve
    end

    A->>T: dispatch(write_file)
    T->>F: call_tool(write_file)
    F-->>T: success
    T-->>A: result

    A->>P: Summarize changes
    P-->>A: final response
    A-->>C: stream output
    C-->>U: done
```

Source file: [SEQUENCE_SCENARIO_2_READ_EDIT.mmd](planning/SEQUENCE_SCENARIO_2_READ_EDIT.mmd).

## Implementation Highlights

- Agent loop executes one action per step and uses structured JSON contracts.
- Parser hardening handles fenced JSON and malformed response recovery paths.
- Tool runtime enforces safety (`confirm`) and productivity (`auto`) modes.
- MCP integration namescopes tools and supports cross-platform env expansion.
- RAG pipeline uses chunking + embeddings + persistent vector storage with fusion retrieval.
- Deployment and usage docs now include accurate commands and common troubleshooting.

## Validation Evidence

- Unit/integration tests pass (`pytest -q`)
- Deployment checks exist in [DEPLOYMENT.md](../DEPLOYMENT.md)
- Usage guide exists in [HOW_TO_USE.md](../HOW_TO_USE.md)
- Demo video artifact: [docs/demo/demo-video.mp4](demo/demo-video.mp4)

## Limitations and Future Work

- Provider/model quality varies by availability and quota.
- Some hosted models may return incompatible tool-calling responses.
- Future improvement: stricter quality rubric and validator pass for generated markdown docs.
- Future improvement: export Mermaid diagrams to PNG/SVG for static submission bundles.

## Appendix: Artifact Index

- Architecture summary: [ARCHITECTURE.md](../ARCHITECTURE.md)
- State diagram source: [STATE_DIAGRAM.mmd](planning/STATE_DIAGRAM.mmd)
- Sequence 1 source: [SEQUENCE_SCENARIO_1_DOC_RAG.mmd](planning/SEQUENCE_SCENARIO_1_DOC_RAG.mmd)
- Sequence 2 source: [SEQUENCE_SCENARIO_2_READ_EDIT.mmd](planning/SEQUENCE_SCENARIO_2_READ_EDIT.mmd)
- Deployment guide: [DEPLOYMENT.md](../DEPLOYMENT.md)
- How-to guide: [HOW_TO_USE.md](../HOW_TO_USE.md)
