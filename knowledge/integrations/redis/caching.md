# Redis Caching Strategies

> **Purpose**: Caching patterns with Redis.

---

## Base Client

```python
"""Redis caching client."""

import json
from typing import Any, TypeVar
from datetime import timedelta

import redis.asyncio as redis

from {context}_api.core.config import settings

T = TypeVar("T")


class CacheClient:
    """Caching client."""

    def __init__(self, redis_client: redis.Redis):
        """
        Initialize.

        Args:
            redis_client: Redis client instance.
        """
        self.redis = redis_client
        self.default_ttl = timedelta(minutes=5)

    async def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Value or None.
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
        Save value to cache.

        Args:
            key: Cache key.
            value: Value to save.
            ttl: Time to live.
        """
        ttl = ttl or self.default_ttl
        data = json.dumps(value, default=str)
        await self.redis.set(key, data, ex=int(ttl.total_seconds()))

    async def delete(self, key: str) -> None:
        """
        Delete key from cache.

        Args:
            key: Key to delete.
        """
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete keys by pattern.

        Args:
            pattern: Key pattern (e.g., "user:*").

        Returns:
            Number of deleted keys.
        """
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists.

        Args:
            key: Key to check.

        Returns:
            True if exists.
        """
        return bool(await self.redis.exists(key))
```

---

## Cache-Aside Pattern

```python
"""Cache-Aside (Lazy Loading) pattern."""

from typing import Callable, Awaitable, TypeVar
from datetime import timedelta

T = TypeVar("T")


class CacheService:
    """Caching service with Cache-Aside."""

    def __init__(self, cache: CacheClient):
        """Initialize."""
        self.cache = cache

    async def get_or_set(
        self,
        key: str,
        fetch_func: Callable[[], Awaitable[T]],
        ttl: timedelta | None = None,
    ) -> T:
        """
        Get from cache or fetch and cache.

        Args:
            key: Cache key.
            fetch_func: Data fetching function.
            ttl: Cache time to live.

        Returns:
            Cached or fetched data.
        """
        # Try to get from cache
        cached = await self.cache.get(key)
        if cached is not None:
            return cached

        # Fetch data
        data = await fetch_func()

        # Save to cache
        if data is not None:
            await self.cache.set(key, data, ttl)

        return data


# Usage
class UserService:
    """Service with caching."""

    def __init__(self, data_client: DataApiClient, cache: CacheService):
        """Initialize."""
        self.data_client = data_client
        self.cache = cache

    async def get_user(self, user_id: UUID) -> UserDTO:
        """Get user with caching."""
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

## Write-Through Pattern

```python
"""Write-Through pattern."""

from uuid import UUID


class UserService:
    """Service with Write-Through caching."""

    async def update_user(self, user_id: UUID, dto: UpdateUserDTO) -> UserDTO:
        """
        Update user with cache update.

        Args:
            user_id: User ID.
            dto: Update data.

        Returns:
            Updated user.
        """
        # Update in Data API
        data = await self.data_client.update_user(user_id, dto.model_dump())

        # Update cache
        cache_key = f"user:{user_id}"
        await self.cache.set(cache_key, data, ttl=timedelta(minutes=10))

        return UserDTO.model_validate(data)

    async def delete_user(self, user_id: UUID) -> None:
        """
        Delete user with cache invalidation.

        Args:
            user_id: User ID.
        """
        # Delete in Data API
        await self.data_client.delete_user(user_id)

        # Invalidate cache
        cache_key = f"user:{user_id}"
        await self.cache.delete(cache_key)
```

---

## Cache Invalidation

```python
"""Cache invalidation strategies."""

from typing import List


class CacheInvalidator:
    """Cache invalidator."""

    def __init__(self, cache: CacheClient):
        """Initialize."""
        self.cache = cache

    async def invalidate_user(self, user_id: UUID) -> None:
        """
        Invalidate user cache.

        Args:
            user_id: User ID.
        """
        # Primary key
        await self.cache.delete(f"user:{user_id}")

        # Related keys
        await self.cache.delete_pattern(f"user:{user_id}:*")

    async def invalidate_user_orders(self, user_id: UUID) -> None:
        """
        Invalidate user orders cache.

        Args:
            user_id: User ID.
        """
        await self.cache.delete_pattern(f"orders:user:{user_id}:*")

    async def invalidate_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        related_patterns: List[str] | None = None,
    ) -> None:
        """
        Universal entity invalidation.

        Args:
            entity_type: Entity type.
            entity_id: Entity ID.
            related_patterns: Additional patterns.
        """
        # Primary key
        await self.cache.delete(f"{entity_type}:{entity_id}")

        # Related patterns
        if related_patterns:
            for pattern in related_patterns:
                await self.cache.delete_pattern(pattern.format(id=entity_id))
```

---

## Cache Keys

```python
"""Cache key generation."""


class CacheKeys:
    """Cache key generator."""

    # Key patterns
    USER = "user:{user_id}"
    USER_BY_EMAIL = "user:email:{email}"
    USER_ORDERS = "orders:user:{user_id}:page:{page}"
    ORDER = "order:{order_id}"
    RESTAURANT = "restaurant:{restaurant_id}"
    RESTAURANT_MENU = "restaurant:{restaurant_id}:menu"

    @classmethod
    def user(cls, user_id: UUID) -> str:
        """User key."""
        return cls.USER.format(user_id=user_id)

    @classmethod
    def user_by_email(cls, email: str) -> str:
        """User by email key."""
        return cls.USER_BY_EMAIL.format(email=email)

    @classmethod
    def user_orders(cls, user_id: UUID, page: int = 1) -> str:
        """User orders key."""
        return cls.USER_ORDERS.format(user_id=user_id, page=page)

    @classmethod
    def order(cls, order_id: UUID) -> str:
        """Order key."""
        return cls.ORDER.format(order_id=order_id)

    @classmethod
    def restaurant_menu(cls, restaurant_id: UUID) -> str:
        """Restaurant menu key."""
        return cls.RESTAURANT_MENU.format(restaurant_id=restaurant_id)
```

---

## TTL Strategies

```python
"""TTL for different data types."""

from datetime import timedelta


class CacheTTL:
    """TTL constants."""

    # Frequently changing data
    USER = timedelta(minutes=5)
    ORDER = timedelta(minutes=2)

    # Rarely changing data
    RESTAURANT = timedelta(hours=1)
    MENU = timedelta(minutes=30)

    # Reference data
    CATEGORIES = timedelta(hours=24)
    CONFIG = timedelta(hours=12)

    # Temporary data
    SESSION = timedelta(hours=2)
    OTP = timedelta(minutes=5)
```

---

## Checklist

- [ ] CacheClient implemented
- [ ] Cache-Aside for reads
- [ ] Write-Through for writes
- [ ] Invalidation configured
- [ ] Keys standardized
- [ ] TTL defined for data types
