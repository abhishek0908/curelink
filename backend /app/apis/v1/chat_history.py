from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.db.session import get_db
from app.models.chat_model import ChatMessage

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/{user_id}/history")
def load_history(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at)
        .offset(offset)
        .limit(limit)
    )
    return db.exec(stmt).all()
