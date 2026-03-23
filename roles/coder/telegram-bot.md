# Function: Stage 4.5 — Telegram Bot

> **Purpose**: Creating a Telegram bot using aiogram 3.x.

---

## Goal

Create a Telegram bot that interacts with the Business API
to provide functionality to users through Telegram.

---

## When to Apply

```
if "Telegram" in FR or "bot" in FR:
    → Create Telegram Bot service
else:
    → Skip this stage
```

---

## Architectural Principle

```
RULE: Telegram Bot uses the Business API,
      and does not access the database directly.

Telegram User ──▶ Bot ──HTTP──▶ Business API ──HTTP──▶ Data API

Bot contains UI logic (handlers, keyboards),
but business logic resides in the Business API.
```

---

## Telegram Bot Structure

```
services/{context}_bot/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── src/
│   └── {context}_bot/
│       ├── __init__.py
│       ├── main.py
│       ├── handlers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── start.py
│       │   └── {entity}_handlers.py
│       ├── keyboards/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {entity}_keyboards.py
│       ├── states/
│       │   ├── __init__.py
│       │   └── {entity}_states.py
│       ├── middlewares/
│       │   ├── __init__.py
│       │   └── logging_middleware.py
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   └── http/
│       │       ├── __init__.py
│       │       └── business_api_client.py
│       └── core/
│           ├── __init__.py
│           ├── config.py
│           └── logging.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── unit/
        └── test_handlers.py
```

---

## Components

### 1. main.py

```python
"""Telegram bot entry point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from {context}_bot.core.config import settings
from {context}_bot.core.logging import setup_logging
from {context}_bot.handlers import register_handlers
from {context}_bot.middlewares import register_middlewares
from {context}_bot.infrastructure.http.business_api_client import BusinessApiClient


async def main():
    """Start the bot."""
    setup_logging()
    logger = logging.getLogger(__name__)

    # Initialization
    bot = Bot(
        token=settings.bot_token,
        default={"parse_mode": ParseMode.HTML},
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # HTTP client for Business API
    api_client = BusinessApiClient(settings.business_api_url)
    dp["api_client"] = api_client

    # Register middleware and handlers
    register_middlewares(dp)
    register_handlers(dp)

    logger.info("Bot is starting...")

    try:
        await dp.start_polling(bot)
    finally:
        await api_client.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Config (core/config.py)

```python
"""Bot configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Bot settings."""

    # Telegram
    bot_token: str

    # Business API
    business_api_url: str = "http://localhost:8000"

    # General
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

### 3. HTTP Client (infrastructure/http/)

```python
"""HTTP client for Business API."""

from typing import Any
from uuid import UUID

import httpx


class BusinessApiClient:
    """Client for interacting with the Business API."""

    def __init__(self, base_url: str):
        """Initialize the client."""
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def list_{entities}(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """Get list of {entities}."""
        response = await self.client.get(
            "/api/v1/{entities}",
            params={"page": page, "page_size": page_size},
        )
        response.raise_for_status()
        return response.json()

    async def get_{entity}(self, {entity}_id: UUID) -> dict[str, Any] | None:
        """Get {entity} by ID."""
        response = await self.client.get(f"/api/v1/{entities}/{{{entity}_id}}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def create_{entity}(self, data: dict) -> dict[str, Any]:
        """Create {entity}."""
        response = await self.client.post("/api/v1/{entities}", json=data)
        response.raise_for_status()
        return response.json()
```

### 4. Handlers (handlers/)

```python
"""Base handler."""

from aiogram import Router

router = Router()
```

```python
"""Handler for the /start command."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from {context}_bot.keyboards.base import get_main_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """/start command handler."""
    await message.answer(
        "Welcome! Choose an action:",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """/help command handler."""
    help_text = (
        "<b>Available commands:</b>\n\n"
        "/start - Start working\n"
        "/help - Show help\n"
        "/list - List {entities}\n"
    )
    await message.answer(help_text)
```

