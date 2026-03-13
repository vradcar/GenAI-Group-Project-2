from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    rag_collection: str = Field(default="langchain_docs", alias="RAG_COLLECTION")
    rag_top_k: int = Field(default=5, alias="RAG_TOP_K")
    rag_vector_dir: str = Field(default=".vectorstore", alias="RAG_VECTOR_DIR")
    rag_docs_dir: str = Field(default="docs/source_docs", alias="RAG_DOCS_DIR")
    rag_technique: str = Field(default="fusion", alias="RAG_TECHNIQUE")


def get_rag_settings() -> RAGSettings:
    return RAGSettings()
