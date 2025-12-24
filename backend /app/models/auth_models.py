from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class AuthUser(SQLModel, table=True):
    __tablename__ = "auth_users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True
    )
    email: str = Field(
        unique=True,
        index=True,
        nullable=False
    )
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.timetz)

