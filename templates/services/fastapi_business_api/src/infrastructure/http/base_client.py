"""
Базовый HTTP клиент.

Общий функционал для всех HTTP клиентов.
"""

from typing import Any

import httpx
import structlog

from src.core.exceptions import ExternalServiceError


logger = structlog.get_logger()


class BaseHttpClient:
    """Базовый HTTP клиент с обработкой ошибок."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        service_name: str = "external",
        request_id: str | None = None,
    ):
        """
        Инициализация клиента.

        Args:
            client: HTTP клиент httpx.
            service_name: Название сервиса для логов.
            request_id: ID запроса для корреляции.
        """
        self.client = client
        self.service_name = service_name
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

    async def _handle_response(
        self,
        response: httpx.Response,
    ) -> dict[str, Any]:
        """
        Обработать ответ.

        Args:
            response: HTTP ответ.

        Returns:
            JSON данные ответа.

        Raises:
            ExternalServiceError: При ошибке сервиса.
        """
        if response.status_code >= 400:
            logger.error(
                "Ошибка HTTP запроса",
                service=self.service_name,
                status_code=response.status_code,
                url=str(response.url),
            )

            try:
                error_data = response.json()
                message = error_data.get("detail", str(response.text))
            except Exception:
                message = str(response.text)

            raise ExternalServiceError(
                service=self.service_name,
                message=message,
                status_code=response.status_code,
            )

        return response.json()

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        GET запрос.

        Args:
            path: Путь запроса.
            params: Query параметры.

        Returns:
            JSON данные ответа.
        """
        logger.debug(
            "HTTP GET запрос",
            service=self.service_name,
            path=path,
        )

        response = await self.client.get(
            path,
            params=params,
            headers=self._get_headers(),
        )

        return await self._handle_response(response)

    async def post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        POST запрос.

        Args:
            path: Путь запроса.
            data: Данные для отправки.

        Returns:
            JSON данные ответа.
        """
        logger.debug(
            "HTTP POST запрос",
            service=self.service_name,
            path=path,
        )

        response = await self.client.post(
            path,
            json=data,
            headers=self._get_headers(),
        )

        return await self._handle_response(response)

    async def put(
        self,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        PUT запрос.

        Args:
            path: Путь запроса.
            data: Данные для отправки.

        Returns:
            JSON данные ответа.
        """
        logger.debug(
            "HTTP PUT запрос",
            service=self.service_name,
            path=path,
        )

        response = await self.client.put(
            path,
            json=data,
            headers=self._get_headers(),
        )

        return await self._handle_response(response)

    async def delete(
        self,
        path: str,
    ) -> dict[str, Any] | None:
        """
        DELETE запрос.

        Args:
            path: Путь запроса.

        Returns:
            JSON данные ответа или None.
        """
        logger.debug(
            "HTTP DELETE запрос",
            service=self.service_name,
            path=path,
        )

        response = await self.client.delete(
            path,
            headers=self._get_headers(),
        )

        if response.status_code == 204:
            return None

        return await self._handle_response(response)
