"""
Middleware для логирования HTTP запросов по Log-Driven Design.

Обеспечивает:
- Полное логирование входящих запросов с path_params
- Установку контекста трассировки (request_id, correlation_id, causation_id, user_id)
- Логирование auth_context после аутентификации
- Логирование rate_limit информации
- Логирование ответов с duration_ms и error_code
- Извлечение версии API из пути
"""

import re
import time
from typing import Any, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match

from shared.utils.request_id import (
    extract_tracing_from_headers,
    setup_tracing_context,
    clear_tracing_context,
    get_request_id,
    set_user_id,
)
from shared.utils.log_helpers import get_error_code_from_status


logger = structlog.get_logger()


# Паттерн для извлечения версии API из пути
API_VERSION_PATTERN = re.compile(r"/api/(v\d+)/")

# Заголовки для rate limiting
RATE_LIMIT_REMAINING_HEADER = "X-RateLimit-Remaining"
RATE_LIMIT_LIMIT_HEADER = "X-RateLimit-Limit"


def extract_api_version(path: str) -> str | None:
    """
    Извлечь версию API из пути.

    Args:
        path: URL путь.

    Returns:
        Версия API (v1, v2) или None.
    """
    match = API_VERSION_PATTERN.search(path)
    return match.group(1) if match else None


def extract_path_params(request: Request) -> dict[str, Any] | None:
    """
    Извлечь path параметры из запроса.

    Использует роутинг FastAPI для определения параметров.

    Args:
        request: HTTP запрос.

    Returns:
        Словарь path параметров или None.

    Example:
        Для роута /api/v1/orders/{order_id} и пути /api/v1/orders/abc-123
        вернёт {"order_id": "abc-123"}
    """
    # Получаем app из scope
    app = request.scope.get("app")
    if not app:
        return None

    # Проходим по всем роутам и ищем совпадение
    for route in app.routes:
        match, scope = route.matches(request.scope)
        if match == Match.FULL:
            path_params = scope.get("path_params", {})
            if path_params:
                return dict(path_params)

    return None


