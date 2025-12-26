from fastapi import APIRouter, Depends, status
from typing import List
from app.schema.response import APIResponse
from app.schema.chat_schema import ChatHistoryResponse
from app.core.exceptions import AppException
from sqlmodel import Session, select
from app.core.dependencies import get_db, get_current_auth_id
from app.models.chat_models import ChatMessage

from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/history", response_model=APIResponse[List[ChatHistoryResponse]])
def load_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    auth_id: str = Depends(get_current_auth_id) # Using string as it comes from dependency
):
    logger.info(f"Loading chat history for auth_id: {auth_id} (limit: {limit}, offset: {offset})")
    from app.models.user_model import UserOnboarding
    
    try:
        # 1. Get UserOnboarding id
        user = db.exec(
            select(UserOnboarding).where(UserOnboarding.auth_user_id == auth_id)
        ).first()
        
        if not user:
            return APIResponse.success_response(data=[])

        # 2. Get Messages (DESC for pagination)
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user.id)
            .order_by(ChatMessage.id.desc())
            .offset(offset)
            .limit(limit)
        )
        messages = db.exec(stmt).all()
        
        return APIResponse.success_response(data=messages)
    except Exception as e:
        logger.error(f"Failed to load chat history for {auth_id}: {str(e)}")
        raise AppException(
            code="CHAT_HISTORY_ERROR",
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
