# Функция: Stage 4.5 — Telegram Bot

> **Назначение**: Создание Telegram бота на aiogram 3.x.

---

## Цель

Создать Telegram бота, который взаимодействует с Business API
для предоставления функциональности пользователям через Telegram.

---

## Когда применяется

```
if "Telegram" in FR or "бот" in FR:
    → Создать Telegram Bot сервис
else:
    → Пропустить этот этап
```

---

## Архитектурный принцип

```
ПРАВИЛО: Telegram Bot использует Business API,
         а не обращается к БД напрямую.

Telegram User ──▶ Bot ──HTTP──▶ Business API ──HTTP──▶ Data API

Bot содержит UI логику (handlers, keyboards),
но бизнес-логика находится в Business API.
```

---

## Структура Telegram Bot

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

## Компоненты

### 1. main.py

```python
"""Точка входа Telegram бота."""

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
    """Запуск бота."""
    setup_logging()
    logger = logging.getLogger(__name__)

    # Инициализация
    bot = Bot(
        token=settings.bot_token,
        default={"parse_mode": ParseMode.HTML},
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # HTTP клиент для Business API
    api_client = BusinessApiClient(settings.business_api_url)
    dp["api_client"] = api_client

    # Регистрация middleware и handlers
    register_middlewares(dp)
    register_handlers(dp)

    logger.info("Бот запускается...")

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
"""Конфигурация бота."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки бота."""

    # Telegram
    bot_token: str

    # Business API
    business_api_url: str = "http://localhost:8000"

    # Общие
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

### 3. HTTP Client (infrastructure/http/)

```python
"""HTTP клиент для Business API."""

from typing import Any
from uuid import UUID

import httpx


class BusinessApiClient:
    """Клиент для взаимодействия с Business API."""

    def __init__(self, base_url: str):
        """Инициализация клиента."""
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Получить HTTP клиент."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Закрыть соединение."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def list_{entities}(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """Получить список {entities}."""
        response = await self.client.get(
            "/api/v1/{entities}",
            params={"page": page, "page_size": page_size},
        )
        response.raise_for_status()
        return response.json()

    async def get_{entity}(self, {entity}_id: UUID) -> dict[str, Any] | None:
        """Получить {entity} по ID."""
        response = await self.client.get(f"/api/v1/{entities}/{{{entity}_id}}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def create_{entity}(self, data: dict) -> dict[str, Any]:
        """Создать {entity}."""
        response = await self.client.post("/api/v1/{entities}", json=data)
        response.raise_for_status()
        return response.json()
```

### 4. Handlers (handlers/)

```python
"""Базовый handler."""

from aiogram import Router

router = Router()
```

```python
"""Handler для команды /start."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from {context}_bot.keyboards.base import get_main_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    help_text = (
        "<b>Доступные команды:</b>\n\n"
        "/start - Начать работу\n"
        "/help - Показать справку\n"
        "/list - Список {entities}\n"
    )
    await message.answer(help_text)
```

```python
"""Handlers для {Entity}."""

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


@router.message(F.text == "📋 Список {entities}")
async def show_{entity}_list(message: Message, api_client: BusinessApiClient):
    """Показать список {entities}."""
    result = await api_client.list_{entities}()
    items = result.get("items", [])

    if not items:
        await message.answer("Список пуст.")
        return

    await message.answer(
        "Выберите {entity}:",
        reply_markup=get_{entity}_list_keyboard(items),
    )


@router.callback_query(F.data.startswith("{entity}:"))
async def show_{entity}_detail(
    callback: CallbackQuery,
    api_client: BusinessApiClient,
):
    """Показать детали {entity}."""
    {entity}_id = UUID(callback.data.split(":")[1])
    {entity} = await api_client.get_{entity}({entity}_id)

    if {entity} is None:
        await callback.answer("{Entity} не найден", show_alert=True)
        return

    text = (
        f"<b>{{{entity}['name']}}</b>\n\n"
        f"ID: {{{entity}['id']}}\n"
        # ... другие поля ...
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_{entity}_detail_keyboard({entity}_id),
    )
    await callback.answer()


@router.message(F.text == "➕ Создать {entity}")
async def start_create_{entity}(message: Message, state: FSMContext):
    """Начать создание {entity}."""
    await message.answer("Введите название {entity}:")
    await state.set_state(Create{Entity}State.waiting_for_name)


@router.message(Create{Entity}State.waiting_for_name)
async def process_{entity}_name(
    message: Message,
    state: FSMContext,
    api_client: BusinessApiClient,
):
    """Обработать название {entity}."""
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("Название слишком короткое. Попробуйте ещё раз:")
        return

    # Создание через API
    {entity} = await api_client.create_{entity}({"name": name})

    await message.answer(
        f"✅ {Entity} '{{{entity}['name']}}' создан!",
    )
    await state.clear()
```

### 5. Keyboards (keyboards/)

```python
"""Базовые клавиатуры."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Список {entities}"),
                KeyboardButton(text="➕ Создать {entity}"),
            ],
            [
                KeyboardButton(text="❓ Помощь"),
            ],
        ],
        resize_keyboard=True,
    )
