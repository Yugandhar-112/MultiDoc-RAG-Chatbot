"""
Central configuration for the app.

Everything here is loaded from environment variables (see .env.example).
Keeping config in one place makes it obvious what knobs exist for tuning
the RAG pipeline (chunk size, top-k, model choice, etc.) without hunting
through the codebase.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- LLM ---
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-5"

    # --- Embeddings ---
    embedding_model: str = "all-MiniLM-L6-v2"

    # --- Vector store ---
    chroma_persist_dir: str = "./data/chroma_db"

    # --- Chunking ---
    chunk_size_tokens: int = 500
    chunk_overlap_tokens: int = 75

    # --- Retrieval ---
    top_k_chunks: int = 5

    # --- CORS ---
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    # lru_cache means we only parse the environment once per process
    return Settings()
