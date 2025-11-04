"""Configuration settings for the application"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "RAG Pipeline API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # AI Settings
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Vector Store Settings
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "pdf_documents"
    
    # Chunking Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Query Settings
    DEFAULT_TOP_K: int = 3
    MAX_TOP_K: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()