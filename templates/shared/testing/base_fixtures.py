"""
Базовые pytest фикстуры.

Переиспользуемые фикстуры для тестирования сервисов.
"""

from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest


# === Моки для настроек ===

@pytest.fixture
def mock_settings() -> MagicMock:
    """
    Мок для настроек приложения.

    Использование:
        ```python
        def test_something(mock_settings):
            mock_settings.debug = True
            mock_settings.database_url = "postgresql://test"
            ...
        ```
    """
    settings = MagicMock()
    settings.debug = True
    settings.environment = "test"
    settings.log_level = "DEBUG"
    settings.service_name = "test-service"
    return settings


# === Моки для HTTP клиентов ===

@pytest.fixture
def mock_http_client() -> AsyncMock:
    """
    Мок для HTTP клиента.

    Использование:
        ```python
        def test_api_call(mock_http_client):
            mock_http_client._get.return_value = {"id": "123", "name": "Test"}
            result = await service.get_item("123")
            mock_http_client._get.assert_called_once_with("/items/123")
        ```
    """
    client = AsyncMock()

    # Настройка методов
    client._get = AsyncMock(return_value={})
    client._post = AsyncMock(return_value={})
    client._put = AsyncMock(return_value={})
    client._patch = AsyncMock(return_value={})
    client._delete = AsyncMock(return_value=None)
    client.close = AsyncMock()
    client.health_check = AsyncMock(return_value=True)

    return client


# === Моки для баз данных ===

@pytest.fixture
def mock_database() -> MagicMock:
    """
    Мок для подключения к базе данных.

    Использование:
        ```python
        def test_repository(mock_database):
            mock_database.execute.return_value = MagicMock(
                scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
            )
        ```
    """
    db = MagicMock()

    # Настройка для SQLAlchemy async session
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    db.close = AsyncMock()

    # Настройка для контекстного менеджера
    db.__aenter__ = AsyncMock(return_value=db)
    db.__aexit__ = AsyncMock(return_value=None)

    return db


# === Утилиты для асинхронных моков ===

def async_mock(return_value: Any = None) -> AsyncMock:
    """
    Создать AsyncMock с заданным возвращаемым значением.

    Args:
        return_value: Значение, которое вернёт мок.

    Returns:
        Настроенный AsyncMock.

    Использование:
        ```python
        service.get_user = async_mock({"id": "123", "name": "John"})
        result = await service.get_user("123")
        assert result["name"] == "John"
        ```
    """
    return AsyncMock(return_value=return_value)


def create_test_response(
    data: dict[str, Any] | list | None = None,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> MagicMock:
    """
    Создать мок HTTP ответа.

    Args:
        data: JSON данные ответа.
        status_code: HTTP статус код.
        headers: Заголовки ответа.

    Returns:
        Мок ответа с настроенными атрибутами.

    Использование:
        ```python
        response = create_test_response(
            data={"items": [], "total": 0},
            status_code=200,
        )
        mock_client._request.return_value = response
        ```
    """
    response = MagicMock()
    response.status_code = status_code
    response.is_success = 200 <= status_code < 300
    response.json = MagicMock(return_value=data or {})
    response.text = str(data) if data else ""
    response.headers = headers or {"content-type": "application/json"}
    response.elapsed = MagicMock(total_seconds=MagicMock(return_value=0.1))
    return response


# === Фикстуры для ID ===

@pytest.fixture
def test_uuid() -> str:
    """Сгенерировать тестовый UUID."""
    return str(uuid4())


@pytest.fixture
def test_uuids() -> list[str]:
    """Сгенерировать список тестовых UUID."""
    return [str(uuid4()) for _ in range(5)]


# === Фикстуры для временных данных ===

@pytest.fixture
def frozen_time():
    """
    Заморозить время для тестов.

    Требует установки: pip install freezegun

    Использование:
        ```python
        def test_timestamp(frozen_time):
            with frozen_time("2024-01-15 12:00:00"):
                result = get_current_time()
                assert result.hour == 12
        ```
    """
    try:
        from freezegun import freeze_time
        return freeze_time
    except ImportError:
        pytest.skip("freezegun не установлен")


# === Фикстуры для переменных окружения ===

@pytest.fixture
def mock_env_vars():
    """
    Контекстный менеджер для мока переменных окружения.

    Использование:
        ```python
        def test_config(mock_env_vars):
            with mock_env_vars(DATABASE_URL="postgresql://test"):
                config = Settings()
                assert "test" in config.database_url
        ```
    """
    import os
    from contextlib import contextmanager

    @contextmanager
    def _mock_env(**env_vars):
        original = {}
        for key, value in env_vars.items():
            original[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            yield
        finally:
            for key, orig_value in original.items():
                if orig_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = orig_value

    return _mock_env


# === Фикстуры для логирования ===

@pytest.fixture
def capture_logs():
    """
    Захватить логи для проверки.

    Использование:
        ```python
        def test_logging(capture_logs):
            logs = capture_logs()
            do_something_that_logs()
            assert any("error" in log.lower() for log in logs)
        ```
    """
    import structlog

    captured = []

    def capture_processor(logger, method_name, event_dict):
        captured.append(event_dict.copy())
        return event_dict

    original_processors = structlog.get_config().get("processors", [])

    structlog.configure(
        processors=[capture_processor] + original_processors,
    )

    def get_logs():
        return captured

    return get_logs


# === Асинхронные фикстуры ===

@pytest.fixture
async def async_generator_mock() -> AsyncGenerator[Any, None]:
    """
    Мок для асинхронных генераторов.

    Использование в тестах, где нужен async generator.
    """
    yield MagicMock()


# === Хелперы для тестов ===

class TestHelpers:
    """Набор хелперов для тестов."""

    @staticmethod
    def assert_dict_contains(actual: dict, expected: dict) -> None:
        """
        Проверить, что словарь содержит ожидаемые ключи/значения.

        Args:
            actual: Фактический словарь.
            expected: Ожидаемые ключи/значения.
        """
        for key, value in expected.items():
            assert key in actual, f"Ключ '{key}' не найден в {actual}"
            assert actual[key] == value, (
                f"Значение для '{key}': ожидалось {value}, получено {actual[key]}"
            )

    @staticmethod
    def assert_called_with_any_of(
        mock: MagicMock | AsyncMock,
        *expected_calls,
    ) -> None:
        """
        Проверить, что мок был вызван с одним из ожидаемых наборов аргументов.

        Args:
            mock: Мок для проверки.
            *expected_calls: Ожидаемые вызовы.
        """
        actual_calls = mock.call_args_list
        for expected in expected_calls:
            if expected in actual_calls:
                return
        raise AssertionError(
            f"Ни один из ожидаемых вызовов {expected_calls} "
            f"не найден в {actual_calls}"
        )


@pytest.fixture
def test_helpers() -> TestHelpers:
    """Хелперы для тестов."""
    return TestHelpers()
