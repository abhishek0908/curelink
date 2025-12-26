from fastapi import WebSocket, WebSocketDisconnect, APIRouter, HTTPException
from sqlmodel import Session

from app.database.database import engine
from app.core.redis import redis_client
from app.services.redis_service.redis_service import RedisChatService
from app.services.llm_service.llm_service import LLMService
from app.services.chat_service.chat_service import ChatService
from app.core.dependencies import get_current_auth_id
from app.core.security import jwt_handler
from app.schema.chat_schema import WSChatMessage, WSErrorMessage
from app.core.logger import get_logger

logger = get_logger(__name__)


router = APIRouter()


@router.websocket("/ws/chat")
async def ws_chat_endpoint(websocket: WebSocket):
    # 🔐 Extract token safely
    token = websocket.query_params.get("token")
    
    # Check Sec-WebSocket-Protocol header for token (prevents log leakage)
    if not token:
        protocols = websocket.headers.get("sec-websocket-protocol")
        if protocols:
            # Browser sends "token, <jwt>" or just "<jwt>"
            # We take the last part if comma separated
            token = protocols.split(",")[-1].strip()

    if not token:
        await websocket.close(code=1008)
        return

    try:
        auth_id = jwt_handler.get_subject(token)
    except HTTPException:
        await websocket.close(code=1008)
        return

    # If we got the token from the subprotocol, we must echo it back during accept
    subprotocol = None
    if websocket.headers.get("sec-websocket-protocol"):
        subprotocol = websocket.headers.get("sec-websocket-protocol").split(",")[-1].strip()

    await chat_websocket(websocket, auth_id, subprotocol)


async def chat_websocket(websocket: WebSocket, auth_id: str, subprotocol: str = None):
    await websocket.accept(subprotocol=subprotocol)

    # Instantiate services that don't depend on the DB session
    redis_service = RedisChatService()
    llm_service = LLMService()

    try:
        # 1. BOOTSTRAP: Open a temporary session to validate user and load context
        with Session(engine) as db:
            chat_service = ChatService(
                db=db,
                redis_service=redis_service,
                llm_service=llm_service
            )

            if not chat_service.validate_user(auth_id):
                await websocket.close(code=1008)
                return

            # FIRST CONNECTION → load summary + last messages into Redis (for AI context)
            await chat_service.bootstrap_context(auth_id)
            logger.info(f"User {auth_id} connected, bootstrapping context complete")
            
        # 2. MESSAGE LOOP: Wait for messages and open a fresh session for each
        while True:
            user_text = await websocket.receive_text()

            # Open a fresh session for THIS specific message exchange
            with Session(engine) as db:
                chat_service = ChatService(
                    db=db,
                    redis_service=redis_service,
                    llm_service=llm_service
                )

                try:
                    ai_reply = await chat_service.handle_message(
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
        if not websocket.client_state.name == "DISCONNECTED":
            await websocket.close(code=1011)
