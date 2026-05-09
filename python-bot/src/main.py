from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config import config
from src.infrastructure.database import db
from src.routes import chat, conversations, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: подключение к БД при старте и отключение при остановке"""
    await db.connect()
    print("PostgreSQL connected")
    yield
    await db.disconnect()
    print("PostgreSQL disconnected")

app = FastAPI(
    title="YandexGPT Broker",
    description="API-прослойка для интеграции YandexGPT с Java веб-приложением",
    version="1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(health.router)
