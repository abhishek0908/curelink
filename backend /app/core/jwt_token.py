from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from fastapi import HTTPException, status


class JWTHandler:
    """
    Handles JWT creation, decoding, and validation
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    # ----------------------------
    # CREATE ACCESS TOKEN
    # ----------------------------
    def create_access_token(self, subject: str) -> str:
        """
        subject = usually user_id
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )

        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    # ----------------------------
    # DECODE TOKEN
    # ----------------------------
    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

    # ----------------------------
    # GET USER ID FROM TOKEN
    # ----------------------------
    def get_subject(self, token: str) -> str:
        payload = self.decode_token(token)
        subject = payload.get("sub")

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return subject

    # ----------------------------
    # OPTIONAL: TOKEN VALIDATION ONLY
    # ----------------------------
    def validate_token(self, token: str) -> bool:
        self.decode_token(token)
        return True
