"""Service for generating embeddings"""

from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config.config import get_settings

class EmbeddingsService:
    _instance = None
    embeddings: HuggingFaceEmbeddings

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            settings = get_settings()
            cls._instance.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL
            )
        return cls._instance

    def get_embeddings(self):
        return self.embeddings
