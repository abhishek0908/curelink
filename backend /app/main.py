from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import get_settings
from app.apis.v1 import auth,user
from app.database.database import engine
from sqlmodel import SQLModel
from sqlmodel import  text
settings = get_settings()

app = FastAPI(
    title="Chat Backend",
    version="1.0.0",
    debug=settings.DEBUG,
)

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
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

@app.on_event("startup")
def startup_db_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✅ Database connected successfully")
    except Exception as e:
        print("❌ Database connection failed")
        raise e