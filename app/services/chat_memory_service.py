from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import time
import json
import redis.asyncio as redis_async

class BaseChatMemory(ABC):
    """Abstract chat memory interface."""

    @abstractmethod
    async def append_message(self, conversation_id: str, role: str, text: str) -> None:
        ...

    @abstractmethod
    async def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict]:
        ...

    @abstractmethod
    async def clear_conversation(self, conversation_id: str) -> None:
        ...


class RedisChatMemory(BaseChatMemory):
    """
    Redis-backed chat memory.
    Uses a Redis list per conversation key. Values are JSON strings.
    """

    def __init__(
        self,
        redis_url: str,
        ttl_seconds: Optional[int] = 86400,
        namespace: str = "chat_mem:"
    ):
        if not redis_async:
            raise RuntimeError("redis.asyncio is required for RedisChatMemory (install redis>=4.5.0)")

        self._client = redis_async.from_url(redis_url, decode_responses=True)
        self._ttl = ttl_seconds
        self._ns = namespace

    def _key(self, conversation_id: str) -> str:
        """Generate namespaced Redis key."""
        return f"{self._ns}{conversation_id}"

    async def append_message(self, conversation_id: str, role: str, text: str) -> None:
        """Append a message to the Redis list."""
        key = self._key(conversation_id)
        payload = json.dumps({"ts": int(time.time()), "role": role, "text": text})
        await self._client.rpush(key, payload)
        await self._client.expire(key, self._ttl)

    async def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve the message history."""
        key = self._key(conversation_id)
        if limit is None:
            values = await self._client.lrange(key, 0, -1)
        else:
            values = await self._client.lrange(key, -limit, -1)
        return [json.loads(v) for v in values if v]

    async def clear_conversation(self, conversation_id: str) -> None:
        """Delete all messages for a conversation."""
        key = self._key(conversation_id)
        await self._client.delete(key)
