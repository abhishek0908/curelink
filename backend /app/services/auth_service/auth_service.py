from datetime import datetime
from sqlmodel import Session, select
from fastapi import HTTPException, status

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
                user = self.db.exec(stmt).first()

                if not user:
                    user = AuthUser(
                        email=email,
                        is_verified=False,
                        created_at=datetime.utcnow(),
                    )
                    self.db.add(user)
                    self.db.flush()  
                    # 👆 flush assigns user.id WITHOUT committing

                    # Create onboarding/profile in SAME transaction
                    profile = self.user_service.ensure_user_state(user.id)

                else:
                    profile = self.user_service.ensure_user_state(user.id)

            # 🔓 COMMIT happens automatically here if no error

        except Exception as e:
            # ❌ Any error → full rollback
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed, please try again",
            )

        # ✅ Safe to generate token AFTER transaction
        access_token = jwt_handler.create_access_token(
            subject=str(user.id)
        )

        return AuthResponse(
            access_token=access_token,
            user_id=str(user.id),
            user_email=user.email,
            is_verified=user.is_verified,
            onboarding_completed=profile.onboarding_completed,
        )
