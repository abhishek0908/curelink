# app/core/redis.py
import redis
from app.core.settings import get_settings
settings = get_settings()
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=settings.REDIS_DECODE_RESPONSES
)
