# Обработка ошибок HTTP

> **Назначение**: Стратегии обработки ошибок при HTTP взаимодействии.

---

## Исключения

```python
"""Исключения для HTTP клиентов."""


class ExternalServiceError(Exception):
    """Ошибка внешнего сервиса."""

    def __init__(
        self,
        service: str,
        message: str,
        status_code: int | None = None,
    ):
        """
        Инициализация.

        Args:
            service: Имя сервиса.
            message: Сообщение об ошибке.
            status_code: HTTP код ответа.
        """
        self.service = service
        self.message = message
        self.status_code = status_code
        super().__init__(f"{service}: {message}")


class DataApiError(ExternalServiceError):
    """Ошибка Data API."""

    def __init__(self, message: str, status_code: int | None = None):
        """Инициализация."""
        super().__init__("Data API", message, status_code)


class DataApiNotFoundError(DataApiError):
    """Ресурс не найден в Data API."""

    def __init__(self, resource: str, resource_id: str):
        """
        Инициализация.

        Args:
            resource: Тип ресурса.
            resource_id: ID ресурса.
        """
        super().__init__(
            f"{resource} {resource_id} not found",
            status_code=404,
        )
        self.resource = resource
        self.resource_id = resource_id


class DataApiValidationError(DataApiError):
    """Ошибка валидации в Data API."""

    def __init__(self, message: str, errors: list | None = None):
        """
        Инициализация.

        Args:
            message: Сообщение об ошибке.
            errors: Детали ошибок валидации.
        """
        super().__init__(message, status_code=422)
        self.errors = errors or []


class DataApiConflictError(DataApiError):
    """Конфликт данных в Data API."""

    def __init__(self, message: str):
        """Инициализация."""
        super().__init__(message, status_code=409)
```

---

## Маппинг ошибок

```python
"""Маппинг ошибок HTTP в исключения."""

from typing import Any
import httpx


def map_data_api_error(response: httpx.Response) -> DataApiError:
    """
    Преобразовать HTTP ответ в исключение.

    Args:
        response: HTTP ответ с ошибкой.

    Returns:
        Соответствующее исключение.
    """
    status_code = response.status_code

    try:
        body = response.json()
        message = body.get("detail", response.text)
        errors = body.get("errors", [])
    except Exception:
        message = response.text
        errors = []

    if status_code == 404:
        return DataApiNotFoundError("Resource", "unknown")

    if status_code == 409:
        return DataApiConflictError(message)

    if status_code == 422:
        return DataApiValidationError(message, errors)

    return DataApiError(message, status_code)


class DataApiClient:
    """Клиент с маппингом ошибок."""

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        """Запрос с обработкой ошибок."""
        response = await self.client.request(
            method,
            f"{self.base_url}{path}",
            **kwargs,
        )

        if response.status_code >= 400:
            raise map_data_api_error(response)

        if response.status_code == 204:
            return None

        return response.json()
```

---

## Обработка в сервисе

```python
"""Обработка ошибок в Application Service."""

from uuid import UUID

from {context}_api.core.exceptions import NotFoundError, ValidationError
from {context}_api.infrastructure.http.data_api_client import (
    DataApiClient,
    DataApiNotFoundError,
    DataApiConflictError,
)


class UserService:
    """Сервис с обработкой ошибок."""

    def __init__(self, data_client: DataApiClient):
        """Инициализация."""
        self.data_client = data_client

    async def get_user(self, user_id: UUID) -> UserDTO:
        """
        Получить пользователя.

        Args:
            user_id: ID пользователя.

        Returns:
            Данные пользователя.

        Raises:
            NotFoundError: Если пользователь не найден.
        """
        try:
            result = await self.data_client.get_user(user_id)
            return UserDTO.model_validate(result)
        except DataApiNotFoundError:
            # Преобразуем в бизнес-исключение
            raise NotFoundError("User", str(user_id))

    async def create_user(self, dto: CreateUserDTO) -> UserDTO:
        """
        Создать пользователя.

        Args:
            dto: Данные для создания.

        Returns:
            Созданный пользователь.

        Raises:
            ValidationError: Если email занят.
        """
        try:
            result = await self.data_client.create_user(dto.model_dump())
            return UserDTO.model_validate(result)
        except DataApiConflictError as e:
            raise ValidationError(str(e), field="email")
```

---

## Обработчики FastAPI

```python
"""Обработчики исключений для HTTP ошибок."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from {context}_api.infrastructure.http.exceptions import (
    ExternalServiceError,
    DataApiError,
)


def setup_http_error_handlers(app: FastAPI) -> None:
    """Настроить обработчики HTTP ошибок."""

    @app.exception_handler(ExternalServiceError)
    async def external_service_handler(
        request: Request,
        exc: ExternalServiceError,
    ) -> JSONResponse:
        """Обработать ошибку внешнего сервиса."""
        return JSONResponse(
            status_code=502,
            content={
                "detail": f"External service error: {exc.message}",
                "code": "EXTERNAL_SERVICE_ERROR",
                "service": exc.service,
            },
        )

    @app.exception_handler(DataApiError)
    async def data_api_handler(
        request: Request,
        exc: DataApiError,
    ) -> JSONResponse:
        """Обработать ошибку Data API."""
        # Для некоторых ошибок прокидываем статус
        if exc.status_code in (404, 409, 422):
            status_code = exc.status_code
        else:
            status_code = 502

        return JSONResponse(
            status_code=status_code,
            content={
                "detail": exc.message,
                "code": "DATA_API_ERROR",
            },
        )
```

---

## Логирование ошибок

```python
"""Логирование HTTP ошибок."""

import logging
from functools import wraps
from typing import TypeVar, Callable, Awaitable

import httpx

logger = logging.getLogger(__name__)
T = TypeVar("T")


def log_http_errors(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """
    Декоратор для логирования HTTP ошибок.

    Args:
        func: Асинхронная функция.

    Returns:
        Обёрнутая функция.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except httpx.RequestError as e:
            logger.error(
                f"HTTP request error in {func.__name__}: {e}",
                extra={
                    "function": func.__name__,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )
            raise
        except ExternalServiceError as e:
            logger.error(
                f"External service error in {func.__name__}: {e}",
                extra={
                    "function": func.__name__,
                    "service": e.service,
                    "status_code": e.status_code,
                    "error_message": e.message,
                },
            )
            raise

    return wrapper


# Использование
class DataApiClient:
    @log_http_errors
    async def get_user(self, user_id: UUID) -> dict | None:
        """Получить пользователя с логированием."""
        return await self._request("GET", f"/api/v1/users/{user_id}")
```

---

## Таблица обработки ошибок

| HTTP код | Тип ошибки | Действие |
|----------|------------|----------|
| 400 | Bad Request | Вернуть 400 клиенту |
| 401 | Unauthorized | Вернуть 401 клиенту |
| 403 | Forbidden | Вернуть 403 клиенту |
| 404 | Not Found | NotFoundError |
| 409 | Conflict | ConflictError/ValidationError |
| 422 | Validation | ValidationError |
| 500 | Server Error | Вернуть 502 (Bad Gateway) |
| 502 | Bad Gateway | Retry, затем 502 |
| 503 | Unavailable | Retry, затем 503 |
| 504 | Timeout | Retry, затем 504 |

---

## Чек-лист

- [ ] Иерархия исключений определена
- [ ] Маппинг HTTP кодов в исключения
- [ ] Бизнес-исключения отделены от HTTP
- [ ] Обработчики зарегистрированы в FastAPI
- [ ] Логирование ошибок настроено
