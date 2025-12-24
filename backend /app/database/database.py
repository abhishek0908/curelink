from sqlmodel import SQLModel, Session, create_engine
from app.core.settings import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

