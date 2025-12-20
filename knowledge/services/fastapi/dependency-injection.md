# Внедрение зависимостей FastAPI

> **Назначение**: Паттерны DI в FastAPI.

---

## Базовая структура

```python
"""Зависимости API."""

from fastapi import Depends, Request

from {context}_api.application.services.user_service import UserService
from {context}_api.infrastructure.http.data_api_client import DataApiClient


def get_http_client(request: Request) -> DataApiClient:
    """
    Получить HTTP клиент из состояния приложения.

    Args:
        request: HTTP запрос.

    Returns:
        Настроенный HTTP клиент.
    """
    return DataApiClient(request.app.state.http_client)


def get_user_service(
    data_client: DataApiClient = Depends(get_http_client),
) -> UserService:
    """
    Создать сервис пользователей.

    Args:
        data_client: HTTP клиент для Data API.

    Returns:
        Экземпляр сервиса.
    """
    return UserService(data_client)


def get_order_service(
    data_client: DataApiClient = Depends(get_http_client),
) -> OrderService:
    """
    Создать сервис заказов.

    Args:
        data_client: HTTP клиент для Data API.

    Returns:
        Экземпляр сервиса.
    """
    return OrderService(data_client)
```

---

## Граф зависимостей

```
Request
    │
    ▼
get_http_client()
    │
    ├───────────────────┬───────────────────┐
    ▼                   ▼                   ▼
get_user_service() get_order_service() get_restaurant_service()
    │                   │                   │
    ▼                   ▼                   ▼
UserRoutes          OrderRoutes         RestaurantRoutes
```

---

## Request-scoped зависимости

```python
"""Зависимости с временем жизни запроса."""

from contextlib import asynccontextmanager
from fastapi import Depends, Request


async def get_request_id(request: Request) -> str:
    """
    Получить ID запроса.

    Args:
        request: HTTP запрос.

    Returns:
        ID запроса.
    """
    return getattr(request.state, "request_id", "unknown")


async def get_current_user(
    request: Request,
    user_service: UserService = Depends(get_user_service),
) -> User:
    """
    Получить текущего пользователя из токена.

    Args:
        request: HTTP запрос.
        user_service: Сервис пользователей.

    Returns:
        Текущий пользователь.

    Raises:
        HTTPException: Если токен невалидный.
    """
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = decode_token(token)
    return await user_service.get_user(user_id)
```

---

## Параметризованные зависимости

```python
"""Зависимости с параметрами."""

from functools import lru_cache


class PaginationParams:
    """Параметры пагинации."""

    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100,
    ):
        """
        Инициализация параметров.

        Args:
            page: Номер страницы.
            page_size: Размер страницы.
            max_page_size: Максимальный размер.
        """
        self.page = max(1, page)
        self.page_size = min(page_size, max_page_size)
        self.offset = (self.page - 1) * self.page_size


def pagination_params(
    page: int = 1,
    page_size: int = 20,
) -> PaginationParams:
    """
    Создать параметры пагинации.

    Args:
        page: Номер страницы.
        page_size: Размер страницы.

    Returns:
        Параметры пагинации.
    """
    return PaginationParams(page=page, page_size=page_size)


# Использование
@router.get("")
async def list_items(
    pagination: PaginationParams = Depends(pagination_params),
):
    """Список с пагинацией."""
    return await service.list(
        offset=pagination.offset,
        limit=pagination.page_size,
    )
```

---

## Фабрика зависимостей

```python
"""Фабрика для создания зависимостей с параметрами."""

def get_service_with_config(service_class, config_key: str):
    """
    Создать фабрику сервиса с конфигурацией.

    Args:
        service_class: Класс сервиса.
        config_key: Ключ конфигурации.

    Returns:
        Функция-зависимость.
    """
    def dependency(
        data_client: DataApiClient = Depends(get_http_client),
    ):
        config = get_config(config_key)
        return service_class(data_client, config)

    return dependency


# Использование
get_order_service = get_service_with_config(OrderService, "orders")
```

---

## Кэширование зависимостей

```python
"""Кэширование на уровне приложения."""

from functools import lru_cache


@lru_cache
def get_settings():
    """
    Получить настройки (кэшируется).

    Returns:
        Объект настроек.
    """
    return Settings()


# Использование в роутах
@router.get("/info")
async def get_info(
    settings = Depends(get_settings),
):
    """Информация о сервисе."""
    return {"service": settings.service_name}
```

---

## Антипаттерны

```python
# ❌ ПЛОХО: Создание клиента в каждом запросе
def get_client():
    return httpx.AsyncClient()  # Утечка ресурсов!

# ✅ ХОРОШО: Использование состояния приложения
def get_client(request: Request):
    return request.app.state.http_client


# ❌ ПЛОХО: Глобальные переменные
_service = None

def get_service():
    global _service
    if _service is None:
        _service = MyService()
    return _service

# ✅ ХОРОШО: Depends цепочка
def get_service(client = Depends(get_client)):
    return MyService(client)
```
