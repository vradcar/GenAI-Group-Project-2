from pathlib import Path

from rag_server.settings import RAGSettings


class TemplateRetriever:
    def __init__(self, settings: RAGSettings) -> None:
        self.settings = settings
        self.vector_dir = Path(settings.rag_vector_dir)

    def ensure_vector_store(self) -> None:
        self.vector_dir.mkdir(parents=True, exist_ok=True)

    def query(self, question: str) -> dict:
        self.ensure_vector_store()
        return {
            "question": question,
            "technique": self.settings.rag_technique,
            "chunks": [
                "Template chunk 1: replace with vector retrieval output.",
                "Template chunk 2: add citations and reranking/fusion output.",
            ],
            "answer": "Template answer from custom RAG MCP server.",
        }
