# Middleware Aiogram

> **Назначение**: Настройка middleware для бота.

---

## Базовый middleware

```python
"""Базовый middleware."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Выполнить middleware.

        Args:
            handler: Следующий обработчик.
            event: Telegram событие.
            data: Данные контекста.

        Returns:
            Результат обработчика.
        """
        import logging
        logger = logging.getLogger(__name__)

        # До обработки
        logger.info(f"Received: {type(event).__name__}")

        # Вызов обработчика
        result = await handler(event, data)

        # После обработки
        logger.info(f"Handled: {type(event).__name__}")

        return result
```

---

## Middleware аутентификации

```python
"""Middleware проверки пользователя."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from {context}_bot.infrastructure.http.business_api_client import BusinessApiClient


class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки и регистрации пользователя."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """
        Проверить пользователя.

        Args:
            handler: Следующий обработчик.
            event: Сообщение.
            data: Данные контекста.

        Returns:
            Результат обработчика.
        """
        api_client: BusinessApiClient = data["api_client"]
        telegram_id = event.from_user.id

        # Получить или создать пользователя
        user = await api_client.get_or_create_user(
            telegram_id=telegram_id,
            username=event.from_user.username,
            first_name=event.from_user.first_name,
        )

        # Добавить пользователя в контекст
        data["user"] = user

        return await handler(event, data)
```

---

## Middleware throttling

```python
"""Middleware для ограничения частоты запросов."""

from typing import Any, Awaitable, Callable, Dict
from datetime import datetime, timedelta

from aiogram import BaseMiddleware
from aiogram.types import Message


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для throttling."""

    def __init__(self, rate_limit: float = 0.5):
        """
        Инициализация middleware.

        Args:
            rate_limit: Минимальный интервал между сообщениями (секунды).
        """
        self.rate_limit = rate_limit
        self.users: Dict[int, datetime] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """
        Проверить rate limit.

        Args:
            handler: Следующий обработчик.
            event: Сообщение.
            data: Данные контекста.

        Returns:
            Результат обработчика или None.
        """
        user_id = event.from_user.id
        now = datetime.now()

        # Проверить время последнего сообщения
        if user_id in self.users:
            last_time = self.users[user_id]
            if (now - last_time).total_seconds() < self.rate_limit:
                # Игнорировать сообщение
                return None

        # Обновить время
        self.users[user_id] = now

        return await handler(event, data)
```

---

## Middleware метрик

```python
"""Middleware для сбора метрик."""

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class MetricsMiddleware(BaseMiddleware):
    """Middleware для сбора метрик."""

    def __init__(self):
        """Инициализация middleware."""
        self.request_count = 0
        self.total_time = 0.0

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Собрать метрики.

        Args:
            handler: Следующий обработчик.
            event: Telegram событие.
            data: Данные контекста.

        Returns:
            Результат обработчика.
        """
        start_time = time.perf_counter()

        try:
            result = await handler(event, data)
            return result
        finally:
            elapsed = time.perf_counter() - start_time
            self.request_count += 1
            self.total_time += elapsed
```

---

## Middleware обработки ошибок

```python
"""Middleware для обработки ошибок."""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message


class ErrorHandlerMiddleware(BaseMiddleware):
    """Middleware для обработки ошибок."""

    def __init__(self):
        """Инициализация middleware."""
        self.logger = logging.getLogger(__name__)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """
        Обработать ошибки.

        Args:
            handler: Следующий обработчик.
            event: Сообщение.
            data: Данные контекста.

        Returns:
            Результат обработчика.
        """
        try:
            return await handler(event, data)
        except Exception as e:
            self.logger.exception(f"Error handling message: {e}")

            # Отправить сообщение об ошибке пользователю
            await event.answer(
                "Произошла ошибка. Попробуйте позже."
            )

            return None
```

---

## Регистрация middleware

```python
"""Регистрация middleware."""

from aiogram import Dispatcher

from {context}_bot.middlewares.logging import LoggingMiddleware
from {context}_bot.middlewares.auth import AuthMiddleware
from {context}_bot.middlewares.throttling import ThrottlingMiddleware


def setup_middlewares(dp: Dispatcher) -> None:
    """
    Настроить middleware.

    Args:
        dp: Диспетчер.
    """
    # Outer middleware (выполняется первым)
    dp.message.outer_middleware(LoggingMiddleware())

    # Middleware (выполняется для всех сообщений)
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
    dp.message.middleware(AuthMiddleware())

    # Для callback query
    dp.callback_query.middleware(AuthMiddleware())


# main.py
dp = Dispatcher()
setup_middlewares(dp)
```

---

## Порядок выполнения

```
Запрос
    │
    ▼
LoggingMiddleware (outer)
    │
    ▼
ThrottlingMiddleware
    │
    ▼
AuthMiddleware
    │
    ▼
Handler
    │
    ▼
AuthMiddleware (после)
    │
    ▼
ThrottlingMiddleware (после)
    │
    ▼
LoggingMiddleware (после)
    │
    ▼
Ответ
```

---

## Чек-лист

- [ ] Логирование настроено
- [ ] Throttling добавлен
- [ ] Ошибки обрабатываются
- [ ] Пользователь проверяется
- [ ] Middleware зарегистрированы в правильном порядке
