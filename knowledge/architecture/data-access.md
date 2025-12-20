# HTTP-only доступ к данным

> **Назначение**: Принцип изоляции доступа к данным через HTTP.

---

## Принцип

```
ПРАВИЛО: Бизнес-сервисы НИКОГДА не обращаются к базе данных напрямую.
         Доступ к данным только через HTTP вызовы к Data API.

Business Service ──HTTP──▶ Data API ──SQL──▶ Database
```

---

## Почему HTTP-only?

### 1. Изоляция

```
✓ Чёткие границы между сервисами
✓ Каждый сервис можно развивать независимо
✓ Изменения в БД не влияют на бизнес-сервисы
```

### 2. Масштабирование

```
✓ Data API можно масштабировать отдельно
✓ Можно добавить кэширование в Data API
✓ Business API не нужен connection pool к БД
```

### 3. Безопасность

```
✓ Единая точка доступа к данным
✓ Валидация на уровне Data API
✓ Аудит всех операций с данными
```

### 4. Тестирование

```
✓ Легко мокировать HTTP клиент
✓ Независимые тесты для каждого сервиса
✓ Integration тесты через HTTP
```

---

## Архитектура

### Data API (единственный с доступом к БД)

```python
"""Data API — сервис доступа к данным."""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/orders")
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_session),
):
    """Создать заказ в БД."""
    repo = OrderRepository(session)
    order = await repo.create(**data.model_dump())
    return order


@router.get("/orders/{order_id}")
async def get_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Получить заказ из БД."""
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order
```

### Business API (использует HTTP клиент)

```python
"""Business API — бизнес-логика через HTTP."""

from infrastructure.http import DataApiClient


class OrderService:
    """Сервис заказов."""

    def __init__(self, data_client: DataApiClient):
        self.data_client = data_client

    async def create_order(self, data: CreateOrderDTO) -> OrderDTO:
        """Создать заказ с бизнес-логикой."""
        # Бизнес-валидация
        await self._validate_business_rules(data)

        # Расчёт итогов
        total = await self._calculate_total(data.items)

        # Сохранение через Data API (HTTP!)
        result = await self.data_client.create_order({
            "customer_id": data.customer_id,
            "items": [item.model_dump() for item in data.items],
            "total": total,
        })

        return OrderDTO.model_validate(result)
```

### HTTP клиент

```python
"""HTTP клиент для Data API."""

import httpx


class DataApiClient:
    """Клиент для взаимодействия с Data API."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
            )
        return self._client

    async def create_order(self, data: dict) -> dict:
        """Создать заказ через Data API."""
        response = await self.client.post("/api/v1/orders", json=data)
        response.raise_for_status()
        return response.json()

    async def get_order(self, order_id: UUID) -> dict | None:
        """Получить заказ через Data API."""
        response = await self.client.get(f"/api/v1/orders/{order_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
```

---

## Что НЕЛЬЗЯ делать

### ❌ Импорт SQLAlchemy в Business API

```python
# ПЛОХО! SQLAlchemy в бизнес-сервисе
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class OrderService:
    def __init__(self, session: AsyncSession):  # ❌
        self.session = session

    async def create_order(self, data):
        order = Order(**data)
        self.session.add(order)  # ❌ Прямой доступ к БД
        await self.session.commit()
```

### ❌ Connection string в Business API

```python
# ПЛОХО! DATABASE_URL в бизнес-сервисе
DATABASE_URL = "postgresql://..."  # ❌

engine = create_async_engine(DATABASE_URL)  # ❌
```

### ❌ Прямые SQL запросы

```python
# ПЛОХО! SQL в бизнес-коде
result = await connection.execute(
    "SELECT * FROM orders WHERE id = :id",  # ❌
    {"id": order_id}
)
```

---

## Что НУЖНО делать

### ✓ HTTP клиент для Data API

```python
# ХОРОШО! HTTP клиент
from infrastructure.http import DataApiClient

class OrderService:
    def __init__(self, data_client: DataApiClient):  # ✓
        self.data_client = data_client

    async def create_order(self, data):
        result = await self.data_client.create_order(data)  # ✓
        return result
```

### ✓ DATA_API_URL вместо DATABASE_URL

```python
# ХОРОШО! URL Data API
DATA_API_URL = "http://localhost:8001"  # ✓

data_client = DataApiClient(DATA_API_URL)  # ✓
```

---

## Проверка соблюдения

```bash
# Поиск нарушений в Business API

# SQLAlchemy импорты
grep -r "from sqlalchemy" services/{context}_api/

# Прямые подключения к БД
grep -r "DATABASE_URL" services/{context}_api/
grep -r "create_engine" services/{context}_api/

# Если найдено — НАРУШЕНИЕ!
```

---

## Обработка ошибок

```python
"""Обработка ошибок HTTP клиента."""

class DataApiError(Exception):
    """Ошибка Data API."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class DataApiClient:
    async def _request(self, method: str, path: str, **kwargs) -> dict:
        try:
            response = await self.client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise DataApiError(
                f"Data API error: {e.response.status_code}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise DataApiError(f"Data API connection error: {e}")
```

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| `improved-hybrid.md` | Общая архитектура |
| `../integrations/http/client-patterns.md` | Паттерны HTTP клиентов |
