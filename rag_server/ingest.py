from pathlib import Path

from rag_server.settings import get_rag_settings


def run_ingestion() -> str:
    settings = get_rag_settings()
    docs_dir = Path(settings.rag_docs_dir)
    vector_dir = Path(settings.rag_vector_dir)
    vector_dir.mkdir(parents=True, exist_ok=True)

    if not docs_dir.exists():
        return (
            f"No docs found at {docs_dir}. Add source docs, then re-run ingestion. "
            f"Vector directory initialized at {vector_dir}."
        )

    count = sum(1 for p in docs_dir.rglob("*") if p.is_file())
    return (
        f"Template ingestion complete for {count} files into {vector_dir}. "
        "Replace with chunking/embedding/vector insert logic."
    )


if __name__ == "__main__":
    print(run_ingestion())
