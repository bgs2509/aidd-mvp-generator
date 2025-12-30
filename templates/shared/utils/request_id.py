"""
Генерация и управление трассировкой запросов.

Утилиты для сквозной трассировки запросов между сервисами
по принципам Log-Driven Design:
- request_id: уникальный ID текущей операции в сервисе
- correlation_id: ID изначального запроса от клиента (не меняется между сервисами)
- causation_id: ID события, которое вызвало текущее действие
- user_id: ID аутентифицированного пользователя (если есть)
"""

import uuid
from contextvars import ContextVar
from typing import Callable


# === Context Variables для трассировки ===

_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
_correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_causation_id_ctx: ContextVar[str | None] = ContextVar("causation_id", default=None)
_user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)


# === Константы ===

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"
CAUSATION_ID_HEADER = "X-Causation-ID"


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


# === Функции для correlation_id ===


def get_correlation_id() -> str | None:
    """
    Получить текущий correlation_id из контекста.

    Returns:
        Correlation ID или None.
    """
    return _correlation_id_ctx.get()


def set_correlation_id(correlation_id: str | None) -> None:
    """
    Установить correlation_id в контексте.

    Args:
        correlation_id: ID корреляции.
    """
    _correlation_id_ctx.set(correlation_id)


def get_or_create_correlation_id() -> str:
    """
    Получить correlation_id или создать новый.

    Returns:
        Существующий или новый correlation_id.
    """
    correlation_id = get_correlation_id()
    if correlation_id is None:
        correlation_id = generate_request_id()
        set_correlation_id(correlation_id)
    return correlation_id


# === Функции для causation_id ===


def get_causation_id() -> str | None:
    """
    Получить текущий causation_id из контекста.

    Returns:
        Causation ID или None.
    """
    return _causation_id_ctx.get()


def set_causation_id(causation_id: str | None) -> None:
    """
    Установить causation_id в контексте.

    Args:
        causation_id: ID причины.
    """
    _causation_id_ctx.set(causation_id)


# === Функции для user_id ===


def get_user_id() -> str | None:
    """
    Получить текущий user_id из контекста.

    Returns:
        User ID или None если пользователь не аутентифицирован.
    """
    return _user_id_ctx.get()


def set_user_id(user_id: str | None) -> None:
    """
    Установить user_id в контексте.

    Вызывается после успешной аутентификации пользователя.

    Args:
        user_id: ID пользователя.
    """
    _user_id_ctx.set(user_id)


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

    Note:
        Для полной трассировки используйте create_tracing_headers().
    """
    if request_id is None:
        request_id = get_or_create_request_id()

    return {REQUEST_ID_HEADER: request_id}


def extract_tracing_from_headers(
    headers: dict[str, str],
    generate_if_missing: bool = True,
) -> dict[str, str | None]:
    """
    Извлечь все ID трассировки из HTTP заголовков.

    Args:
        headers: Словарь заголовков (case-insensitive).
        generate_if_missing: Генерировать request_id если отсутствует.

    Returns:
        Словарь с request_id, correlation_id, causation_id.
    """
    normalized = {k.lower(): v for k, v in headers.items()}

    request_id = normalized.get(REQUEST_ID_HEADER.lower())
    correlation_id = normalized.get(CORRELATION_ID_HEADER.lower())
    causation_id = normalized.get(CAUSATION_ID_HEADER.lower())

    if request_id is None and generate_if_missing:
        request_id = generate_request_id()

    # Если correlation_id не передан, используем request_id
    if correlation_id is None and request_id:
        correlation_id = request_id

    return {
        "request_id": request_id,
        "correlation_id": correlation_id,
        "causation_id": causation_id,
    }


def create_tracing_headers() -> dict[str, str]:
    """
    Создать заголовки для полной трассировки исходящего запроса.

    При исходящем вызове текущий request_id передаётся как causation_id,
    чтобы следующий сервис знал, какое событие вызвало его работу.

    Returns:
        Словарь с заголовками X-Request-ID, X-Correlation-ID, X-Causation-ID.

    Example:
        ```python
        # В HTTP клиенте:
        headers = create_tracing_headers()
        response = await client.get("/api/v1/users", headers=headers)
        ```
    """
    headers = {}

    # Correlation ID передаём без изменений
    correlation_id = get_correlation_id()
    if correlation_id:
        headers[CORRELATION_ID_HEADER] = correlation_id

    # Текущий request_id становится causation_id для следующего сервиса
    current_request_id = get_request_id()
    if current_request_id:
        headers[CAUSATION_ID_HEADER] = current_request_id

    # Генерируем новый request_id для исходящего запроса
    # (принимающий сервис может использовать его или сгенерировать свой)
    headers[REQUEST_ID_HEADER] = generate_request_id()

    return headers


def setup_tracing_context(
    request_id: str | None = None,
    correlation_id: str | None = None,
    causation_id: str | None = None,
    user_id: str | None = None,
) -> None:
    """
    Установить полный контекст трассировки.

    Используется в middleware при получении входящего запроса.

    Args:
        request_id: ID текущего запроса (генерируется если None).
        correlation_id: ID корреляции (используется request_id если None).
        causation_id: ID причины (может быть None).
        user_id: ID пользователя (может быть None для анонимных запросов).

    Example:
        ```python
        # В FastAPI middleware:
        tracing = extract_tracing_from_headers(dict(request.headers))
        setup_tracing_context(**tracing)

        # После аутентификации:
        set_user_id(str(current_user.id))
        ```
    """
    if request_id is None:
        request_id = generate_request_id()

    set_request_id(request_id)
    set_correlation_id(correlation_id or request_id)
    set_causation_id(causation_id)
    set_user_id(user_id)


def clear_tracing_context() -> None:
    """
    Очистить контекст трассировки.

    Используется в middleware после обработки запроса.
    """
    set_request_id(None)
    set_correlation_id(None)
    set_causation_id(None)
    set_user_id(None)
