"""
Кастомные исключения {context}_api.

Иерархия исключений для бизнес-логики.
"""

from typing import Any


class AppException(Exception):
    """Базовое исключение приложения."""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        details: dict[str, Any] | None = None,
    ):
        """
        Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
            code: Код ошибки.
            details: Дополнительные детали.
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    """Ресурс не найден."""

    def __init__(
        self,
        resource: str,
        resource_id: str | None = None,
    ):
        """
        Инициализация исключения.

        Args:
            resource: Тип ресурса.
            resource_id: ID ресурса.
        """
        message = f"{resource} не найден"
        if resource_id:
            message = f"{resource} с ID {resource_id} не найден"

        super().__init__(
            message=message,
            code="NOT_FOUND",
            details={"resource": resource, "resource_id": resource_id},
        )


class ValidationError(AppException):
    """Ошибка валидации."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
    ):
        """
        Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
            field: Поле с ошибкой.
        """
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field} if field else {},
        )


class ConflictError(AppException):
    """Конфликт ресурса."""

    def __init__(
        self,
        message: str,
        resource: str | None = None,
    ):
        """
        Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
            resource: Тип ресурса.
        """
        super().__init__(
            message=message,
            code="CONFLICT",
            details={"resource": resource} if resource else {},
        )


class ExternalServiceError(AppException):
    """Ошибка внешнего сервиса."""

    def __init__(
        self,
        service: str,
        message: str,
        status_code: int | None = None,
    ):
        """
        Инициализация исключения.

        Args:
            service: Название сервиса.
            message: Сообщение об ошибке.
            status_code: HTTP код ответа.
        """
        super().__init__(
            message=f"Ошибка сервиса {service}: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            details={
                "service": service,
                "status_code": status_code,
            },
        )
