from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.schema.auth_schema import LoginRequest, AuthResponse
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
    response_model=AuthResponse,
)
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    return auth_service.login(
        email=body.email,
    )
