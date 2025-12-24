from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.dependencies import get_db
from app.services.user_service.user_service import UserService
from app.schema.user_schema import (
    OnboardingCreateRequest,
    OnboardingUpdateRequest,
    OnboardingResponse,
    OnboardingStatusResponse,
)
from app.core.dependencies import get_current_user_id  # assume this exists

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.get("/status", response_model=OnboardingStatusResponse)
def onboarding_status(
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    service = UserService(db)
    onboarding = service.get_onboarding(user_id)

    return {
        "onboarding_completed": onboarding.onboarding_completed
    }


@router.get("", response_model=OnboardingResponse)
def get_onboarding(
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    service = UserService(db)
    onboarding = service.get_onboarding(user_id)

    return onboarding


@router.post(
    "",
    response_model=OnboardingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_onboarding(
    payload: OnboardingCreateRequest,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    service = UserService(db)

    try:
        onboarding = service.create_onboarding(user_id, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return onboarding


@router.patch("", response_model=OnboardingResponse)
def update_onboarding(
    payload: OnboardingUpdateRequest,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    service = UserService(db)
    onboarding = service.update_onboarding(user_id, payload)
    return onboarding
