# Redis Connection Management

> **Purpose**: Setting up and managing Redis connections.

---

## Basic Connection

```python
"""Redis connection."""

import redis.asyncio as redis

from {context}_api.core.config import settings


async def create_redis_client() -> redis.Redis:
    """
    Create Redis client.

    Returns:
        Configured Redis client.
    """
    return redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


# In lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle with Redis."""
    # Create client
    app.state.redis = await create_redis_client()

    yield

    # Close
    await app.state.redis.close()
```

---

## Connection Pool

```python
"""Redis with connection pool."""

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from {context}_api.core.config import settings


def create_redis_pool() -> ConnectionPool:
    """
    Create Redis connection pool.

    Returns:
        Configured connection pool.
    """
    return ConnectionPool.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=settings.redis_max_connections,
    )


async def get_redis_client(pool: ConnectionPool) -> redis.Redis:
    """
    Get client from pool.

    Args:
        pool: Connection pool.

    Returns:
        Redis client.
    """
    return redis.Redis(connection_pool=pool)


# In lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle with Redis pool."""
    # Create pool
    app.state.redis_pool = create_redis_pool()
    app.state.redis = await get_redis_client(app.state.redis_pool)

    yield

    # Close
    await app.state.redis.close()
    await app.state.redis_pool.disconnect()
```

---

## Configuration

```python
"""Redis configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings with Redis."""

    # Redis URL
    redis_url: str = "redis://localhost:6379/0"

    # Connection pool
    redis_max_connections: int = 10

    # Timeouts
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
"""Redis health check."""

import redis.asyncio as redis


async def check_redis_health(client: redis.Redis) -> dict:
    """
    Check Redis health.

    Args:
        client: Redis client.

    Returns:
        Connection status.
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


# In health route
@router.get("/health/redis")
async def redis_health(request: Request) -> dict:
    """Check Redis."""
    return await check_redis_health(request.app.state.redis)
```

---

## Dependency Injection

```python
"""DI for Redis."""

from fastapi import Depends, Request
import redis.asyncio as redis

from {context}_api.infrastructure.cache.client import CacheClient


def get_redis(request: Request) -> redis.Redis:
    """
    Get Redis client.

    Args:
        request: HTTP request.

    Returns:
        Redis client.
    """
    return request.app.state.redis


def get_cache_client(
    redis_client: redis.Redis = Depends(get_redis),
) -> CacheClient:
    """
    Get cache client.

    Args:
        redis_client: Redis client.

    Returns:
        Cache client.
    """
    return CacheClient(redis_client)
```

---

## Sentinel for HA

```python
"""Redis Sentinel for High Availability."""

from redis.asyncio.sentinel import Sentinel

from {context}_api.core.config import settings


async def create_sentinel_client() -> redis.Redis:
    """
    Create client via Sentinel.

    Returns:
        Redis client via Sentinel.
    """
    sentinel = Sentinel(
        settings.redis_sentinels,  # [("host1", 26379), ("host2", 26379)]
        socket_timeout=settings.redis_socket_timeout,
    )

    # Get master
    master = sentinel.master_for(
        settings.redis_master_name,
        socket_timeout=settings.redis_socket_timeout,
        decode_responses=True,
    )

    return master


# Sentinel configuration
class Settings(BaseSettings):
    """Settings with Sentinel."""

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
    Create Redis Cluster client.

    Returns:
        Redis Cluster client.
    """
    return RedisCluster.from_url(
        settings.redis_cluster_url,
        decode_responses=True,
    )


# Cluster configuration
class Settings(BaseSettings):
    """Settings with Cluster."""

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

## Environment Variables

```bash
# .env

# Simple connection
REDIS_URL=redis://localhost:6379/0

# With password
REDIS_URL=redis://:password@localhost:6379/0

# SSL
REDIS_URL=rediss://localhost:6379/0

# Pool settings
REDIS_MAX_CONNECTIONS=10
REDIS_SOCKET_TIMEOUT=5.0
REDIS_SOCKET_CONNECT_TIMEOUT=5.0
```

---

## Checklist

- [ ] Connection via redis.asyncio
- [ ] Connection pool configured
- [ ] Health check implemented
- [ ] DI via Depends
- [ ] Closed in lifespan
- [ ] Timeouts configured
