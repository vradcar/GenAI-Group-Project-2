from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from rag_server.retriever import Retriever
from rag_server.settings import get_rag_settings

mcp = FastMCP("local-rag")


def _build_retriever() -> Retriever:
    settings = get_rag_settings()
    return Retriever(settings)


@mcp.tool()
def rag_query_docs(question: str) -> dict:
    retriever = _build_retriever()
    return retriever.query(question)


@mcp.tool()
def rag_health() -> dict:
    settings = get_rag_settings()
    return {
        "service": "local-rag",
        "collection": settings.rag_collection,
        "vector_dir": settings.rag_vector_dir,
        "top_k": settings.rag_top_k,
        "technique": settings.rag_technique,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
