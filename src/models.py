from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None
    temperature: float = Field(0.3, ge=0.0, le=1.0)
    max_tokens: int = Field(300, ge=50, le=4000)

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    tokens_used: Optional[int] = None
    timestamp: str

class ConversationResponse(BaseModel):
    id: str
    created_at: datetime
    message_count: int

class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime
