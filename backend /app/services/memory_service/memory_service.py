from typing import List
from datetime import datetime
from sqlmodel import Session, select

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.models.chat_models import ChatMessage, UserSummary
from app.services.redis_service.redis_service import RedisChatService
import asyncio
MAX_SUMMARY_WORDS = 180
LONG_TERM_TRIGGER_COUNT = 2


class MemoryService:
    def __init__(
        self,
        db: Session,
        redis_service: RedisChatService,
    ):
        self.db = db
        self.redis = redis_service

        # ⚠️ For dev only — move to env var later
        self.llm = ChatOpenAI(
            api_key="testing",
            base_url="https://openrouter.ai/api/v1",

            model="gpt-4o-mini",
            temperature=0,
            max_tokens=300,
        )

    # =====================================================
    # REDIS COUNTER (AUTH_ID BASED)
    # =====================================================

    def initialize_message_count(self, auth_id: str, user_id: int):
        """
        Call ONCE when WebSocket connection is established.
        Redis key uses auth_id, DB uses user_id.
        """
        # If Redis already initialized, skip
        if self.redis.get_count(auth_id) > 0:
            return

        summary = self.get_long_term_summary(user_id)
        last_id = summary.last_summarized_message_id if summary else 0

        stmt = select(ChatMessage.id).where(
            ChatMessage.user_id == user_id,
            ChatMessage.id > last_id,
        )

        count = len(self.db.exec(stmt).all())
        self.redis.init_count(auth_id, count)

        # Warm Redis summary cache
        if summary:
            self.redis.set_summary(auth_id, summary.summary)

    def increment_message_count(self, auth_id: str) -> int:
        """
        Call on EVERY new message (user + assistant).
        """
        return self.redis.incr_count(auth_id)

    def should_update_summary(self, auth_id: str) -> bool:
        """
        Redis-only check (NO DB HIT).
        """
        print("redis count", self.redis.get_count(auth_id))
        return self.redis.get_count(auth_id) >= LONG_TERM_TRIGGER_COUNT

    def reset_message_count(self, auth_id: str):
        self.redis.reset_count(auth_id)

    # =====================================================
    # LONG-TERM SUMMARY (POSTGRES — USER_ID BASED)
    # =====================================================

    def get_long_term_summary(self, user_id: int) -> UserSummary | None:
        stmt = select(UserSummary).where(UserSummary.user_id == user_id)
        return self.db.exec(stmt).first()

    def save_long_term_summary(
        self,
        user_id: int,
        summary: str,
        last_msg_id: int,
        auth_id: str,
    ):
        summary = self._cap_summary(summary)

        record = self.get_long_term_summary(user_id)
        if record:
            record.summary = summary
            record.last_summarized_message_id = last_msg_id
            record.updated_at = datetime.utcnow()
        else:
            self.db.add(
                UserSummary(
                    user_id=user_id,
                    summary=summary,
                    last_summarized_message_id=last_msg_id,
                )
            )

        self.db.commit()

        # Sync Redis cache (auth_id!)
        self.redis.set_summary(auth_id, summary)

    # =====================================================
    # LLM SUMMARY UPDATE (ASYNC SAFE)
    # =====================================================
    async def update_summary_with_llm_async(self, auth_id: str, user_id: int):
        try:
            await asyncio.to_thread(
                self.update_summary_with_llm,
                auth_id,
                user_id,
            )
        except Exception as e:
            print("Summary update failed",e)

    def update_summary_with_llm(self, auth_id: str, user_id: int):
        """
        Called ASYNC when Redis counter >= threshold.
        """
        print(auth_id,"hello")

        summary_record = self.get_long_term_summary(user_id)
        old_summary = summary_record.summary if summary_record else ""
        last_id = summary_record.last_summarized_message_id if summary_record else 0
        print(summary_record,"hello")
        stmt = (
            select(ChatMessage)
            .where(
                ChatMessage.user_id == user_id,
                ChatMessage.id > last_id,
            )
            .order_by(ChatMessage.id.asc())        )

        messages: List[ChatMessage] = self.db.exec(stmt).all()
        if not messages:
            return

        convo = "\n".join(
            f"{m.role}: {m.message}" for m in messages
        )

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You maintain a long-term medical summary.

RULES:
- Keep under {max_words} words
- Remove outdated or resolved symptoms
- Preserve allergies, chronic conditions, and preferences
- Resolve contradictions
"""
            ),
            (
                "user",
                """
EXISTING SUMMARY:
{old_summary}

NEW MESSAGES:
{conversation}

OUTPUT:
Updated summary only.
"""
            )
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "max_words": MAX_SUMMARY_WORDS,
            "old_summary": old_summary,
            "conversation": convo,
        })

        new_summary = response.content.strip()
        last_msg_id = messages[-1].id

        # 1️⃣ Save to Postgres
        self.save_long_term_summary(
            user_id=user_id,
            summary=new_summary,
            last_msg_id=last_msg_id,
            auth_id=auth_id,
        )

        # 2️⃣ Reset Redis counter
        self.reset_message_count(auth_id)

    # =====================================================
    # UTIL
    # =====================================================

    def _cap_summary(self, text: str) -> str:
        words = text.split()
        return " ".join(words[:MAX_SUMMARY_WORDS])
