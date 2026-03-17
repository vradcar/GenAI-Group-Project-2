# rag_server/retriever.py
from pathlib import Path
from typing import List, Dict
from transformers import pipeline
from rag_server.settings import RAGSettings
import chromadb
import numpy as np


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

        # Initialize generator for fusion RAG
        # Use 'text-generation' which is compatible with current Transformers
        self.generator = pipeline(
            task="text-generation",
            model="google/flan-t5-small"
        )

    def query(self, question: str) -> Dict:
        """
        Retrieve top-k chunks and generate a fusion answer.
        """
        if not question.strip():
            return {
                "question": question,
                "answer": "No question provided.",
                "chunks": []
            }

        # Step 1: Retrieve top-k relevant chunks
        results = self.collection.query(
            query_texts=[question],
            n_results=self.settings.rag_top_k
        )

        chunks: List[str] = results['documents'][0] if results['documents'] else []

        if not chunks:
            return {
                "question": question,
                "answer": "No relevant documents found.",
                "chunks": []
            }

        # Step 2: Fuse retrieved chunks into a single context
        context = "\n".join(chunks)

        # Step 3: Generate answer using text-generation model
        prompt = f"Question: {question}\nContext: {context}\nAnswer:"
        generated = self.generator(prompt, max_new_tokens=256)
        answer_text = generated[0]['generated_text']

        return {
            "question": question,
            "answer": answer_text,
            "chunks": chunks
        }