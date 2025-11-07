"""Controller for query operations"""

from typing import Optional

from app.services.vector_store_service import VectorStoreService
from app.services.ai.llm_service import LLMService
from app.models.response_models import QueryResponse, SourceDocument
from app.core.config import get_settings
from app.services.chat_memory_service import BaseChatMemory
class QueryController:
    def __init__(self, memory_service: Optional[BaseChatMemory] = None):
        self.vector_store_service = VectorStoreService()
        self.llm_service = LLMService()
        self.settings = get_settings()
        self.memory = memory_service

    async def query_documents(
        self,
        question: str,
        top_k: int = None,
        collection_name: str = None,
        conversation_id: Optional[str] = None,
        use_memory: bool = True
    ) -> QueryResponse:
        """Query documents and generate an LLM-based answer with optional chat memory"""

        k = top_k or self.settings.DEFAULT_TOP_K

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
                model_used=self.settings.GEMINI_MODEL,
            )

        context = "\n\n".join([doc.page_content for doc in docs])[:3000]

        conv_history = None
        if use_memory and conversation_id and self.memory:
            conv_history = await self.memory.get_messages(conversation_id)

        answer = self.llm_service.generate_answer(
            context=context,
            question=question,
            conversation_history=conv_history,
        )

        if use_memory and conversation_id and self.memory:
            await self.memory.append_message(conversation_id, "user", question)
            await self.memory.append_message(conversation_id, "assistant", answer)

        sources = [
            SourceDocument(
                content=doc.page_content[:300] + "...",
                metadata=doc.metadata,
                score=0.0,
            )
            for doc in docs
        ]

        return QueryResponse(
            question=question,
            answer=answer,
            sources=sources,
            model_used=self.settings.GEMINI_MODEL,
        )
