"""Service for ChromaDB vector store operations"""

from langchain_community.vectorstores import Chroma
from typing import List, Optional
from langchain_core.documents import Document
from app.core.config import get_settings
from app.core.exceptions import VectorStoreError
from app.services.ai.embeddings_service import EmbeddingsService

class VectorStoreService:
    def __init__(self):
        self.settings = get_settings()
        self.embeddings = EmbeddingsService().get_embeddings()
        self._vectorstore = None
    
    def get_or_create_vectorstore(self, collection_name: Optional[str] = None) -> Chroma:
        """Get or create vector store"""
        try:
            collection = collection_name or self.settings.CHROMA_COLLECTION_NAME
            
            if self._vectorstore is None:
                self._vectorstore = Chroma(
                    collection_name=collection,
                    embedding_function=self.embeddings,
                    persist_directory=self.settings.CHROMA_PERSIST_DIR
                )
            
            return self._vectorstore
        
        except Exception as e:
            raise VectorStoreError(f"Error accessing vector store: {str(e)}")
    
    def add_documents(self, documents: List[Document], collection_name: Optional[str] = None):
        """Add documents to vector store"""
        try:
            vectorstore = self.get_or_create_vectorstore(collection_name)
            
            if vectorstore._collection.count() == 0:
                # Create new vector store
                self._vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.settings.CHROMA_PERSIST_DIR,
                    collection_name=collection_name or self.settings.CHROMA_COLLECTION_NAME
                )
            else:
                vectorstore.add_documents(documents)
            
            self._vectorstore.persist()
        
        except Exception as e:
            raise VectorStoreError(f"Error adding documents: {str(e)}")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 3,
        collection_name: Optional[str] = None
    ) -> List[Document]:
        """Search for similar documents"""
        try:
            vectorstore = self.get_or_create_vectorstore(collection_name)
            return vectorstore.similarity_search(query, k=k)
        
        except Exception as e:
            raise VectorStoreError(f"Error searching documents: {str(e)}")
    
    def check_health(self) -> bool:
        """Check if vector store is accessible"""
        try:
            vectorstore = self.get_or_create_vectorstore()
            return True
        except:
            return False

