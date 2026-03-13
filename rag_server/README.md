# Custom RAG MCP Server Template

This folder contains the local server template required by the project rubric.

## Responsibilities
- Load source docs from `docs/source_docs/`
- Split/chunk docs
- Embed chunks
- Store vectors in persistent DB (`.vectorstore/`)
- Expose retrieval as MCP tools
- Implement one advanced RAG technique (`RAG_TECHNIQUE=fusion|hyde|semantic_chunking`)

## Template Commands
- `python -m rag_server.ingest`
- `python -m rag_server.server serve`
- `python -m rag_server.server ask "What is LangChain LCEL?"`

## Required implementation points
- MCP tool registration in `server.py`
- Real retrieval pipeline in `retriever.py`
- Production ingestion in `ingest.py`
