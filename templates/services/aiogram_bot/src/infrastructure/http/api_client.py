"""
Клиент Business API.

HTTP клиент для взаимодействия с Business API.
"""

from typing import Any

import httpx
import structlog

from src.core.config import settings


logger = structlog.get_logger()


class BusinessApiClient:
    """Клиент для Business API."""

    def __init__(self, request_id: str | None = None):
        """
        Инициализация клиента.

        Args:
            request_id: ID запроса для корреляции.
        """
        self.base_url = settings.business_api_url
        self.timeout = settings.business_api_timeout
        self.request_id = request_id

    def _get_headers(self) -> dict[str, str]:
        """
        Получить заголовки запроса.

        Returns:
            Словарь заголовков.
        """
        headers = {"Content-Type": "application/json"}
        if self.request_id:
            headers["X-Request-ID"] = self.request_id
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Выполнить HTTP запрос.

        Args:
            method: HTTP метод.
            path: Путь запроса.
            **kwargs: Дополнительные параметры.

        Returns:
            JSON данные ответа.

        Raises:
            Exception: При ошибке запроса.
        """
        url = f"{self.base_url}{path}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.debug(
                "HTTP запрос",
                method=method,
                url=url,
            )

            response = await client.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                **kwargs,
            )

            if response.status_code >= 400:
                logger.error(
                    "Ошибка HTTP запроса",
                    status_code=response.status_code,
                    url=url,
                )
                response.raise_for_status()

            return response.json()

    async def get(self, path: str, **kwargs) -> dict[str, Any]:
        """GET запрос."""
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, data: dict | None = None, **kwargs) -> dict[str, Any]:
        """POST запрос."""
        return await self._request("POST", path, json=data, **kwargs)

    async def put(self, path: str, data: dict | None = None, **kwargs) -> dict[str, Any]:
        """PUT запрос."""
        return await self._request("PUT", path, json=data, **kwargs)

    async def delete(self, path: str, **kwargs) -> dict[str, Any] | None:
        """DELETE запрос."""
        return await self._request("DELETE", path, **kwargs)

    # === Пример методов для домена ===
    # async def get_user(self, user_id: int) -> dict[str, Any]:
    #     """Получить пользователя по Telegram ID."""
    #     return await self.get(f"/api/v1/users/telegram/{user_id}")
