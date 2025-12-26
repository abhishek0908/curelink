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
from app.core.dependencies import get_current_auth_id
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.get("/status", response_model=APIResponse[OnboardingStatusResponse])
def onboarding_status(
    db: Session = Depends(get_db),
    auth_id=Depends(get_current_auth_id),
):
    logger.info(f"Checking onboarding status for {auth_id}")
    service = UserService(db)
    try:
        onboarding = service.get_onboarding(auth_id)
        return APIResponse.success_response(data={
            "onboarding_completed": onboarding.onboarding_completed
        })
    except Exception as e:
        logger.error(f"Error checking onboarding status for {auth_id}: {str(e)}")
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
    logger.info(f"Fetching onboarding data for {auth_id}")
    service = UserService(db)
    try:
        onboarding = service.get_onboarding(auth_id)
        return APIResponse.success_response(data=onboarding)
    except Exception as e:
        logger.error(f"Error fetching onboarding for {auth_id}: {str(e)}")
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
    logger.info(f"Creating onboarding for {auth_id}")
    service = UserService(db)

    try:
        onboarding = service.create_onboarding(auth_id, payload)
        logger.info(f"Onboarding successfully created for {auth_id}")
        return APIResponse.success_response(data=onboarding)
    except ValueError as e:
        logger.error(f"Validation error creating onboarding for {auth_id}: {str(e)}")
        raise AppException(
            code="INVALID_VALUE",
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        logger.error(f"Unexpected error creating onboarding for {auth_id}: {str(e)}")
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
    logger.info(f"Updating onboarding for {auth_id}")
    service = UserService(db)
    try:
        onboarding = service.update_onboarding(auth_id, payload)
        logger.info(f"Onboarding successfully updated for {auth_id}")
        return APIResponse.success_response(data=onboarding)
    except Exception as e:
        logger.error(f"Error updating onboarding for {auth_id}: {str(e)}")
        raise AppException(
            code="UPDATE_ONBOARDING_ERROR",
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
