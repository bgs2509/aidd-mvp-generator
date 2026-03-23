# AIDD-MVP Hybrid Architecture

> **Purpose**: Description of the improved hybrid architecture of the framework.

---

## Overview

AIDD-MVP uses a hybrid architecture combining:
- **DDD (Domain-Driven Design)** — for organizing business logic
- **Hexagonal Architecture** — for isolation from external dependencies
- **HTTP-only Data Access** — for service separation

---

## Core Principles

### 1. Service Separation

```
┌─────────────────────────────────────────────────────────────┐
│                    AIDD-MVP Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Business API │    │ Telegram Bot │    │   Worker     │  │
│  │  (FastAPI)   │    │  (aiogram)   │    │  (asyncio)   │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
│         │     HTTP calls    │                   │           │
│         └───────────────────┼───────────────────┘           │
│                             │                               │
│                             ▼                               │
│                    ┌──────────────┐                        │
│                    │   Data API   │                        │
│                    │  (FastAPI)   │                        │
│                    └──────┬───────┘                        │
│                           │                                │
│                           │ SQL                            │
│                           ▼                                │
│                    ┌──────────────┐                        │
│                    │  PostgreSQL  │                        │
│                    └──────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. HTTP-only Data Access

```
RULE: Business services NEVER access the database directly.

Business API --HTTP--> Data API --SQL--> Database

Why:
- Service isolation
- Independent scaling
- Clear contracts (API)
- Simplified testing
```

### 3. DDD Within a Service

```
service/
├── api/                 <- Incoming adapter (HTTP)
│   └── v1/
│       └── routes.py
├── application/         <- Application services
│   ├── services/
│   └── dtos/
├── domain/              <- Core (business logic)
│   ├── entities/
│   ├── value_objects/
│   └── services/
└── infrastructure/      <- Outgoing adapters
    └── http/            (HTTP clients, not SQL!)
```

---

## System Components

### Business API

```python
"""Business logic service."""

# Uses HTTP client for Data API
from infrastructure.http import DataApiClient

class OrderService:
    def __init__(self, data_client: DataApiClient):
        self.data_client = data_client

    async def create_order(self, data: CreateOrderDTO) -> Order:
        # Business logic
        validated = self.validate(data)

        # Save via Data API (HTTP!)
        result = await self.data_client.create_order(validated)

        return Order.from_dict(result)
```

### Data API

```python
"""Data access service."""

# The only service with database access
from sqlalchemy.ext.asyncio import AsyncSession

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> Order:
        order = Order(**data)
        self.session.add(order)
        await self.session.commit()
        return order
```

### Telegram Bot

```python
"""Telegram bot uses Business API."""

from infrastructure.http import BusinessApiClient

@router.message(Command("order"))
async def create_order(message: Message, api_client: BusinessApiClient):
    # Call business logic via HTTP
    result = await api_client.create_order({
        "user_id": message.from_user.id,
        "items": [...],
    })

    await message.answer(f"Order {result['id']} created!")
```

---

## Advantages

### 1. Isolation

```
- Each service is independent
- Internal implementation can be changed
- Clear boundaries of responsibility
```

### 2. Scalability

```
- Independent service scaling
- Data API can cache results
- Business API can be replicated
```

### 3. Testability

```
- Mocks for HTTP clients
- Isolated unit tests
- Integration tests via HTTP
```

### 4. Maintainability

```
- Clear structure
- Easy to add new services
- Minimal dependencies between services
```

---

## Architecture Rules

### DO

```
✓ Use HTTP clients for inter-service communication
✓ Keep business logic in the domain layer
✓ Define clear API contracts
✓ Use DI for dependencies
✓ Write async code
```

### DON'T

```
✗ Import SQLAlchemy in business services
✗ Access DB directly from Business API
✗ Create circular dependencies
✗ Mix DDD layers
✗ Use synchronous code in async applications
```

---

## Default Ports

| Service | Port | Description |
|--------|------|----------|
| Business API | 8000 | REST API for clients |
| Data API | 8001 | PostgreSQL access |
| Data API Mongo | 8002 | MongoDB access |
| PostgreSQL | 5432 | Primary DB |
| MongoDB | 27017 | Document DB |
| Redis | 6379 | Cache, sessions |

---

## Related Documents

| Document | Description |
|----------|----------|
| `ddd-hexagonal.md` | DDD and Hexagonal principles |
| `data-access.md` | HTTP-only data access |
| `service-separation.md` | Service separation |
