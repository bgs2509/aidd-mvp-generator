# Базовая настройка Aiogram

> **Назначение**: Настройка Telegram бота на Aiogram 3.x.

---

## Точка входа

```python
"""Точка входа Telegram бота."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from {context}_bot.core.config import settings
from {context}_bot.handlers import start, menu, orders


async def main() -> None:
    """Запустить бота."""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Создание бота
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )

    # Создание диспетчера
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(orders.router)

    # Запуск поллинга
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Конфигурация

```python
"""Конфигурация бота."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Telegram бота."""

    # Telegram
    bot_token: str

    # API URLs
    business_api_url: str = "http://localhost:8000"

    # Настройки
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## Структура проекта

```
{context}_bot/
├── __init__.py
├── main.py                  # Точка входа
│
├── handlers/                # Обработчики
│   ├── __init__.py
│   ├── start.py            # /start, /help
│   ├── menu.py             # Главное меню
│   └── {feature}.py        # Обработчики фичи
│
├── keyboards/               # Клавиатуры
│   ├── __init__.py
│   ├── base.py             # Базовые клавиатуры
│   └── {feature}.py        # Клавиатуры фичи
│
├── states/                  # FSM состояния
│   ├── __init__.py
│   └── {feature}.py        # Состояния фичи
│
├── middlewares/            # Middleware
│   ├── __init__.py
│   └── logging.py          # Логирование
│
├── infrastructure/         # Внешние сервисы
│   ├── __init__.py
│   └── http/
│       ├── __init__.py
│       └── business_api_client.py
│
└── core/                   # Конфигурация
    ├── __init__.py
    ├── config.py
    └── logging.py
```

---

## Базовый обработчик

```python
"""Обработчик команды /start."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from {context}_bot.keyboards.base import get_main_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """
    Обработать команду /start.

    Args:
        message: Входящее сообщение.
    """
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=get_main_keyboard(),
    )
```

---

## С HTTP клиентом

```python
"""Точка входа с HTTP клиентом."""

import asyncio
import httpx

from aiogram import Bot, Dispatcher

from {context}_bot.core.config import settings
from {context}_bot.handlers import start, menu
from {context}_bot.infrastructure.http.business_api_client import BusinessApiClient


async def main() -> None:
    """Запустить бота с HTTP клиентом."""
    # Создание HTTP клиента
    async with httpx.AsyncClient(
        base_url=settings.business_api_url,
        timeout=httpx.Timeout(30.0),
    ) as http_client:
        # Обёртка над HTTP клиентом
        api_client = BusinessApiClient(http_client)

        # Создание бота и диспетчера
        bot = Bot(token=settings.bot_token)
        dp = Dispatcher()

        # Передача зависимостей через workflow_data
        dp.workflow_data["api_client"] = api_client

        # Регистрация роутеров
        dp.include_router(start.router)
        dp.include_router(menu.router)

        # Запуск
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

## Чек-лист

- [ ] Bot создан с DefaultBotProperties
- [ ] ParseMode установлен (HTML/Markdown)
- [ ] Диспетчер создан
- [ ] Роутеры зарегистрированы
- [ ] HTTP клиент закрывается при завершении
- [ ] Логирование настроено
