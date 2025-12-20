"""
Клиент для Data API.

HTTP клиент для взаимодействия с Data API сервисами.
"""

from typing import Any, TypeVar
from uuid import UUID

import structlog

from .base_client import BaseHTTPClient
from ..utils.pagination import (
    PaginationParams,
    PaginatedResult,
    PaginationMeta,
)


logger = structlog.get_logger(__name__)

T = TypeVar("T")


class DataAPIClient(BaseHTTPClient):
    """
    Клиент для Data API сервиса.

    Предоставляет CRUD операции для работы с сущностями
    через HTTP-only Data API.

    Использование:
        ```python
        # Инициализация
        client = DataAPIClient(
            base_url="http://users-data:8001",
            service_name="users-data",
            entity_name="users",
        )

        # CRUD операции
        user = await client.get_by_id(user_id)
        users = await client.get_list(page=1, page_size=20)
        created = await client.create({"name": "John", "email": "john@example.com"})
        updated = await client.update(user_id, {"name": "John Doe"})
        await client.delete(user_id)
        ```
    """

    def __init__(
        self,
        base_url: str,
        service_name: str,
        entity_name: str,
        api_version: str = "v1",
        **kwargs: Any,
    ) -> None:
        """
        Инициализировать клиент Data API.

        Args:
            base_url: Базовый URL Data API сервиса.
            service_name: Название сервиса для логов.
            entity_name: Название сущности (например, "users").
            api_version: Версия API (по умолчанию "v1").
            **kwargs: Дополнительные параметры для BaseHTTPClient.
        """
        super().__init__(base_url, service_name, **kwargs)
        self.entity_name = entity_name
        self.api_version = api_version
        self._base_path = f"/api/{api_version}/{entity_name}"

    # === CRUD операции ===

    async def get_by_id(self, entity_id: UUID | str) -> dict[str, Any]:
        """
        Получить сущность по ID.

        Args:
            entity_id: Идентификатор сущности.

        Returns:
            Данные сущности.

        Raises:
            NotFoundError: Сущность не найдена.
        """
        return await self._get(f"{self._base_path}/{entity_id}")

    async def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> PaginatedResult[dict[str, Any]]:
        """
        Получить список сущностей с пагинацией.

        Args:
            page: Номер страницы (начиная с 1).
            page_size: Размер страницы.
            filters: Фильтры (передаются как query параметры).
            sort_by: Поле для сортировки.
            sort_order: Порядок сортировки ("asc" или "desc").

        Returns:
            Пагинированный результат.
        """
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }

        if filters:
            params.update(filters)

        if sort_by:
            params["sort_by"] = sort_by
            params["sort_order"] = sort_order

        response = await self._get(self._base_path, params=params)

        # Парсим пагинированный ответ
        items = response.get("items", [])
        pagination = response.get("pagination", {})

        meta = PaginationMeta(
            page=pagination.get("page", page),
            page_size=pagination.get("page_size", page_size),
            total_items=pagination.get("total_items", len(items)),
            total_pages=pagination.get("total_pages", 1),
            has_next=pagination.get("has_next", False),
            has_prev=pagination.get("has_prev", False),
        )

        return PaginatedResult(items=items, meta=meta)

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Создать новую сущность.

        Args:
            data: Данные для создания.

        Returns:
            Созданная сущность.
        """
        return await self._post(self._base_path, data=data)

    async def update(
        self,
        entity_id: UUID | str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Обновить сущность.

        Args:
            entity_id: Идентификатор сущности.
            data: Данные для обновления.

        Returns:
            Обновлённая сущность.

        Raises:
            NotFoundError: Сущность не найдена.
        """
        return await self._put(f"{self._base_path}/{entity_id}", data=data)

    async def partial_update(
        self,
        entity_id: UUID | str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Частично обновить сущность.

        Args:
            entity_id: Идентификатор сущности.
            data: Данные для обновления (только изменяемые поля).

        Returns:
            Обновлённая сущность.

        Raises:
            NotFoundError: Сущность не найдена.
        """
        return await self._patch(f"{self._base_path}/{entity_id}", data=data)

    async def delete(self, entity_id: UUID | str) -> None:
        """
        Удалить сущность.

        Args:
            entity_id: Идентификатор сущности.

        Raises:
            NotFoundError: Сущность не найдена.
        """
        await self._delete(f"{self._base_path}/{entity_id}")

    # === Дополнительные операции ===

    async def exists(self, entity_id: UUID | str) -> bool:
        """
        Проверить существование сущности.

        Args:
            entity_id: Идентификатор сущности.

        Returns:
            True если существует.
        """
        try:
            await self.get_by_id(entity_id)
            return True
        except Exception:
            return False

    async def get_by_ids(
        self,
        entity_ids: list[UUID | str],
    ) -> list[dict[str, Any]]:
        """
        Получить несколько сущностей по ID.

        Args:
            entity_ids: Список идентификаторов.

        Returns:
            Список найденных сущностей.
        """
        return await self._post(
            f"{self._base_path}/batch",
            data={"ids": [str(id) for id in entity_ids]},
        )

    async def count(
        self,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """
        Получить количество сущностей.

        Args:
            filters: Фильтры.

        Returns:
            Количество сущностей.
        """
        params = filters or {}
        response = await self._get(f"{self._base_path}/count", params=params)
        return response.get("count", 0)

    async def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        fields: list[str] | None = None,
    ) -> PaginatedResult[dict[str, Any]]:
        """
        Поиск сущностей.

        Args:
            query: Поисковый запрос.
            page: Номер страницы.
            page_size: Размер страницы.
            fields: Поля для поиска.

        Returns:
            Пагинированный результат поиска.
        """
        params: dict[str, Any] = {
            "q": query,
            "page": page,
            "page_size": page_size,
        }

        if fields:
            params["fields"] = ",".join(fields)

        response = await self._get(f"{self._base_path}/search", params=params)

        items = response.get("items", [])
        pagination = response.get("pagination", {})

        meta = PaginationMeta(
            page=pagination.get("page", page),
            page_size=pagination.get("page_size", page_size),
            total_items=pagination.get("total_items", len(items)),
            total_pages=pagination.get("total_pages", 1),
            has_next=pagination.get("has_next", False),
            has_prev=pagination.get("has_prev", False),
        )

        return PaginatedResult(items=items, meta=meta)

    # === Специфичные методы для связанных сущностей ===

    async def get_related(
        self,
        entity_id: UUID | str,
        relation_name: str,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[dict[str, Any]]:
        """
        Получить связанные сущности.

        Args:
            entity_id: ID основной сущности.
            relation_name: Название связи (например, "orders").
            page: Номер страницы.
            page_size: Размер страницы.

        Returns:
            Пагинированный список связанных сущностей.
        """
        params = {"page": page, "page_size": page_size}

        response = await self._get(
            f"{self._base_path}/{entity_id}/{relation_name}",
            params=params,
        )

        items = response.get("items", [])
        pagination = response.get("pagination", {})

        meta = PaginationMeta(
            page=pagination.get("page", page),
            page_size=pagination.get("page_size", page_size),
            total_items=pagination.get("total_items", len(items)),
            total_pages=pagination.get("total_pages", 1),
            has_next=pagination.get("has_next", False),
            has_prev=pagination.get("has_prev", False),
        )

        return PaginatedResult(items=items, meta=meta)
