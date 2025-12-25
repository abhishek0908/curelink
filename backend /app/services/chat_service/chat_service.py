from sqlmodel import Session, select

from app.models.chat_models import ChatMessage, UserSummary
from app.models.user_model import UserOnboarding
from app.services.redis_service.redis_service import RedisChatService
from app.services.llm_service.llm_service import LLMService
from app.utility.role_enum import ChatRole
from app.core.settings import get_settings
from app.core.security import jwt_handler
from app.services.memory_service.memory_service import MemoryService
from fastapi import BackgroundTasks
import asyncio
settings = get_settings()

class ChatService:
    def __init__(self, db: Session, redis_service: RedisChatService, llm_service: LLMService):
        self.db = db
        self.redis = redis_service
        self.llm = llm_service
        self.memory = MemoryService(db, redis_service)

    def get_user(self, auth_id: str) -> UserOnboarding | None:
        stmt = select(UserOnboarding).where(
            UserOnboarding.auth_user_id == auth_id
        )
        return self.db.exec(stmt).first()

    def validate_user(self, auth_id: str) -> bool:
        return self.get_user(auth_id) is not None

    def bootstrap_context(self, auth_id: str, limit: int = 3) -> None:
        if self.redis.exists(auth_id):
            return

        user = self.get_user(auth_id)
        if not user:
            return

        user_id = user.id

        # 1️⃣ Load recent messages into Redis for prompt context
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.id.desc())
            .limit(limit)
        )

        messages = list(reversed(self.db.exec(stmt).all()))
        for msg in messages:
            self.redis.push_message(
                auth_id,
                role=msg.role,
                content=msg.message,
            )
        get_long_term_summary = self.memory.get_long_term_summary(user_id)
        if get_long_term_summary:
            self.redis.set_summary(
                auth_id,
                long_summary=get_long_term_summary.long_summary or "",
            )

        # 2️⃣ Sync Long-term summary and unsummarized count into Redis
        self.memory.initialize_message_count(auth_id=auth_id,user_id=user_id)

    def handle_message(self, auth_id: str, user_text: str,    background_tasks: BackgroundTasks,
) -> str:
        user = self.get_user(auth_id)
        if not user:
            raise ValueError("Invalid user")

        user_id = user.id

        # Save user message
        self.db.add(
            ChatMessage(
                user_id=user_id,
                role=ChatRole.USER.value,
                message=user_text,   # ✅ FIX
            )
        )
        self.db.commit()

        self.redis.push_message(
            auth_id,
            role=ChatRole.USER.value,
            content=user_text,
            limit=settings.chat_context_limit,
        )

        ai_reply = self.llm.generate_reply(
            summary=self.redis.get_summary(auth_id),
            messages=self.redis.get_messages(auth_id),
            user_input=user_text,
        )

        # Save AI message
        self.db.add(
            ChatMessage(
                user_id=user_id,
                role=ChatRole.ASSISTANT.value,
                message=ai_reply,    # ✅ FIX
            )
        )
        self.db.commit()

        self.redis.push_message(
            auth_id,
            role=ChatRole.ASSISTANT.value,
            content=ai_reply,
            limit=settings.chat_context_limit,
        )

        if self.memory.should_update_summary(auth_id):
            asyncio.create_task(
                self.memory.update_summary_with_llm_async(auth_id, user_id)
            )

        return ai_reply
