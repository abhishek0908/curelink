import json
from typing import List, Dict
from uuid import UUID
from app.core.redis import redis_client
from app.core.settings import get_settings

class RedisChatService:
    def __init__(self):
        self.client = redis_client
        self.ttl = get_settings().REDIS_CACHE_EXPIRE

    def _messages_key(self, auth_id: UUID) -> str:
        return f"chat:{auth_id}:messages"

    def _summary_key(self, auth_id: UUID) -> str:
        return f"chat:{auth_id}:summary"

    def _user_context_key(self, auth_id: UUID) -> str:
        return f"chat:{auth_id}:user_context"

    def _count_key(self, auth_id: UUID) -> str:
        return f"chat:{auth_id}:count"
    
    def _lock_key(self, auth_id: UUID) -> str:
        return f"chat:{auth_id}:summary_lock"

    # -------- messages --------
    def exists(self, auth_id: UUID) -> bool:
        return self.client.exists(self._messages_key(auth_id))

    def get_messages(self, auth_id: UUID) -> List[Dict]:
        msgs = self.client.lrange(self._messages_key(auth_id), 0, -1)
        return [json.loads(m) for m in msgs]

    def push_message(self, auth_id: UUID, role: str, content: str, limit: int = 3):
        key = self._messages_key(auth_id)
        pipe = self.client.pipeline()
        pipe.rpush(key, json.dumps({"role": role, "content": content}))
        pipe.ltrim(key, -limit, -1)
        pipe.expire(key, self.ttl)
        pipe.execute()

    def clear_messages(self, auth_id: UUID):
        """Removes the chat cache for a user"""
        self.client.delete(self._messages_key(auth_id))

    # -------- summary --------
    def get_summary(self, auth_id: UUID) -> str:
        return self.client.get(self._summary_key(auth_id)) or ""

    def set_summary(self, auth_id: UUID, long_summary: str):
        self.client.set(self._summary_key(auth_id), long_summary or "", ex=self.ttl)

    def set_user_context(self, auth_id: UUID, context: str):
        self.client.set(self._user_context_key(auth_id), context, ex=self.ttl)

    def get_user_context(self, auth_id: UUID) -> str | None:
        val = self.client.get(self._user_context_key(auth_id))
        return val if val else None

    # -------------------------
    # LONG-TERM MESSAGE COUNT
    # -------------------------

    def init_count(self, auth_id: UUID, count: int):
        self.client.set(self._count_key(auth_id), count, ex=self.ttl)

    def get_count(self, auth_id: UUID) -> int:
        value = self.client.get(self._count_key(auth_id))
        return int(value) if value else 0

    def incr_count(self, auth_id: UUID) -> int:
        key = self._count_key(auth_id)
        count = self.client.incr(key)
        self.client.expire(key, self.ttl)
        return count

    def reset_count(self, auth_id: UUID):
        self.client.set(self._count_key(auth_id), 0, ex=self.ttl)

    # -------------------------
    # DISTRIBUTED LOCKING
    # -------------------------

    def acquire_summary_lock(self, auth_id: UUID, ttl: int = 60) -> bool:
        """
        Try to acquire a distributed lock for summary update.
        Returns True if lock acquired, False if already locked.
        TTL ensures lock auto-releases if process crashes.
        """
        lock_key = self._lock_key(auth_id)
        # SET with NX (only if not exists) and EX (expire time)
        acquired = self.client.set(lock_key, "1", nx=True, ex=ttl)
        return acquired is not None

    def release_summary_lock(self, auth_id: UUID):
        """
        Release the distributed lock after summary update completes.
        """
        self.client.delete(self._lock_key(auth_id))

