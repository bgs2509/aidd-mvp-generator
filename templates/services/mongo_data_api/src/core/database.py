"""
Подключение к MongoDB.

Async Motor клиент.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.core.config import settings


class MongoDB:
    """Менеджер подключения к MongoDB."""

    def __init__(self):
        """Инициализация менеджера."""
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """Установить подключение к MongoDB."""
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_database]

        # Проверка подключения
        await self.client.admin.command("ping")

    async def disconnect(self) -> None:
        """Закрыть подключение к MongoDB."""
        if self.client:
            self.client.close()

    def get_collection(self, name: str):
        """
        Получить коллекцию.

        Args:
            name: Название коллекции.

        Returns:
            Коллекция MongoDB.
        """
        return self.db[name]


# Синглтон подключения
mongodb = MongoDB()
