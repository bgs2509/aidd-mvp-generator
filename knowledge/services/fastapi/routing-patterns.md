# Паттерны маршрутизации FastAPI

> **Назначение**: Организация роутеров и эндпоинтов.

---

## Структура роутеров

```
api/
├── __init__.py
├── dependencies.py      # Общие зависимости
└── v1/
    ├── __init__.py
    ├── router.py        # Главный роутер v1
    ├── user_routes.py   # Роуты пользователей
    └── order_routes.py  # Роуты заказов
```

---

## Главный роутер

```python
"""Главный роутер API v1."""

from fastapi import APIRouter

from {context}_api.api.v1 import user_routes, order_routes

api_router = APIRouter()

# Подключение роутеров сущностей
api_router.include_router(
    user_routes.router,
    prefix="/users",
    tags=["users"],
)

api_router.include_router(
    order_routes.router,
    prefix="/orders",
    tags=["orders"],
)
```

---

## Роутер сущности

```python
"""Роуты пользователей."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from {context}_api.api.dependencies import get_user_service
from {context}_api.application.services.user_service import UserService
from {context}_api.schemas.user_schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Создать нового пользователя.

    Args:
        data: Данные для создания.
        service: Сервис пользователей.

    Returns:
        Созданный пользователь.
    """
    return await service.create_user(data)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Получить пользователя",
)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Получить пользователя по ID.

    Args:
        user_id: ID пользователя.
        service: Сервис пользователей.

    Returns:
        Данные пользователя.

    Raises:
        HTTPException: Если пользователь не найден.
    """
    user = await service.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user


@router.get(
    "",
    response_model=UserListResponse,
    summary="Список пользователей",
)
async def list_users(
    page: int = 1,
    page_size: int = 20,
    service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """
    Получить список пользователей с пагинацией.

    Args:
        page: Номер страницы.
        page_size: Размер страницы.
        service: Сервис пользователей.

    Returns:
        Список пользователей.
    """
    return await service.list_users(page=page, page_size=page_size)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Обновить пользователя",
)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Обновить данные пользователя.

    Args:
        user_id: ID пользователя.
        data: Данные для обновления.
        service: Сервис пользователей.

    Returns:
        Обновлённый пользователь.
    """
    return await service.update_user(user_id, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
)
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> None:
    """
    Удалить пользователя.

    Args:
        user_id: ID пользователя.
        service: Сервис пользователей.
    """
    await service.delete_user(user_id)
```

---

## Именование путей

```
CRUD операции:
POST   /api/v1/{entities}           → Создать
GET    /api/v1/{entities}           → Список
GET    /api/v1/{entities}/{id}      → Получить
PUT    /api/v1/{entities}/{id}      → Обновить
DELETE /api/v1/{entities}/{id}      → Удалить

Вложенные ресурсы:
GET    /api/v1/users/{id}/orders    → Заказы пользователя

Действия:
POST   /api/v1/orders/{id}/cancel   → Отменить заказ
POST   /api/v1/orders/{id}/confirm  → Подтвердить заказ
```

---

## Правила

| Элемент | Формат | Пример |
|---------|--------|--------|
| Путь | kebab-case, мн.ч. | `/user-profiles` |
| Path параметр | snake_case | `{user_id}` |
| Query параметр | snake_case | `?page_size=20` |
| Тег | lowercase | `users` |

---

## Версионирование

```python
# api/v1/router.py
api_v1_router = APIRouter(prefix="/api/v1")

# api/v2/router.py
api_v2_router = APIRouter(prefix="/api/v2")

# main.py
app.include_router(api_v1_router)
app.include_router(api_v2_router)
```
