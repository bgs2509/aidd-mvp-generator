"""
Схемы ошибок.

Pydantic схемы для стандартизированных ответов об ошибках.
"""

from typing import Any

from pydantic import Field

from .base import BaseResponseSchema


class ErrorDetail(BaseResponseSchema):
    """
    Детали ошибки.

    Attributes:
        code: Код ошибки (например, "NOT_FOUND").
        message: Человекочитаемое сообщение.
        details: Дополнительная информация.
    """

    code: str = Field(
        ...,
        description="Код ошибки",
        examples=["NOT_FOUND", "VALIDATION_ERROR"],
    )
    message: str = Field(
        ...,
        description="Сообщение об ошибке",
        examples=["Ресурс не найден"],
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Дополнительные детали",
    )


class ErrorResponse(BaseResponseSchema):
    """
    Стандартный ответ об ошибке.

    Формат ответа:
        ```json
        {
            "error": {
                "code": "NOT_FOUND",
                "message": "Пользователь с ID 123 не найден",
                "details": {"entity": "User", "id": "123"}
            }
        }
        ```

    Использование в FastAPI:
        ```python
        @router.get(
            "/users/{user_id}",
            responses={
                404: {"model": ErrorResponse, "description": "Не найден"}
            }
        )
        async def get_user(user_id: UUID):
            ...
        ```
    """

    error: ErrorDetail = Field(..., description="Информация об ошибке")

    @classmethod
    def create(
        cls,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> "ErrorResponse":
        """
        Создать ответ об ошибке.

        Args:
            code: Код ошибки.
            message: Сообщение.
            details: Дополнительные детали.

        Returns:
            Объект ErrorResponse.
        """
        return cls(
            error=ErrorDetail(
                code=code,
                message=message,
                details=details,
            )
        )


class ValidationErrorDetail(BaseResponseSchema):
    """
    Детали ошибки валидации для одного поля.

    Attributes:
        field: Путь к полю (например, "body.email").
        message: Сообщение об ошибке.
        type: Тип ошибки валидации.
    """

    field: str = Field(
        ...,
        description="Путь к полю",
        examples=["body.email", "query.page"],
    )
    message: str = Field(
        ...,
        description="Сообщение об ошибке",
        examples=["Поле обязательно для заполнения"],
    )
    type: str = Field(
        ...,
        description="Тип ошибки",
        examples=["missing", "string_too_short", "value_error"],
    )


class ValidationErrorResponse(BaseResponseSchema):
    """
    Ответ об ошибках валидации.

    Формат ответа:
        ```json
        {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Ошибка валидации входных данных"
            },
            "validation_errors": [
                {
                    "field": "body.email",
                    "message": "Невалидный email адрес",
                    "type": "value_error"
                }
            ]
        }
        ```

    Использование в FastAPI:
        ```python
        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc):
            return JSONResponse(
                status_code=422,
                content=ValidationErrorResponse.from_pydantic(exc).model_dump()
            )
        ```
    """

    error: ErrorDetail = Field(
        default_factory=lambda: ErrorDetail(
            code="VALIDATION_ERROR",
            message="Ошибка валидации входных данных",
        ),
        description="Общая информация об ошибке",
    )
    validation_errors: list[ValidationErrorDetail] = Field(
        ...,
        alias="validationErrors",
        description="Список ошибок валидации",
    )

    @classmethod
    def from_pydantic(cls, exc: Any) -> "ValidationErrorResponse":
        """
        Создать из Pydantic ValidationError или FastAPI RequestValidationError.

        Args:
            exc: Исключение валидации.

        Returns:
            ValidationErrorResponse.
        """
        errors = []

        # Получаем список ошибок
        raw_errors = getattr(exc, "errors", lambda: [])()

        for error in raw_errors:
            # Формируем путь к полю
            loc = error.get("loc", ())
            field = ".".join(str(x) for x in loc)

            errors.append(
                ValidationErrorDetail(
                    field=field,
                    message=error.get("msg", "Ошибка валидации"),
                    type=error.get("type", "value_error"),
                )
            )

        return cls(validation_errors=errors)

    @classmethod
    def create(
        cls,
        errors: list[tuple[str, str, str]],
    ) -> "ValidationErrorResponse":
        """
        Создать из списка кортежей (field, message, type).

        Args:
            errors: Список ошибок в формате (поле, сообщение, тип).

        Returns:
            ValidationErrorResponse.
        """
        validation_errors = [
            ValidationErrorDetail(field=f, message=m, type=t)
            for f, m, t in errors
        ]
        return cls(validation_errors=validation_errors)


# === Предопределённые ответы об ошибках ===

class NotFoundResponse(ErrorResponse):
    """Ответ 404 Not Found."""

    error: ErrorDetail = Field(
        default_factory=lambda: ErrorDetail(
            code="NOT_FOUND",
            message="Ресурс не найден",
        )
    )


class UnauthorizedResponse(ErrorResponse):
    """Ответ 401 Unauthorized."""

    error: ErrorDetail = Field(
        default_factory=lambda: ErrorDetail(
            code="UNAUTHORIZED",
            message="Требуется авторизация",
        )
    )


class ForbiddenResponse(ErrorResponse):
    """Ответ 403 Forbidden."""

    error: ErrorDetail = Field(
        default_factory=lambda: ErrorDetail(
            code="FORBIDDEN",
            message="Доступ запрещён",
        )
    )


class ConflictResponse(ErrorResponse):
    """Ответ 409 Conflict."""

    error: ErrorDetail = Field(
        default_factory=lambda: ErrorDetail(
            code="CONFLICT",
            message="Конфликт данных",
        )
    )


class InternalErrorResponse(ErrorResponse):
    """Ответ 500 Internal Server Error."""

    error: ErrorDetail = Field(
        default_factory=lambda: ErrorDetail(
            code="INTERNAL_ERROR",
            message="Внутренняя ошибка сервера",
        )
    )


# === Словарь стандартных ответов для OpenAPI ===

STANDARD_ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Некорректный запрос"},
    401: {"model": UnauthorizedResponse, "description": "Не авторизован"},
    403: {"model": ForbiddenResponse, "description": "Доступ запрещён"},
    404: {"model": NotFoundResponse, "description": "Не найден"},
    409: {"model": ConflictResponse, "description": "Конфликт"},
    422: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
    500: {"model": InternalErrorResponse, "description": "Внутренняя ошибка"},
}
