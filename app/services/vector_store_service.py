"""Service for ChromaDB vector store operations"""

from langchain_community.vectorstores import Chroma
from typing import List, Optional
from langchain_core.documents import Document
from app.core.config import get_settings
from app.core.exceptions import VectorStoreError
from app.services.ai.embeddings_service import EmbeddingsService
from app.config.logger import logger

class VectorStoreService:
    def __init__(self):
        self.settings = get_settings()
        self.embeddings = EmbeddingsService().get_embeddings()
        self._vectorstore = None
        logger.info("VectorStoreService initialized with embeddings and configuration")

    def get_or_create_vectorstore(self, collection_name: Optional[str] = None) -> Chroma:
        """Get or create vector store"""
        try:
            collection = collection_name or self.settings.CHROMA_COLLECTION_NAME
            
            if self._vectorstore is None:
                logger.info(f"Creating new Chroma vector store for collection: {collection}")
                self._vectorstore = Chroma(
                    collection_name=collection,
                    embedding_function=self.embeddings,
                    persist_directory=self.settings.CHROMA_PERSIST_DIR
                )
            else:
                logger.debug(f"Using existing vector store for collection: {collection}")
            return self._vectorstore
        
        except Exception as e:
            logger.exception(f"Error accessing or creating vector store '{collection}': {e}")
            raise VectorStoreError(f"Error accessing vector store: {str(e)}")
    
    def add_documents(self, documents: List[Document], collection_name: Optional[str] = None):
        """Add documents to vector store"""
        collection = collection_name or self.settings.CHROMA_COLLECTION_NAME
        try:
            logger.info(f"Adding {len(documents)} documents to collection: {collection}")
            vectorstore = self.get_or_create_vectorstore(collection_name)
            
            if vectorstore._collection.count() == 0:
                logger.debug(f"Collection '{collection}' is empty — creating new Chroma index")
                self._vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.settings.CHROMA_PERSIST_DIR,
                    collection_name=collection_name or self.settings.CHROMA_COLLECTION_NAME
                )
            else:
                logger.debug(f"Collection '{collection}' already exists — adding documents")
                vectorstore.add_documents(documents)
            
            self._vectorstore.persist()
            logger.info(f"Successfully persisted collection: {collection}")
        
        except Exception as e:
            logger.exception(f"Error adding documents to collection '{collection}': {e}")
            raise VectorStoreError(f"Error adding documents: {str(e)}")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 3,
        collection_name: Optional[str] = None
    ) -> List[Document]:
        """Search for similar documents"""
        collection = collection_name or self.settings.CHROMA_COLLECTION_NAME
        try:
            logger.info("Performing similarity search on '%s' for query: %.80s...", collection, query)
            vectorstore = self.get_or_create_vectorstore(collection_name)
            results = vectorstore.similarity_search(query, k=k)
            logger.info("Found %d similar documents in collection: %s", len(results), collection)
            return results
        
        except Exception as e:
            
            logger.exception("Error searching documents in '%s': %s", collection, e)
            raise VectorStoreError(f"Error searching documents: {str(e)}")
    
    def check_health(self) -> bool:
        """Check if vector store is accessible"""
        try:
            vectorstore = self.get_or_create_vectorstore()
            if vectorstore is None:
                logger.warning("Vector store is None during health check")
                return False
            count = vectorstore._collection.count() if hasattr(vectorstore, "_collection") else None

            if count is not None:
                logger.debug("Vector store health check passed — collection contains %d items", count)
                return True
            else:
                logger.warning("Vector store health check failed — collection count unavailable")
                return False
        except Exception as e:
            logger.exception("Vector store health check failed: %s", e)
            return False

