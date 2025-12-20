"""
Базовый репозиторий.

Generic CRUD операции для всех сущностей.
"""

from typing import Any, Generic, Sequence, TypeVar
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с CRUD операциями."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        """
        Инициализация репозитория.

        Args:
            model: Класс модели SQLAlchemy.
            session: Async сессия БД.
        """
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> ModelType | None:
        """
        Получить сущность по ID.

        Args:
            entity_id: UUID сущности.

        Returns:
            Сущность или None.
        """
        return await self.session.get(self.model, entity_id)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        """
        Получить список сущностей.

        Args:
            offset: Смещение.
            limit: Лимит записей.

        Returns:
            Список сущностей.
        """
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count(self) -> int:
        """
        Подсчитать количество сущностей.

        Returns:
            Количество записей.
        """
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def create(self, data: dict[str, Any]) -> ModelType:
        """
        Создать сущность.

        Args:
            data: Данные для создания.

        Returns:
            Созданная сущность.
        """
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(
        self,
        entity_id: UUID,
        data: dict[str, Any],
    ) -> ModelType | None:
        """
        Обновить сущность.

        Args:
            entity_id: UUID сущности.
            data: Данные для обновления.

        Returns:
            Обновлённая сущность или None.
        """
        entity = await self.get_by_id(entity_id)

        if entity is None:
            return None

        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        await self.session.commit()
        await self.session.refresh(entity)

        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """
        Удалить сущность.

        Args:
            entity_id: UUID сущности.

        Returns:
            True если удалено, False если не найдено.
        """
        entity = await self.get_by_id(entity_id)

        if entity is None:
            return False

        await self.session.delete(entity)
        await self.session.commit()

        return True
