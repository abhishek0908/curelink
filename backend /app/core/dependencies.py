from fastapi import Depends, HTTPException,status
from sqlmodel import Session
from app.database.database import engine
import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from uuid import UUID

from app.core.security import jwt_handler

security = HTTPBearer()

def get_db():
    with Session(engine) as session:
        yield session

def get_current_auth_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    token = credentials.credentials
    auth_id = jwt_handler.get_subject(token)

    if not auth_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return UUID(auth_id)