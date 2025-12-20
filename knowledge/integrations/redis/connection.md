# Управление соединениями Redis

> **Назначение**: Настройка и управление подключением к Redis.

---

## Базовое подключение

```python
"""Подключение к Redis."""

import redis.asyncio as redis

from {context}_api.core.config import settings


async def create_redis_client() -> redis.Redis:
    """
    Создать клиент Redis.

    Returns:
        Настроенный клиент Redis.
    """
    return redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


# В lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл с Redis."""
    # Создание клиента
    app.state.redis = await create_redis_client()

    yield

    # Закрытие
    await app.state.redis.close()
```

---

## Пул соединений

```python
"""Redis с пулом соединений."""

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from {context}_api.core.config import settings


def create_redis_pool() -> ConnectionPool:
    """
    Создать пул соединений Redis.

    Returns:
        Настроенный пул соединений.
    """
    return ConnectionPool.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=settings.redis_max_connections,
    )


async def get_redis_client(pool: ConnectionPool) -> redis.Redis:
    """
    Получить клиент из пула.

    Args:
        pool: Пул соединений.

    Returns:
        Клиент Redis.
    """
    return redis.Redis(connection_pool=pool)


# В lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл с пулом Redis."""
    # Создание пула
    app.state.redis_pool = create_redis_pool()
    app.state.redis = await get_redis_client(app.state.redis_pool)

    yield

    # Закрытие
    await app.state.redis.close()
    await app.state.redis_pool.disconnect()
```

---

## Конфигурация

```python
"""Конфигурация Redis."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки с Redis."""

    # Redis URL
    redis_url: str = "redis://localhost:6379/0"

    # Пул соединений
    redis_max_connections: int = 10

    # Таймауты
    redis_socket_timeout: float = 5.0
    redis_socket_connect_timeout: float = 5.0

    # Retry
    redis_retry_on_timeout: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## Health Check

```python
"""Health check Redis."""

import redis.asyncio as redis


async def check_redis_health(client: redis.Redis) -> dict:
    """
    Проверить состояние Redis.

    Args:
        client: Клиент Redis.

    Returns:
        Статус подключения.
    """
    try:
        await client.ping()
        info = await client.info("server")
        return {
            "status": "healthy",
            "version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
        }
    except redis.RedisError as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


# В роуте health
@router.get("/health/redis")
async def redis_health(request: Request) -> dict:
    """Проверить Redis."""
    return await check_redis_health(request.app.state.redis)
```

---

## Dependency Injection

```python
"""DI для Redis."""

from fastapi import Depends, Request
import redis.asyncio as redis

from {context}_api.infrastructure.cache.client import CacheClient


def get_redis(request: Request) -> redis.Redis:
    """
    Получить клиент Redis.

    Args:
        request: HTTP запрос.

    Returns:
        Клиент Redis.
    """
    return request.app.state.redis


def get_cache_client(
    redis_client: redis.Redis = Depends(get_redis),
) -> CacheClient:
    """
    Получить клиент кэширования.

    Args:
        redis_client: Клиент Redis.

    Returns:
        Клиент кэширования.
    """
    return CacheClient(redis_client)
```

---

## Sentinel для HA

```python
"""Redis Sentinel для High Availability."""

from redis.asyncio.sentinel import Sentinel

from {context}_api.core.config import settings


async def create_sentinel_client() -> redis.Redis:
    """
    Создать клиент через Sentinel.

    Returns:
        Клиент Redis через Sentinel.
    """
    sentinel = Sentinel(
        settings.redis_sentinels,  # [("host1", 26379), ("host2", 26379)]
        socket_timeout=settings.redis_socket_timeout,
    )

    # Получить мастер
    master = sentinel.master_for(
        settings.redis_master_name,
        socket_timeout=settings.redis_socket_timeout,
        decode_responses=True,
    )

    return master


# Конфигурация для Sentinel
class Settings(BaseSettings):
    """Настройки с Sentinel."""

    redis_sentinels: list[tuple[str, int]] = [
        ("sentinel1", 26379),
        ("sentinel2", 26379),
        ("sentinel3", 26379),
    ]
    redis_master_name: str = "mymaster"
```

---

## Cluster

```python
"""Redis Cluster."""

from redis.asyncio.cluster import RedisCluster

from {context}_api.core.config import settings


async def create_cluster_client() -> RedisCluster:
    """
    Создать клиент Redis Cluster.

    Returns:
        Клиент Redis Cluster.
    """
    return RedisCluster.from_url(
        settings.redis_cluster_url,
        decode_responses=True,
    )


# Конфигурация для Cluster
class Settings(BaseSettings):
    """Настройки с Cluster."""

    redis_cluster_url: str = "redis://node1:6379"
```

---

## Docker Compose

```yaml
# docker-compose.yml

services:
  {context}-redis:
    image: redis:7-alpine
    container_name: {context}-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis_data:
```

---

## Переменные окружения

```bash
# .env

# Простое подключение
REDIS_URL=redis://localhost:6379/0

# С паролем
REDIS_URL=redis://:password@localhost:6379/0

# SSL
REDIS_URL=rediss://localhost:6379/0

# Настройки пула
REDIS_MAX_CONNECTIONS=10
REDIS_SOCKET_TIMEOUT=5.0
REDIS_SOCKET_CONNECT_TIMEOUT=5.0
```

---

## Чек-лист

- [ ] Подключение через redis.asyncio
- [ ] Пул соединений настроен
- [ ] Health check реализован
- [ ] DI через Depends
- [ ] Закрытие в lifespan
- [ ] Таймауты настроены
