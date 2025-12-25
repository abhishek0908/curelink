import json
from typing import List, Dict
import redis


class RedisChatService:
    def __init__(self, client: redis.Redis):
        self.client = client

    def _messages_key(self, auth_id: int) -> str:
        return f"chat:{auth_id}:messages"

    def _summary_key(self, auth_id: int) -> str:
        return f"chat:{auth_id}:summary"

    def _count_key(self, auth_id: int) -> str:
        return f"chat:{auth_id}:count"
    # -------- messages --------
    def exists(self, auth_id: int) -> bool:
        return self.client.exists(self._messages_key(auth_id))

    def get_messages(self, auth_id: int) -> List[Dict]:
        msgs = self.client.lrange(self._messages_key(auth_id), 0, -1)
        return [json.loads(m) for m in msgs]

    def push_message(self, auth_id: int, role: str, content: str, limit: int = 3):
        key = self._messages_key(auth_id)
        pipe = self.client.pipeline()
        pipe.rpush(key, json.dumps({"role": role, "content": content}))
        pipe.ltrim(key, -limit, -1)
        pipe.execute()

    # -------- summary --------
    def get_summary(self, auth_id: int) -> str:
        return self.client.get(self._summary_key(auth_id)) or ""

    def set_summary(self, auth_id: int, long_summary: str):
        self.client.set(self._summary_key(auth_id), long_summary)


     # -------------------------
    # LONG-TERM MESSAGE COUNT
    # -------------------------

    def init_count(self, auth_id: int, count: int):
        """
        Called ONCE on WebSocket connection.
        Initializes Redis count from DB.
        """
        self.client.set(self._count_key(auth_id), count)

    def get_count(self, auth_id: int) -> int:
        """
        Returns current unsummarized message count.
        """
        value = self.client.get(self._count_key(auth_id))
        print("redis count", value,auth_id,self._count_key(auth_id))
        return int(value) if value else 0

    def incr_count(self, auth_id: int) -> int:
        """
        Increment count on EVERY new message.
        Returns updated count.
        """
        return self.client.incr(self._count_key(auth_id))

    def reset_count(self, auth_id: int):
        """
        Reset count after long-term memory update.
        """
        self.client.set(self._count_key(auth_id), 0)
