from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)
from sqlalchemy import select, delete
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, List, Dict, Any

from src.config import config
from src.models.db_models import Conversation, Message


class Database:
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.async_session_maker: Optional[async_sessionmaker] = None

    async def connect(self):
        """Создаёт engine и sessionmaker"""

        db_url = config.database_url.replace("postgresql://", "postgresql+asyncpg://")

        self.engine = create_async_engine(
            db_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )

        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def disconnect(self):
        """Закрывает соединения"""
        if self.engine:
            await self.engine.dispose()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекстный менеджер для сессии"""
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    # Методы для работы с Conversation

    async def create_conversation(self, conv_id: str) -> Conversation:
        """Создать новый диалог"""
        async with self.get_session() as session:
            conversation = Conversation(id=conv_id)
            session.add(conversation)
            await session.flush()
            await session.refresh(conversation)
            return conversation

    async def get_conversation_messages(
            self, conv_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Получить историю сообщений диалога"""
        async with self.get_session() as session:
            stmt = select(Message).where(
                Message.conversation_id == conv_id
            ).order_by(Message.timestamp.asc())

            if limit:
                stmt = stmt.limit(limit)

            result = await session.execute(stmt)
            messages = result.scalars().all()

            return [
                {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
                for msg in messages
            ]

    async def add_message(
            self, conv_id: str, role: str, content: str
    ) -> Message:
        """Добавить сообщение в диалог"""
        async with self.get_session() as session:
            message = Message(
                conversation_id=conv_id,
                role=role,
                content=content
            )
            session.add(message)
            await session.flush()
            await session.refresh(message)
            return message

    async def get_or_create_conversation(self, conv_id: str) -> Conversation:
        """Получить диалог или создать новый"""
        async with self.get_session() as session:
            stmt = select(Conversation).where(Conversation.id == conv_id)
            result = await session.execute(stmt)
            conversation = result.scalar_one_or_none()

            if not conversation:
                conversation = Conversation(id=conv_id)
                session.add(conversation)
                await session.flush()
                await session.refresh(conversation)

            return conversation

    async def get_all_conversations(self, limit: int = 50) -> List[Dict]:
        """Список всех диалогов с количеством сообщений"""
        async with self.get_session() as session:
            from sqlalchemy import func

            stmt = select(
                Conversation.id,
                Conversation.created_at,
                func.count(Message.id).label("message_count")
            ).outerjoin(
                Message, Conversation.id == Message.conversation_id
            ).group_by(
                Conversation.id
            ).order_by(
                Conversation.created_at.desc()
            ).limit(limit)

            result = await session.execute(stmt)
            rows = result.all()

            return [
                {
                    "id": row.id,
                    "created_at": row.created_at,
                    "message_count": row.message_count
                }
                for row in rows
            ]

    async def delete_conversation(self, conv_id: str) -> bool:
        """Удалить диалог"""
        async with self.get_session() as session:
            stmt = delete(Conversation).where(Conversation.id == conv_id)
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount > 0


db = Database()
