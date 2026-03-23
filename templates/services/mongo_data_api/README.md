# {context}_data — MongoDB Data API Service

> **Type**: Data API (FastAPI + Motor)
> **Purpose**: HTTP API for working with MongoDB database

---

## Description

Data API service for working with MongoDB.
Provides CRUD operations via HTTP API.
Used by Business API services following the HTTP-only principle.

---

## Structure

```
{context}_data/
├── Dockerfile
├── requirements.txt
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
│   │   └── models/             # Pydantic models
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
│       ├── database.py         # MongoDB connection
│       └── logging.py
└── tests/
    ├── __init__.py
    └── conftest.py
```

---

## Replacement Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{context}` | Project context | `booking`, `analytics` |
| `{domain}` | Entity domain | `event`, `log`, `metric` |
| `{Domain}` | Domain (PascalCase) | `Event`, `Log`, `Metric` |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run in dev mode
uvicorn src.main:app --reload --port 8001

# Run tests
pytest tests/ -v
```

---

## Configuration

Environment variables (`.env`):

```bash
# MongoDB
# SECURITY: Replace YOUR_USER and YOUR_PASSWORD with real credentials!
# For local development without auth: mongodb://localhost:27017
MONGODB_URL=mongodb://YOUR_USER:YOUR_PASSWORD@localhost:27017
MONGODB_DATABASE={context}_db

# Application
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
```

---

## Dependencies

- FastAPI 0.100+
- motor (async MongoDB driver)
- pydantic-settings
- structlog

---

## Checklist

- [ ] Replace `{context}` with the project name
- [ ] Create models in `domain/models/`
- [ ] Create repositories in `repositories/`
- [ ] Configure indexes in `core/database.py`
- [ ] Add tests