```

```python
"""Клавиатуры для {Entity}."""

from uuid import UUID

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_{entity}_list_keyboard(items: list[dict]) -> InlineKeyboardMarkup:
    """Клавиатура списка {entities}."""
    buttons = [
        [InlineKeyboardButton(
            text=item["name"],
            callback_data=f"{entity}:{item['id']}",
        )]
        for item in items
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_{entity}_detail_keyboard({entity}_id: UUID) -> InlineKeyboardMarkup:
    """Клавиатура деталей {entity}."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✏️ Редактировать",
                callback_data=f"edit_{entity}:{{{entity}_id}}",
            ),
            InlineKeyboardButton(
                text="🗑 Удалить",
                callback_data=f"delete_{entity}:{{{entity}_id}}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="back_to_list",
            ),
        ],
    ])
```

### 6. States (states/)

```python
"""FSM состояния для {Entity}."""

from aiogram.fsm.state import State, StatesGroup


class Create{Entity}State(StatesGroup):
    """Состояния создания {entity}."""

    waiting_for_name = State()
    waiting_for_description = State()
    confirmation = State()


class Edit{Entity}State(StatesGroup):
    """Состояния редактирования {entity}."""

    selecting_field = State()
    waiting_for_value = State()
```

### 7. Регистрация handlers (handlers/__init__.py)

```python
"""Регистрация handlers."""

from aiogram import Dispatcher

from {context}_bot.handlers import start, {entity}_handlers


def register_handlers(dp: Dispatcher):
    """Зарегистрировать все handlers."""
    dp.include_router(start.router)
    dp.include_router({entity}_handlers.router)
```

---

## Шаблон для использования

```
templates/services/aiogram_bot/
```

---

## Порядок создания

```
1. Создать структуру директорий
2. Создать Dockerfile
3. Создать requirements.txt
4. Создать core/config.py, logging.py
5. Создать infrastructure/http/business_api_client.py
6. Создать handlers/base.py, start.py
7. Создать keyboards/base.py
8. Создать states/{entity}_states.py
9. Создать handlers/{entity}_handlers.py
10. Создать keyboards/{entity}_keyboards.py
11. Создать handlers/__init__.py (регистрация)
12. Создать main.py
```

---

## Качественные ворота

### TELEGRAM_BOT_READY

- [ ] Структура проекта создана по шаблону
- [ ] HTTP клиент для Business API создан
- [ ] Handlers для всех команд созданы
- [ ] Keyboards созданы
- [ ] FSM states настроены
- [ ] Dockerfile создан
- [ ] `docker-compose up {context}-bot` запускается
- [ ] Бот отвечает на /start

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/services/aiogram/basic-setup.md` | Базовая настройка |
| `knowledge/services/aiogram/handler-patterns.md` | Паттерны handlers |
| `knowledge/services/aiogram/state-management.md` | FSM |
| `templates/services/aiogram_bot/` | Шаблон сервиса |
