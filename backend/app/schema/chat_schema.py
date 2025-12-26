from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

class ChatHistoryResponse(BaseModel):
    id: int
    role: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class ChatContextMessage(BaseModel):
    role: str
    content: str 

class WSMessage(BaseModel):
    type: str
    data: Optional[dict] = None

# Specific WS Response Schemas
class WSInfoMessage(BaseModel):
    type: Literal["history"]
    messages: List[ChatContextMessage]

class WSChatMessage(BaseModel):
    type: Literal["message"]
    role: str
    content: str

class WSErrorMessage(BaseModel):
    type: Literal["error"]
    message: str
