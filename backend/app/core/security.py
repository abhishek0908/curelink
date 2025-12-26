from app.core.settings import get_settings
from app.core.jwt_token import JWTHandler

settings = get_settings()

jwt_handler = JWTHandler(
    secret_key=settings.SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM,
    access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
)
