# Обработка ошибок FastAPI

> **Назначение**: Паттерны обработки и возврата ошибок.

---

## Кастомные исключения

```python
"""Кастомные исключения."""


class AppError(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str, code: str | None = None):
        """
        Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
            code: Код ошибки.
        """
        self.message = message
        self.code = code or "APP_ERROR"
        super().__init__(self.message)


class NotFoundError(AppError):
    """Ресурс не найден."""

    def __init__(self, resource: str, resource_id: str):
        """
        Инициализация исключения.

        Args:
            resource: Тип ресурса.
            resource_id: ID ресурса.
        """
        super().__init__(
            message=f"{resource} with id {resource_id} not found",
            code="NOT_FOUND",
        )
        self.resource = resource
        self.resource_id = resource_id


class ValidationError(AppError):
    """Ошибка валидации."""

    def __init__(self, message: str, field: str | None = None):
        """
        Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
            field: Поле с ошибкой.
        """
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.field = field


class ConflictError(AppError):
    """Конфликт данных."""

    def __init__(self, message: str):
        """
        Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
        """
        super().__init__(message=message, code="CONFLICT")


class DataApiError(AppError):
    """Ошибка Data API."""

    def __init__(self, message: str, status_code: int):
        """
        Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
            status_code: HTTP код от Data API.
        """
        super().__init__(message=message, code="DATA_API_ERROR")
        self.status_code = status_code
```

---

## Обработчики исключений

```python
"""Обработчики исключений для FastAPI."""

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
    Настроить обработчики исключений.

    Args:
        app: FastAPI приложение.
    """

    @app.exception_handler(NotFoundError)
    async def not_found_handler(
        request: Request,
        exc: NotFoundError,
    ) -> JSONResponse:
        """Обработчик NotFoundError."""
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
        """Обработчик ValidationError."""
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
        """Обработчик ConflictError."""
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
        """Обработчик DataApiError."""
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
        """Обработчик ошибок валидации запроса."""
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
        """Обработчик непредвиденных ошибок."""
        # Логирование ошибки
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

## Использование в сервисе

```python
"""Пример использования исключений в сервисе."""

from uuid import UUID

from {context}_api.core.exceptions import NotFoundError, ValidationError


class UserService:
    """Сервис пользователей."""

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
        user = await self.data_client.get_user(user_id)

        if user is None:
            raise NotFoundError("User", str(user_id))

        return UserDTO.model_validate(user)

    async def create_user(self, data: CreateUserDTO) -> UserDTO:
        """
        Создать пользователя.

        Args:
            data: Данные для создания.

        Returns:
            Созданный пользователь.

        Raises:
            ValidationError: Если email уже существует.
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

## Формат ответов об ошибках

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

## Иерархия исключений

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

## Чек-лист

- [ ] Все кастомные исключения наследуют AppError
- [ ] Обработчики зарегистрированы в setup_exception_handlers
- [ ] Исключения содержат понятные сообщения
- [ ] Непредвиденные ошибки логируются
- [ ] Формат ответов унифицирован
