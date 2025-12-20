"""
Настройка логирования {context}_data.

Структурированное логирование с structlog.
"""

import logging
import structlog
from structlog.types import Processor


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
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
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
