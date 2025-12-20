# Корреляция логов

> **Назначение**: Отслеживание запросов через сервисы.

---

## Request ID

```python
"""Генерация и передача Request ID."""

import uuid
from fastapi import FastAPI, Request
from structlog.contextvars import bind_contextvars, clear_contextvars


def setup_request_id_middleware(app: FastAPI) -> None:
    """Настроить middleware для Request ID."""

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        """Добавить Request ID к запросу."""
        # Получить или сгенерировать
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        # Сохранить в state
        request.state.request_id = request_id

        # Привязать к логам
        bind_contextvars(request_id=request_id)

        try:
            response = await call_next(request)

            # Добавить в ответ
            response.headers["X-Request-ID"] = request_id

            return response
        finally:
            clear_contextvars()
```

---

## Передача между сервисами

```python
"""Передача Request ID через HTTP."""

import httpx
from fastapi import Request


class DataApiClient:
    """Клиент с передачей Request ID."""

    def __init__(self, client: httpx.AsyncClient, request_id: str | None = None):
        """
        Инициализация клиента.

        Args:
            client: HTTP клиент.
            request_id: ID запроса для корреляции.
        """
        self.client = client
        self.request_id = request_id

    def _get_headers(self) -> dict:
        """Получить заголовки с Request ID."""
        headers = {}
        if self.request_id:
            headers["X-Request-ID"] = self.request_id
        return headers

    async def get(self, path: str, **kwargs) -> dict:
        """GET запрос с Request ID."""
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}
        response = await self.client.get(path, headers=headers, **kwargs)
        return response.json()

    async def post(self, path: str, **kwargs) -> dict:
        """POST запрос с Request ID."""
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}
        response = await self.client.post(path, headers=headers, **kwargs)
        return response.json()


# В dependencies.py
def get_data_client(request: Request) -> DataApiClient:
    """Создать клиент с Request ID."""
    request_id = getattr(request.state, "request_id", None)
    return DataApiClient(
        client=request.app.state.http_client,
        request_id=request_id,
    )
```

---

## Логирование с корреляцией

```python
"""Логирование с корреляцией."""

import structlog
from structlog.contextvars import bind_contextvars

logger = structlog.get_logger()


class UserService:
    """Сервис с корреляцией логов."""

    async def create_user(self, data: CreateUserDTO) -> UserDTO:
        """Создать пользователя."""
        logger.info("Creating user", email=data.email)

        # Вызов Data API (request_id передастся автоматически)
        result = await self.data_client.post(
            "/api/v1/users",
            json=data.model_dump(),
        )

        logger.info("User created", user_id=result["id"])

        return UserDTO.model_validate(result)
```

---

## Data API: приём Request ID

```python
"""Приём Request ID в Data API."""

from fastapi import FastAPI, Request
from structlog.contextvars import bind_contextvars, clear_contextvars
import structlog

logger = structlog.get_logger()


def setup_correlation_middleware(app: FastAPI) -> None:
    """Настроить корреляцию в Data API."""

    @app.middleware("http")
    async def correlation_middleware(request: Request, call_next):
        """Принять и использовать Request ID."""
        # Получить от вызывающего сервиса
        request_id = request.headers.get("X-Request-ID", "no-correlation")

        # Привязать к логам
        bind_contextvars(
            request_id=request_id,
            service="data-api",
        )

        logger.info("Request received", path=request.url.path)

        try:
            response = await call_next(request)

            logger.info(
                "Request completed",
                status_code=response.status_code,
            )

            return response
        finally:
            clear_contextvars()
```

---

## Трассировка в логах

```
# Business API (request_id: abc-123)
{"timestamp": "...", "level": "info", "event": "Request started", "request_id": "abc-123", "service": "business-api", "path": "/api/v1/users"}
{"timestamp": "...", "level": "info", "event": "Creating user", "request_id": "abc-123", "service": "business-api", "email": "test@example.com"}

# Data API (тот же request_id: abc-123)
{"timestamp": "...", "level": "info", "event": "Request received", "request_id": "abc-123", "service": "data-api", "path": "/api/v1/users"}
{"timestamp": "...", "level": "info", "event": "User saved to database", "request_id": "abc-123", "service": "data-api", "user_id": "456"}
{"timestamp": "...", "level": "info", "event": "Request completed", "request_id": "abc-123", "service": "data-api", "status_code": 201}

# Business API (продолжение)
{"timestamp": "...", "level": "info", "event": "User created", "request_id": "abc-123", "service": "business-api", "user_id": "456"}
{"timestamp": "...", "level": "info", "event": "Request completed", "request_id": "abc-123", "service": "business-api", "status_code": 201}
```

---

## Дополнительные поля

```python
"""Дополнительные поля для корреляции."""

from structlog.contextvars import bind_contextvars


async def process_with_context(request: Request):
    """Обработка с полным контекстом."""
    bind_contextvars(
        request_id=request.state.request_id,
        service="business-api",
        method=request.method,
        path=request.url.path,
        user_agent=request.headers.get("User-Agent"),
        client_ip=request.client.host,
    )
```

---

## Telegram Bot: корреляция

```python
"""Корреляция в Telegram боте."""

import uuid
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars
from aiogram import BaseMiddleware
from aiogram.types import Message

logger = structlog.get_logger()


class CorrelationMiddleware(BaseMiddleware):
    """Middleware для корреляции в боте."""

    async def __call__(self, handler, event: Message, data: dict):
        """Добавить корреляцию."""
        request_id = str(uuid.uuid4())

        bind_contextvars(
            request_id=request_id,
            service="telegram-bot",
            telegram_user_id=event.from_user.id,
            chat_id=event.chat.id,
        )

        # Передать request_id в API клиент
        data["request_id"] = request_id

        try:
            logger.info("Message received", text=event.text[:50] if event.text else None)
            return await handler(event, data)
        finally:
            clear_contextvars()
```

---

## Чек-лист

- [ ] Request ID генерируется на входе
- [ ] Request ID передаётся между сервисами
- [ ] Все сервисы логируют request_id
- [ ] Логи можно фильтровать по request_id
- [ ] Дополнительный контекст добавлен
