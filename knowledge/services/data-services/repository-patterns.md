# Паттерны репозиториев

> **Назначение**: Паттерны доступа к данным через репозитории.

---

## Базовый репозиторий

```python
"""Базовый репозиторий."""

from typing import Generic, TypeVar, Sequence
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.domain.entities.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий для CRUD операций."""

    def __init__(self, session: AsyncSession, model: type[ModelType]):
        """
        Инициализация репозитория.

        Args:
            session: Сессия SQLAlchemy.
            model: Класс модели.
        """
        self.session = session
        self.model = model

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """
        Получить запись по ID.

        Args:
            id: Идентификатор записи.

        Returns:
            Найденная запись или None.
        """
        return await self.session.get(self.model, id)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        """
        Получить все записи с пагинацией.

        Args:
            offset: Смещение.
            limit: Лимит записей.

        Returns:
            Список записей.
        """
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        """
        Создать запись.

        Args:
            **kwargs: Поля записи.

        Returns:
            Созданная запись.
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs) -> ModelType | None:
        """
        Обновить запись.

        Args:
            id: Идентификатор записи.
            **kwargs: Поля для обновления.

        Returns:
            Обновлённая запись или None.
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
        Удалить запись.

        Args:
            id: Идентификатор записи.

        Returns:
            True если удалено, False если не найдено.
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def count(self) -> int:
        """
        Подсчитать количество записей.

        Returns:
            Количество записей.
        """
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def exists(self, id: UUID) -> bool:
        """
        Проверить существование записи.

        Args:
            id: Идентификатор записи.

        Returns:
            True если существует.
        """
        instance = await self.get_by_id(id)
        return instance is not None
```

---

## Репозиторий сущности

```python
"""Репозиторий пользователей."""

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.domain.entities.user import User
from {context}_data.infrastructure.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями."""

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория.

        Args:
            session: Сессия SQLAlchemy.
        """
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        """
        Получить пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            Найденный пользователь или None.
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
        Получить активных пользователей.

        Args:
            offset: Смещение.
            limit: Лимит записей.

        Returns:
            Список активных пользователей.
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
        Поиск пользователей по имени.

        Args:
            name_query: Поисковый запрос.

        Returns:
            Список найденных пользователей.
        """
        query = select(User).where(User.name.ilike(f"%{name_query}%"))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def deactivate(self, user_id: UUID) -> bool:
        """
        Деактивировать пользователя.

        Args:
            user_id: ID пользователя.

        Returns:
            True если успешно.
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return False

        user.is_active = False
        await self.session.flush()
        return True
```

---

## Репозиторий со связями

```python
"""Репозиторий заказов со связями."""

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.domain.entities.order import Order
from {context}_data.infrastructure.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Репозиторий заказов."""

    def __init__(self, session: AsyncSession):
        """Инициализация."""
        super().__init__(session, Order)

    async def get_with_items(self, order_id: UUID) -> Order | None:
        """
        Получить заказ с товарами.

        Args:
            order_id: ID заказа.

        Returns:
            Заказ с загруженными товарами.
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
        Получить заказы пользователя.

        Args:
            user_id: ID пользователя.
            offset: Смещение.
            limit: Лимит.

        Returns:
            Список заказов.
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
"""Зависимости API."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.infrastructure.database.connection import get_session
from {context}_data.infrastructure.repositories.user_repository import UserRepository
from {context}_data.infrastructure.repositories.order_repository import OrderRepository


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    """
    Получить репозиторий пользователей.

    Args:
        session: Сессия БД.

    Returns:
        Репозиторий пользователей.
    """
    return UserRepository(session)


async def get_order_repository(
    session: AsyncSession = Depends(get_session),
) -> OrderRepository:
    """
    Получить репозиторий заказов.

    Args:
        session: Сессия БД.

    Returns:
        Репозиторий заказов.
    """
    return OrderRepository(session)
```

---

## Использование в роутах

```python
"""Роуты пользователей."""

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
    """Создать пользователя."""
    # Проверка уникальности email
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
    """Получить пользователя."""
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return UserResponse.model_validate(user)
```

---

## Паттерн Unit of Work (опционально)

```python
"""Unit of Work для транзакций."""

from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.infrastructure.repositories.user_repository import UserRepository
from {context}_data.infrastructure.repositories.order_repository import OrderRepository


class UnitOfWork:
    """Unit of Work для управления транзакциями."""

    def __init__(self, session: AsyncSession):
        """Инициализация."""
        self.session = session
        self.users = UserRepository(session)
        self.orders = OrderRepository(session)

    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Откатить транзакцию."""
        await self.session.rollback()
```

---

## Чек-лист

- [ ] BaseRepository реализован с CRUD
- [ ] Репозитории сущностей наследуют BaseRepository
- [ ] Сложные запросы в отдельных методах
- [ ] selectinload для связей
- [ ] DI через Depends
- [ ] Транзакции управляются на уровне сессии