def extract_rate_limit_from_headers(headers: dict[str, str]) -> tuple[int | None, int | None]:
    """
    Извлечь информацию о rate limit из заголовков.

    Args:
        headers: Заголовки ответа.

    Returns:
        Tuple (remaining, limit) или (None, None).
    """
    remaining = headers.get(RATE_LIMIT_REMAINING_HEADER.lower())
    limit = headers.get(RATE_LIMIT_LIMIT_HEADER.lower())

    try:
        remaining_int = int(remaining) if remaining else None
        limit_int = int(limit) if limit else None
        return remaining_int, limit_int
    except ValueError:
        return None, None


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для структурированного логирования запросов.

    Реализует принципы Log-Driven Design:
    - Полный контекст запроса при старте (включая path_params)
    - Установка трассировки через ContextVars (включая user_id)
    - Логирование auth_context и rate_limit
    - Логирование завершения с метриками и error_code

    Attributes:
        skip_paths: Пути, которые не логируются (health checks).

    Note:
        Для auth_context: установите request.state.auth_context в auth dependency.
        Для user_id: вызовите set_user_id() после аутентификации.
    """

    def __init__(
        self,
        app,
        skip_paths: set[str] | None = None,
    ):
        """
        Инициализация middleware.

        Args:
            app: ASGI приложение.
            skip_paths: Пути для пропуска логирования.
        """
        super().__init__(app)
        self.skip_paths = skip_paths or {"/health", "/metrics", "/ready"}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Обработать запрос с логированием.

        Args:
            request: HTTP запрос.
            call_next: Следующий обработчик.

        Returns:
            HTTP ответ.
        """
        # Пропуск логирования для служебных эндпоинтов
        if request.url.path in self.skip_paths:
            return await call_next(request)

        # === Установка контекста трассировки ===
        tracing = extract_tracing_from_headers(
            dict(request.headers),
            generate_if_missing=True,
        )
        setup_tracing_context(**tracing)

        # Привязка контекста к structlog
        structlog.contextvars.bind_contextvars(
            request_id=tracing["request_id"],
            correlation_id=tracing["correlation_id"],
        )
        if tracing["causation_id"]:
            structlog.contextvars.bind_contextvars(
                causation_id=tracing["causation_id"],
            )

        # Сохранение request_id в state для использования в handlers
        request.state.request_id = tracing["request_id"]

        # === Логирование начала запроса ===
        start_time = time.perf_counter()

        # Извлечение контекстной информации
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params) if request.query_params else None
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        api_version = extract_api_version(path)
        content_length = request.headers.get("content-length")
        request_body_size = int(content_length) if content_length else None

        # === Извлечение path_params ===
        path_params = extract_path_params(request)

        # Базовые данные для логирования запроса
        log_request_data: dict[str, Any] = {
            "method": method,
            "path": path,
        }

        if query_params:
            log_request_data["query_params"] = query_params

        if path_params:
            log_request_data["path_params"] = path_params

        if request_body_size is not None:
            log_request_data["request_body_size"] = request_body_size

        if client_ip:
            log_request_data["client_ip"] = client_ip

        if user_agent:
            log_request_data["user_agent"] = user_agent

        if api_version:
            log_request_data["api_version"] = api_version

        logger.info("request_started", **log_request_data)

        try:
            # === Выполнение запроса ===
            response = await call_next(request)

            # === Извлечение auth_context после обработки ===
            # auth_context устанавливается в auth dependency через request.state.auth_context
            auth_context: dict[str, Any] | None = getattr(
                request.state, "auth_context", None
            )

            # Если есть user_id в auth_context, устанавливаем в ContextVars
            if auth_context and auth_context.get("user_id"):
                set_user_id(str(auth_context["user_id"]))
                structlog.contextvars.bind_contextvars(
                    user_id=str(auth_context["user_id"])
                )

            # === Логирование завершения ===
            duration_ms = (time.perf_counter() - start_time) * 1000
            response_body_size = response.headers.get("content-length")

            log_data: dict[str, Any] = {
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }

            if response_body_size:
                log_data["response_body_size"] = int(response_body_size)

            # Добавляем auth_context если был установлен
            if auth_context:
                log_data["auth_context"] = auth_context

            # Извлекаем rate limit из заголовков ответа
            rate_remaining, rate_limit = extract_rate_limit_from_headers(
                dict(response.headers)
            )
            if rate_remaining is not None and rate_limit is not None:
                log_data["rate_limit_remaining"] = rate_remaining
                log_data["rate_limit_limit"] = rate_limit

            # === Добавляем error_code для 4xx/5xx ===
            if response.status_code >= 400:
                # Извлекаем error_code из state если был установлен в exception handler
                error_code = getattr(request.state, "error_code", None)
                error_message = getattr(request.state, "error_message", None)

                if error_code:
                    log_data["error_code"] = error_code
                else:
                    # Автоматически определяем по статусу
                    log_data["error_code"] = get_error_code_from_status(
                        response.status_code
                    )

                if error_message:
                    log_data["error_message"] = error_message

            # Уровень логирования зависит от статуса
            if response.status_code >= 500:
                logger.error("request_completed", **log_data)
            elif response.status_code >= 400:
                logger.warning("request_completed", **log_data)
            else:
                logger.info("request_completed", **log_data)

            # Добавление request_id в заголовки ответа
            response.headers["X-Request-ID"] = tracing["request_id"]

            return response

        except Exception as e:
            # === Логирование ошибки ===
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Определяем error_code по типу исключения
            error_code = get_error_code_from_status(500, type(e).__name__)

            logger.exception(
                "request_failed",
                method=method,
                path=path,
                duration_ms=round(duration_ms, 2),
                error=str(e),
                error_type=type(e).__name__,
                error_code=error_code,
            )
            raise

        finally:
            # === Очистка контекста ===
            clear_tracing_context()
            structlog.contextvars.clear_contextvars()
