"""
Базовый репозиторий MongoDB.

Generic CRUD операции для всех коллекций.
"""

from typing import Any, Generic, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from src.domain.models.base import MongoModel


ModelType = TypeVar("ModelType", bound=MongoModel)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с CRUD операциями."""

    def __init__(
        self,
        collection: AsyncIOMotorCollection,
        model: type[ModelType],
    ):
        """
        Инициализация репозитория.

        Args:
            collection: Коллекция MongoDB.
            model: Класс модели.
        """
        self.collection = collection
        self.model = model

    async def get_by_id(self, entity_id: str) -> ModelType | None:
        """
        Получить документ по ID.

        Args:
            entity_id: ID документа.

        Returns:
            Модель или None.
        """
        doc = await self.collection.find_one({"_id": ObjectId(entity_id)})
        if doc is None:
            return None
        return self.model.from_mongo(doc)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
        filter_query: dict | None = None,
    ) -> list[ModelType]:
        """
        Получить список документов.

        Args:
            offset: Смещение.
            limit: Лимит записей.
            filter_query: Фильтр.

        Returns:
            Список моделей.
        """
        cursor = self.collection.find(filter_query or {})
        cursor = cursor.skip(offset).limit(limit)

        docs = await cursor.to_list(length=limit)
        return [self.model.from_mongo(doc) for doc in docs]

    async def count(self, filter_query: dict | None = None) -> int:
        """
        Подсчитать количество документов.

        Args:
            filter_query: Фильтр.

        Returns:
            Количество записей.
        """
        return await self.collection.count_documents(filter_query or {})

    async def create(self, data: dict[str, Any]) -> ModelType:
        """
        Создать документ.

        Args:
            data: Данные для создания.

        Returns:
            Созданная модель.
        """
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self.model.from_mongo(doc)

    async def update(
        self,
        entity_id: str,
        data: dict[str, Any],
    ) -> ModelType | None:
        """
        Обновить документ.

        Args:
            entity_id: ID документа.
            data: Данные для обновления.

        Returns:
            Обновлённая модель или None.
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(entity_id)},
            {"$set": data},
        )

        if result.matched_count == 0:
            return None

        return await self.get_by_id(entity_id)

    async def delete(self, entity_id: str) -> bool:
        """
        Удалить документ.

        Args:
            entity_id: ID документа.

        Returns:
            True если удалено, False если не найдено.
        """
        result = await self.collection.delete_one({"_id": ObjectId(entity_id)})
        return result.deleted_count > 0
