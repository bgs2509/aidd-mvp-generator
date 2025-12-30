"""
Структурированное логирование по Log-Driven Design.

Настройка structlog для JSON логов с полной трассировкой:
- request_id, correlation_id, causation_id
- entity_type, entity_id для операций над сущностями
- Стандартизированные поля для AI-агентов
- Автоматическая фильтрация секретных данных (SensitiveDataFilter)
"""

import logging
import re
from typing import Any

import structlog
from structlog.types import Processor


# === Конфигурация секретных данных ===

# Поля, которые ВСЕГДА маскируются (case-insensitive)
SENSITIVE_FIELD_NAMES: set[str] = {
    # Аутентификация
    "password",
    "passwd",
    "pwd",
    "secret",
    "secret_key",
    "api_key",
    "apikey",
    "api_secret",
    "token",
    "access_token",
    "refresh_token",
    "auth_token",
    "jwt",
    "bearer",
    "authorization",
    # База данных
    "database_url",
    "db_password",
    "connection_string",
    "dsn",
    # Внешние сервисы
    "telegram_bot_token",
    "bot_token",
    "webhook_secret",
    "sentry_dsn",
    "smtp_password",
    "redis_password",
    # Криптография
    "private_key",
    "public_key",
    "encryption_key",
    "signing_key",
    # Платёжные системы
    "credit_card",
    "card_number",
    "cvv",
    "cvc",
    "pin",
    # SSH/TLS
    "ssh_key",
    "ssl_key",
    "certificate",
    # Прочее
    "credentials",
    "client_secret",
    "consumer_secret",
}

# Паттерны для поиска секретов в значениях (независимо от имени поля)
SENSITIVE_VALUE_PATTERNS: list[re.Pattern] = [
    # JWT токены
    re.compile(r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"),
    # Bearer токены
    re.compile(r"Bearer\s+[a-zA-Z0-9_-]+", re.IGNORECASE),
    # API ключи (общий паттерн)
    re.compile(r"[a-zA-Z0-9]{32,}"),
    # Пароли в URL (postgresql://user:password@host)
    re.compile(r"://[^:]+:([^@]+)@"),
    # Base64 encoded secrets (длинные)
    re.compile(r"[A-Za-z0-9+/]{40,}={0,2}"),
]

# Значение для замены секретов
REDACTED_VALUE = "***REDACTED***"


def _is_sensitive_field(field_name: str) -> bool:
    """
    Проверить, является ли поле секретным по имени.

    Args:
        field_name: Имя поля.

    Returns:
        True если поле секретное.
    """
    normalized = field_name.lower().replace("-", "_")
    return normalized in SENSITIVE_FIELD_NAMES


def _mask_sensitive_value(value: Any) -> Any:
    """
    Замаскировать секретное значение.

    Args:
        value: Значение для маскировки.

    Returns:
        Замаскированное значение или оригинал если не секрет.
    """
    if value is None:
        return value

    if isinstance(value, str):
        # Проверяем паттерны в строковых значениях
        for pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(value):
                return REDACTED_VALUE
        return value

    if isinstance(value, dict):
        return _sanitize_dict(value)

    if isinstance(value, (list, tuple)):
        return type(value)(_mask_sensitive_value(item) for item in value)

    return value


def _sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Рекурсивно очистить словарь от секретных данных.

    Args:
        data: Словарь для очистки.

    Returns:
        Очищенный словарь.
    """
    result = {}
    for key, value in data.items():
        if _is_sensitive_field(key):
            result[key] = REDACTED_VALUE
        elif isinstance(value, dict):
            result[key] = _sanitize_dict(value)
        elif isinstance(value, (list, tuple)):
            result[key] = type(value)(_mask_sensitive_value(item) for item in value)
        else:
            result[key] = _mask_sensitive_value(value)
    return result


def sanitize_sensitive_data(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """
    Structlog процессор для фильтрации секретных данных.

    Автоматически маскирует:
    - Поля с секретными именами (password, token, secret, etc.)
    - Значения, соответствующие паттернам секретов (JWT, API keys)
    - Вложенные структуры (dict, list)

    Args:
        logger: Логгер (не используется).
        method_name: Название метода логирования.
        event_dict: Словарь события.

    Returns:
        Очищенный словарь события.

    Example:
        >>> event = {"user": "john", "password": "secret123"}
        >>> sanitize_sensitive_data(None, "info", event)
        {"user": "john", "password": "***REDACTED***"}
    """
    return _sanitize_dict(event_dict)


def add_tracing_context(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """
    Процессор для добавления контекста трассировки.

    Автоматически добавляет request_id, correlation_id, causation_id, user_id
    из ContextVars в каждое сообщение лога.

    Args:
        logger: Логгер (не используется).
        method_name: Название метода логирования.
        event_dict: Словарь события.

    Returns:
        Обновлённый словарь события.
    """
    # Ленивый импорт для избежания циклических зависимостей
    from shared.utils.request_id import (
        get_causation_id,
        get_correlation_id,
        get_request_id,
        get_user_id,
    )

    # Добавляем ID трассировки если их нет в event_dict
    if "request_id" not in event_dict:
        request_id = get_request_id()
        if request_id:
            event_dict["request_id"] = request_id

    if "correlation_id" not in event_dict:
        correlation_id = get_correlation_id()
        if correlation_id:
            event_dict["correlation_id"] = correlation_id

    if "causation_id" not in event_dict:
        causation_id = get_causation_id()
        if causation_id:
            event_dict["causation_id"] = causation_id

    # user_id добавляется если пользователь аутентифицирован
    if "user_id" not in event_dict:
        user_id = get_user_id()
        if user_id:
            event_dict["user_id"] = user_id

    return event_dict


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
    service_name: str = "app",
) -> None:
    """
    Настроить структурированное логирование.

    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR).
        json_logs: Использовать JSON формат (True для production).
        service_name: Название сервиса для логов.
    """
    # Общие процессоры
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        add_tracing_context,  # Log-Driven Design: добавляем request_id, correlation_id, causation_id
        sanitize_sensitive_data,  # SECURITY: фильтрация секретных данных ПЕРЕД логированием
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        # Добавление названия сервиса и callsite
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
    ]

    if json_logs:
        # Production: JSON формат
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Консольный формат с цветами
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Привязка названия сервиса
    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """
    Получить логгер.

    Args:
        name: Имя модуля (опционально).

    Returns:
        Bound logger structlog.
    """
    logger = structlog.get_logger()
    if name:
        logger = logger.bind(module=name)
    return logger
