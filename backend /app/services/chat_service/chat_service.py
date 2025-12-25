from sqlmodel import Session, select
from app.models.chat_models import ChatMessage,UserSummary
from app.models.user_model import UserOnboarding
from app.core.redis_chat import RedisChatService
from app.services.llm_service import LLMService
from app.utility.role_enum import ChatRole
from app.core.settings import get_settings
settings = get_settings()

class ChatService:
    def __init__(
        self,
        db: Session,
        redis_service: RedisChatService,
        llm_service: LLMService,
    ):
        self.db = db
        self.redis = redis_service
        self.llm = llm_service

    # 1️⃣ Validate user
    def validate_user(self, user_id: int) -> bool:
        return self.db.get(UserOnboarding, user_id) is not None

    # 2️⃣ Load last 3 messages + summary into Redis (only once)
    def bootstrap_context(self, user_id: int, limit: int = 3):
        if self.redis.exists(user_id):
            return

        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )

        messages = list(reversed(self.db.exec(stmt).all()))
        for msg in messages:
            self.redis.push_message(user_id, msg.role, msg.content)

        summary = self.db.get(UserSummary, user_id)
        self.redis.set_summary(user_id, summary.short_summary)

    # 3️⃣ Handle one user message
    def handle_message(self, user_id: int, user_text: str) -> str:
    # 1️⃣ Save user message to DB
        self.db.add(ChatMessage(
            user_id=user_id,
            role=ChatRole.USER.value,
            content=user_text
        ))
        self.db.commit()

        # 2️⃣ Push user message to Redis (auto-trims)
        self.redis.push_message(
            user_id,
            role=ChatRole.USER.value,
            content=user_text,
            limit=settings.chat_context_limit
        )

        # 3️⃣ Generate AI reply
        ai_reply = self.llm.generate_reply(
            summary=self.redis.get_summary(user_id),
            messages=self.redis.get_messages(user_id),
            user_input=user_text
        )

        # 4️⃣ Save AI message to DB
        self.db.add(ChatMessage(
            user_id=user_id,
            role=ChatRole.ASSISTANT.value,
            content=ai_reply
        ))
        self.db.commit()

        # 5️⃣ Push AI message to Redis (auto-trims)
        self.redis.push_message(
            user_id,
            role=ChatRole.ASSISTANT.value,
            content=ai_reply,
            limit=settings.chat_context_limit
        )

        return ai_reply
