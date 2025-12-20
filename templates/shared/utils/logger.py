"""
Структурированное логирование.

Настройка structlog для JSON логов.
"""

import logging
import structlog
from structlog.types import Processor


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
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        # Добавление названия сервиса
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
