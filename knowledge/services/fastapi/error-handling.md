# FastAPI Error Handling

> **Purpose**: Error handling and response patterns.

---

## Custom Exceptions

```python
"""Custom exceptions."""


class AppError(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str | None = None):
        """
        Initialize exception.

        Args:
            message: Error message.
            code: Error code.
        """
        self.message = message
        self.code = code or "APP_ERROR"
        super().__init__(self.message)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: str):
        """
        Initialize exception.

        Args:
            resource: Resource type.
            resource_id: Resource ID.
        """
        super().__init__(
            message=f"{resource} with id {resource_id} not found",
            code="NOT_FOUND",
        )
        self.resource = resource
        self.resource_id = resource_id


class ValidationError(AppError):
    """Validation error."""

    def __init__(self, message: str, field: str | None = None):
        """
        Initialize exception.

        Args:
            message: Error message.
            field: Field with error.
        """
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.field = field


class ConflictError(AppError):
    """Data conflict."""

    def __init__(self, message: str):
        """
        Initialize exception.

        Args:
            message: Error message.
        """
        super().__init__(message=message, code="CONFLICT")


class DataApiError(AppError):
    """Data API error."""

    def __init__(self, message: str, status_code: int):
        """
        Initialize exception.

        Args:
            message: Error message.
            status_code: HTTP code from Data API.
        """
        super().__init__(message=message, code="DATA_API_ERROR")
        self.status_code = status_code
```

---

## Exception Handlers

```python
"""Exception handlers for FastAPI."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from {context}_api.core.exceptions import (
    AppError,
    NotFoundError,
    ValidationError,
    ConflictError,
    DataApiError,
)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Set up exception handlers.

    Args:
        app: FastAPI application.
    """

    @app.exception_handler(NotFoundError)
    async def not_found_handler(
        request: Request,
        exc: NotFoundError,
    ) -> JSONResponse:
        """Handle NotFoundError."""
        return JSONResponse(
            status_code=404,
            content={
                "detail": exc.message,
                "code": exc.code,
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        """Handle ValidationError."""
        return JSONResponse(
            status_code=400,
            content={
                "detail": exc.message,
                "code": exc.code,
                "field": exc.field,
            },
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(
        request: Request,
        exc: ConflictError,
    ) -> JSONResponse:
        """Handle ConflictError."""
        return JSONResponse(
            status_code=409,
            content={
                "detail": exc.message,
                "code": exc.code,
            },
        )

    @app.exception_handler(DataApiError)
    async def data_api_handler(
        request: Request,
        exc: DataApiError,
    ) -> JSONResponse:
        """Handle DataApiError."""
        return JSONResponse(
            status_code=502,
            content={
                "detail": exc.message,
                "code": exc.code,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle request validation errors."""
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": list(error["loc"]),
                "msg": error["msg"],
                "type": error["type"],
            })

        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "code": "VALIDATION_ERROR",
                "errors": errors,
            },
        )

    @app.exception_handler(Exception)
    async def generic_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected errors."""
        # Log the error
        import logging
        logging.exception("Unhandled exception")

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "code": "INTERNAL_ERROR",
            },
        )
```

---

## Usage in Service

```python
"""Example of using exceptions in a service."""

from uuid import UUID

from {context}_api.core.exceptions import NotFoundError, ValidationError


class UserService:
    """User service."""

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
        user = await self.data_client.get_user(user_id)

        if user is None:
            raise NotFoundError("User", str(user_id))

        return UserDTO.model_validate(user)

    async def create_user(self, data: CreateUserDTO) -> UserDTO:
        """
        Create a user.

        Args:
            data: Creation data.

        Returns:
            Created user.

        Raises:
            ValidationError: If email already exists.
        """
        existing = await self.data_client.get_user_by_email(data.email)

        if existing:
            raise ValidationError(
                message=f"Email {data.email} already exists",
                field="email",
            )

        return await self.data_client.create_user(data.model_dump())
```

---

## Error Response Format

```json
// 404 Not Found
{
    "detail": "User with id 123e4567-e89b-12d3-a456-426614174000 not found",
    "code": "NOT_FOUND"
}

// 400 Bad Request
{
    "detail": "Email already exists",
    "code": "VALIDATION_ERROR",
    "field": "email"
}

// 422 Validation Error
{
    "detail": "Validation error",
    "code": "VALIDATION_ERROR",
    "errors": [
        {
            "loc": ["body", "email"],
            "msg": "value is not a valid email address",
            "type": "value_error.email"
        }
    ]
}

// 500 Internal Server Error
{
    "detail": "Internal server error",
    "code": "INTERNAL_ERROR"
}
```

---

## Exception Hierarchy

```
Exception
└── AppError
    ├── NotFoundError
    ├── ValidationError
    ├── ConflictError
    ├── DataApiError
    └── AuthenticationError
```

---

## Checklist

- [ ] All custom exceptions inherit AppError
- [ ] Handlers registered in setup_exception_handlers
- [ ] Exceptions contain clear messages
- [ ] Unexpected errors are logged
- [ ] Response format is unified
