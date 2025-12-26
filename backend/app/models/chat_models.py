# app/models/chat_model.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from uuid import UUID
import uuid


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: UUID = Field(
        foreign_key="user_onboarding.id",
        index=True,
        nullable=False
    )
    role: str = Field(nullable=False)
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow,index=True)

    user: Optional["UserOnboarding"] = Relationship(back_populates="chat_messages")



class UserSummary(SQLModel, table=True):
    __tablename__ = "user_summary"

    id: UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    user_id: UUID = Field(
        foreign_key="user_onboarding.id",
        unique=True,
        nullable=False,
        index=True
    )
    last_summarized_message_id: Optional[int] = None
    short_summary: Optional[str] = None
    long_summary: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["UserOnboarding"] = Relationship(back_populates="summary")
