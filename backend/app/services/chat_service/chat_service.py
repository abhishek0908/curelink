from sqlmodel import Session, select
import threading

from app.models.chat_models import ChatMessage, UserSummary
from app.models.user_model import UserOnboarding
from app.services.redis_service.redis_service import RedisChatService
from app.services.llm_service.llm_service import LLMService
from app.utility.role_enum import ChatRole
from app.services.memory_service.memory_service import MemoryService
from app.core.settings import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)
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

    async def bootstrap_context(self, auth_id: str, limit: int = None) -> None:
        """
        Initializes the chat session in Redis. 
        Clears old cache to prevent duplicates and loads fresh context from DB.
        """
        if limit is None:
            limit = settings.CHAT_CACHE_LIMIT

        user = self.get_user(auth_id)
        if not user:
            return

        user_id = user.id

        # 1️⃣ Clear old chat cache to prevent duplicates on reconnect
        self.redis.clear_messages(auth_id)

        # 2️⃣ Load recent messages into Redis for prompt context
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.id.desc())
            .limit(settings.CHAT_CACHE_LIMIT)
        )

        messages = list(reversed(self.db.exec(stmt).all()))
        for msg in messages:
            self.redis.push_message(
                auth_id,
                role=msg.role,
                content=msg.message,
                limit=settings.CHAT_CACHE_LIMIT
            )

        # 3️⃣ Sync Summary
        get_long_term_summary = self.memory.get_long_term_summary(user_id)
        self.redis.set_summary(
            auth_id,
            long_summary=get_long_term_summary.long_summary if get_long_term_summary else "",
        )

        # 4️⃣ Initialize count & User Context
        self.memory.initialize_message_count(auth_id=auth_id, user_id=user_id)
        self.memory.load_user_context(auth_id=auth_id, user_id=user_id)

    async def handle_message(self, auth_id: str, user_text: str) -> str:
        """
        Handle incoming user message, generate AI reply, and trigger summary update if needed.
        """
        user = self.get_user(auth_id)
        if not user:
            raise ValueError("Invalid user")

        user_id = user.id

        # Save user message
        self.db.add(
            ChatMessage(
                user_id=user_id,
                role=ChatRole.USER.value,
                message=user_text,
            )
        )
        self.db.commit()

        self.redis.push_message(
            auth_id,
            role=ChatRole.USER.value,
            content=user_text,
            limit=settings.CHAT_CACHE_LIMIT,
        )
        self.memory.increment_message_count(auth_id)
        #TODO : we need to make sure that if we fallback from redis we use postgres as of now we are assuming data availabe in redis
        ai_reply = await self.llm.generate_reply(
            summary=self.redis.get_summary(auth_id),
            messages=self.redis.get_messages(auth_id),
            user_input=user_text,
            user_info=self.redis.get_user_context(auth_id),
        )

        # Save AI message
        self.db.add(
            ChatMessage(
                user_id=user_id,
                role=ChatRole.ASSISTANT.value,
                message=ai_reply,
            )
        )
        self.db.commit()

        self.redis.push_message(
            auth_id,
            role=ChatRole.ASSISTANT.value,
            content=ai_reply,
            limit=settings.CHAT_CACHE_LIMIT,
        )
        self.memory.increment_message_count(auth_id)

        #TODO : Use threading instead of BackgroundTasks (which doesn't work with WebSocket) but we can face issue in  threading in scale so we need to implement using asyncio.to_thread
        if self.memory.should_update_summary(auth_id):
            logger.info(f"Triggering summary update in background thread for {auth_id}")
            thread = threading.Thread(
                target=self.memory.update_summary_with_llm,
                args=(auth_id, user_id),
                daemon=True  # Daemon thread won't prevent app shutdown
            )
            thread.start()

        return ai_reply

