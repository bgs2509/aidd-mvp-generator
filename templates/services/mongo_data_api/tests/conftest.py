"""
Фикстуры для тестов {context}_data.

Фикстуры для MongoDB тестов.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.main import create_app
from src.api.dependencies import get_database


@pytest.fixture
def mock_database() -> MagicMock:
    """Мок базы данных MongoDB."""
    mock = MagicMock(spec=AsyncIOMotorDatabase)
    mock.__getitem__ = MagicMock(return_value=AsyncMock())
    return mock


@pytest.fixture
def app(mock_database):
    """Тестовое приложение."""
    app = create_app()

    # Подмена зависимости базы данных
    app.dependency_overrides[get_database] = lambda: mock_database

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
async def client(app) -> AsyncClient:
    """Асинхронный тест-клиент."""
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client
