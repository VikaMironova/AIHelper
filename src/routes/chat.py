from fastapi import APIRouter, HTTPException
from datetime import datetime
from uuid import UUID

from src.infrastructure.database import db
from src.infrastructure.yandexgpt_client import call_yandexgpt
from src.models.schemas import ChatResponse, ChatRequest

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Отправить сообщение AI-помощнику"""

    conv_id = str(request.conversation_id)

    await db.get_or_create_conversation(conv_id)

    history = await db.get_conversation_messages(conv_id)

    messages = [
        {"role": "system",
         "content": "Ты помощник ресторана. Отвечай кратко, по-русски, помогай с выбором блюд и подсчётом калорий."
                    "Обсуждай только тему нашего ресторана и еды. Остальное: извините, я общаюсь в рамках наших блюд."}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": request.message})

    await db.add_message(conv_id, "user", request.message)

    result = await call_yandexgpt(messages, request.temperature, request.max_tokens)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    await db.add_message(conv_id, "assistant", result["content"])

    return ChatResponse(
        reply=result["content"],
        conversation_id=UUID(conv_id),
        tokens_used=result.get("tokens_used"),
        timestamp=datetime.now().isoformat()
    )
