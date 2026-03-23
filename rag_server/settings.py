import os
from typing import Optional
from pydantic import BaseModel, Field

try:
    from pydantic_settings import BaseSettings
except Exception:
    class BaseSettings(BaseModel):
        def __init__(self, **data):
            merged = {}
            for field_name, field_info in self.__class__.model_fields.items():
                env_name = field_info.alias or field_name
                if env_name in os.environ:
                    merged[field_name] = os.environ[env_name]
            merged.update(data)
            super().__init__(**merged)

class RAGSettings(BaseSettings):
    """
    Configuration for the custom RAG MCP server.
    All fields have type annotations and defaults to avoid Pydantic v1 errors.
    Environment variables can override these defaults.
    """

    # Collection name in Chroma vector store
    rag_collection: str = Field(default="langchain_docs", alias="RAG_COLLECTION")

    # Number of top chunks to retrieve per query
    rag_top_k: int = Field(default=5, alias="RAG_TOP_K")

    # Directory for persistent vector store
    rag_vector_dir: str = Field(default=".vectorstore", alias="RAG_VECTOR_DIR")

    # Directory for source documents to ingest
    rag_docs_dir: str = Field(default="docs/source_docs", alias="RAG_DOCS_DIR")

    # Advanced RAG technique to use: "fusion", "hyde", "semantic_chunking"
    rag_technique: str = Field(default="fusion", alias="RAG_TECHNIQUE")

    # Optional flag if Chroma server should run without a local vector DB file
    chroma_server_nofile: Optional[bool] = Field(default=False, alias="CHROMA_SERVER_NOFILE")


def get_rag_settings() -> RAGSettings:
    """
    Returns a ready-to-use settings object.
    Reads values from .env if present.
    """
    return RAGSettings()