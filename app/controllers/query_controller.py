"""Controller for query operations"""

from app.services.vector_store_service import VectorStoreService
from app.services.ai.llm_service import LLMService
from app.models.response_models import QueryResponse, SourceDocument
from app.core.config import get_settings
from typing import Optional
from app.services.chat_memory_service import BaseChatMemory
class QueryController:
    def __init__(self, memory_service: Optional[BaseChatMemory] = None):
        self.vector_store_service = VectorStoreService()
        self.llm_service = LLMService()
        self.settings = get_settings()
        self.memory = memory_service
        
    def query_documents(
        self,
        question: str,
        top_k: int = None,
        collection_name: str = None,
        conversation_id: Optional[str] = None,
        use_memory: bool = True
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
        
        conv_history = None
        if use_memory and conversation_id and self.memory:
            # memory returns list of messages with role/text
            # This is async in Redis implementation, so call sync wrapper using asyncio.run if necessary.
            # To keep controller sync, we'll run the coroutine to get messages.
            import asyncio
            conv_history = asyncio.get_event_loop().run_until_complete(
                self.memory.get_messages(conversation_id)
            )

        # Generate answer
        answer = self.llm_service.generate_answer(context, question, conversation_history=conv_history)

        # Save to memory (user question and assistant answer)
        if use_memory and conversation_id and self.memory:
            import asyncio
            loop = asyncio.get_event_loop()
            # append user message
            loop.run_until_complete(self.memory.append_message(conversation_id, "user", question))
            # append assistant message
            loop.run_until_complete(self.memory.append_message(conversation_id, "assistant", answer))

        # Prepare sources
        sources = [
            SourceDocument(
                content=doc.page_content[:300] + "...",
                metadata=doc.metadata,
                score=0.0
            ) for doc in docs
        ]

        return QueryResponse(
            question=question,
            answer=answer,
            sources=sources,
            model_used=self.settings.GEMINI_MODEL
        )