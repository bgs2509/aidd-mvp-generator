"""
Фикстуры для тестов {context}_bot.

Общие фикстуры для тестирования бота.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from aiogram import Bot, Dispatcher
from aiogram.types import User, Chat, Message


@pytest.fixture
def bot() -> AsyncMock:
    """Мок бота."""
    mock = AsyncMock(spec=Bot)
    mock.id = 123456789
    return mock


@pytest.fixture
def dp() -> Dispatcher:
    """Диспетчер для тестов."""
    return Dispatcher()


@pytest.fixture
def user() -> User:
    """Тестовый пользователь."""
    return User(
        id=12345,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser",
        language_code="ru",
    )


@pytest.fixture
def chat() -> Chat:
    """Тестовый чат."""
    return Chat(
        id=12345,
        type="private",
    )


@pytest.fixture
def message(user: User, chat: Chat) -> MagicMock:
    """Тестовое сообщение."""
    mock = MagicMock(spec=Message)
    mock.from_user = user
    mock.chat = chat
    mock.text = "/start"
    mock.answer = AsyncMock()
    return mock
