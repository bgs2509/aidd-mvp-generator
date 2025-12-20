"""
Генерация и управление request_id.

Утилиты для трассировки запросов между сервисами.
"""

import uuid
from contextvars import ContextVar
from typing import Callable


# === Context Variable для request_id ===

_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


# === Константы ===

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"


def generate_request_id() -> str:
    """
    Сгенерировать уникальный request_id.

    Returns:
        UUID4 строка без дефисов.
    """
    return uuid.uuid4().hex


def get_request_id() -> str | None:
    """
    Получить текущий request_id из контекста.

    Returns:
        Request ID или None.
    """
    return _request_id_ctx.get()


def set_request_id(request_id: str | None) -> None:
    """
    Установить request_id в контексте.

    Args:
        request_id: ID запроса.
    """
    _request_id_ctx.set(request_id)


def get_or_create_request_id() -> str:
    """
    Получить request_id или создать новый.

    Returns:
        Существующий или новый request_id.
    """
    request_id = get_request_id()
    if request_id is None:
        request_id = generate_request_id()
        set_request_id(request_id)
    return request_id


class RequestIdContext:
    """
    Контекстный менеджер для request_id.

    Устанавливает request_id на время выполнения блока,
    затем восстанавливает предыдущее значение.

    Example:
        ```python
        with RequestIdContext("abc123"):
            # request_id == "abc123"
            do_something()
        # request_id восстановлен
        ```
    """

    def __init__(self, request_id: str | None = None) -> None:
        """
        Инициализировать контекст.

        Args:
            request_id: ID запроса (генерируется если None).
        """
        self.request_id = request_id or generate_request_id()
        self._token = None

    def __enter__(self) -> str:
        """Войти в контекст."""
        self._token = _request_id_ctx.set(self.request_id)
        return self.request_id

    def __exit__(self, *args) -> None:
        """Выйти из контекста."""
        if self._token is not None:
            _request_id_ctx.reset(self._token)


def with_request_id(func: Callable) -> Callable:
    """
    Декоратор для автоматического создания request_id.

    Создаёт новый request_id если его нет в контексте.

    Args:
        func: Декорируемая функция.

    Returns:
        Обёрнутая функция.

    Example:
        ```python
        @with_request_id
        def process_data():
            request_id = get_request_id()  # Всегда не None
            ...
        ```
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request_id = get_request_id()
        if request_id is None:
            with RequestIdContext():
                return func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


async def async_with_request_id(func: Callable) -> Callable:
    """
    Асинхронный декоратор для request_id.

    Args:
        func: Асинхронная функция.

    Returns:
        Обёрнутая функция.
    """
    import functools

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        request_id = get_request_id()
        if request_id is None:
            with RequestIdContext():
                return await func(*args, **kwargs)
        return await func(*args, **kwargs)

    return wrapper


# === Утилиты для HTTP заголовков ===

def extract_request_id_from_headers(
    headers: dict[str, str],
    generate_if_missing: bool = True,
) -> str | None:
    """
    Извлечь request_id из HTTP заголовков.

    Проверяет оба заголовка: X-Request-ID и X-Correlation-ID.

    Args:
        headers: Словарь заголовков (case-insensitive).
        generate_if_missing: Генерировать если отсутствует.

    Returns:
        Request ID или None.
    """
    # Нормализуем ключи к нижнему регистру
    normalized = {k.lower(): v for k, v in headers.items()}

    # Проверяем оба заголовка
    request_id = (
        normalized.get(REQUEST_ID_HEADER.lower())
        or normalized.get(CORRELATION_ID_HEADER.lower())
    )

    if request_id is None and generate_if_missing:
        request_id = generate_request_id()

    return request_id


def create_request_id_headers(request_id: str | None = None) -> dict[str, str]:
    """
    Создать заголовки с request_id.

    Args:
        request_id: ID запроса (из контекста если None).

    Returns:
        Словарь с заголовком X-Request-ID.
    """
    if request_id is None:
        request_id = get_or_create_request_id()

    return {REQUEST_ID_HEADER: request_id}
