# Aiogram Middleware

> **Purpose**: Setting up middleware for the bot.

---

## Basic Middleware

```python
"""Basic middleware."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class LoggingMiddleware(BaseMiddleware):
    """Logging middleware."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Execute middleware.

        Args:
            handler: Next handler.
            event: Telegram event.
            data: Context data.

        Returns:
            Handler result.
        """
        import logging
        logger = logging.getLogger(__name__)

        # Before handling
        logger.info(f"Received: {type(event).__name__}")

        # Call handler
        result = await handler(event, data)

        # After handling
        logger.info(f"Handled: {type(event).__name__}")

        return result
```

---

## Authentication Middleware

```python
"""User verification middleware."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from {context}_bot.infrastructure.http.business_api_client import BusinessApiClient


class AuthMiddleware(BaseMiddleware):
    """Middleware for user verification and registration."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """
        Verify user.

        Args:
            handler: Next handler.
            event: Message.
            data: Context data.

        Returns:
            Handler result.
        """
        api_client: BusinessApiClient = data["api_client"]
        telegram_id = event.from_user.id

        # Get or create user
        user = await api_client.get_or_create_user(
            telegram_id=telegram_id,
            username=event.from_user.username,
            first_name=event.from_user.first_name,
        )

        # Add user to context
        data["user"] = user

        return await handler(event, data)
```

---

## Throttling Middleware

```python
"""Rate limiting middleware."""

from typing import Any, Awaitable, Callable, Dict
from datetime import datetime, timedelta

from aiogram import BaseMiddleware
from aiogram.types import Message


class ThrottlingMiddleware(BaseMiddleware):
    """Throttling middleware."""

    def __init__(self, rate_limit: float = 0.5):
        """
        Initialize middleware.

        Args:
            rate_limit: Minimum interval between messages (seconds).
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
        Check rate limit.

        Args:
            handler: Next handler.
            event: Message.
            data: Context data.

        Returns:
            Handler result or None.
        """
        user_id = event.from_user.id
        now = datetime.now()

        # Check last message time
        if user_id in self.users:
            last_time = self.users[user_id]
            if (now - last_time).total_seconds() < self.rate_limit:
                # Ignore message
                return None

        # Update time
        self.users[user_id] = now

        return await handler(event, data)
```

---

## Metrics Middleware

```python
"""Metrics collection middleware."""

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class MetricsMiddleware(BaseMiddleware):
    """Metrics collection middleware."""

    def __init__(self):
        """Initialize middleware."""
        self.request_count = 0
        self.total_time = 0.0

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Collect metrics.

        Args:
            handler: Next handler.
            event: Telegram event.
            data: Context data.

        Returns:
            Handler result.
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

## Error Handling Middleware

```python
"""Error handling middleware."""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message


class ErrorHandlerMiddleware(BaseMiddleware):
    """Error handling middleware."""

    def __init__(self):
        """Initialize middleware."""
        self.logger = logging.getLogger(__name__)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """
        Handle errors.

        Args:
            handler: Next handler.
            event: Message.
            data: Context data.

        Returns:
            Handler result.
        """
        try:
            return await handler(event, data)
        except Exception as e:
            self.logger.exception(f"Error handling message: {e}")

            # Send error message to user
            await event.answer(
                "An error occurred. Please try again later."
            )

            return None
```

---

## Middleware Registration

```python
"""Middleware registration."""

from aiogram import Dispatcher

from {context}_bot.middlewares.logging import LoggingMiddleware
from {context}_bot.middlewares.auth import AuthMiddleware
from {context}_bot.middlewares.throttling import ThrottlingMiddleware


def setup_middlewares(dp: Dispatcher) -> None:
    """
    Set up middleware.

    Args:
        dp: Dispatcher.
    """
    # Outer middleware (executed first)
    dp.message.outer_middleware(LoggingMiddleware())

    # Middleware (executed for all messages)
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
    dp.message.middleware(AuthMiddleware())

    # For callback queries
    dp.callback_query.middleware(AuthMiddleware())


# main.py
dp = Dispatcher()
setup_middlewares(dp)
```

---

## Execution Order

```
Request
    |
    v
LoggingMiddleware (outer)
    |
    v
ThrottlingMiddleware
    |
    v
AuthMiddleware
    |
    v
Handler
    |
    v
AuthMiddleware (after)
    |
    v
ThrottlingMiddleware (after)
    |
    v
LoggingMiddleware (after)
    |
    v
Response
```

---

## Checklist

- [ ] Logging configured
- [ ] Throttling added
- [ ] Errors handled
- [ ] User verified
- [ ] Middleware registered in correct order
