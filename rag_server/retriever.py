# rag_server/retriever.py
from pathlib import Path
from typing import Any, Dict, List
from rag_server.settings import RAGSettings
import chromadb


class Retriever:
    """
    Custom RAG Retriever supporting 'fusion' technique.
    Retrieves top-k relevant chunks from Chroma and
    generates answers using a text generation model.
    """

    def __init__(self, settings: RAGSettings):
        self.settings = settings
        self.vector_dir = Path(settings.rag_vector_dir)

        # Initialize Chroma persistent client
        self.client = chromadb.PersistentClient(path=str(self.vector_dir))
        self.collection = self.client.get_or_create_collection(settings.rag_collection)

    def _expand_queries(self, question: str) -> list[str]:
        base = question.strip()
        return [
            base,
            f"Explain: {base}",
            f"Implementation details for: {base}",
            f"Troubleshooting related to: {base}",
        ]

    def _rrf(self, ranked_lists: list[list[str]], k: int = 60) -> list[str]:
        scores: dict[str, float] = {}
        for ranked in ranked_lists:
            for rank, doc in enumerate(ranked, start=1):
                scores[doc] = scores.get(doc, 0.0) + (1.0 / (k + rank))
        return [doc for doc, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)]

    def _summarize(self, question: str, chunks: list[str]) -> str:
        if not chunks:
            return "No relevant documents found."
        top = chunks[:3]
        summary_lines = [
            f"Question: {question}",
            "Answer (grounded in retrieved chunks):",
            "- " + "\n- ".join(part[:220] for part in top),
        ]
        return "\n".join(summary_lines)

    def query(self, question: str) -> Dict[str, Any]:
        """
        Retrieve top-k chunks and generate a fusion answer.
        """
        if not question.strip():
            return {
                "question": question,
                "answer": "No question provided.",
                "chunks": []
            }

        ranked_lists: list[list[str]] = []
        for query in self._expand_queries(question):
            results = self.collection.query(
                query_texts=[query],
                n_results=self.settings.rag_top_k,
            )
            docs: List[str] = results.get("documents", [[]])[0] if results else []
            if docs:
                ranked_lists.append(docs)

        fused = self._rrf(ranked_lists) if ranked_lists else []
        chunks = fused[: self.settings.rag_top_k]

        if not chunks:
            return {
                "question": question,
                "answer": "No relevant documents found.",
                "chunks": []
            }

        answer_text = self._summarize(question=question, chunks=chunks)

        return {
            "question": question,
            "answer": answer_text,
            "chunks": chunks,
            "technique": self.settings.rag_technique,
            "queries_used": self._expand_queries(question),
        }