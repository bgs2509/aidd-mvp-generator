# {context}_api — Business API Service

> **Type**: Business API (FastAPI)
> **Purpose**: HTTP API for business logic

---

## Description

Business API service on FastAPI implementing the application's business logic.
Operates on the HTTP-only data access principle through the Data API.

---

## Structure

```
{context}_api/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # Main v1 router
│   │   │   ├── health.py       # Health check
│   │   │   └── {domain}/       # Domain (users, orders, etc.)
│   │   │       ├── __init__.py
│   │   │       ├── router.py
│   │   │       └── schemas.py
│   │   └── dependencies.py     # DI dependencies
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/           # Application services
│   │   │   └── {domain}_service.py
│   │   └── dtos/               # Data Transfer Objects
│   │       └── {domain}_dto.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/           # Domain entities
│   │   ├── value_objects/      # Value Objects
│   │   └── services/           # Domain services
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── http/               # HTTP clients
│   │   │   ├── __init__.py
│   │   │   ├── base_client.py
│   │   │   └── data_api_client.py
│   │   └── cache/              # Caching
│   │       └── redis_client.py
│   └── core/
│       ├── __init__.py
│       ├── config.py           # Configuration
│       ├── logging.py          # Logging setup
│       └── exceptions.py       # Custom exceptions
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    └── integration/
```

---

## Replacement Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{context}` | Project context (snake_case) | `booking`, `ecommerce` |
| `{domain}` | Entity domain | `user`, `order`, `product` |
| `{Domain}` | Entity domain (PascalCase) | `User`, `Order`, `Product` |
| `{CONTEXT}` | Context (UPPER_CASE) | `BOOKING`, `ECOMMERCE` |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run in dev mode
uvicorn src.main:app --reload --port 8000

# Run tests
pytest tests/ -v
```

---

## Configuration

Environment variables (`.env`):

```bash
# Application
APP_NAME={context}_api
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Data API
DATA_API_URL=http://data-api:8001
DATA_API_TIMEOUT=30

# Redis (optional)
REDIS_URL=redis://redis:6379/0
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/{domain}s` | List entities |
| POST | `/api/v1/{domain}s` | Create entity |
| GET | `/api/v1/{domain}s/{id}` | Get by ID |
| PUT | `/api/v1/{domain}s/{id}` | Update |
| DELETE | `/api/v1/{domain}s/{id}` | Delete |

---

## Dependencies

- FastAPI 0.100+
- httpx (HTTP client)
- pydantic-settings
- structlog
- redis (optional)

---

## Checklist

- [ ] Replace `{context}` with the project name
- [ ] Replace `{domain}` with the domain name
- [ ] Configure `.env`
- [ ] Implement business logic in `application/services/`
- [ ] Add tests
