"""
Кастомные исключения.

Базовые исключения для использования во всех сервисах.
"""

from typing import Any


class BaseAppException(Exception):
    """
    Базовое исключение приложения.

    Все кастомные исключения должны наследоваться от этого класса.

    Attributes:
        message: Сообщение об ошибке.
        code: Код ошибки для API.
        details: Дополнительные детали ошибки.
    """

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Инициализировать исключение.

        Args:
            message: Сообщение об ошибке.
            code: Код ошибки для API.
            details: Дополнительные детали ошибки.
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """
        Преобразовать в словарь для API ответа.

        Returns:
            Словарь с информацией об ошибке.
        """
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


# === Ошибки валидации ===

class ValidationError(BaseAppException):
    """Ошибка валидации данных."""

    def __init__(
        self,
        message: str = "Ошибка валидации",
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Инициализировать ошибку валидации.

        Args:
            message: Сообщение об ошибке.
            field: Поле, вызвавшее ошибку.
            details: Дополнительные детали.
        """
        if field:
            details = details or {}
            details["field"] = field
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class InvalidInputError(ValidationError):
    """Невалидные входные данные."""

    def __init__(
        self,
        message: str = "Невалидные входные данные",
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, field, details)
        self.code = "INVALID_INPUT"


# === Ошибки сущностей ===

class NotFoundError(BaseAppException):
    """Сущность не найдена."""

    def __init__(
        self,
        entity: str,
        identifier: Any = None,
        message: str | None = None,
    ) -> None:
        """
        Инициализировать ошибку "не найдено".

        Args:
            entity: Название сущности.
            identifier: Идентификатор сущности.
            message: Кастомное сообщение.
        """
        if message is None:
            if identifier is not None:
                message = f"{entity} с ID '{identifier}' не найден"
            else:
                message = f"{entity} не найден"

        super().__init__(
            message,
            code="NOT_FOUND",
            details={"entity": entity, "identifier": str(identifier)},
        )


class AlreadyExistsError(BaseAppException):
    """Сущность уже существует."""

    def __init__(
        self,
        entity: str,
        identifier: Any = None,
        message: str | None = None,
    ) -> None:
        """
        Инициализировать ошибку "уже существует".

        Args:
            entity: Название сущности.
            identifier: Идентификатор сущности.
            message: Кастомное сообщение.
        """
        if message is None:
            if identifier is not None:
                message = f"{entity} с ID '{identifier}' уже существует"
            else:
                message = f"{entity} уже существует"

        super().__init__(
            message,
            code="ALREADY_EXISTS",
            details={"entity": entity, "identifier": str(identifier)},
        )


class ConflictError(BaseAppException):
    """Конфликт при операции."""

    def __init__(
        self,
        message: str = "Конфликт данных",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code="CONFLICT", details=details)


# === Ошибки авторизации ===

class UnauthorizedError(BaseAppException):
    """Не авторизован."""

    def __init__(
        self,
        message: str = "Требуется авторизация",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code="UNAUTHORIZED", details=details)


class ForbiddenError(BaseAppException):
    """Доступ запрещён."""

    def __init__(
        self,
        message: str = "Доступ запрещён",
        resource: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        if resource:
            details = details or {}
            details["resource"] = resource
        super().__init__(message, code="FORBIDDEN", details=details)


# === Ошибки внешних сервисов ===

class ExternalServiceError(BaseAppException):
    """Ошибка внешнего сервиса."""

    def __init__(
        self,
        service: str,
        message: str | None = None,
        original_error: Exception | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Инициализировать ошибку внешнего сервиса.

        Args:
            service: Название сервиса.
            message: Сообщение об ошибке.
            original_error: Оригинальное исключение.
            details: Дополнительные детали.
        """
        if message is None:
            message = f"Ошибка при обращении к сервису {service}"

        details = details or {}
        details["service"] = service
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(message, code="EXTERNAL_SERVICE_ERROR", details=details)


class ServiceUnavailableError(ExternalServiceError):
    """Сервис недоступен."""

    def __init__(
        self,
        service: str,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        if message is None:
            message = f"Сервис {service} временно недоступен"
        super().__init__(service, message, details=details)
        self.code = "SERVICE_UNAVAILABLE"


class TimeoutError(ExternalServiceError):
    """Таймаут при обращении к сервису."""

    def __init__(
        self,
        service: str,
        timeout_seconds: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        message = f"Таймаут при обращении к сервису {service}"
        if timeout_seconds:
            message += f" (>{timeout_seconds}s)"
            details = details or {}
            details["timeout_seconds"] = timeout_seconds
        super().__init__(service, message, details=details)
        self.code = "TIMEOUT"


# === Бизнес-ошибки ===

class BusinessLogicError(BaseAppException):
    """Ошибка бизнес-логики."""

    def __init__(
        self,
        message: str,
        code: str = "BUSINESS_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)


class InsufficientFundsError(BusinessLogicError):
    """Недостаточно средств."""

    def __init__(
        self,
        required: float,
        available: float,
        message: str | None = None,
    ) -> None:
        if message is None:
            message = f"Недостаточно средств: требуется {required}, доступно {available}"
        super().__init__(
            message,
            code="INSUFFICIENT_FUNDS",
            details={"required": required, "available": available},
        )


class QuotaExceededError(BusinessLogicError):
    """Превышена квота."""

    def __init__(
        self,
        resource: str,
        limit: int,
        message: str | None = None,
    ) -> None:
        if message is None:
            message = f"Превышена квота для {resource}: лимит {limit}"
        super().__init__(
            message,
            code="QUOTA_EXCEEDED",
            details={"resource": resource, "limit": limit},
        )


class RateLimitError(BusinessLogicError):
    """Превышен лимит запросов."""

    def __init__(
        self,
        retry_after: int | None = None,
        message: str = "Слишком много запросов",
    ) -> None:
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", details=details)
