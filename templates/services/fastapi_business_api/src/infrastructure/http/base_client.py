"""
Базовый HTTP клиент.

Общий функционал для всех HTTP клиентов.
Реализует Log-Driven Design для исходящих вызовов.
"""

from typing import Any

import httpx
import structlog

from src.core.exceptions import ExternalServiceError
from shared.utils.request_id import create_tracing_headers
from shared.utils.log_helpers import log_external_call_start, log_external_call_end


logger = structlog.get_logger()


class BaseHttpClient:
    """
    Базовый HTTP клиент с обработкой ошибок и Log-Driven Design.

    Реализует:
    - Автоматическую передачу tracing headers (request_id, correlation_id, causation_id)
    - Логирование начала и завершения вызовов с duration_ms
    - Классификацию ошибок (timeout, connection_error)
    - Флаг is_retryable для ошибок
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        service_name: str = "external",
    ):
        """
        Инициализация клиента.

        Args:
            client: HTTP клиент httpx.
            service_name: Название сервиса для логов.
        """
        self.client = client
        self.service_name = service_name

    def _get_headers(self) -> dict[str, str]:
        """
        Получить заголовки запроса с полной трассировкой.

        Передаёт request_id, correlation_id, causation_id для
        сквозной трассировки между сервисами.

        Returns:
            Словарь заголовков.
        """
        headers = {"Content-Type": "application/json"}
        # Добавляем все tracing headers (Log-Driven Design)
        headers.update(create_tracing_headers())
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
        operation: str | None = None,
    ) -> dict[str, Any]:
        """
        GET запрос.

        Args:
            path: Путь запроса.
            params: Query параметры.
            operation: Название операции для логов.

        Returns:
            JSON данные ответа.
        """
        op_name = operation or f"GET {path}"
        start_time = log_external_call_start(
            logger,
            service=self.service_name,
            operation=op_name,
            method="GET",
            endpoint=path,
        )

        try:
            response = await self.client.get(
                path,
                params=params,
                headers=self._get_headers(),
            )

            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                status_code=response.status_code,
            )

            return await self._handle_response(response)

        except httpx.TimeoutException:
            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                error_type="timeout",
                is_retryable=True,
            )
            raise

        except httpx.ConnectError:
            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                error_type="connection_error",
                is_retryable=True,
            )
            raise

    async def post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        operation: str | None = None,
    ) -> dict[str, Any]:
        """
        POST запрос.

        Args:
            path: Путь запроса.
            data: Данные для отправки.
            operation: Название операции для логов.

        Returns:
            JSON данные ответа.
        """
        op_name = operation or f"POST {path}"
        start_time = log_external_call_start(
            logger,
            service=self.service_name,
            operation=op_name,
            method="POST",
            endpoint=path,
        )

        try:
            response = await self.client.post(
                path,
                json=data,
                headers=self._get_headers(),
            )

            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                status_code=response.status_code,
            )

            return await self._handle_response(response)

        except httpx.TimeoutException:
            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                error_type="timeout",
                is_retryable=True,
            )
            raise

        except httpx.ConnectError:
            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                error_type="connection_error",
                is_retryable=True,
            )
            raise

    async def put(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        operation: str | None = None,
    ) -> dict[str, Any]:
        """
        PUT запрос.

        Args:
            path: Путь запроса.
            data: Данные для отправки.
            operation: Название операции для логов.

        Returns:
            JSON данные ответа.
        """
        op_name = operation or f"PUT {path}"
        start_time = log_external_call_start(
            logger,
            service=self.service_name,
            operation=op_name,
            method="PUT",
            endpoint=path,
        )

        try:
            response = await self.client.put(
                path,
                json=data,
                headers=self._get_headers(),
            )

            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                status_code=response.status_code,
            )

            return await self._handle_response(response)

        except httpx.TimeoutException:
            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                error_type="timeout",
                is_retryable=True,
            )
            raise

        except httpx.ConnectError:
            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                error_type="connection_error",
                is_retryable=True,
            )
            raise

    async def delete(
        self,
        path: str,
        operation: str | None = None,
    ) -> dict[str, Any] | None:
        """
        DELETE запрос.

        Args:
            path: Путь запроса.
            operation: Название операции для логов.

        Returns:
            JSON данные ответа или None.
        """
        op_name = operation or f"DELETE {path}"
        start_time = log_external_call_start(
            logger,
            service=self.service_name,
            operation=op_name,
            method="DELETE",
            endpoint=path,
        )

        try:
            response = await self.client.delete(
                path,
                headers=self._get_headers(),
            )

            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                status_code=response.status_code,
            )

            if response.status_code == 204:
                return None

            return await self._handle_response(response)

        except httpx.TimeoutException:
            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                error_type="timeout",
                is_retryable=True,
            )
            raise

        except httpx.ConnectError:
            log_external_call_end(
                logger,
                service=self.service_name,
                operation=op_name,
                start_time=start_time,
                error_type="connection_error",
                is_retryable=True,
            )
            raise
