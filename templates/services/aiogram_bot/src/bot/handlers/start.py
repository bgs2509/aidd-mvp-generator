"""
Обработчики команд /start и /help.

Базовые команды бота.
"""

import structlog
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message


logger = structlog.get_logger()
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обработчик команды /start.

    Args:
        message: Входящее сообщение.
    """
    logger.info(
        "Команда /start",
        user_id=message.from_user.id,
        username=message.from_user.username,
    )

    await message.answer(
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Я бот {context}.\n\n"
        "Используйте /help для просмотра доступных команд."
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Обработчик команды /help.

    Args:
        message: Входящее сообщение.
    """
    logger.info(
        "Команда /help",
        user_id=message.from_user.id,
    )

    help_text = (
        "📚 <b>Доступные команды:</b>\n\n"
        "/start — Начать работу с ботом\n"
        "/help — Показать это сообщение\n"
        # Добавьте свои команды:
        # "/{domain} — Описание команды\n"
    )

    await message.answer(help_text)
