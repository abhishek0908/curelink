from app.core.settings import get_settings
from app.core.jwt_token import JWTHandler

settings = get_settings()

jwt_handler = JWTHandler(
    secret_key="abc",
    algorithm="HS256",
    access_token_expire_minutes=30,
)

