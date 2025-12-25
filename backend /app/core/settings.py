from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/chat_app"
    DEBUG: bool = False
    CACHE_MESSAGE_LIMIT: int = 3
    CACHE_MESSAGE_EXPIRE: int = 3600
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    chat_context_limit: int = 3
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }
    REDIS_DECODE_RESPONSES: bool = True


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
