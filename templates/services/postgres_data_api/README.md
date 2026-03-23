# {context}_data — PostgreSQL Data API Service

> **Type**: Data API (FastAPI + SQLAlchemy)
> **Purpose**: HTTP API for working with PostgreSQL database

---

## Description

Data API service for working with PostgreSQL.
Provides CRUD operations via HTTP API.
Used by Business API services following the HTTP-only principle.

---

## Structure

```
{context}_data/
├── Dockerfile
├── requirements.txt
├── alembic.ini                 # Alembic configuration
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/               # Migrations
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── {domain}/       # Domain CRUD router
│   │   └── dependencies.py
│   ├── domain/
│   │   ├── __init__.py
│   │   └── entities/           # SQLAlchemy models
│   │       ├── __init__.py
│   │       ├── base.py         # Base model
│   │       └── {domain}.py     # Domain model
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py             # Base repository
│   │   └── {domain}_repository.py
│   └── core/
│       ├── __init__.py
│       ├── config.py
│       ├── database.py         # DB connection
│       └── logging.py
└── tests/
    ├── __init__.py
    └── conftest.py
```

---

## Replacement Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{context}` | Project context | `booking`, `ecommerce` |
| `{domain}` | Entity domain | `user`, `order` |
| `{Domain}` | Domain (PascalCase) | `User`, `Order` |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Migrations
alembic upgrade head

# Run in dev mode
uvicorn src.main:app --reload --port 8001

# Run tests
pytest tests/ -v
```

---

## Configuration

Environment variables (`.env`):

```bash
# Database
# SECURITY: Replace YOUR_USER and YOUR_PASSWORD with real credentials!
DATABASE_URL=postgresql+asyncpg://YOUR_USER:YOUR_PASSWORD@localhost:5432/{context}_db

# Application
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/{domain}s` | List with pagination |
| POST | `/api/v1/{domain}s` | Create |
| GET | `/api/v1/{domain}s/{id}` | Get by ID |
| PUT | `/api/v1/{domain}s/{id}` | Update |
| DELETE | `/api/v1/{domain}s/{id}` | Delete |

---

## Dependencies

- FastAPI 0.100+
- SQLAlchemy 2.0+ (async)
- asyncpg
- alembic
- pydantic-settings
- structlog

---

## Checklist

- [ ] Replace `{context}` with the project name
- [ ] Create models in `domain/entities/`
- [ ] Create repositories in `repositories/`
- [ ] Create migrations: `alembic revision --autogenerate`
- [ ] Apply migrations: `alembic upgrade head`
- [ ] Add tests
