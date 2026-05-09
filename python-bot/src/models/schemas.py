from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: UUID
    temperature: float = Field(0.3, ge=0.0, le=1.0)
    max_tokens: int = Field(300, ge=50, le=4000)

class ChatResponse(BaseModel):
    reply: str
    conversation_id: UUID
    tokens_used: int | None = None
    timestamp: str

class ConversationResponse(BaseModel):
    id: UUID
    created_at: datetime
    message_count: int

class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime
