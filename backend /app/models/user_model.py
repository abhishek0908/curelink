# app/models/user_model.py
from sqlmodel import SQLModel, Field
from typing import Optional, List
from uuid import UUID
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class UserOnboarding(SQLModel, table=True):
    __tablename__ = "user_onboarding"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: UUID = Field(index=True, unique=True)

    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

    previous_diseases: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSONB)
    )

    current_symptoms: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSONB)
    )

    medications: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSONB)
    )

    allergies: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSONB)
    )

    additional_notes: Optional[str] = None

    onboarding_completed: bool = Field(default=False)
