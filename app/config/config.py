"""Configuration settings for the application"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Application Config
    APP_NAME: str = "RAG Pipeline API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API Keys
    LLM_API_KEY: str
    OPENWEATHER_API_KEY: str
    LANGSMITH_API_KEY: str
    RAPIDAPI_KEY: str

    # ML Models
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Chroma DB
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "pdf_documents"

    # Chunk Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Search Settings
    DEFAULT_TOP_K: int = 1
    MAX_TOP_K: int = 10

    # Redis / Chat Memory
    REDIS_URL: Optional[str] = "redis://:admin12345@localhost:6379"
    CHAT_MEMORY_BACKEND: str = "memory"
    CHAT_MEMORY_TTL_SECONDS: Optional[int] = 60 * 60 * 24
    CHAT_MEMORY_NAMESPACE: str = "chat_mem:"

    # Pydantic v2 config
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
