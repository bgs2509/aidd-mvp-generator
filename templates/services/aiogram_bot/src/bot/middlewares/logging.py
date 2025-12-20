"""
Middleware логирования.

Логирование всех входящих событий.
"""

import uuid
from typing import Any, Awaitable, Callable, Dict

import structlog
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from structlog.contextvars import bind_contextvars, clear_contextvars


logger = structlog.get_logger()


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования событий."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Обработка события.

        Args:
            handler: Следующий обработчик.
            event: Telegram событие.
            data: Данные контекста.

        Returns:
            Результат обработки.
        """
        # Генерация request_id
        request_id = str(uuid.uuid4())

        # Определение данных пользователя
        user_id = None
        chat_id = None
        event_type = "unknown"

        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            chat_id = event.chat.id
            event_type = "message"
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            chat_id = event.message.chat.id if event.message else None
            event_type = "callback"

        # Привязка контекста
        bind_contextvars(
            request_id=request_id,
            service="{context}_bot",
            user_id=user_id,
            chat_id=chat_id,
        )

        # Передача request_id в данные
        data["request_id"] = request_id

        try:
            logger.info(
                "Событие получено",
                event_type=event_type,
            )

            result = await handler(event, data)

            logger.info(
                "Событие обработано",
                event_type=event_type,
            )

            return result

        except Exception as e:
            logger.exception(
                "Ошибка обработки события",
                event_type=event_type,
                error=str(e),
            )
            raise

        finally:
            clear_contextvars()
