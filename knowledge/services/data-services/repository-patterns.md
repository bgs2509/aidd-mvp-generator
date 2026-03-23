# Repository Patterns

> **Purpose**: Data access patterns using repositories.

---

## Base Repository

```python
"""Base repository."""

from typing import Generic, TypeVar, Sequence
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.domain.entities.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository for CRUD operations."""

    def __init__(self, session: AsyncSession, model: type[ModelType]):
        """
        Initialize repository.

        Args:
            session: SQLAlchemy session.
            model: Model class.
        """
        self.session = session
        self.model = model

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """
        Get record by ID.

        Args:
            id: Record identifier.

        Returns:
            Found record or None.
        """
        return await self.session.get(self.model, id)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        """
        Get all records with pagination.

        Args:
            offset: Offset.
            limit: Record limit.

        Returns:
            List of records.
        """
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        """
        Create a record.

        Args:
            **kwargs: Record fields.

        Returns:
            Created record.
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs) -> ModelType | None:
        """
        Update a record.

        Args:
            id: Record identifier.
            **kwargs: Fields to update.

        Returns:
            Updated record or None.
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """
        Delete a record.

        Args:
            id: Record identifier.

        Returns:
            True if deleted, False if not found.
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def count(self) -> int:
        """
        Count records.

        Returns:
            Number of records.
        """
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def exists(self, id: UUID) -> bool:
        """
        Check if record exists.

        Args:
            id: Record identifier.

        Returns:
            True if exists.
        """
        instance = await self.get_by_id(id)
        return instance is not None
```

---

## Entity Repository

```python
"""User repository."""

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.domain.entities.user import User
from {context}_data.infrastructure.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for working with users."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository.

        Args:
            session: SQLAlchemy session.
        """
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email.

        Args:
            email: User email.

        Returns:
            Found user or None.
        """
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_active_users(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[User]:
        """
        Get active users.

        Args:
            offset: Offset.
            limit: Record limit.

        Returns:
            List of active users.
        """
        query = (
            select(User)
            .where(User.is_active == True)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search_by_name(self, name_query: str) -> Sequence[User]:
        """
        Search users by name.

        Args:
            name_query: Search query.

        Returns:
            List of found users.
        """
        query = select(User).where(User.name.ilike(f"%{name_query}%"))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def deactivate(self, user_id: UUID) -> bool:
        """
        Deactivate a user.

        Args:
            user_id: User ID.

        Returns:
            True if successful.
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return False

        user.is_active = False
        await self.session.flush()
        return True
```

---

## Repository with Relations

```python
"""Order repository with relations."""

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.domain.entities.order import Order
from {context}_data.infrastructure.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Order repository."""

    def __init__(self, session: AsyncSession):
        """Initialize."""
        super().__init__(session, Order)

    async def get_with_items(self, order_id: UUID) -> Order | None:
        """
        Get order with items.

        Args:
            order_id: Order ID.

        Returns:
            Order with loaded items.
        """
        query = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_orders(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[Order]:
        """
        Get user orders.

        Args:
            user_id: User ID.
            offset: Offset.
            limit: Limit.

        Returns:
            List of orders.
        """
        query = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
```

---

## Dependency Injection

```python
"""API dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.infrastructure.database.connection import get_session
from {context}_data.infrastructure.repositories.user_repository import UserRepository
from {context}_data.infrastructure.repositories.order_repository import OrderRepository


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    """
    Get user repository.

    Args:
        session: Database session.

    Returns:
        User repository.
    """
    return UserRepository(session)


async def get_order_repository(
    session: AsyncSession = Depends(get_session),
) -> OrderRepository:
    """
    Get order repository.

    Args:
        session: Database session.

    Returns:
        Order repository.
    """
    return OrderRepository(session)
```

---

## Usage in Routes

```python
"""User routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from {context}_data.api.dependencies import get_user_repository
from {context}_data.infrastructure.repositories.user_repository import UserRepository
from {context}_data.schemas.user_schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    repo: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Create a user."""
    # Check email uniqueness
    existing = await repo.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email {data.email} already exists",
        )

    user = await repo.create(**data.model_dump())
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    repo: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Get a user."""
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return UserResponse.model_validate(user)
```

---

## Unit of Work Pattern (optional)

```python
"""Unit of Work for transactions."""

from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.infrastructure.repositories.user_repository import UserRepository
from {context}_data.infrastructure.repositories.order_repository import OrderRepository


class UnitOfWork:
    """Unit of Work for transaction management."""

    def __init__(self, session: AsyncSession):
        """Initialize."""
        self.session = session
        self.users = UserRepository(session)
        self.orders = OrderRepository(session)

    async def commit(self) -> None:
        """Commit transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback transaction."""
        await self.session.rollback()
```

---

## Checklist

- [ ] BaseRepository implemented with CRUD
- [ ] Entity repositories inherit BaseRepository
- [ ] Complex queries in separate methods
- [ ] selectinload for relations
- [ ] DI via Depends
- [ ] Transactions managed at session level
