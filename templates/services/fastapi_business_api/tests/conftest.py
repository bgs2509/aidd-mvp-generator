"""
Фикстуры для тестов {context}_api.

Общие фикстуры для unit и integration тестов.
"""

import pytest
from unittest.mock import AsyncMock

from httpx import AsyncClient
from fastapi import FastAPI

from src.main import create_app
from src.api.dependencies import get_data_api_client
from src.infrastructure.http.data_api_client import DataApiClient


@pytest.fixture
def app() -> FastAPI:
    """Тестовое приложение."""
    return create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    """Асинхронный тест-клиент."""
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def mock_data_api_client() -> AsyncMock:
    """Мок клиента Data API."""
    mock = AsyncMock(spec=DataApiClient)
    return mock


@pytest.fixture
def app_with_mocks(
    app: FastAPI,
    mock_data_api_client: AsyncMock,
) -> FastAPI:
    """Приложение с подменёнными зависимостями."""
    app.dependency_overrides[get_data_api_client] = lambda: mock_data_api_client
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def client_with_mocks(app_with_mocks: FastAPI) -> AsyncClient:
    """Клиент с моками."""
    async with AsyncClient(
        app=app_with_mocks,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client
