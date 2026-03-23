# Service Separation

> **Purpose**: Principles for splitting the system into independent services.

---

## Principle

```
Each service is a separate deployment unit with clear responsibility.
Services communicate only via HTTP (REST API).
```

---

## Service Types

### 1. Business API

```
Responsibility:
- Business logic
- Business rules validation
- Orchestrating calls to Data API
- REST API for clients

Uses:
- HTTP client for Data API
- Does NOT use direct DB access
```

### 2. Data API

```
Responsibility:
- CRUD operations with DB
- Data schema validation
- Database migrations

Uses:
- SQLAlchemy / Motor
- Direct DB connection
- Alembic for migrations
```

### 3. Telegram Bot

```
Responsibility:
- Telegram UI
- Command and message handling
- FSM for complex dialogs

Uses:
- HTTP client for Business API
- Does NOT call Data API directly
```

### 4. Background Worker

```
Responsibility:
- Background tasks
- Periodic operations
- Queue processing

Uses:
- HTTP client for Business API
- Redis for queues (optional)
```

---

## Interaction Diagram

```
                    ┌─────────────────┐
                    │   Telegram      │
                    │     User        │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Web Client     │   │  Telegram Bot   │   │    Worker       │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │
         │                     │ HTTP                │
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │  Business API   │
                    │   (FastAPI)     │
                    └────────┬────────┘
                             │
                             │ HTTP
                             │
                             ▼
                    ┌─────────────────┐
                    │    Data API     │
                    │   (FastAPI)     │
                    └────────┬────────┘
                             │
                             │ SQL
                             │
                             ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    └─────────────────┘
```

---

## Separation Rules

### 1. Code Isolation

```
RULE: Services do NOT import code from each other.

# BAD
from booking_data.models import Order  # ❌

# GOOD
# Each service has its own models/schemas
from booking_api.schemas import OrderResponse  # ✓
```

### 2. Data Isolation

```
RULE: Only Data API has access to the database.

Business API:
- Does not know about SQLAlchemy
- Does not have DATABASE_URL
- Works through HTTP client

Data API:
- The only one with DB access
- Manages migrations
- Validates data
```

### 3. Configuration Isolation

```
RULE: Each service has its own configuration.

# Business API
DATA_API_URL=http://booking-data:8001
LOG_LEVEL=INFO

# Data API
DATABASE_URL=postgresql://...
LOG_LEVEL=INFO

# Bot
BOT_TOKEN=...
BUSINESS_API_URL=http://booking-api:8000
```

### 4. Deployment Isolation

```
RULE: Each service is a separate Docker container.

docker-compose.yml:
- booking-api
- booking-data
- booking-bot
- booking-worker
- postgres
- redis
```

---

## Directory Structure

```
project/
├── services/
│   ├── booking_api/           # Business API
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── booking_api/
│   │
│   ├── booking_data/          # Data API
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── booking_data/
│   │
│   ├── booking_bot/           # Telegram Bot
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── booking_bot/
│   │
│   └── booking_worker/        # Background Worker
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
│           └── booking_worker/
│
├── docker-compose.yml
├── docker-compose.dev.yml
└── Makefile
```

---

## Docker Compose

```yaml
version: "3.8"

services:
  # Business API
  booking-api:
    build: ./services/booking_api
    ports:
      - "8000:8000"
    environment:
      - DATA_API_URL=http://booking-data:8001
    depends_on:
      - booking-data

  # Data API
  booking-data:
    build: ./services/booking_data
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/booking
    depends_on:
      - postgres

  # Telegram Bot
  booking-bot:
    build: ./services/booking_bot
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - BUSINESS_API_URL=http://booking-api:8000
    depends_on:
      - booking-api

  # Background Worker
  booking-worker:
    build: ./services/booking_worker
    environment:
      - BUSINESS_API_URL=http://booking-api:8000
    depends_on:
      - booking-api

  # Database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=booking
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Isolation Verification

```bash
# Check that services do not import from each other

# booking_api should not have imports from booking_data
grep -r "from booking_data" services/booking_api/
grep -r "import booking_data" services/booking_api/

# booking_bot should not have imports from booking_data
grep -r "from booking_data" services/booking_bot/

# Result should be empty!
```

---

## Related Documents

| Document | Description |
|----------|----------|
| `improved-hybrid.md` | Overall architecture |
| `data-access.md` | HTTP-only access |
