"""
Фикстуры для тестов {context}_worker.

Общие фикстуры для тестирования воркера.
"""

import pytest
from unittest.mock import AsyncMock

from src.tasks.base import BaseTask


@pytest.fixture
def mock_api_client() -> AsyncMock:
    """Мок API клиента."""
    mock = AsyncMock()
    return mock


class TestTask(BaseTask):
    """Тестовая задача."""

    name = "test_task"
    interval_seconds = 60

    async def execute(self) -> None:
        """Выполнение тестовой задачи."""
        pass


@pytest.fixture
def test_task() -> TestTask:
    """Экземпляр тестовой задачи."""
    return TestTask()
