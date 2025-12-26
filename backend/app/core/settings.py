from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str 
    DEBUG: bool 
    CACHE_MESSAGE_EXPIRE: int
    REDIS_HOST: str
    REDIS_PORT: int
    CHAT_CACHE_LIMIT: int 
    MAX_SUMMARY_WORDS: int 
    LONG_TERM_TRIGGER_COUNT: int 
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str
    OPENROUTER_BASE_URL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    model_config = {
        "env_file": ".env.production",
        "extra": "ignore",
    }
    REDIS_DECODE_RESPONSES: bool = True


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
