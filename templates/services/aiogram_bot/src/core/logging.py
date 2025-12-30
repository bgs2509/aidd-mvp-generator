"""
Настройка логирования {context}_bot.

Структурированное логирование с structlog.
Включает фильтрацию секретных данных (sanitize_sensitive_data).
"""

import logging
import structlog
from structlog.types import Processor

from shared.utils.logger import sanitize_sensitive_data


def setup_logging(log_level: str = "INFO") -> None:
    """
    Настроить структурированное логирование.

    Args:
        log_level: Уровень логирования.
    """
    # SECURITY: sanitize_sensitive_data ДОЛЖЕН быть перед JSONRenderer
    # чтобы маскировать секреты ДО записи в лог
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        sanitize_sensitive_data,  # SECURITY: фильтрация секретов
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
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
