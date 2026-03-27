# ForgePilot Demo Script

Read this script while recording your demo video. Each section is a scene.
Lines in **bold** are what you say. Lines in `code blocks` are what you type.

---

## Pre-Recording Checklist

Before hitting record, confirm these in a terminal:

```bash
# Verify keys and mode
cat .env | grep -E "GROQ_API_KEY|CONTEXT7_API_KEY|DEFAULT_PROVIDER|EXECUTION_MODE"

# Ensure RAG vectors are ingested
./scripts/sh/run_rag_ingest.sh

# Clean any previous demo artifacts
rm -rf demo_output
```

---

## Scene 1: Introduction (~20 seconds)

**"This is ForgePilot — a CLI coding assistant with an agentic reasoning loop
and MCP integration. It connects to three MCP servers: a filesystem server,
a local RAG server, and Context7 as an external server. Every tool call is
displayed with its arguments, confirmed by the user, and the result is shown.
I'll walk through three non-trivial tasks — creating directories, writing
markdown files, and editing them — each using a different MCP server."**

---

## Scene 2: Start the REPL (~10 seconds)

**"I'll start the interactive REPL."**

```bash
.venv/bin/python -m forgepilot.cli repl
```

**"The mode is set to confirm, so I'll approve each tool call as it happens."**

---

## Scene 3: Task 1 — Read a file and write a summary (FILESYSTEM MCP)

**"First, a simple task using the filesystem MCP server."**

Type at the `>` prompt:

```
Read the README.md file and create a short summary of it in a new file called demo_output/SUMMARY.md
```

**What to narrate as each tool call appears:**

- **`filesystem__read_file`** — **"The agent calls the filesystem MCP server
  to read the README."** → type `y` → **"Result returned."**

- **`filesystem__write_file`** or **`write_file`** — **"Now it creates the
  directory and writes a new markdown file — that's two non-trivial
  operations: creating a directory and writing a markdown file. And that's
  the full tool-call lifecycle — call displayed, confirmed, result shown."**
  → type `y`

---

## Scene 4: Task 2 — Query local RAG documents (LOCAL RAG MCP)

**"Next, I'll use the local RAG MCP server to query our project's
knowledge base."**

Type at the `>` prompt:

```
Query our project documents about what RAG is and write the answer to demo_output/RAG_NOTES.md
```

**What to narrate:**

- **`rag__rag_query_docs`** — **"This is the local RAG MCP server — it
  queries our ChromaDB vector store."** → type `y` → **"Chunks retrieved
  from our ingested documents."**

- **`filesystem__write_file`** or **`write_file`** — **"It writes the RAG
  answer into another new markdown file — again, non-trivial work: querying
  a knowledge base and producing a written document from the results."**
  → type `y`

---

## Scene 5: Task 3 — Fetch external docs (EXTERNAL CONTEXT7 MCP)

**"Finally, the external MCP server — Context7 — to fetch live
documentation."**

Type at the `>` prompt:

```
Look up the langchain library on Context7 and save a short description of it to demo_output/LANGCHAIN.md
```

**What to narrate:**

- **`context7__resolve-library-id`** — **"Context7, our external MCP server,
  resolving the library ID over the network."** → type `y`

- **`context7__get-library-docs`** — **"Fetching live documentation from the
  external API."** → type `y`

- **`filesystem__write_file`** or **`write_file`** — **"And it writes a new
  markdown file from the external documentation — creating and writing
  markdown from live external sources is the kind of non-trivial task this
  agent is built for."** → type `y`

---

## Scene 6: Wrap-up (~20 seconds)

```
exit
```

**"To recap — three non-trivial tasks involving creating directories, writing
markdown files, and producing documents from retrieved knowledge. Three MCP
server categories were all visibly invoked: filesystem for file operations,
local RAG for querying our vector database, and Context7 for fetching live
external documentation. Every tool call was displayed, confirmed, and its
result shown."**

---

## Recovery Tips (don't read aloud)

- **Agent loops on same action:** type `exit`, `/mode` to switch to auto,
  retry, `/mode` back to confirm.
- **Task exhausts steps:** re-enter the same prompt.
- **Context7 fails:** check `CONTEXT7_API_KEY` in `.env`.
- **RAG returns nothing:** re-run `./scripts/sh/run_rag_ingest.sh`.
- **Reset between takes:** `rm -rf demo_output` and restart the REPL.
