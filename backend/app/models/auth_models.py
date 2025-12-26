from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from uuid import UUID


class AuthUser(SQLModel, table=True):
    __tablename__ = "auth_users"
    id: UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    email: str = Field(
        unique=True,
        index=True,
        nullable=False
    )
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

