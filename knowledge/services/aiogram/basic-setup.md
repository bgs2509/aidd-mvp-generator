# Aiogram Basic Setup

> **Purpose**: Setting up a Telegram bot on Aiogram 3.x.

---

## Entry Point

```python
"""Telegram bot entry point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from {context}_bot.core.config import settings
from {context}_bot.handlers import start, menu, orders


async def main() -> None:
    """Start the bot."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create bot
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )

    # Create dispatcher
    dp = Dispatcher()

    # Register routers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(orders.router)

    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Configuration

```python
"""Bot configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Telegram bot settings."""

    # Telegram
    bot_token: str

    # API URLs
    business_api_url: str = "http://localhost:8000"

    # Settings
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## Project Structure

```
{context}_bot/
├── __init__.py
├── main.py                  # Entry point
│
├── handlers/                # Handlers
│   ├── __init__.py
│   ├── start.py            # /start, /help
│   ├── menu.py             # Main menu
│   └── {feature}.py        # Feature handlers
│
├── keyboards/               # Keyboards
│   ├── __init__.py
│   ├── base.py             # Base keyboards
│   └── {feature}.py        # Feature keyboards
│
├── states/                  # FSM states
│   ├── __init__.py
│   └── {feature}.py        # Feature states
│
├── middlewares/            # Middleware
│   ├── __init__.py
│   └── logging.py          # Logging
│
├── infrastructure/         # External services
│   ├── __init__.py
│   └── http/
│       ├── __init__.py
│       └── business_api_client.py
│
└── core/                   # Configuration
    ├── __init__.py
    ├── config.py
    └── logging.py
```

---

## Basic Handler

```python
"""/start command handler."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from {context}_bot.keyboards.base import get_main_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """
    Handle /start command.

    Args:
        message: Incoming message.
    """
    await message.answer(
        "Welcome! Choose an action:",
        reply_markup=get_main_keyboard(),
    )
```

---

## With HTTP Client

```python
"""Entry point with HTTP client."""

import asyncio
import httpx

from aiogram import Bot, Dispatcher

from {context}_bot.core.config import settings
from {context}_bot.handlers import start, menu
from {context}_bot.infrastructure.http.business_api_client import BusinessApiClient


async def main() -> None:
    """Start bot with HTTP client."""
    # Create HTTP client
    async with httpx.AsyncClient(
        base_url=settings.business_api_url,
        timeout=httpx.Timeout(30.0),
    ) as http_client:
        # HTTP client wrapper
        api_client = BusinessApiClient(http_client)

        # Create bot and dispatcher
        bot = Bot(token=settings.bot_token)
        dp = Dispatcher()

        # Pass dependencies via workflow_data
        dp.workflow_data["api_client"] = api_client

        # Register routers
        dp.include_router(start.router)
        dp.include_router(menu.router)

        # Start
        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["python", "-m", "src.{context}_bot.main"]
```

---

## Checklist

- [ ] Bot created with DefaultBotProperties
- [ ] ParseMode set (HTML/Markdown)
- [ ] Dispatcher created
- [ ] Routers registered
- [ ] HTTP client closed on shutdown
- [ ] Logging configured
