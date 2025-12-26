from typing import List
from datetime import datetime
from sqlmodel import Session, select

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.models.chat_models import ChatMessage, UserSummary
from app.models.user_model import UserOnboarding
from app.services.redis_service.redis_service import RedisChatService
from app.core.logger import get_logger
from app.core.settings import get_settings

settings = get_settings()
logger = get_logger(__name__)

MAX_SUMMARY_WORDS = settings.MAX_SUMMARY_WORDS
LONG_TERM_TRIGGER_COUNT = settings.LONG_TERM_TRIGGER_COUNT


class MemoryService:
    def __init__(
        self,
        db: Session,
        redis_service: RedisChatService,
    ):
        self.db = db
        self.redis = redis_service
        # NOTE: LLM is NOT shared - created per-call for thread safety

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


    def increment_message_count(self, auth_id: str) -> int:
        """
        Call on EVERY new message (user + assistant).
        """
        return self.redis.incr_count(auth_id)

    def should_update_summary(self, auth_id: str) -> bool:
        """
        Redis-only check with distributed lock to prevent duplicate threads.
        Returns True only if count >= threshold AND lock is acquired.
        """
        count = self.redis.get_count(auth_id)
        logger.info(f"Redis message count for {auth_id}: {count}")
        
        if count < LONG_TERM_TRIGGER_COUNT:
            return False
        
        # Try to acquire lock - prevents duplicate threads
        if not self.redis.acquire_summary_lock(auth_id, ttl=120):
            logger.info(f"Summary lock already held for {auth_id}, skipping")
            return False
        
        return True

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
            record.long_summary = summary
            record.last_summarized_message_id = last_msg_id
            record.updated_at = datetime.utcnow()
        else:
            self.db.add(
                UserSummary(
                    user_id=user_id,
                    long_summary=summary,
                    last_summarized_message_id=last_msg_id,
                )
            )

        self.db.commit()

        # Sync Redis cache (auth_id!)
        self.redis.set_summary(auth_id, summary)



    def load_user_context(self, auth_id: str, user_id: int) -> None:
        """
        Loads user onboarding data into Redis as system context.
        Called once during chat bootstrap.
        """
        try:
            logger.info(f"Loading user context for {auth_id}")

            # Avoid duplicate loading
            if self.redis.get_user_context(auth_id) is not None:
                logger.debug(f"User context already loaded for {auth_id}")
                return

            stmt = select(UserOnboarding).where(
                UserOnboarding.auth_user_id == auth_id
            )
            onboarding = self.db.exec(stmt).first()
            logger.info(f"User onboarding data: {onboarding}")
            # If onboarding not found, still mark as initialized
            if not onboarding:
                logger.warning(f"No onboarding data found for {auth_id}, initializing empty context")
                self.redis.set_user_context(auth_id, "")
                return

            context_parts: list[str] = []

            if onboarding.full_name:
                context_parts.append(f"Name: {onboarding.full_name}")

            if onboarding.age:
                context_parts.append(f"Age: {onboarding.age}")

            if onboarding.gender:
                context_parts.append(f"Gender: {onboarding.gender}")

            if onboarding.previous_diseases:
                context_parts.append(
                    "Previous diseases: " + ", ".join(onboarding.previous_diseases)
                )

            if onboarding.current_symptoms:
                context_parts.append(
                    "Current symptoms: " + ", ".join(onboarding.current_symptoms)
                )

            if onboarding.medications:
                context_parts.append(
                    "Medications: " + ", ".join(onboarding.medications)
                )

            if onboarding.allergies:
                context_parts.append(
                    "Allergies: " + ", ".join(onboarding.allergies)
                )

            if onboarding.additional_notes:
                context_parts.append(
                    f"Additional notes: {onboarding.additional_notes}"
                )

            user_context = "\n".join(context_parts)

            # Store in Redis (auth_id scoped)
            self.redis.set_user_context(auth_id, user_context)
            logger.info(f"User context successfully loaded for {auth_id}")

        except Exception as e:
            logger.error(f"Error loading user context for {auth_id}: {e}")



    # =====================================================
    # LLM SUMMARY UPDATE (ASYNC SAFE)
    # =====================================================

    def update_summary_with_llm(self, auth_id: str, user_id: int):
        """
        Called ASYNC when Redis counter >= threshold.
        Creates its own DB session since background tasks run after original session closes.
        """
        from app.database.database import engine  # Import here to avoid circular imports
        from sqlmodel import Session
        
        logger.info(f"Updating summary for auth_id: {auth_id}")
        
        try:
            with Session(engine) as db:
                # Get existing summary
                stmt = select(UserSummary).where(UserSummary.user_id == user_id)
                summary_record = db.exec(stmt).first()
                
                old_summary = summary_record.long_summary if summary_record else ""
                last_id = summary_record.last_summarized_message_id if summary_record else 0
                logger.debug(f"Previous summary record: {summary_record}")
                
                # Get new messages
                stmt = (
                    select(ChatMessage)
                    .where(
                        ChatMessage.user_id == user_id,
                        ChatMessage.id > last_id,
                    )
                    .order_by(ChatMessage.id.asc())
                )

                messages: List[ChatMessage] = db.exec(stmt).all()
                if not messages:
                    logger.info(f"No new messages to summarize for {auth_id}")
                    return

                convo = "\n".join(
                    f"{m.role}: {m.message}" for m in messages
                )

                prompt = ChatPromptTemplate.from_messages([
                    (
                        "system",
                        """
Your name is disha. You are a long-term medical summary assistant.

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

                # Create LLM client per-call for thread safety
                llm = ChatOpenAI(
                    api_key=settings.OPENROUTER_API_KEY,
                    base_url=settings.OPENROUTER_BASE_URL,
                    model=settings.OPENROUTER_MODEL,
                    temperature=0,
                    max_tokens=300,
                )

                chain = prompt | llm
                response = chain.invoke({
                    "max_words": MAX_SUMMARY_WORDS,
                    "old_summary": old_summary,
                    "conversation": convo,
                })

                new_summary = response.content.strip()
                new_summary = self._cap_summary(new_summary)
                last_msg_id = messages[-1].id

                # Save to Postgres
                if summary_record:
                    summary_record.long_summary = new_summary
                    summary_record.last_summarized_message_id = last_msg_id
                    summary_record.updated_at = datetime.utcnow()
                else:
                    db.add(
                        UserSummary(
                            user_id=user_id,
                            long_summary=new_summary,
                            last_summarized_message_id=last_msg_id,
                        )
                    )

                db.commit()
                logger.info(f"Summary updated successfully for {auth_id}")

                # Sync Redis cache
                self.redis.set_summary(auth_id, new_summary)

                # Reset Redis counter
                self.reset_message_count(auth_id)
                
        except Exception as e:
            logger.error(f"Error updating summary for {auth_id}: {e}")
        finally:
            # Always release lock, even on error
            self.redis.release_summary_lock(auth_id)

    # =====================================================
    # UTIL
    # =====================================================

    def _cap_summary(self, text: str) -> str:
        words = text.split()
        return " ".join(words[:MAX_SUMMARY_WORDS])
