# app/models/user_model.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
import uuid


class UserOnboarding(SQLModel, table=True):
    __tablename__ = "user_onboarding"

    id: UUID = Field(
    default_factory=uuid.uuid4,
    primary_key=True,
    index=True
)
    auth_user_id: UUID = Field(
        foreign_key="auth_users.id",
        nullable=False,
        unique=True,
        index=True
    )
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

    previous_diseases: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    current_symptoms: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    medications: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    allergies: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))

    additional_notes: Optional[str] = None
    onboarding_completed: bool = Field(default=False)

    # 1 → many
    chat_messages: List["ChatMessage"] = Relationship(back_populates="user")

    # 1 → 1
    summary: Optional["UserSummary"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False}
    )
