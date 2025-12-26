from fastapi import APIRouter, Depends, status
from app.core.exceptions import AppException
from app.schema.response import APIResponse
from sqlmodel import Session

from app.core.dependencies import get_db
from app.services.user_service.user_service import UserService
from app.schema.user_schema import (
    OnboardingCreateRequest,
    OnboardingUpdateRequest,
    OnboardingResponse,
    OnboardingStatusResponse,
)
from app.core.dependencies import get_current_auth_id  # assume this exists

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.get("/status", response_model=APIResponse[OnboardingStatusResponse])
def onboarding_status(
    db: Session = Depends(get_db),
    auth_id=Depends(get_current_auth_id),
):
    service = UserService(db)
    try:
        onboarding = service.get_onboarding(auth_id)
        return APIResponse.success_response(data={
            "onboarding_completed": onboarding.onboarding_completed
        })
    except Exception as e:
        raise AppException(
            code="ONBOARDING_STATUS_ERROR",
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("", response_model=APIResponse[OnboardingResponse])
def get_onboarding(
    db: Session = Depends(get_db),
    auth_id=Depends(get_current_auth_id),
):
    service = UserService(db)
    try:
        onboarding = service.get_onboarding(auth_id)
        return APIResponse.success_response(data=onboarding)
    except Exception as e:
        raise AppException(
            code="GET_ONBOARDING_ERROR",
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post(
    "",
    response_model=APIResponse[OnboardingResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_onboarding(
    payload: OnboardingCreateRequest,
    db: Session = Depends(get_db),
    auth_id=Depends(get_current_auth_id),
):
    service = UserService(db)

    try:
        onboarding = service.create_onboarding(auth_id, payload)
        return APIResponse.success_response(data=onboarding)
    except ValueError as e:
        raise AppException(
            code="INVALID_VALUE",
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        raise AppException(
            code="CREATE_ONBOARDING_ERROR",
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.patch("", response_model=APIResponse[OnboardingResponse])
def update_onboarding(
    payload: OnboardingUpdateRequest,
    db: Session = Depends(get_db),
    auth_id=Depends(get_current_auth_id),
):
    service = UserService(db)
    try:
        onboarding = service.update_onboarding(auth_id, payload)
        return APIResponse.success_response(data=onboarding)
    except Exception as e:
        raise AppException(
            code="UPDATE_ONBOARDING_ERROR",
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
