# app/models/chat_model.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from app.models.user_model import UserOnboarding
from app.utility.role_enum import ChatRole


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(
        foreign_key="user_onboarding.id",
        index=True
    )

    role: ChatRole = Field(
        nullable=False,
        description="sender of the message: user or assistant"
    )

    message: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[UserOnboarding] = Relationship(
        back_populates="chat_messages"
    )


class UserSummary(SQLModel, table=True):
    __tablename__ = "user_summary"
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True
    )
    user_id: int = Field(foreign_key="user_onboarding.id", index=True)
    short_summary: str
    long_summary: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[UserOnboarding] = Relationship(back_populates="user_summary")