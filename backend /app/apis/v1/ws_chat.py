from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from sqlmodel import Session

from app.database.database import engine
from app.core.redis import redis_client
from app.services.redis_service.redis_service import RedisChatService
from app.services.llm_service.llm_service import LLMService
from app.services.chat_service.chat_service import ChatService
from app.core.dependencies import get_current_auth_id
from app.core.security import jwt_handler
from fastapi import HTTPException, BackgroundTasks


router = APIRouter()


@router.websocket("/ws/chat")
async def ws_chat_endpoint(websocket: WebSocket, background_tasks: BackgroundTasks):
    # 🔐 Single source of truth for auth
    token = websocket.query_params.get("token")
    print("token fronm user",token)
    if not token:
        await websocket.close(code=1008)
        return

    try:
        auth_id = jwt_handler.get_subject(token)
    except HTTPException:
        await websocket.close(code=1008)
        return

    await chat_websocket(websocket, auth_id, background_tasks)


async def chat_websocket(websocket: WebSocket, auth_id: str, background_tasks: BackgroundTasks):
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

        # FIRST CONNECTION → load summary + last messages into Redis
        chat_service.bootstrap_context(auth_id)
        print("it is running or not ")
        # Send cached messages
        await websocket.send_json({
            "type": "history",
            "messages": chat_service.redis.get_messages(auth_id)
        })

        try:
            while True:
                user_text = await websocket.receive_text()

                ai_reply = chat_service.handle_message(
                    auth_id=auth_id,
                    user_text=user_text,
                    background_tasks=background_tasks
                )

                await websocket.send_json({
                    "type": "message",
                    "role": "assistant",
                    "content": ai_reply
                })

        except WebSocketDisconnect:
            print(f"user {auth_id} disconnected")
