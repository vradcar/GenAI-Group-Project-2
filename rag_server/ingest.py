# rag_server/ingest.py

from pathlib import Path
from typing import List
import hashlib
from rag_server.settings import get_rag_settings

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb


def load_documents(docs_dir: Path) -> List[str]:
    """
    Load all text files from the source docs directory.
    """
    documents = []
    for file in docs_dir.rglob("*"):
        if file.is_file() and file.suffix in {".txt", ".md"}:
            try:
                text = file.read_text(encoding="utf-8")
                if text.strip():
                    documents.append(text)
            except Exception as e:
                print(f"Skipping {file}: {e}")
    return documents


def chunk_documents(documents: List[str]) -> List[str]:
    """
    Split documents into chunks using RecursiveCharacterTextSplitter.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = []
    for doc in documents:
        chunks.extend(splitter.split_text(doc))
    return chunks


def build_vector_store(chunks: List[str], vector_dir: Path, settings) -> int:
    """
    Embed chunks using SentenceTransformer and store in Chroma vector DB.
    """
    # 1️⃣ Embed the text chunks
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)

    # 2️⃣ Use the new Chroma PersistentClient
    client = chromadb.PersistentClient(path=str(vector_dir))

    # 3️⃣ Get or create the collection
    collection = client.get_or_create_collection(settings.rag_collection)

    # 4️⃣ Upsert chunks with stable IDs for re-runs
    ids = [hashlib.sha1(chunk.encode("utf-8")).hexdigest() for chunk in chunks]
    collection.upsert(documents=chunks, embeddings=embeddings.tolist(), ids=ids)

    return len(chunks)


def run_ingestion():
    """
    Load, chunk, embed, and store documents in the vector database.
    """
    settings = get_rag_settings()
    docs_dir = Path(settings.rag_docs_dir)
    vector_dir = Path(settings.rag_vector_dir)
    vector_dir.mkdir(parents=True, exist_ok=True)

    if not docs_dir.exists():
        return f"No docs found at {docs_dir}"

    print(f"Loading documents from {docs_dir}...")
    documents = load_documents(docs_dir)
    if not documents:
        return f"No valid text documents found in {docs_dir}."

    print(f"Loaded {len(documents)} documents")

    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")

    inserted = build_vector_store(chunks, vector_dir, settings)
    return f"Ingestion complete: {inserted} chunks stored in {vector_dir}"


if __name__ == "__main__":
    print(run_ingestion())