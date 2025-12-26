# app/services/user_service.py
from sqlmodel import Session, select
from app.models.user_model import UserOnboarding
from app.schema.user_schema import (
    OnboardingCreateRequest,
    OnboardingUpdateRequest,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


class UserService:

    def __init__(self, db: Session):
        self.db = db

    def ensure_user_state(self, auth_id):
        onboarding = self.db.exec(
            select(UserOnboarding).where(UserOnboarding.auth_user_id == auth_id)
        ).first()

        if not onboarding:
            logger.info(f"Creating default onboarding state for auth_id: {auth_id}")
            onboarding = UserOnboarding(auth_user_id=auth_id)
            self.db.add(onboarding)
            self.db.flush()   
        else:
            logger.debug(f"Onboarding record found for auth_id: {auth_id}")

        return onboarding

    def get_onboarding(self, auth_user_id):
        return self.ensure_user_state(auth_user_id)

    def create_onboarding(self, auth_id, data: OnboardingCreateRequest):
        onboarding = self.ensure_user_state(auth_id)

        if onboarding.onboarding_completed:
            raise ValueError("Onboarding already completed")

        for key, value in data.model_dump().items():
            setattr(onboarding, key, value)

        onboarding.onboarding_completed = True
        logger.info(f"Onboarding created for user {onboarding.auth_user_id}")
        self.db.add(onboarding)
        self.db.commit()
        self.db.refresh(onboarding)

        return onboarding
    def update_onboarding(self, auth_id, data: OnboardingUpdateRequest):
        onboarding = self.ensure_user_state(auth_id)

        logger.info(f"Updating onboarding for user {auth_id}")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(onboarding, key, value)

        onboarding.onboarding_completed = True

        self.db.add(onboarding)
        self.db.commit()
        self.db.refresh(onboarding)
        logger.info(f"Onboarding updated successfully for user {auth_id}")

        return onboarding
