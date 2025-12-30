"""
Middleware логирования по Log-Driven Design.

Полное логирование Telegram событий:
- update_id, update_type
- user_id, username, chat_id, chat_type
- Команды (/start, /help)
- callback_data
- Длина сообщения, наличие медиа
- FSM состояние (before/after)
- Детальный разбор Telegram API ошибок
- Response type (text/photo/callback_answer)
"""

import time
import uuid
from typing import Any, Awaitable, Callable, Dict

import structlog
from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNotFound,
    TelegramRetryAfter,
    TelegramUnauthorizedError,
)
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    TelegramObject,
    Update,
)
from structlog.contextvars import bind_contextvars, clear_contextvars

from shared.utils.request_id import clear_tracing_context, setup_tracing_context


logger = structlog.get_logger()


def _classify_telegram_error(error: Exception) -> dict[str, Any]:
    """
    Классифицировать Telegram API ошибку для логирования.

    Args:
        error: Исключение Telegram API.

    Returns:
        Словарь с деталями ошибки для логирования.
    """
    error_info: dict[str, Any] = {
        "error": str(error),
        "error_type": type(error).__name__,
    }

    if isinstance(error, TelegramRetryAfter):
        # Rate limiting - HTTP 429
        error_info.update({
            "error_code": 429,
            "is_rate_limited": True,
            "retry_after": error.retry_after,
            "is_retryable": True,
        })
    elif isinstance(error, TelegramForbiddenError):
        # Бот заблокирован или нет прав - HTTP 403
        error_info.update({
            "error_code": 403,
            "is_user_blocked": "bot was blocked" in str(error).lower(),
            "is_chat_kicked": "bot was kicked" in str(error).lower(),
            "is_retryable": False,
        })
    elif isinstance(error, TelegramNotFound):
        # Чат/сообщение не найдено - HTTP 404
        error_info.update({
            "error_code": 404,
            "is_chat_not_found": "chat not found" in str(error).lower(),
            "is_message_not_found": "message" in str(error).lower(),
            "is_retryable": False,
        })
    elif isinstance(error, TelegramBadRequest):
        # Некорректный запрос - HTTP 400
        error_info.update({
            "error_code": 400,
            "is_retryable": False,
        })
    elif isinstance(error, TelegramUnauthorizedError):
        # Невалидный токен - HTTP 401
        error_info.update({
            "error_code": 401,
            "is_retryable": False,
        })
    elif isinstance(error, TelegramAPIError):
        # Общая ошибка Telegram API
        error_info.update({
            "is_retryable": False,
        })

    return error_info


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для логирования событий по Log-Driven Design.

    Логирует:
    - Все входящие Telegram updates с update_id
    - FSM состояния (before/after)
    - Время обработки
    - Ошибки с детальной классификацией Telegram API
    - Тип ответа (text/photo/callback_answer)
    """

    @staticmethod
    def _extract_command(event: TelegramObject) -> str | None:
        """Извлечь команду из сообщения."""
        if isinstance(event, Message) and event.text:
            text = event.text.strip()
            if text.startswith("/"):
                # /command@bot_name -> /command
                command = text.split()[0].split("@")[0]
                return command
        return None

    @staticmethod
    def _get_callback_data(event: TelegramObject) -> str | None:
        """Получить callback_data (безопасно маскируя чувствительные данные)."""
        if isinstance(event, CallbackQuery) and event.data:
            # Логируем только первые 50 символов
            return event.data[:50] if len(event.data) > 50 else event.data
        return None

    @staticmethod
    def _has_media(event: TelegramObject) -> bool:
        """Проверить наличие медиа в сообщении."""
        if isinstance(event, Message):
            return bool(
                event.photo
                or event.video
                or event.audio
                or event.document
                or event.voice
                or event.video_note
                or event.sticker
                or event.animation
            )
        return False

    @staticmethod
    def _get_media_type(event: TelegramObject) -> str | None:
        """Получить тип медиа в сообщении."""
        if isinstance(event, Message):
            if event.photo:
                return "photo"
            if event.video:
                return "video"
            if event.audio:
                return "audio"
            if event.document:
                return "document"
            if event.voice:
                return "voice"
            if event.video_note:
                return "video_note"
            if event.sticker:
                return "sticker"
            if event.animation:
                return "animation"
        return None

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Обработка события с полным логированием.

        Args:
            handler: Следующий обработчик.
            event: Telegram событие.
            data: Данные контекста.

        Returns:
            Результат обработки.
        """
        start_time = time.perf_counter()

        # Генерация request_id и установка контекста трассировки
        request_id = uuid.uuid4().hex
        setup_tracing_context(request_id=request_id)

        # === Извлечение update_id ===
        update_id: int | None = None
        update: Update | None = data.get("event_update")
        if update:
            update_id = update.update_id

        # === Извлечение контекстной информации ===
        user_id: int | None = None
        username: str | None = None
        chat_id: int | None = None
        chat_type: str | None = None
        event_type = "unknown"
        message_text_length = 0
        reply_to_message_id: int | None = None

        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            username = event.from_user.username if event.from_user else None
            chat_id = event.chat.id
            chat_type = event.chat.type
            event_type = "message"
            message_text_length = len(event.text) if event.text else 0
            reply_to_message_id = (
                event.reply_to_message.message_id
                if event.reply_to_message
                else None
            )
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            username = event.from_user.username
            chat_id = event.message.chat.id if event.message else None
            chat_type = event.message.chat.type if event.message else None
            event_type = "callback"

        # Привязка контекста к structlog
        bind_contextvars(
            request_id=request_id,
            service="{context}_bot",
            user_id=user_id,
            chat_id=chat_id,
        )

        # Передача request_id в данные
        data["request_id"] = request_id

        # === FSM состояние ДО обработки ===
        fsm_state_before: str | None = None
        fsm_data_keys: list[str] = []
        state: FSMContext | None = data.get("state")
        if state:
            try:
                fsm_state_before = await state.get_state()
                fsm_data = await state.get_data()
                fsm_data_keys = list(fsm_data.keys()) if fsm_data else []
            except Exception:
                pass  # FSM может быть недоступен

        # === Логирование получения события (Log-Driven Design) ===
        log_data: Dict[str, Any] = {
            "event_type": event_type,
            "chat_id": chat_id,
            "user_id": user_id,
        }

        # update_id для дедупликации и трассировки
        if update_id is not None:
            log_data["update_id"] = update_id

        # Опциональные поля
        if username:
            log_data["username"] = username
        if chat_type:
            log_data["chat_type"] = chat_type

        command = self._extract_command(event)
        if command:
            log_data["command"] = command

        callback_data = self._get_callback_data(event)
        if callback_data:
            log_data["callback_data"] = callback_data

        if message_text_length > 0:
            log_data["message_text_length"] = message_text_length

        media_type = self._get_media_type(event)
        if media_type:
            log_data["has_media"] = True
            log_data["media_type"] = media_type

        if reply_to_message_id:
            log_data["reply_to_message_id"] = reply_to_message_id

        # FSM состояние до обработки
        if fsm_state_before:
            log_data["fsm_state_before"] = fsm_state_before
        if fsm_data_keys:
            log_data["fsm_data_keys"] = fsm_data_keys

        logger.info("telegram_update_received", **log_data)

        try:
            result = await handler(event, data)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # === FSM состояние ПОСЛЕ обработки ===
            fsm_state_after: str | None = None
            if state:
                try:
                    fsm_state_after = await state.get_state()
                except Exception:
                    pass

            # === Определение типа ответа ===
            response_info = self._analyze_response(result)

            # === Логирование успешной обработки ===
            completion_log: Dict[str, Any] = {
                "event_type": event_type,
                "duration_ms": round(duration_ms, 2),
            }

            if update_id is not None:
                completion_log["update_id"] = update_id

            # FSM переход (если состояние изменилось)
            if fsm_state_before != fsm_state_after:
                completion_log["fsm_state_before"] = fsm_state_before
                completion_log["fsm_state_after"] = fsm_state_after
            elif fsm_state_after:
                completion_log["fsm_state"] = fsm_state_after

            # Информация об ответе
            completion_log.update(response_info)

            logger.info("telegram_update_processed", **completion_log)

            return result

        except TelegramAPIError as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # === Детальный разбор Telegram API ошибки ===
            error_info = _classify_telegram_error(e)
            error_info.update({
                "event_type": event_type,
                "duration_ms": round(duration_ms, 2),
            })

            if update_id is not None:
                error_info["update_id"] = update_id

            # Уровень логирования в зависимости от типа ошибки
            if isinstance(e, TelegramRetryAfter):
                logger.warning("telegram_rate_limited", **error_info)
            elif isinstance(e, TelegramForbiddenError):
                logger.warning("telegram_forbidden", **error_info)
            else:
                logger.error("telegram_api_error", **error_info)

            raise

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # === Логирование общей ошибки ===
            logger.exception(
                "telegram_update_failed",
                event_type=event_type,
                update_id=update_id,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2),
            )
            raise

        finally:
            clear_tracing_context()
            clear_contextvars()

    @staticmethod
    def _analyze_response(result: Any) -> Dict[str, Any]:
        """
        Анализировать результат обработки для логирования.

        Args:
            result: Результат handler'а.

        Returns:
            Словарь с информацией об ответе.
        """
        response_info: Dict[str, Any] = {}

        if result is None:
            return response_info

        # Анализ типа ответа
        if isinstance(result, Message):
            # Ответ - сообщение
            if result.text:
                response_info["response_type"] = "text"
                response_info["response_length"] = len(result.text)
            elif result.photo:
                response_info["response_type"] = "photo"
            elif result.document:
                response_info["response_type"] = "document"
            elif result.video:
                response_info["response_type"] = "video"
            elif result.audio:
                response_info["response_type"] = "audio"
            elif result.voice:
                response_info["response_type"] = "voice"
            elif result.sticker:
                response_info["response_type"] = "sticker"
            elif result.animation:
                response_info["response_type"] = "animation"
            else:
                response_info["response_type"] = "message"

            # Наличие клавиатуры
            if result.reply_markup:
                markup_type = type(result.reply_markup).__name__
                if "Inline" in markup_type:
                    response_info["has_keyboard"] = "inline"
                elif "Reply" in markup_type:
                    response_info["has_keyboard"] = "reply"
                elif "Remove" in markup_type:
                    response_info["has_keyboard"] = "remove"
                else:
                    response_info["has_keyboard"] = "other"

        elif isinstance(result, bool):
            # callback_query.answer() возвращает True
            response_info["response_type"] = "callback_answer"

        return response_info


class OuterLoggingMiddleware(BaseMiddleware):
    """
    Outer middleware для логирования на уровне Update.

    Используется для доступа к update_id, который недоступен
    в inner middleware для конкретных типов событий.

    Регистрируется на уровне диспетчера:
        dp.update.outer_middleware(OuterLoggingMiddleware())
    """

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        """
        Сохранить Update в data для доступа во внутренних middleware.

        Args:
            handler: Следующий обработчик.
            event: Telegram Update.
            data: Данные контекста.

        Returns:
            Результат обработки.
        """
        # Сохраняем Update для доступа к update_id во внутренних middleware
        data["event_update"] = event
        return await handler(event, data)
