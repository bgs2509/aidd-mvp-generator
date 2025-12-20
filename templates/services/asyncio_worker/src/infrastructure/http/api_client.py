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

    def __init__(self):
        """Инициализация клиента."""
        self.base_url = settings.business_api_url
        self.timeout = settings.business_api_timeout

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
                headers={"Content-Type": "application/json"},
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
