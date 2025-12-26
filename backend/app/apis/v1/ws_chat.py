from fastapi import WebSocket, WebSocketDisconnect, APIRouter, HTTPException
from sqlmodel import Session

from app.database.database import engine
from app.core.redis import redis_client
from app.services.redis_service.redis_service import RedisChatService
from app.services.llm_service.llm_service import LLMService
from app.services.chat_service.chat_service import ChatService
from app.core.dependencies import get_current_auth_id
from app.core.security import jwt_handler
from app.schema.chat_schema import WSInfoMessage, WSChatMessage, WSErrorMessage, ChatContextMessage
from app.core.logger import get_logger

logger = get_logger(__name__)


router = APIRouter()


@router.websocket("/ws/chat")
async def ws_chat_endpoint(websocket: WebSocket):
    # 🔐 Single source of truth for auth
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        auth_id = jwt_handler.get_subject(token)
    except HTTPException:
        await websocket.close(code=1008)
        return

    await chat_websocket(websocket, auth_id)


async def chat_websocket(websocket: WebSocket, auth_id: str):
    await websocket.accept()

    with Session(engine) as db:
        chat_service = ChatService(
            db=db,
            redis_service=RedisChatService(redis_client),
            llm_service=LLMService()
        )

        # Optional safety check
        if not chat_service.validate_user(auth_id):
            await websocket.close(code=1008)
            return

        try:
            # FIRST CONNECTION → load summary + last messages into Redis
            chat_service.bootstrap_context(auth_id)
            logger.info(f"User {auth_id} connected, bootstrapping context")
            
            # Send cached messages
            # Convert dicts from redis to pydantic models to ensure validity
            redis_msgs_data = chat_service.redis.get_messages(auth_id)
            # Assuming redis_msgs_data is list of dicts consistent with ChatContextMessage
            
            await websocket.send_json(
                WSInfoMessage(
                    type="history",
                    messages=[ChatContextMessage(**m) for m in redis_msgs_data]
                ).model_dump()
            )

            while True:
                user_text = await websocket.receive_text()

                try:
                    ai_reply = chat_service.handle_message(
                        auth_id=auth_id,
                        user_text=user_text
                    )

                    await websocket.send_json(
                        WSChatMessage(
                            type="message",
                            role="assistant",
                            content=ai_reply
                        ).model_dump()
                    )
                except Exception as e:
                    logger.error(f"Error processing message for {auth_id}: {e}")
                    await websocket.send_json(
                        WSErrorMessage(
                            type="error",
                            message="An error occurred while processing your message."
                        ).model_dump()
                    )

        except WebSocketDisconnect:
            logger.info(f"User {auth_id} disconnected")
        except Exception as e:
            logger.error(f"WebSocket Error for {auth_id}: {e}")
            await websocket.close(code=1011) # Internal Error

