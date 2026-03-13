from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    forgepilot_name: str = Field(default="ForgePilot", alias="FORGEPILOT_NAME")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    workspace_root: str = Field(default=".", alias="WORKSPACE_ROOT")
    execution_mode: str = Field(default="confirm", alias="EXECUTION_MODE")

    default_provider: str = Field(default="ollama", alias="DEFAULT_PROVIDER")
    default_model: str = Field(default="llama3.1:8b", alias="DEFAULT_MODEL")
    temperature: float = Field(default=0.1, alias="TEMPERATURE")
    max_tokens: int = Field(default=2048, alias="MAX_TOKENS")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")

    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", alias="ANTHROPIC_MODEL")

    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-70b-versatile", alias="GROQ_MODEL")

    mcp_config_path: str = Field(default="./configs/mcp.servers.example.json", alias="MCP_CONFIG_PATH")
    mcp_timeout_seconds: int = Field(default=30, alias="MCP_TIMEOUT_SECONDS")

    rag_mcp_url: str = Field(default="http://127.0.0.1:8010", alias="RAG_MCP_URL")
    rag_collection: str = Field(default="langchain_docs", alias="RAG_COLLECTION")
    rag_top_k: int = Field(default=5, alias="RAG_TOP_K")


def get_settings() -> Settings:
    return Settings()
