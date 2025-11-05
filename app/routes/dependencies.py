"""Shared API dependencies"""

from app.controllers.document_controller import DocumentController
from app.controllers.query_controller import QueryController
from app.core.config import get_settings
from app.services.chat_memory_service import InMemoryChatMemory, RedisChatMemory, BaseChatMemory

_memory_instance: BaseChatMemory = None

def get_chat_memory() -> BaseChatMemory:
    """
    Singleton provider for chat memory service.
    Call this from FastAPI Depends(...) in endpoints/controllers.
    """
    global _memory_instance
    if _memory_instance is not None:
        return _memory_instance

    settings = get_settings()
    backend = getattr(settings, "CHAT_MEMORY_BACKEND", "memory")

    if backend == "redis" and getattr(settings, "REDIS_URL", None):
        _memory_instance = RedisChatMemory(
            redis_url=settings.REDIS_URL,
            ttl_seconds=getattr(settings, "CHAT_MEMORY_TTL_SECONDS", None),
            namespace=getattr(settings, "CHAT_MEMORY_NAMESPACE", "chat_mem:")
        )
    else:
        _memory_instance = InMemoryChatMemory()

    return _memory_instance

def get_document_controller() -> DocumentController:
    return DocumentController()

def get_query_controller() -> QueryController:
    return QueryController()
