from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.dependencies import get_db, get_current_auth_id
from app.models.chat_models import ChatMessage

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/history")
def load_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    auth_id: str = Depends(get_current_auth_id) # Using string as it comes from dependency
):
    from app.models.user_model import UserOnboarding
    
    # 1. Get UserOnboarding id
    user = db.exec(
        select(UserOnboarding).where(UserOnboarding.auth_user_id == auth_id)
    ).first()
    
    if not user:
        return []

    # 2. Get Messages (DESC for pagination)
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.id.desc())
        .offset(offset)
        .limit(limit)
    )
    messages = db.exec(stmt).all()
    
    # Return reversed so client gets [oldest ... newest] if fetching page 0?
    # Actually client usually wants them to prepend. 
    # Let's return them as is (newest first) and let client handle sorting/prepending.
    return messages
