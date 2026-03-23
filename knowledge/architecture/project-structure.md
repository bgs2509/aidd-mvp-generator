# Project Structure

> **Purpose**: Standard project structure for AIDD-MVP.

---

## Root Structure

```
{project}/
├── services/                    # Services
│   ├── {context}_api/          # Business API
│   ├── {context}_data/         # Data API
│   ├── {context}_bot/          # Telegram Bot (optional)
│   └── {context}_worker/       # Background Worker (optional)
│
├── ai-docs/                     # AI agent documents
│   └── docs/
│       ├── prd/                # PRD documents
│       ├── architecture/       # Architecture decisions
│       ├── plans/              # Implementation plans
│       ├── reports/            # Reports (review, qa, validation)
│       └── rtm.md              # Requirements Traceability Matrix
│
├── docs/                        # Project documentation
│   └── api/                    # API documentation
│
├── docker-compose.yml           # Main configuration
├── docker-compose.dev.yml       # Dev overrides
├── docker-compose.prod.yml      # Production configuration (Level 3+)
├── .env.example                 # Environment variables example
├── Makefile                     # Development commands
├── README.md                    # Project documentation
└── .gitignore                   # Ignored files
```

---

## Business API Structure

```
services/{context}_api/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
│
├── src/
│   └── {context}_api/
│       ├── __init__.py
│       ├── main.py              # Entry point, application factory
│       │
│       ├── api/                 # Incoming adapters (HTTP)
│       │   ├── __init__.py
│       │   ├── dependencies.py  # DI dependencies
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py    # Main router
│       │       └── {entity}_routes.py
│       │
│       ├── application/         # Application layer
│       │   ├── __init__.py
│       │   ├── services/        # Application services
│       │   │   ├── __init__.py
│       │   │   └── {entity}_service.py
│       │   └── dtos/            # Data Transfer Objects
│       │       ├── __init__.py
│       │       └── {entity}_dtos.py
│       │
│       ├── domain/              # Domain layer (core)
│       │   ├── __init__.py
│       │   ├── entities/        # Domain entities
│       │   │   ├── __init__.py
│       │   │   └── {entity}.py
│       │   ├── value_objects/   # Value Objects
│       │   │   └── __init__.py
│       │   └── services/        # Domain services
│       │       └── __init__.py
│       │
│       ├── infrastructure/      # Outgoing adapters
│       │   ├── __init__.py
│       │   └── http/            # HTTP clients
│       │       ├── __init__.py
│       │       ├── base_client.py
│       │       └── data_api_client.py
│       │
│       ├── schemas/             # Pydantic schemas
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {entity}_schemas.py
│       │
│       └── core/                # Shared components
│           ├── __init__.py
│           ├── config.py        # Configuration
│           ├── logging.py       # Logging setup
│           └── exceptions.py    # Custom exceptions
│
└── tests/
    ├── __init__.py
    ├── conftest.py              # Fixtures
    ├── unit/
    │   ├── __init__.py
    │   └── test_{entity}_service.py
    └── integration/
        ├── __init__.py
        └── test_{entity}_api.py
```

---

## Data API Structure

```
services/{context}_data/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── alembic.ini                  # Migration configuration
│
├── migrations/                  # Alembic migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── {revision}_{description}.py
│
├── src/
│   └── {context}_data/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── dependencies.py
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py
│       │       └── {entity}_routes.py
│       │
│       ├── domain/
│       │   ├── __init__.py
│       │   └── entities/
│       │       ├── __init__.py
│       │       ├── base.py      # SQLAlchemy Base
│       │       └── {entity}.py  # ORM models
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── database/
│       │   │   ├── __init__.py
│       │   │   ├── connection.py
│       │   │   └── session.py
│       │   └── repositories/
│       │       ├── __init__.py
│       │       ├── base.py
│       │       └── {entity}_repository.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {entity}_schemas.py
│       │
│       └── core/
│           ├── __init__.py
│           ├── config.py
│           └── logging.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   └── test_{entity}_repository.py
    └── integration/
        └── test_{entity}_api.py
```

---

## Telegram Bot Structure

```
services/{context}_bot/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
│
├── src/
│   └── {context}_bot/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── handlers/            # Message handlers
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── start.py
│       │   └── {feature}_handlers.py
│       │
│       ├── keyboards/           # Keyboards
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {feature}_keyboards.py
│       │
│       ├── states/              # FSM states
│       │   ├── __init__.py
│       │   └── {feature}_states.py
│       │
│       ├── middlewares/         # Middleware
│       │   ├── __init__.py
│       │   └── logging_middleware.py
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   └── http/
│       │       ├── __init__.py
│       │       └── business_api_client.py
│       │
│       └── core/
│           ├── __init__.py
│           ├── config.py
│           └── logging.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── unit/
        └── test_handlers.py
```

---

## Background Worker Structure

```
services/{context}_worker/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
│
├── src/
│   └── {context}_worker/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── tasks/               # Task handlers
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {task_name}_task.py
│       │
│       ├── scheduler/           # Scheduler
│       │   ├── __init__.py
│       │   └── scheduler.py
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   └── http/
│       │       ├── __init__.py
│       │       └── business_api_client.py
│       │
│       └── core/
│           ├── __init__.py
│           ├── config.py
│           └── logging.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── unit/
        └── test_tasks.py
```

---

## Key Files

### main.py (Business API)

```python
"""Business API entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from {context}_api.api.v1.router import api_router
from {context}_api.core.config import settings
from {context}_api.core.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    # startup
    yield
    # shutdown

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.service_name,
        version="1.0.0",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix="/api/v1")
    return app

app = create_app()
```

### config.py

```python
"""Service configuration."""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "{Context} API"
    debug: bool = False
    log_level: str = "INFO"

    # URLs
    data_api_url: str = "http://localhost:8001"

    class Config:
        env_file = ".env"

settings = Settings()
```
