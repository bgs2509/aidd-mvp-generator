"""
Точка входа {context}_bot.

Запуск Telegram бота.
"""

import asyncio

import structlog
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from src.core.config import settings
from src.core.logging import setup_logging
from src.bot.handlers import start
from src.bot.middlewares.logging import LoggingMiddleware


logger = structlog.get_logger()


async def main() -> None:
    """Главная функция запуска бота."""
    # Настройка логирования
    setup_logging(log_level=settings.log_level)

    logger.info("Запуск бота", bot_name=settings.bot_name)

    # Создание бота
    bot = Bot(
        token=settings.telegram_bot_token,
        default={"parse_mode": ParseMode.HTML},
    )

    # Хранилище FSM
    storage = RedisStorage.from_url(settings.redis_url)

    # Создание диспетчера
    dp = Dispatcher(storage=storage)

    # Регистрация middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Регистрация роутеров
    dp.include_router(start.router)
    # dp.include_router({domain}.router)

    try:
        # Удаление webhook (для polling)
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("Бот запущен, ожидание сообщений...")

        # Запуск polling
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        logger.info("Остановка бота")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
