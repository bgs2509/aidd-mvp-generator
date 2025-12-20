"""
Клиент Data API.

HTTP клиент для взаимодействия с Data API сервисом.
"""

from typing import Any
from uuid import UUID

import httpx

from src.infrastructure.http.base_client import BaseHttpClient


class DataApiClient(BaseHttpClient):
    """Клиент для Data API."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        request_id: str | None = None,
    ):
        """
        Инициализация клиента.

        Args:
            client: HTTP клиент httpx.
            request_id: ID запроса для корреляции.
        """
        super().__init__(
            client=client,
            service_name="data-api",
            request_id=request_id,
        )

    # === Generic CRUD методы ===

    async def list_entities(
        self,
        entity_type: str,
        page: int = 1,
        page_size: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Получить список сущностей.

        Args:
            entity_type: Тип сущности (users, orders, etc.).
            page: Номер страницы.
            page_size: Размер страницы.
            filters: Фильтры.

        Returns:
            Пагинированный список сущностей.
        """
        params = {
            "page": page,
            "page_size": page_size,
            **(filters or {}),
        }

        return await self.get(
            f"/api/v1/{entity_type}",
            params=params,
        )

    async def get_entity(
        self,
        entity_type: str,
        entity_id: UUID | str,
    ) -> dict[str, Any]:
        """
        Получить сущность по ID.

        Args:
            entity_type: Тип сущности.
            entity_id: ID сущности.

        Returns:
            Данные сущности.
        """
        return await self.get(f"/api/v1/{entity_type}/{entity_id}")

    async def create_entity(
        self,
        entity_type: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Создать сущность.

        Args:
            entity_type: Тип сущности.
            data: Данные для создания.

        Returns:
            Созданная сущность.
        """
        return await self.post(
            f"/api/v1/{entity_type}",
            data=data,
        )

    async def update_entity(
        self,
        entity_type: str,
        entity_id: UUID | str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Обновить сущность.

        Args:
            entity_type: Тип сущности.
            entity_id: ID сущности.
            data: Данные для обновления.

        Returns:
            Обновлённая сущность.
        """
        return await self.put(
            f"/api/v1/{entity_type}/{entity_id}",
            data=data,
        )

    async def delete_entity(
        self,
        entity_type: str,
        entity_id: UUID | str,
    ) -> None:
        """
        Удалить сущность.

        Args:
            entity_type: Тип сущности.
            entity_id: ID сущности.
        """
        await self.delete(f"/api/v1/{entity_type}/{entity_id}")

    # === Пример специфичных методов для домена ===
    # async def get_user(self, user_id: UUID) -> dict[str, Any]:
    #     """Получить пользователя по ID."""
    #     return await self.get_entity("users", user_id)
    #
    # async def create_user(self, data: dict[str, Any]) -> dict[str, Any]:
    #     """Создать пользователя."""
    #     return await self.create_entity("users", data)
