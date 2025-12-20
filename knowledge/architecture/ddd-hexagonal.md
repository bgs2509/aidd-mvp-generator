# DDD и Hexagonal Architecture

> **Назначение**: Принципы Domain-Driven Design и Hexagonal Architecture.

---

## Domain-Driven Design (DDD)

### Основная идея

```
Организация кода вокруг бизнес-домена, а не технических деталей.

Фокус на:
- Ubiquitous Language (единый язык с бизнесом)
- Bounded Contexts (ограниченные контексты)
- Domain Model (модель предметной области)
```

### Слои DDD

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

Правило зависимостей:
API → Application → Domain ← Infrastructure
              ↓
    Domain НЕ зависит от Infrastructure
```

### Компоненты Domain Layer

#### Entity

```python
"""Сущность с идентичностью."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class Order:
    """Сущность заказа."""

    id: UUID
    customer_id: UUID
    items: list["OrderItem"]
    status: "OrderStatus"
    total: "Money"

    def add_item(self, item: "OrderItem") -> None:
        """Добавить товар в заказ."""
        if self.status != OrderStatus.DRAFT:
            raise DomainError("Cannot modify confirmed order")
        self.items.append(item)
        self._recalculate_total()

    def confirm(self) -> None:
        """Подтвердить заказ."""
        if not self.items:
            raise DomainError("Cannot confirm empty order")
        self.status = OrderStatus.CONFIRMED
```

#### Value Object

```python
"""Объект-значение без идентичности."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Денежное значение."""

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
"""Доменный сервис для логики, не принадлежащей одной сущности."""

class PricingService:
    """Сервис расчёта цен."""

    def calculate_discount(
        self,
        order: Order,
        customer: Customer,
    ) -> Money:
        """Рассчитать скидку."""
        discount = Money(Decimal("0"))

        # Скидка за объём
        if order.total > Money(Decimal("10000")):
            discount += order.total * Decimal("0.05")

        # Скидка постоянному клиенту
        if customer.is_vip:
            discount += order.total * Decimal("0.10")

        return discount
```

---

## Hexagonal Architecture

### Основная идея

```
Изоляция бизнес-логики от внешнего мира через порты и адаптеры.

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
│        (входящие)        (ядро)       (исходящие)│
└─────────────────────────────────────────────────┘
```

### Порты (Интерфейсы)

```python
"""Порт — интерфейс для взаимодействия с внешним миром."""

from abc import ABC, abstractmethod
from uuid import UUID


# Исходящий порт (Secondary Port)
class OrderRepositoryPort(ABC):
    """Порт для работы с хранилищем заказов."""

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Получить заказ по ID."""
        pass

    @abstractmethod
    async def save(self, order: Order) -> None:
        """Сохранить заказ."""
        pass


# Входящий порт (Primary Port) — обычно это Use Case
class CreateOrderUseCase(ABC):
    """Порт для создания заказа."""

    @abstractmethod
    async def execute(self, command: CreateOrderCommand) -> Order:
        """Создать заказ."""
        pass
```

### Адаптеры (Реализации)

```python
"""Адаптер — реализация порта для конкретной технологии."""

# Исходящий адаптер: HTTP клиент
class HttpOrderRepository(OrderRepositoryPort):
    """HTTP адаптер для репозитория заказов."""

    def __init__(self, http_client: DataApiClient):
        self.client = http_client

    async def get_by_id(self, order_id: UUID) -> Order | None:
        data = await self.client.get(f"/orders/{order_id}")
        return Order.from_dict(data) if data else None

    async def save(self, order: Order) -> None:
        await self.client.post("/orders", order.to_dict())


# Исходящий адаптер: SQL база данных (только для Data API!)
class SqlOrderRepository(OrderRepositoryPort):
    """SQL адаптер для репозитория заказов."""

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

## Применение в AIDD-MVP

### Business API

```
Использует:
- DDD слои (api, application, domain, infrastructure)
- Hexagonal порты и адаптеры
- HTTP адаптер для Data API (исходящий)
- FastAPI как входящий адаптер
```

### Data API

```
Использует:
- DDD слои
- SQL адаптер для БД (исходящий)
- FastAPI как входящий адаптер
```

### Telegram Bot

```
Использует:
- Handlers как входящие адаптеры
- HTTP адаптер для Business API (исходящий)
```

---

## Правила

### DO (Делать)

```
✓ Domain слой не зависит от Infrastructure
✓ Бизнес-логика в Domain
✓ Use Cases в Application
✓ Внешние зависимости через порты
✓ Инверсия зависимостей
```

### DON'T (Не делать)

```
✗ Импортировать Infrastructure в Domain
✗ Бизнес-логика в контроллерах
✗ Прямые зависимости на внешние сервисы
✗ Анемичные модели (логика вне сущностей)
```

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| `improved-hybrid.md` | Общая архитектура |
| `data-access.md` | HTTP-only доступ |
