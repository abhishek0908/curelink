from fastapi import WebSocket, WebSocketDisconnect,APIRouter
from sqlmodel import Session

from app.database.database import engine
from app.core.redis import redis_client
from app.services.redis_service.redis_service import RedisChatService
from app.services.llm_service.llm_service import LLMService
from app.services.chat_service.chat_service import ChatService

router = APIRouter()

@router.websocket("/ws/chat/{user_id}")
async def ws_chat_endpoint(websocket: WebSocket, user_id: int):
    await chat_websocket(websocket, user_id)


async def chat_websocket(websocket: WebSocket, user_id: int):
    await websocket.accept()

    with Session(engine) as db:
        chat_service = ChatService(
            db=db,
            redis_service=RedisChatService(redis_client),
            llm_service=LLMService()
        )

        if not chat_service.validate_user(user_id):
            await websocket.close(code=1008)
            return

        # FIRST CONNECTION
        chat_service.bootstrap_context(user_id)

        # Send cached messages
        await websocket.send_json({
            "type": "history",
            "messages": chat_service.redis.get_messages(user_id)
        })

        try:
            while True:
                user_text = await websocket.receive_text()
                ai_reply = chat_service.handle_message(user_id, user_text)

                await websocket.send_json({
                    "type": "message",
                    "role": "assistant",
                    "content": ai_reply
                })

        except WebSocketDisconnect:
            print(f"user {user_id} disconnected")
