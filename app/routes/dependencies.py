"""Shared API dependencies"""

from fastapi import Depends
from app.controllers.document_controller import DocumentController
from app.controllers.query_controller import QueryController
from app.config.config import get_settings
from app.services.chat_memory_service import RedisChatMemory, BaseChatMemory

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
    if not getattr(settings, "REDIS_URL", None):
        raise RuntimeError("REDIS_URL is required for RedisChatMemory")

    _memory_instance = RedisChatMemory(
        redis_url=settings.REDIS_URL,
        ttl_seconds=getattr(settings, "CHAT_MEMORY_TTL_SECONDS", 86400),
        namespace=getattr(settings, "CHAT_MEMORY_NAMESPACE", "chat_mem:")
    )
    return _memory_instance

def get_document_controller() -> DocumentController:
    return DocumentController()

def get_query_controller(memory_service: BaseChatMemory = Depends(get_chat_memory)) -> QueryController:
    """Inject chat memory into QueryController"""
    return QueryController(memory_service=memory_service)