from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import get_settings
from app.core.logger import setup_logging, get_logger

# Setup logging immediately
setup_logging()
logger = get_logger(__name__)

from app.apis.v1 import auth,user
from app.apis.v1 import ws_chat, chat_history
from app.database.database import engine
from sqlmodel import SQLModel
from sqlmodel import  text
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exception_handlers import http_exception_handler, validation_exception_handler, global_exception_handler, app_exception_handler
from app.core.exceptions import AppException
from app.schema.response import APIResponse
settings = get_settings()

app = FastAPI(
    title="Chat Backend",
    version="1.0.0",
    debug=settings.DEBUG,
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Routers
# ---------------------------
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(ws_chat.router)
app.include_router(chat_history.router)
# ---------------------------
# Startup event
# ---------------------------
@app.on_event("startup")
def on_startup():
    """
    Initialize DB tables (DEV ONLY).
    Use Alembic in production.
    """
    SQLModel.metadata.create_all(engine)


# ---------------------------
# Health check
# ---------------------------
@app.get("/health", tags=["Health"], response_model=APIResponse[dict])
def health_check():
    return APIResponse.success_response(data={"status": "ok"})

@app.on_event("startup")
def startup_db_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("✅ Database connected successfully")
    except Exception as e:
        logger.error("❌ Database connection failed")
        raise e