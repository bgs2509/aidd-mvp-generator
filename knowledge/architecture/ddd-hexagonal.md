# DDD and Hexagonal Architecture

> **Purpose**: Domain-Driven Design and Hexagonal Architecture principles.

---

## Domain-Driven Design (DDD)

### Core Idea

```
Organizing code around the business domain, not technical details.

Focus on:
- Ubiquitous Language (shared language with the business)
- Bounded Contexts
- Domain Model
```

### DDD Layers

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│  (HTTP Controllers, GraphQL Resolvers)                      │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│  (Use Cases, Application Services, DTOs)                    │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│  (Entities, Value Objects, Domain Services, Repositories)   │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                       │
│  (Database, HTTP Clients, Message Queues, External APIs)    │
└─────────────────────────────────────────────────────────────┘

Dependency rule:
API -> Application -> Domain <- Infrastructure
              ↓
    Domain does NOT depend on Infrastructure
```

### Domain Layer Components

#### Entity

```python
"""Entity with identity."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class Order:
    """Order entity."""

    id: UUID
    customer_id: UUID
    items: list["OrderItem"]
    status: "OrderStatus"
    total: "Money"

    def add_item(self, item: "OrderItem") -> None:
        """Add an item to the order."""
        if self.status != OrderStatus.DRAFT:
            raise DomainError("Cannot modify confirmed order")
        self.items.append(item)
        self._recalculate_total()

    def confirm(self) -> None:
        """Confirm the order."""
        if not self.items:
            raise DomainError("Cannot confirm empty order")
        self.status = OrderStatus.CONFIRMED
```

#### Value Object

```python
"""Value object without identity."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Monetary value."""

    amount: Decimal
    currency: str = "RUB"

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: int) -> "Money":
        return Money(self.amount * factor, self.currency)
```

#### Domain Service

```python
"""Domain service for logic not belonging to a single entity."""

class PricingService:
    """Pricing service."""

    def calculate_discount(
        self,
        order: Order,
        customer: Customer,
    ) -> Money:
        """Calculate discount."""
        discount = Money(Decimal("0"))

        # Volume discount
        if order.total > Money(Decimal("10000")):
            discount += order.total * Decimal("0.05")

        # Loyal customer discount
        if customer.is_vip:
            discount += order.total * Decimal("0.10")

        return discount
```

---

## Hexagonal Architecture

### Core Idea

```
Isolating business logic from the outside world through ports and adapters.

┌─────────────────────────────────────────────────┐
│                                                 │
│   ┌─────────┐                    ┌─────────┐   │
│   │  HTTP   │                    │   DB    │   │
│   │ Adapter │◀──┐          ┌────▶│ Adapter │   │
│   └─────────┘   │          │     └─────────┘   │
│                 │          │                   │
│   ┌─────────┐   │  ┌────┐  │     ┌─────────┐   │
│   │   CLI   │◀──┼──│Core│──┼────▶│  HTTP   │   │
│   │ Adapter │   │  └────┘  │     │ Client  │   │
│   └─────────┘   │          │     └─────────┘   │
│                 │          │                   │
│   ┌─────────┐   │          │     ┌─────────┐   │
│   │  gRPC   │◀──┘          └────▶│  Queue  │   │
│   │ Adapter │                    │ Adapter │   │
│   └─────────┘                    └─────────┘   │
│                                                 │
│         Driving           Core           Driven │
│        (incoming)        (core)       (outgoing)│
└─────────────────────────────────────────────────┘
```

### Ports (Interfaces)

```python
"""Port -- interface for interacting with the outside world."""

from abc import ABC, abstractmethod
from uuid import UUID


# Outgoing port (Secondary Port)
class OrderRepositoryPort(ABC):
    """Port for working with the order store."""

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Get order by ID."""
        pass

    @abstractmethod
    async def save(self, order: Order) -> None:
        """Save order."""
        pass


# Incoming port (Primary Port) -- usually a Use Case
class CreateOrderUseCase(ABC):
    """Port for creating an order."""

    @abstractmethod
    async def execute(self, command: CreateOrderCommand) -> Order:
        """Create an order."""
        pass
```

### Adapters (Implementations)

```python
"""Adapter -- port implementation for a specific technology."""

# Outgoing adapter: HTTP client
class HttpOrderRepository(OrderRepositoryPort):
    """HTTP adapter for order repository."""

    def __init__(self, http_client: DataApiClient):
        self.client = http_client

    async def get_by_id(self, order_id: UUID) -> Order | None:
        data = await self.client.get(f"/orders/{order_id}")
        return Order.from_dict(data) if data else None

    async def save(self, order: Order) -> None:
        await self.client.post("/orders", order.to_dict())


# Outgoing adapter: SQL database (only for Data API!)
class SqlOrderRepository(OrderRepositoryPort):
    """SQL adapter for order repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: UUID) -> Order | None:
        result = await self.session.get(OrderModel, order_id)
        return self._to_domain(result) if result else None

    async def save(self, order: Order) -> None:
        model = self._to_model(order)
        self.session.add(model)
        await self.session.commit()
```

---

## Application in AIDD-MVP

### Business API

```
Uses:
- DDD layers (api, application, domain, infrastructure)
- Hexagonal ports and adapters
- HTTP adapter for Data API (outgoing)
- FastAPI as incoming adapter
```

### Data API

```
Uses:
- DDD layers
- SQL adapter for DB (outgoing)
- FastAPI as incoming adapter
```

### Telegram Bot

```
Uses:
- Handlers as incoming adapters
- HTTP adapter for Business API (outgoing)
```

---

## Rules

### DO

```
✓ Domain layer does not depend on Infrastructure
✓ Business logic in Domain
✓ Use Cases in Application
✓ External dependencies through ports
✓ Dependency inversion
```

### DON'T

```
✗ Import Infrastructure in Domain
✗ Business logic in controllers
✗ Direct dependencies on external services
✗ Anemic models (logic outside entities)
```

---

## Related Documents

| Document | Description |
|----------|----------|
| `improved-hybrid.md` | Overall architecture |
| `data-access.md` | HTTP-only access |
