# Function: Defining API Contracts

> **Purpose**: Designing API contracts between services.

---

## Goal

Define clear API contracts for all services,
ensuring correct interaction between components.

---

## API Design Principles

### 1. RESTful

```
GET    /api/v1/{resource}      — list resources
GET    /api/v1/{resource}/{id} — get one
POST   /api/v1/{resource}      — create
PUT    /api/v1/{resource}/{id} — full update
PATCH  /api/v1/{resource}/{id} — partial update
DELETE /api/v1/{resource}/{id} — delete
```

### 2. Versioning

```
/api/v1/...  — first version
/api/v2/...  — second version (if needed)

RULE: Always use versioning starting with v1.
```

### 3. Path Naming

```
RULE: Paths in kebab-case, plural for collections.

✓ /api/v1/restaurants
✓ /api/v1/user-profiles
✓ /api/v1/order-items

✗ /api/v1/restaurant
✗ /api/v1/userProfiles
✗ /api/v1/order_items
```

### 4. Response Format

```json
// Successful response (single object)
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}

// Successful response (list with pagination)
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}

// Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Error description",
    "details": [...]
  }
}
```

---

## API Contract Template

### Business API Contract

```markdown
## Business API: {context}_api

**Base URL**: http://localhost:8000
**Prefix**: /api/v1

### Endpoints

| Method | Path | Description | Req ID |
|--------|------|-------------|--------|
| POST | /restaurants | Create restaurant | FR-001 |
| GET | /restaurants | List restaurants | FR-002 |
| GET | /restaurants/{id} | Get restaurant | FR-003 |
| POST | /bookings | Create booking | FR-004 |
| GET | /bookings/{id} | Get booking | FR-005 |

---

### POST /restaurants

**Description**: Create a new restaurant

**Request Body**:
```json
{
  "name": "string (required)",
  "address": "string (required)",
  "phone": "string (optional)",
  "capacity": "integer (required)"
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "name": "string",
  "address": "string",
  "phone": "string | null",
  "capacity": "integer",
  "created_at": "datetime"
}
```

**Response 400**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {"field": "name", "message": "Field is required"}
    ]
  }
}
```

---

### GET /restaurants

**Description**: Get list of restaurants

**Query Parameters**:
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| page | integer | Page number | 1 |
| page_size | integer | Page size | 20 |
| search | string | Search by name | — |

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "address": "string",
      "capacity": "integer"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```
```

### Data API Contract

```markdown
## Data API: {context}_data

**Base URL**: http://localhost:8001
**Prefix**: /api/v1

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /restaurants | Create record |
| GET | /restaurants | Get records |
| GET | /restaurants/{id} | Get by ID |
| PUT | /restaurants/{id} | Update record |
| DELETE | /restaurants/{id} | Delete record |

---

### Data API Specifics

1. **Direct CRUD** — no business logic
2. **Schema validation** — at the Pydantic level
3. **Used only by Business API** — not by clients directly

---

### POST /restaurants

**Description**: Create a record in DB

**Request Body**:
```json
{
  "name": "string",
  "address": "string",
  "phone": "string | null",
  "capacity": "integer"
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "name": "string",
  "address": "string",
  "phone": "string | null",
  "capacity": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
```

---

## Schemas (Pydantic)

### Base Schemas

```python
"""Base schemas for API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common settings."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamps."""

    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseModel):
    """Paginated response schema."""

    total: int
    page: int
    page_size: int
    pages: int
```

### Resource Schema Example

```python
"""Schemas for restaurants."""

from uuid import UUID

from .base import BaseSchema, TimestampMixin


class RestaurantCreate(BaseSchema):
    """Restaurant creation schema."""

    name: str
    address: str
    phone: str | None = None
    capacity: int


class RestaurantUpdate(BaseSchema):
    """Restaurant update schema."""

    name: str | None = None
    address: str | None = None
    phone: str | None = None
    capacity: int | None = None


class RestaurantResponse(BaseSchema, TimestampMixin):
    """Restaurant response schema."""

    id: UUID
    name: str
    address: str
    phone: str | None
    capacity: int


class RestaurantListResponse(BaseSchema):
    """Restaurant list schema."""

    items: list[RestaurantResponse]
    total: int
    page: int
    page_size: int
    pages: int
```

---

## HTTP Response Codes

| Code | Description | When to Use |
|------|-------------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (creation) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Not authorized |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Conflict (duplicate) |
| 422 | Unprocessable Entity | Business logic error |
| 500 | Internal Server Error | Internal error |

---

## Error Codes

```python
"""API error codes."""

class ErrorCodes:
    """Standard error codes."""

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"

    # Resources
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"

    # Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # Business logic
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"

    # External services
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    DATA_API_ERROR = "DATA_API_ERROR"
```

---

## Service Interactions

### Business API → Data API

```
Business API                          Data API
    │                                     │
    │  POST /api/v1/restaurants           │
    │ ──────────────────────────────────▶ │
    │                                     │
    │  201 Created                        │
    │ ◀────────────────────────────────── │
    │                                     │
```

### Telegram Bot → Business API

```
Telegram Bot                       Business API
    │                                    │
    │  GET /api/v1/restaurants?search=   │
    │ ─────────────────────────────────▶ │
    │                                    │
    │  200 OK (list)                     │
    │ ◀───────────────────────────────── │
    │                                    │
```

---

## Result

```markdown
## Project API Contracts

### Services

| Service | Base URL | Documentation |
|---------|----------|---------------|
| Business API | http://localhost:8000 | /docs |
| Data API | http://localhost:8001 | /docs |

### Contract Files

- ai-docs/docs/api/business-api-contract.md
- ai-docs/docs/api/data-api-contract.md

### Schemas

- services/{context}_api/src/schemas/
- services/{context}_data/src/schemas/
```

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/services/fastapi/routing-patterns.md` | Routing patterns |
| `knowledge/services/fastapi/schema-validation.md` | Schema validation |
| `conventions.md` | Naming conventions |
