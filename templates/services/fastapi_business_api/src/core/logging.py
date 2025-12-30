"""
Настройка логирования {context}_api.

Структурированное логирование с structlog.
Включает фильтрацию секретных данных (sanitize_sensitive_data).
"""

import logging
import structlog
from structlog.types import Processor

from shared.utils.logger import sanitize_sensitive_data


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
) -> None:
    """
    Настроить структурированное логирование.

    Args:
        log_level: Уровень логирования.
        json_logs: Использовать JSON формат.
    """
    # Общие процессоры
    # SECURITY: sanitize_sensitive_data ДОЛЖЕН быть перед JSONRenderer
    # чтобы маскировать секреты ДО записи в лог
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        sanitize_sensitive_data,  # SECURITY: фильтрация секретов
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        # Production: JSON формат
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Консольный формат
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
