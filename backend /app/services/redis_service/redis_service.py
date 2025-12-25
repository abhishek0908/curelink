import json
from typing import List, Dict
import redis


class RedisChatService:
    def __init__(self, client: redis.Redis):
        self.client = client

    def _messages_key(self, user_id: int) -> str:
        return f"chat:{user_id}:messages"

    def _summary_key(self, user_id: int) -> str:
        return f"chat:{user_id}:summary"

    # -------- messages --------
    def exists(self, user_id: int) -> bool:
        return self.client.exists(self._messages_key(user_id))

    def get_messages(self, user_id: int) -> List[Dict]:
        msgs = self.client.lrange(self._messages_key(user_id), 0, -1)
        return [json.loads(m) for m in msgs]

    def push_message(self, user_id: int, role: str, content: str, limit: int = 3):
        key = self._messages_key(user_id)
        pipe = self.client.pipeline()
        pipe.rpush(key, json.dumps({"role": role, "content": content}))
        pipe.ltrim(key, -limit, -1)
        pipe.execute()

    # -------- summary --------
    def get_summary(self, user_id: int) -> str:
        return self.client.get(self._summary_key(user_id)) or ""

    def set_summary(self, user_id: int, summary: str):
        self.client.set(self._summary_key(user_id), summary)
