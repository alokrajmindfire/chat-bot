"""Configuration settings for the application"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "RAG Pipeline API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "pdf_documents"
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    DEFAULT_TOP_K: int = 3
    MAX_TOP_K: int = 10
    REDIS_URL: Optional[str] = "redis://:admin12345@localhost:6379"
    CHAT_MEMORY_BACKEND: str = "memory"
    CHAT_MEMORY_TTL_SECONDS: Optional[int] = 60 * 60 * 24
    CHAT_MEMORY_NAMESPACE: str = "chat_mem:"
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()