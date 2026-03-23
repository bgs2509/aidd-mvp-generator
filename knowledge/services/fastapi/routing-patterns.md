# FastAPI Routing Patterns

> **Purpose**: Organizing routers and endpoints.

---

## Router Structure

```
api/
├── __init__.py
├── dependencies.py      # Shared dependencies
└── v1/
    ├── __init__.py
    ├── router.py        # Main v1 router
    ├── user_routes.py   # User routes
    └── order_routes.py  # Order routes
```

---

## Main Router

```python
"""Main API v1 router."""

from fastapi import APIRouter

from {context}_api.api.v1 import user_routes, order_routes

api_router = APIRouter()

# Include entity routers
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

## Entity Router

```python
"""User routes."""

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
    summary="Create user",
)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Create a new user.

    Args:
        data: Creation data.
        service: User service.

    Returns:
        Created user.
    """
    return await service.create_user(data)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user",
)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Get user by ID.

    Args:
        user_id: User ID.
        service: User service.

    Returns:
        User data.

    Raises:
        HTTPException: If user not found.
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
    summary="List users",
)
async def list_users(
    page: int = 1,
    page_size: int = 20,
    service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """
    Get paginated user list.

    Args:
        page: Page number.
        page_size: Page size.
        service: User service.

    Returns:
        User list.
    """
    return await service.list_users(page=page, page_size=page_size)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Update user data.

    Args:
        user_id: User ID.
        data: Update data.
        service: User service.

    Returns:
        Updated user.
    """
    return await service.update_user(user_id, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
)
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> None:
    """
    Delete a user.

    Args:
        user_id: User ID.
        service: User service.
    """
    await service.delete_user(user_id)
```

---

## Path Naming

```
CRUD operations:
POST   /api/v1/{entities}           → Create
GET    /api/v1/{entities}           → List
GET    /api/v1/{entities}/{id}      → Get
PUT    /api/v1/{entities}/{id}      → Update
DELETE /api/v1/{entities}/{id}      → Delete

Nested resources:
GET    /api/v1/users/{id}/orders    → User orders

Actions:
POST   /api/v1/orders/{id}/cancel   → Cancel order
POST   /api/v1/orders/{id}/confirm  → Confirm order
```

---

## Rules

| Element | Format | Example |
|---------|--------|---------|
| Path | kebab-case, plural | `/user-profiles` |
| Path parameter | snake_case | `{user_id}` |
| Query parameter | snake_case | `?page_size=20` |
| Tag | lowercase | `users` |

---

## Versioning

```python
# api/v1/router.py
api_v1_router = APIRouter(prefix="/api/v1")

# api/v2/router.py
api_v2_router = APIRouter(prefix="/api/v2")

# main.py
app.include_router(api_v1_router)
app.include_router(api_v2_router)
```
