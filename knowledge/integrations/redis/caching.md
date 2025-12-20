# Стратегии кэширования Redis

> **Назначение**: Паттерны кэширования с Redis.

---

## Базовый клиент

```python
"""Клиент Redis для кэширования."""

import json
from typing import Any, TypeVar
from datetime import timedelta

import redis.asyncio as redis

from {context}_api.core.config import settings

T = TypeVar("T")


class CacheClient:
    """Клиент для кэширования."""

    def __init__(self, redis_client: redis.Redis):
        """
        Инициализация.

        Args:
            redis_client: Экземпляр Redis клиента.
        """
        self.redis = redis_client
        self.default_ttl = timedelta(minutes=5)

    async def get(self, key: str) -> Any | None:
        """
        Получить значение из кэша.

        Args:
            key: Ключ кэша.

        Returns:
            Значение или None.
        """
        data = await self.redis.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: timedelta | None = None,
    ) -> None:
        """
        Сохранить значение в кэш.

        Args:
            key: Ключ кэша.
            value: Значение для сохранения.
            ttl: Время жизни.
        """
        ttl = ttl or self.default_ttl
        data = json.dumps(value, default=str)
        await self.redis.set(key, data, ex=int(ttl.total_seconds()))

    async def delete(self, key: str) -> None:
        """
        Удалить ключ из кэша.

        Args:
            key: Ключ для удаления.
        """
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> int:
        """
        Удалить ключи по паттерну.

        Args:
            pattern: Паттерн ключей (например, "user:*").

        Returns:
            Количество удалённых ключей.
        """
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0

    async def exists(self, key: str) -> bool:
        """
        Проверить существование ключа.

        Args:
            key: Ключ для проверки.

        Returns:
            True если существует.
        """
        return bool(await self.redis.exists(key))
```

---

## Cache-Aside паттерн

```python
"""Cache-Aside (Lazy Loading) паттерн."""

from typing import Callable, Awaitable, TypeVar
from datetime import timedelta

T = TypeVar("T")


class CacheService:
    """Сервис кэширования с Cache-Aside."""

    def __init__(self, cache: CacheClient):
        """Инициализация."""
        self.cache = cache

    async def get_or_set(
        self,
        key: str,
        fetch_func: Callable[[], Awaitable[T]],
        ttl: timedelta | None = None,
    ) -> T:
        """
        Получить из кэша или загрузить и закэшировать.

        Args:
            key: Ключ кэша.
            fetch_func: Функция загрузки данных.
            ttl: Время жизни кэша.

        Returns:
            Данные из кэша или загруженные.
        """
        # Попытка получить из кэша
        cached = await self.cache.get(key)
        if cached is not None:
            return cached

        # Загрузка данных
        data = await fetch_func()

        # Сохранение в кэш
        if data is not None:
            await self.cache.set(key, data, ttl)

        return data


# Использование
class UserService:
    """Сервис с кэшированием."""

    def __init__(self, data_client: DataApiClient, cache: CacheService):
        """Инициализация."""
        self.data_client = data_client
        self.cache = cache

    async def get_user(self, user_id: UUID) -> UserDTO:
        """Получить пользователя с кэшированием."""
        cache_key = f"user:{user_id}"

        data = await self.cache.get_or_set(
            key=cache_key,
            fetch_func=lambda: self.data_client.get_user(user_id),
            ttl=timedelta(minutes=10),
        )

        if data is None:
            raise NotFoundError("User", str(user_id))

        return UserDTO.model_validate(data)
```

---

## Write-Through паттерн

```python
"""Write-Through паттерн."""

from uuid import UUID


class UserService:
    """Сервис с Write-Through кэшированием."""

    async def update_user(self, user_id: UUID, dto: UpdateUserDTO) -> UserDTO:
        """
        Обновить пользователя с обновлением кэша.

        Args:
            user_id: ID пользователя.
            dto: Данные для обновления.

        Returns:
            Обновлённый пользователь.
        """
        # Обновляем в Data API
        data = await self.data_client.update_user(user_id, dto.model_dump())

        # Обновляем кэш
        cache_key = f"user:{user_id}"
        await self.cache.set(cache_key, data, ttl=timedelta(minutes=10))

        return UserDTO.model_validate(data)

    async def delete_user(self, user_id: UUID) -> None:
        """
        Удалить пользователя с инвалидацией кэша.

        Args:
            user_id: ID пользователя.
        """
        # Удаляем в Data API
        await self.data_client.delete_user(user_id)

        # Инвалидируем кэш
        cache_key = f"user:{user_id}"
        await self.cache.delete(cache_key)
```

