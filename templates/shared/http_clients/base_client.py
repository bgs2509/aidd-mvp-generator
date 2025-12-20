"""
Базовый HTTP клиент.

Переиспользуемый HTTP клиент на основе httpx.
"""

import asyncio
from typing import Any, TypeVar
from urllib.parse import urljoin

import httpx
import structlog

from ..utils.request_id import (
    REQUEST_ID_HEADER,
    get_or_create_request_id,
)
from ..utils.exceptions import (
    ExternalServiceError,
    ServiceUnavailableError,
    TimeoutError as AppTimeoutError,
    NotFoundError,
)


logger = structlog.get_logger(__name__)

T = TypeVar("T")


class BaseHTTPClient:
    """
    Базовый асинхронный HTTP клиент.

    Особенности:
        - Автоматическая передача request_id.
        - Retry логика с экспоненциальной задержкой.
        - Стандартизированная обработка ошибок.
        - Логирование запросов и ответов.

    Использование:
        ```python
        class MyServiceClient(BaseHTTPClient):
            def __init__(self):
                super().__init__(
                    base_url="http://my-service:8000",
                    service_name="my-service",
                )

            async def get_items(self) -> list[dict]:
                return await self._get("/api/v1/items")
        ```
    """

    def __init__(
        self,
        base_url: str,
        service_name: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Инициализировать клиент.

        Args:
            base_url: Базовый URL сервиса.
            service_name: Название сервиса для логов.
            timeout: Таймаут запросов в секундах.
            max_retries: Максимальное количество повторных попыток.
            retry_delay: Начальная задержка между попытками.
            headers: Дополнительные заголовки.
        """
        self.base_url = base_url.rstrip("/")
        self.service_name = service_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._default_headers = headers or {}
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Получить HTTP клиент (создать если не существует).

        Returns:
            Экземпляр httpx.AsyncClient.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self._default_headers,
            )
        return self._client

    async def close(self) -> None:
        """Закрыть HTTP клиент."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _build_headers(
        self,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """
        Построить заголовки запроса.

        Args:
            extra_headers: Дополнительные заголовки.

        Returns:
            Объединённый словарь заголовков.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            REQUEST_ID_HEADER: get_or_create_request_id(),
        }
        headers.update(self._default_headers)
        if extra_headers:
            headers.update(extra_headers)
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Выполнить HTTP запрос с retry логикой.

        Args:
            method: HTTP метод.
            path: Путь относительно base_url.
            **kwargs: Дополнительные параметры для httpx.

        Returns:
            HTTP ответ.

        Raises:
            ServiceUnavailableError: Сервис недоступен.
            AppTimeoutError: Превышен таймаут.
            ExternalServiceError: Другая ошибка сервиса.
        """
        client = await self._get_client()

        # Добавляем заголовки
        headers = self._build_headers(kwargs.pop("headers", None))

        # Логируем запрос
        log = logger.bind(
            service=self.service_name,
            method=method,
            path=path,
            request_id=headers.get(REQUEST_ID_HEADER),
        )

        last_exception: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                log.debug(
                    "HTTP запрос",
                    attempt=attempt + 1,
                    max_retries=self.max_retries,
                )

                response = await client.request(
                    method=method,
                    url=path,
                    headers=headers,
                    **kwargs,
                )

                log.debug(
                    "HTTP ответ",
                    status_code=response.status_code,
                    elapsed_ms=response.elapsed.total_seconds() * 1000,
                )

                return response

            except httpx.TimeoutException as e:
                last_exception = e
                log.warning(
                    "Таймаут запроса",
                    attempt=attempt + 1,
                    error=str(e),
                )

            except httpx.ConnectError as e:
                last_exception = e
                log.warning(
                    "Ошибка соединения",
                    attempt=attempt + 1,
                    error=str(e),
                )

            except httpx.HTTPError as e:
                last_exception = e
                log.error(
                    "HTTP ошибка",
                    attempt=attempt + 1,
                    error=str(e),
                )

            # Экспоненциальная задержка перед следующей попыткой
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                await asyncio.sleep(delay)

        # Все попытки исчерпаны
        log.error(
            "Все попытки запроса исчерпаны",
            total_attempts=self.max_retries,
        )

        if isinstance(last_exception, httpx.TimeoutException):
            raise AppTimeoutError(
                service=self.service_name,
                timeout_seconds=self.timeout,
            )
        elif isinstance(last_exception, httpx.ConnectError):
            raise ServiceUnavailableError(service=self.service_name)
        else:
            raise ExternalServiceError(
                service=self.service_name,
                original_error=last_exception,
            )

    def _handle_error_response(self, response: httpx.Response) -> None:
        """
        Обработать ошибочный ответ.

        Args:
            response: HTTP ответ с ошибкой.

        Raises:
            NotFoundError: Ресурс не найден (404).
            ExternalServiceError: Другая ошибка.
        """
        if response.status_code == 404:
            raise NotFoundError(
                entity="Resource",
                message=f"Ресурс не найден: {response.url}",
            )

        try:
            error_data = response.json()
            message = error_data.get("error", {}).get(
                "message",
                f"HTTP {response.status_code}",
            )
        except Exception:
            message = f"HTTP {response.status_code}: {response.text[:200]}"

        raise ExternalServiceError(
            service=self.service_name,
            message=message,
            details={
                "status_code": response.status_code,
                "url": str(response.url),
            },
        )

    # === Методы-обёртки ===

    async def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Выполнить GET запрос.

        Args:
            path: Путь.
            params: Query параметры.
            **kwargs: Дополнительные параметры.

        Returns:
            JSON ответ.
        """
        response = await self._request("GET", path, params=params, **kwargs)

        if not response.is_success:
            self._handle_error_response(response)

        return response.json()

    async def _post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Выполнить POST запрос.

        Args:
            path: Путь.
            data: Данные для отправки.
            **kwargs: Дополнительные параметры.

        Returns:
            JSON ответ.
        """
        response = await self._request("POST", path, json=data, **kwargs)

        if not response.is_success:
            self._handle_error_response(response)

        return response.json()

    async def _put(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Выполнить PUT запрос.

        Args:
            path: Путь.
            data: Данные для отправки.
            **kwargs: Дополнительные параметры.

        Returns:
            JSON ответ.
        """
        response = await self._request("PUT", path, json=data, **kwargs)

        if not response.is_success:
            self._handle_error_response(response)

        return response.json()

    async def _patch(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Выполнить PATCH запрос.

        Args:
            path: Путь.
            data: Данные для отправки.
            **kwargs: Дополнительные параметры.

        Returns:
            JSON ответ.
        """
        response = await self._request("PATCH", path, json=data, **kwargs)

        if not response.is_success:
            self._handle_error_response(response)

        return response.json()

    async def _delete(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """
        Выполнить DELETE запрос.

        Args:
            path: Путь.
            **kwargs: Дополнительные параметры.

        Returns:
            JSON ответ или None.
        """
        response = await self._request("DELETE", path, **kwargs)

        if not response.is_success:
            self._handle_error_response(response)

        if response.status_code == 204:
            return None

        return response.json()

    # === Health check ===

    async def health_check(self) -> bool:
        """
        Проверить доступность сервиса.

        Returns:
            True если сервис доступен.
        """
        try:
            response = await self._request("GET", "/health")
            return response.is_success
        except Exception:
            return False
