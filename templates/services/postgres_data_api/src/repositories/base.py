"""
Базовый репозиторий.

Generic CRUD операции для всех сущностей.
Реализует Log-Driven Design для операций с БД.
"""

import time
from typing import Any, Generic, Sequence, TypeVar
from uuid import UUID

import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.base import Base
from src.core.config import settings
from shared.utils.log_helpers import log_db_operation, log_slow_query


logger = structlog.get_logger()

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий с CRUD операциями и Log-Driven Design.

    Автоматически логирует все операции с БД:
    - Тип операции (SELECT/INSERT/UPDATE/DELETE)
    - Время выполнения (duration_ms)
    - Количество затронутых записей
    - Медленные запросы (WARNING)
    """

    # Порог медленного запроса в миллисекундах
    SLOW_QUERY_THRESHOLD_MS = 100.0

    def __init__(self, model: type[ModelType], session: AsyncSession):
        """
        Инициализация репозитория.

        Args:
            model: Класс модели SQLAlchemy.
            session: Async сессия БД.
        """
        self.model = model
        self.session = session
        self._table_name = model.__tablename__

    def _check_slow_query(
        self,
        operation: str,
        duration_ms: float,
    ) -> None:
        """
        Проверить и залогировать медленный запрос.

        Args:
            operation: Название операции.
            duration_ms: Время выполнения.
        """
        threshold = getattr(
            settings,
            "slow_query_threshold_ms",
            self.SLOW_QUERY_THRESHOLD_MS,
        )
        if duration_ms > threshold:
            log_slow_query(
                logger,
                operation=operation,
                table=self._table_name,
                duration_ms=duration_ms,
                threshold_ms=threshold,
            )

    async def get_by_id(self, entity_id: UUID) -> ModelType | None:
        """
        Получить сущность по ID.

        Args:
            entity_id: UUID сущности.

        Returns:
            Сущность или None.
        """
        start = time.perf_counter()
        result = await self.session.get(self.model, entity_id)
        duration_ms = (time.perf_counter() - start) * 1000

        log_db_operation(
            logger,
            operation="get_by_id",
            table=self._table_name,
            query_type="SELECT",
            duration_ms=duration_ms,
            found=result is not None,
            entity_id=str(entity_id),
        )
        self._check_slow_query("get_by_id", duration_ms)

        return result

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
        start = time.perf_counter()
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        entities = result.scalars().all()
        duration_ms = (time.perf_counter() - start) * 1000

        log_db_operation(
            logger,
            operation="get_all",
            table=self._table_name,
            query_type="SELECT",
            duration_ms=duration_ms,
            affected_rows=len(entities),
            offset=offset,
            limit=limit,
        )
        self._check_slow_query("get_all", duration_ms)

        return entities

    async def count(self) -> int:
        """
        Подсчитать количество сущностей.

        Returns:
            Количество записей.
        """
        start = time.perf_counter()
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        count_value = result.scalar_one()
        duration_ms = (time.perf_counter() - start) * 1000

        log_db_operation(
            logger,
            operation="count",
            table=self._table_name,
            query_type="SELECT",
            duration_ms=duration_ms,
            count=count_value,
        )
        self._check_slow_query("count", duration_ms)

        return count_value

    async def create(self, data: dict[str, Any]) -> ModelType:
        """
        Создать сущность.

        Args:
            data: Данные для создания.

        Returns:
            Созданная сущность.
        """
        start = time.perf_counter()
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        duration_ms = (time.perf_counter() - start) * 1000

        log_db_operation(
            logger,
            operation="create",
            table=self._table_name,
            query_type="INSERT",
            duration_ms=duration_ms,
            affected_rows=1,
            entity_id=str(entity.id),
        )
        self._check_slow_query("create", duration_ms)

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
        start = time.perf_counter()
        entity = await self.session.get(self.model, entity_id)

        if entity is None:
            duration_ms = (time.perf_counter() - start) * 1000
            log_db_operation(
                logger,
                operation="update",
                table=self._table_name,
                query_type="UPDATE",
                duration_ms=duration_ms,
                found=False,
                entity_id=str(entity_id),
            )
            return None

        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        await self.session.commit()
        await self.session.refresh(entity)
        duration_ms = (time.perf_counter() - start) * 1000

        log_db_operation(
            logger,
            operation="update",
            table=self._table_name,
            query_type="UPDATE",
            duration_ms=duration_ms,
            affected_rows=1,
            found=True,
            entity_id=str(entity_id),
        )
        self._check_slow_query("update", duration_ms)

        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """
        Удалить сущность.

        Args:
            entity_id: UUID сущности.

        Returns:
            True если удалено, False если не найдено.
        """
        start = time.perf_counter()
        entity = await self.session.get(self.model, entity_id)

        if entity is None:
            duration_ms = (time.perf_counter() - start) * 1000
            log_db_operation(
                logger,
                operation="delete",
                table=self._table_name,
                query_type="DELETE",
                duration_ms=duration_ms,
                found=False,
                entity_id=str(entity_id),
            )
            return False

        await self.session.delete(entity)
        await self.session.commit()
        duration_ms = (time.perf_counter() - start) * 1000

        log_db_operation(
            logger,
            operation="delete",
            table=self._table_name,
            query_type="DELETE",
            duration_ms=duration_ms,
            affected_rows=1,
            found=True,
            entity_id=str(entity_id),
        )
        self._check_slow_query("delete", duration_ms)

        return True
