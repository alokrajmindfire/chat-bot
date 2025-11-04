"""Controller for query operations"""

from app.services.vector_store_service import VectorStoreService
from app.services.ai.llm_service import LLMService
from app.models.response_models import QueryResponse, SourceDocument
from app.core.config import get_settings

class QueryController:
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.llm_service = LLMService()
        self.settings = get_settings()
    
    def query_documents(
        self,
        question: str,
        top_k: int = None,
        collection_name: str = None
    ) -> QueryResponse:
        """Query documents and generate answer"""
        
        k = top_k or self.settings.DEFAULT_TOP_K
        
        # Retrieve relevant documents
        docs = self.vector_store_service.similarity_search(
            query=question,
            k=k,
            collection_name=collection_name
        )
        
        if not docs:
            return QueryResponse(
                question=question,
                answer="No relevant documents found. Please upload a PDF first.",
                sources=[],
                model_used=self.settings.GEMINI_MODEL
            )
        
        # Prepare context
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Generate answer
        answer = self.llm_service.generate_answer(context, question)
        
        # Prepare sources
        sources = [
            SourceDocument(
                content=doc.page_content[:300] + "...",
                metadata=doc.metadata,
                score=0.0  # ChromaDB similarity score would go here
            ) for doc in docs
        ]
        
        return QueryResponse(
            question=question,
            answer=answer,
            sources=sources,
            model_used=self.settings.GEMINI_MODEL
        )
    