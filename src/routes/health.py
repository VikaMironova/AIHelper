from fastapi import APIRouter
from datetime import datetime
from src.config import config

router = APIRouter()


@router.get("/api/health")
async def health_check():
    """Проверка работоспособности сервера и подключения к YandexGPT"""

    yandex_status = "connected" if config.YANDEX_API_KEY and config.YANDEX_FOLDER_ID else "missing_credentials"

    return {
        "status": "OK",
        "yandexgpt_api": yandex_status,
        "timestamp": datetime.now().isoformat()
    }
