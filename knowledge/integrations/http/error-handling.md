# HTTP Error Handling

> **Purpose**: Error handling strategies for HTTP interactions.

---

## Exceptions

```python
"""Exceptions for HTTP clients."""


class ExternalServiceError(Exception):
    """External service error."""

    def __init__(
        self,
        service: str,
        message: str,
        status_code: int | None = None,
    ):
        """
        Initialize.

        Args:
            service: Service name.
            message: Error message.
            status_code: HTTP response code.
        """
        self.service = service
        self.message = message
        self.status_code = status_code
        super().__init__(f"{service}: {message}")


class DataApiError(ExternalServiceError):
    """Data API error."""

    def __init__(self, message: str, status_code: int | None = None):
        """Initialize."""
        super().__init__("Data API", message, status_code)


class DataApiNotFoundError(DataApiError):
    """Resource not found in Data API."""

    def __init__(self, resource: str, resource_id: str):
        """
        Initialize.

        Args:
            resource: Resource type.
            resource_id: Resource ID.
        """
        super().__init__(
            f"{resource} {resource_id} not found",
            status_code=404,
        )
        self.resource = resource
        self.resource_id = resource_id


class DataApiValidationError(DataApiError):
    """Validation error in Data API."""

    def __init__(self, message: str, errors: list | None = None):
        """
        Initialize.

        Args:
            message: Error message.
            errors: Validation error details.
        """
        super().__init__(message, status_code=422)
        self.errors = errors or []


class DataApiConflictError(DataApiError):
    """Data conflict in Data API."""

    def __init__(self, message: str):
        """Initialize."""
        super().__init__(message, status_code=409)
```

---

## Error Mapping

```python
"""HTTP error to exception mapping."""

from typing import Any
import httpx


def map_data_api_error(response: httpx.Response) -> DataApiError:
    """
    Convert HTTP response to exception.

    Args:
        response: HTTP error response.

    Returns:
        Corresponding exception.
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
    """Client with error mapping."""

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        """Request with error handling."""
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

## Service-level Handling

```python
"""Error handling in Application Service."""

from uuid import UUID

from {context}_api.core.exceptions import NotFoundError, ValidationError
from {context}_api.infrastructure.http.data_api_client import (
    DataApiClient,
    DataApiNotFoundError,
    DataApiConflictError,
)


class UserService:
    """Service with error handling."""

    def __init__(self, data_client: DataApiClient):
        """Initialize."""
        self.data_client = data_client

    async def get_user(self, user_id: UUID) -> UserDTO:
        """
        Get a user.

        Args:
            user_id: User ID.

        Returns:
            User data.

        Raises:
            NotFoundError: If user not found.
        """
        try:
            result = await self.data_client.get_user(user_id)
            return UserDTO.model_validate(result)
        except DataApiNotFoundError:
            # Convert to business exception
            raise NotFoundError("User", str(user_id))

    async def create_user(self, dto: CreateUserDTO) -> UserDTO:
        """
        Create a user.

        Args:
            dto: Creation data.

        Returns:
            Created user.

        Raises:
            ValidationError: If email is taken.
        """
        try:
            result = await self.data_client.create_user(dto.model_dump())
            return UserDTO.model_validate(result)
        except DataApiConflictError as e:
            raise ValidationError(str(e), field="email")
```

---

## FastAPI Handlers

```python
"""Exception handlers for HTTP errors."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from {context}_api.infrastructure.http.exceptions import (
    ExternalServiceError,
    DataApiError,
)


def setup_http_error_handlers(app: FastAPI) -> None:
    """Set up HTTP error handlers."""

    @app.exception_handler(ExternalServiceError)
    async def external_service_handler(
        request: Request,
        exc: ExternalServiceError,
    ) -> JSONResponse:
        """Handle external service error."""
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
        """Handle Data API error."""
        # Forward status for certain errors
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

## Error Logging

```python
"""HTTP error logging."""

import logging
from functools import wraps
from typing import TypeVar, Callable, Awaitable

import httpx

logger = logging.getLogger(__name__)
T = TypeVar("T")


def log_http_errors(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """
    Decorator for logging HTTP errors.

    Args:
        func: Async function.

    Returns:
        Wrapped function.
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


# Usage
class DataApiClient:
    @log_http_errors
    async def get_user(self, user_id: UUID) -> dict | None:
        """Get user with logging."""
        return await self._request("GET", f"/api/v1/users/{user_id}")
```

---

## Error Handling Table

| HTTP Code | Error Type | Action |
|-----------|------------|--------|
| 400 | Bad Request | Return 400 to client |
| 401 | Unauthorized | Return 401 to client |
| 403 | Forbidden | Return 403 to client |
| 404 | Not Found | NotFoundError |
| 409 | Conflict | ConflictError/ValidationError |
| 422 | Validation | ValidationError |
| 500 | Server Error | Return 502 (Bad Gateway) |
| 502 | Bad Gateway | Retry, then 502 |
| 503 | Unavailable | Retry, then 503 |
| 504 | Timeout | Retry, then 504 |

---

## Checklist

- [ ] Exception hierarchy defined
- [ ] HTTP code to exception mapping
- [ ] Business exceptions separated from HTTP
- [ ] Handlers registered in FastAPI
- [ ] Error logging configured