---

## Инвалидация кэша

```python
"""Стратегии инвалидации кэша."""

from typing import List


class CacheInvalidator:
    """Инвалидатор кэша."""

    def __init__(self, cache: CacheClient):
        """Инициализация."""
        self.cache = cache

    async def invalidate_user(self, user_id: UUID) -> None:
        """
        Инвалидировать кэш пользователя.

        Args:
            user_id: ID пользователя.
        """
        # Основной ключ
        await self.cache.delete(f"user:{user_id}")

        # Связанные ключи
        await self.cache.delete_pattern(f"user:{user_id}:*")

    async def invalidate_user_orders(self, user_id: UUID) -> None:
        """
        Инвалидировать кэш заказов пользователя.

        Args:
            user_id: ID пользователя.
        """
        await self.cache.delete_pattern(f"orders:user:{user_id}:*")

    async def invalidate_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        related_patterns: List[str] | None = None,
    ) -> None:
        """
        Универсальная инвалидация сущности.

        Args:
            entity_type: Тип сущности.
            entity_id: ID сущности.
            related_patterns: Дополнительные паттерны.
        """
        # Основной ключ
        await self.cache.delete(f"{entity_type}:{entity_id}")

        # Связанные паттерны
        if related_patterns:
            for pattern in related_patterns:
                await self.cache.delete_pattern(pattern.format(id=entity_id))
```

---

## Ключи кэша

```python
"""Генерация ключей кэша."""


class CacheKeys:
    """Генератор ключей кэша."""

    # Паттерны ключей
    USER = "user:{user_id}"
    USER_BY_EMAIL = "user:email:{email}"
    USER_ORDERS = "orders:user:{user_id}:page:{page}"
    ORDER = "order:{order_id}"
    RESTAURANT = "restaurant:{restaurant_id}"
    RESTAURANT_MENU = "restaurant:{restaurant_id}:menu"

    @classmethod
    def user(cls, user_id: UUID) -> str:
        """Ключ пользователя."""
        return cls.USER.format(user_id=user_id)

    @classmethod
    def user_by_email(cls, email: str) -> str:
        """Ключ пользователя по email."""
        return cls.USER_BY_EMAIL.format(email=email)

    @classmethod
    def user_orders(cls, user_id: UUID, page: int = 1) -> str:
        """Ключ заказов пользователя."""
        return cls.USER_ORDERS.format(user_id=user_id, page=page)

    @classmethod
    def order(cls, order_id: UUID) -> str:
        """Ключ заказа."""
        return cls.ORDER.format(order_id=order_id)

    @classmethod
    def restaurant_menu(cls, restaurant_id: UUID) -> str:
        """Ключ меню ресторана."""
        return cls.RESTAURANT_MENU.format(restaurant_id=restaurant_id)
```

---

## TTL стратегии

```python
"""TTL для разных типов данных."""

from datetime import timedelta


class CacheTTL:
    """Константы TTL."""

    # Часто изменяемые данные
    USER = timedelta(minutes=5)
    ORDER = timedelta(minutes=2)

    # Редко изменяемые данные
    RESTAURANT = timedelta(hours=1)
    MENU = timedelta(minutes=30)

    # Справочники
    CATEGORIES = timedelta(hours=24)
    CONFIG = timedelta(hours=12)

    # Временные данные
    SESSION = timedelta(hours=2)
    OTP = timedelta(minutes=5)
```

---

## Чек-лист

- [ ] CacheClient реализован
- [ ] Cache-Aside для чтения
- [ ] Write-Through для записи
- [ ] Инвалидация настроена
- [ ] Ключи стандартизированы
- [ ] TTL определены для типов данных
