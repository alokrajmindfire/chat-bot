from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import time
import json
import asyncio

try:
    import redis.asyncio as redis_async
except Exception:
    redis_async = None


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


class InMemoryChatMemory(BaseChatMemory):
    """Simple in-memory conversation store (not persistent)."""

    def __init__(self):
        # { conversation_id: [ {ts, role, text}, ... ] }
        self._store = {}
        # protect concurrent access
        self._lock = asyncio.Lock()

    async def append_message(self, conversation_id: str, role: str, text: str) -> None:
        async with self._lock:
            messages = self._store.setdefault(conversation_id, [])
            messages.append({"ts": int(time.time()), "role": role, "text": text})

    async def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict]:
        async with self._lock:
            messages = self._store.get(conversation_id, []).copy()
        if limit:
            return messages[-limit:]
        return messages

    async def clear_conversation(self, conversation_id: str) -> None:
        async with self._lock:
            if conversation_id in self._store:
                del self._store[conversation_id]


class RedisChatMemory(BaseChatMemory):
    """
    Redis-backed chat memory.
    Uses a Redis list per conversation key. Values are JSON strings.
    """

    def __init__(self, redis_url: str, ttl_seconds: Optional[int] = None, namespace: str = "chat_mem:"):
        if redis_async is None:
            raise RuntimeError("redis.asyncio is required for RedisChatMemory (install redis>=4.5.0)")
        self._client = redis_async.from_url(redis_url, decode_responses=True)
        self._ttl = ttl_seconds
        self._ns = namespace

    def _key(self, conversation_id: str) -> str:
        return f"{self._ns}{conversation_id}"

    async def append_message(self, conversation_id: str, role: str, text: str) -> None:
        key = self._key(conversation_id)
        payload = json.dumps({"ts": int(time.time()), "role": role, "text": text})
        # push to list (right push)
        await self._client.rpush(key, payload)
        if self._ttl:
            await self._client.expire(key, self._ttl)

    async def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict]:
        key = self._key(conversation_id)
        if limit is None:
            values = await self._client.lrange(key, 0, -1)
        else:
            # get last `limit` items
            values = await self._client.lrange(key, -limit, -1)
        return [json.loads(v) for v in values if v]

    async def clear_conversation(self, conversation_id: str) -> None:
        key = self._key(conversation_id)
        await self._client.delete(key)
