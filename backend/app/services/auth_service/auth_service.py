from datetime import datetime
from sqlmodel import Session, select
from fastapi import status
from app.core.exceptions import AppException
from app.core.logger import get_logger

logger = get_logger(__name__)

from app.models.auth_models import AuthUser
from app.core.security import jwt_handler
from app.schema.auth_schema import AuthResponse
from app.services.user_service.user_service import UserService


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def login(self, email: str):
        """
        Atomic login:
        - Create AuthUser + UserOnboarding together
        - Either both succeed or both fail
        """

        try:
            with self.db.begin():  # 🔐 START TRANSACTION

                stmt = select(AuthUser).where(AuthUser.email == email)
                auth_user = self.db.exec(stmt).first()

                if not auth_user:
                    auth_user = AuthUser(
                        email=email,
                        is_verified=False,
                        created_at=datetime.utcnow(),
                    )
                    self.db.add(auth_user)
                    self.db.flush()  

                    profile = self.user_service.ensure_user_state(auth_user.id)

                else:
                    profile = self.user_service.ensure_user_state(auth_user.id)

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise AppException(
                code="LOGIN_FAILED",
                message="Login failed, please try again",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ✅ Safe to generate token AFTER transaction
        access_token = jwt_handler.create_access_token(
            subject=str(auth_user.id)
        )

        return AuthResponse(
            access_token=access_token,
            user_id=str(auth_user.id),
            user_email=auth_user.email,
            is_verified=auth_user.is_verified,
            onboarding_completed=profile.onboarding_completed,
        )
