from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.schema.auth_schema import LoginRequest, AuthResponse
from app.schema.response import APIResponse
from app.core.exceptions import AppException
from app.core.dependencies import get_db
from app.services.auth_service.auth_service import AuthService

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
    auth_service = AuthService(db)
    try:
        result = auth_service.login(
            email=body.email,
        )
        return APIResponse.success_response(data=result)
    except AppException as e:
        raise e
    except Exception as e:
        raise AppException(
            code="LOGIN_ERROR",
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
