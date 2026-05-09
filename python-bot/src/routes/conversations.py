from fastapi import APIRouter, HTTPException
from uuid import UUID
from src.infrastructure.database import db

router = APIRouter()


@router.get("/api/conversations")
async def get_conversations(limit: int = 50):
    """Список всех диалогов"""
    conversations = await db.get_all_conversations(limit)
    return conversations


@router.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: UUID):
    """История диалога"""
    messages = await db.get_conversation_messages(str(conversation_id))

    if not messages:
        raise HTTPException(404, "Диалог не найден")

    return {
        "conversation_id": str(conversation_id),
        "messages": messages
    }


@router.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: UUID):
    """Удалить диалог"""
    deleted = await db.delete_conversation(str(conversation_id))

    if not deleted:
        raise HTTPException(404, "Диалог не найден")

    return {"ok": True, "conversation_id": str(conversation_id)}