```python
"""Handlers for {Entity}."""

from uuid import UUID

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from {context}_bot.infrastructure.http.business_api_client import BusinessApiClient
from {context}_bot.keyboards.{entity}_keyboards import (
    get_{entity}_list_keyboard,
    get_{entity}_detail_keyboard,
)
from {context}_bot.states.{entity}_states import Create{Entity}State

router = Router()


@router.message(F.text == "📋 List {entities}")
async def show_{entity}_list(message: Message, api_client: BusinessApiClient):
    """Show list of {entities}."""
    result = await api_client.list_{entities}()
    items = result.get("items", [])

    if not items:
        await message.answer("The list is empty.")
        return

    await message.answer(
        "Select {entity}:",
        reply_markup=get_{entity}_list_keyboard(items),
    )


@router.callback_query(F.data.startswith("{entity}:"))
async def show_{entity}_detail(
    callback: CallbackQuery,
    api_client: BusinessApiClient,
):
    """Show {entity} details."""
    {entity}_id = UUID(callback.data.split(":")[1])
    {entity} = await api_client.get_{entity}({entity}_id)

    if {entity} is None:
        await callback.answer("{Entity} not found", show_alert=True)
        return

    text = (
        f"<b>{{{entity}['name']}}</b>\n\n"
        f"ID: {{{entity}['id']}}\n"
        # ... other fields ...
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_{entity}_detail_keyboard({entity}_id),
    )
    await callback.answer()


@router.message(F.text == "➕ Create {entity}")
async def start_create_{entity}(message: Message, state: FSMContext):
    """Start creating {entity}."""
    await message.answer("Enter {entity} name:")
    await state.set_state(Create{Entity}State.waiting_for_name)


@router.message(Create{Entity}State.waiting_for_name)
async def process_{entity}_name(
    message: Message,
    state: FSMContext,
    api_client: BusinessApiClient,
):
    """Process {entity} name."""
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("Name is too short. Try again:")
        return

    # Create via API
    {entity} = await api_client.create_{entity}({"name": name})

    await message.answer(
        f"✅ {Entity} '{{{entity}['name']}}' created!",
    )
    await state.clear()
```

### 5. Keyboards (keyboards/)

```python
"""Base keyboards."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Main keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 List {entities}"),
                KeyboardButton(text="➕ Create {entity}"),
            ],
            [
                KeyboardButton(text="❓ Help"),
            ],
        ],
        resize_keyboard=True,
    )
```

```python
"""Keyboards for {Entity}."""

from uuid import UUID

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_{entity}_list_keyboard(items: list[dict]) -> InlineKeyboardMarkup:
    """{Entity} list keyboard."""
    buttons = [
        [InlineKeyboardButton(
            text=item["name"],
            callback_data=f"{entity}:{item['id']}",
        )]
        for item in items
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_{entity}_detail_keyboard({entity}_id: UUID) -> InlineKeyboardMarkup:
    """{Entity} detail keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✏️ Edit",
                callback_data=f"edit_{entity}:{{{entity}_id}}",
            ),
            InlineKeyboardButton(
                text="🗑 Delete",
                callback_data=f"delete_{entity}:{{{entity}_id}}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◀️ Back",
                callback_data="back_to_list",
            ),
        ],
    ])
```

### 6. States (states/)

```python
"""FSM states for {Entity}."""

from aiogram.fsm.state import State, StatesGroup


class Create{Entity}State(StatesGroup):
    """{Entity} creation states."""

    waiting_for_name = State()
    waiting_for_description = State()
    confirmation = State()


class Edit{Entity}State(StatesGroup):
    """{Entity} editing states."""

    selecting_field = State()
    waiting_for_value = State()
```

### 7. Handler Registration (handlers/__init__.py)

```python
"""Handler registration."""

from aiogram import Dispatcher

from {context}_bot.handlers import start, {entity}_handlers


def register_handlers(dp: Dispatcher):
    """Register all handlers."""
    dp.include_router(start.router)
    dp.include_router({entity}_handlers.router)
```

---

## Template to Use

```
templates/services/aiogram_bot/
```

---

## Creation Order

```
1. Create directory structure
2. Create Dockerfile
3. Create requirements.txt
4. Create core/config.py, logging.py
5. Create infrastructure/http/business_api_client.py
6. Create handlers/base.py, start.py
7. Create keyboards/base.py
8. Create states/{entity}_states.py
9. Create handlers/{entity}_handlers.py
10. Create keyboards/{entity}_keyboards.py
11. Create handlers/__init__.py (registration)
12. Create main.py
```

---

## Quality Gates

### TELEGRAM_BOT_READY

- [ ] Project structure created from template
- [ ] HTTP client for Business API created
- [ ] Handlers for all commands created
- [ ] Keyboards created
- [ ] FSM states configured
- [ ] Dockerfile created
- [ ] `docker-compose up {context}-bot` starts successfully
- [ ] Bot responds to /start

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/services/aiogram/basic-setup.md` | Basic setup |
| `knowledge/services/aiogram/handler-patterns.md` | Handler patterns |
| `knowledge/services/aiogram/state-management.md` | FSM |
| `templates/services/aiogram_bot/` | Service template |
