from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.schema.auth_schema import LoginRequest, AuthResponse
from app.schema.response import APIResponse
from app.core.exceptions import AppException
from app.core.dependencies import get_db
from app.services.auth_service.auth_service import AuthService

from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Request login via email",
    response_model=APIResponse[AuthResponse],
)
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
):
    logger.info(f"Login request received for email: {body.email}")
    auth_service = AuthService(db)
    try:
        result = auth_service.login(
            email=body.email,
        )
        logger.info(f"Login successful for email: {body.email}")
        return APIResponse.success_response(data=result)
    except AppException as e:
        logger.error(f"Login application error for {body.email}: {e.message}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected login error for {body.email}: {str(e)}")
        raise AppException(
            code="LOGIN_ERROR",
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
