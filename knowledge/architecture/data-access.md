# HTTP-only Data Access

> **Purpose**: The principle of isolating data access through HTTP.

---

## Principle

```
RULE: Business services NEVER access the database directly.
      Data access only through HTTP calls to Data API.

Business Service --HTTP--> Data API --SQL--> Database
```

---

## Why HTTP-only?

### 1. Isolation

```
✓ Clear boundaries between services
✓ Each service can evolve independently
✓ DB changes do not affect business services
```

### 2. Scaling

```
✓ Data API can be scaled separately
✓ Caching can be added to Data API
✓ Business API does not need a DB connection pool
```

### 3. Security

```
✓ Single point of data access
✓ Validation at Data API level
✓ Audit of all data operations
```

### 4. Testing

```
✓ Easy to mock HTTP client
✓ Independent tests for each service
✓ Integration tests via HTTP
```

---

## Architecture

### Data API (the only one with DB access)

```python
"""Data API -- data access service."""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/orders")
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create an order in DB."""
    repo = OrderRepository(session)
    order = await repo.create(**data.model_dump())
    return order


@router.get("/orders/{order_id}")
async def get_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get an order from DB."""
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order
```

### Business API (uses HTTP client)

```python
"""Business API -- business logic via HTTP."""

from infrastructure.http import DataApiClient


class OrderService:
    """Order service."""

    def __init__(self, data_client: DataApiClient):
        self.data_client = data_client

    async def create_order(self, data: CreateOrderDTO) -> OrderDTO:
        """Create an order with business logic."""
        # Business validation
        await self._validate_business_rules(data)

        # Calculate totals
        total = await self._calculate_total(data.items)

        # Save via Data API (HTTP!)
        result = await self.data_client.create_order({
            "customer_id": data.customer_id,
            "items": [item.model_dump() for item in data.items],
            "total": total,
        })

        return OrderDTO.model_validate(result)
```

### HTTP Client

```python
"""HTTP client for Data API."""

import httpx


class DataApiClient:
    """Client for interacting with Data API."""

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
        """Create an order via Data API."""
        response = await self.client.post("/api/v1/orders", json=data)
        response.raise_for_status()
        return response.json()

    async def get_order(self, order_id: UUID) -> dict | None:
        """Get an order via Data API."""
        response = await self.client.get(f"/api/v1/orders/{order_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
```

---

## What NOT to Do

### Do NOT import SQLAlchemy in Business API

```python
# BAD! SQLAlchemy in business service
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class OrderService:
    def __init__(self, session: AsyncSession):  # ❌
        self.session = session

    async def create_order(self, data):
        order = Order(**data)
        self.session.add(order)  # ❌ Direct DB access
        await self.session.commit()
```

### Do NOT use connection string in Business API

```python
# BAD! DATABASE_URL in business service
DATABASE_URL = "postgresql://..."  # ❌

engine = create_async_engine(DATABASE_URL)  # ❌
```

### Do NOT use direct SQL queries

```python
# BAD! SQL in business code
result = await connection.execute(
    "SELECT * FROM orders WHERE id = :id",  # ❌
    {"id": order_id}
)
```

---

## What to Do

### Use HTTP client for Data API

```python
# GOOD! HTTP client
from infrastructure.http import DataApiClient

class OrderService:
    def __init__(self, data_client: DataApiClient):  # ✓
        self.data_client = data_client

    async def create_order(self, data):
        result = await self.data_client.create_order(data)  # ✓
        return result
```

### Use DATA_API_URL instead of DATABASE_URL

```python
# GOOD! Data API URL
DATA_API_URL = "http://localhost:8001"  # ✓

data_client = DataApiClient(DATA_API_URL)  # ✓
```

---

## Compliance Verification

```bash
# Search for violations in Business API

# SQLAlchemy imports
grep -r "from sqlalchemy" services/{context}_api/

# Direct DB connections
grep -r "DATABASE_URL" services/{context}_api/
grep -r "create_engine" services/{context}_api/

# If found — VIOLATION!
```

---

## Error Handling

```python
"""HTTP client error handling."""

class DataApiError(Exception):
    """Data API error."""

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

## Related Documents

| Document | Description |
|----------|----------|
| `improved-hybrid.md` | Overall architecture |
| `../integrations/http/client-patterns.md` | HTTP client patterns |
