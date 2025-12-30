"""
Структурированное логирование по Log-Driven Design.

Настройка structlog для JSON логов с полной трассировкой:
- request_id, correlation_id, causation_id
- entity_type, entity_id для операций над сущностями
- Стандартизированные поля для AI-агентов
"""

import logging
from typing import Any

import structlog
from structlog.types import Processor


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
