# Log Correlation

> **Purpose**: Tracking requests across services.

---

## Request ID

```python
"""Request ID generation and propagation."""

import uuid
from fastapi import FastAPI, Request
from structlog.contextvars import bind_contextvars, clear_contextvars


def setup_request_id_middleware(app: FastAPI) -> None:
    """Set up Request ID middleware."""

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        """Add Request ID to request."""
        # Get or generate
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        # Save in state
        request.state.request_id = request_id

        # Bind to logs
        bind_contextvars(request_id=request_id)

        try:
            response = await call_next(request)

            # Add to response
            response.headers["X-Request-ID"] = request_id

            return response
        finally:
            clear_contextvars()
```

---

## Propagation Between Services

```python
"""Request ID propagation via HTTP."""

import httpx
from fastapi import Request


class DataApiClient:
    """Client with Request ID propagation."""

    def __init__(self, client: httpx.AsyncClient, request_id: str | None = None):
        """
        Initialize client.

        Args:
            client: HTTP client.
            request_id: Request ID for correlation.
        """
        self.client = client
        self.request_id = request_id

    def _get_headers(self) -> dict:
        """Get headers with Request ID."""
        headers = {}
        if self.request_id:
            headers["X-Request-ID"] = self.request_id
        return headers

    async def get(self, path: str, **kwargs) -> dict:
        """GET request with Request ID."""
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}
        response = await self.client.get(path, headers=headers, **kwargs)
        return response.json()

    async def post(self, path: str, **kwargs) -> dict:
        """POST request with Request ID."""
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}
        response = await self.client.post(path, headers=headers, **kwargs)
        return response.json()


# In dependencies.py
def get_data_client(request: Request) -> DataApiClient:
    """Create client with Request ID."""
    request_id = getattr(request.state, "request_id", None)
    return DataApiClient(
        client=request.app.state.http_client,
        request_id=request_id,
    )
```

---

## Logging with Correlation

```python
"""Logging with correlation."""

import structlog
from structlog.contextvars import bind_contextvars

logger = structlog.get_logger()


class UserService:
    """Service with log correlation."""

    async def create_user(self, data: CreateUserDTO) -> UserDTO:
        """Create a user."""
        logger.info("Creating user", email=data.email)

        # Data API call (request_id propagated automatically)
        result = await self.data_client.post(
            "/api/v1/users",
            json=data.model_dump(),
        )

        logger.info("User created", user_id=result["id"])

        return UserDTO.model_validate(result)
```

---

## Data API: Receiving Request ID

```python
"""Receiving Request ID in Data API."""

from fastapi import FastAPI, Request
from structlog.contextvars import bind_contextvars, clear_contextvars
import structlog

logger = structlog.get_logger()


def setup_correlation_middleware(app: FastAPI) -> None:
    """Set up correlation in Data API."""

    @app.middleware("http")
    async def correlation_middleware(request: Request, call_next):
        """Receive and use Request ID."""
        # Get from calling service
        request_id = request.headers.get("X-Request-ID", "no-correlation")

        # Bind to logs
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

## Tracing in Logs

```
# Business API (request_id: abc-123)
{"timestamp": "...", "level": "info", "event": "Request started", "request_id": "abc-123", "service": "business-api", "path": "/api/v1/users"}
{"timestamp": "...", "level": "info", "event": "Creating user", "request_id": "abc-123", "service": "business-api", "email": "test@example.com"}

# Data API (same request_id: abc-123)
{"timestamp": "...", "level": "info", "event": "Request received", "request_id": "abc-123", "service": "data-api", "path": "/api/v1/users"}
{"timestamp": "...", "level": "info", "event": "User saved to database", "request_id": "abc-123", "service": "data-api", "user_id": "456"}
{"timestamp": "...", "level": "info", "event": "Request completed", "request_id": "abc-123", "service": "data-api", "status_code": 201}

# Business API (continued)
{"timestamp": "...", "level": "info", "event": "User created", "request_id": "abc-123", "service": "business-api", "user_id": "456"}
{"timestamp": "...", "level": "info", "event": "Request completed", "request_id": "abc-123", "service": "business-api", "status_code": 201}
```

---

## Additional Fields

```python
"""Additional fields for correlation."""

from structlog.contextvars import bind_contextvars


async def process_with_context(request: Request):
    """Processing with full context."""
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

## Telegram Bot: Correlation

```python
"""Correlation in Telegram bot."""

import uuid
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars
from aiogram import BaseMiddleware
from aiogram.types import Message

logger = structlog.get_logger()


class CorrelationMiddleware(BaseMiddleware):
    """Bot correlation middleware."""

    async def __call__(self, handler, event: Message, data: dict):
        """Add correlation."""
        request_id = str(uuid.uuid4())

        bind_contextvars(
            request_id=request_id,
            service="telegram-bot",
            telegram_user_id=event.from_user.id,
            chat_id=event.chat.id,
        )

        # Pass request_id to API client
        data["request_id"] = request_id

        try:
            logger.info("Message received", text=event.text[:50] if event.text else None)
            return await handler(event, data)
        finally:
            clear_contextvars()
```

---

## Checklist

- [ ] Request ID generated on entry
- [ ] Request ID propagated between services
- [ ] All services log request_id
- [ ] Logs can be filtered by request_id
- [ ] Additional context added
