# Структура проекта

> **Назначение**: Стандартная структура проекта AIDD-MVP.

---

## Корневая структура

```
{project}/
├── services/                    # Сервисы
│   ├── {context}_api/          # Business API
│   ├── {context}_data/         # Data API
│   ├── {context}_bot/          # Telegram Bot (опционально)
│   └── {context}_worker/       # Background Worker (опционально)
│
├── ai-docs/                     # Документы AI агентов
│   └── docs/
│       ├── prd/                # PRD документы
│       ├── architecture/       # Архитектурные решения
│       ├── plans/              # Планы реализации
│       ├── reports/            # Отчёты (review, qa, validation)
│       └── rtm.md              # Requirements Traceability Matrix
│
├── docs/                        # Документация проекта
│   └── api/                    # API документация
│
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI pipeline
│       └── cd.yml              # CD pipeline (Level 3+)
│
├── docker-compose.yml           # Основная конфигурация
├── docker-compose.dev.yml       # Dev overrides
├── docker-compose.prod.yml      # Production конфигурация (Level 3+)
├── .env.example                 # Пример переменных окружения
├── Makefile                     # Команды разработки
├── README.md                    # Документация проекта
└── .gitignore                   # Игнорируемые файлы
```

---

## Структура Business API

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
│       ├── main.py              # Точка входа, фабрика приложения
│       │
│       ├── api/                 # Входящие адаптеры (HTTP)
│       │   ├── __init__.py
│       │   ├── dependencies.py  # DI зависимости
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py    # Главный роутер
│       │       └── {entity}_routes.py
│       │
│       ├── application/         # Слой приложения
│       │   ├── __init__.py
│       │   ├── services/        # Application services
│       │   │   ├── __init__.py
│       │   │   └── {entity}_service.py
│       │   └── dtos/            # Data Transfer Objects
│       │       ├── __init__.py
│       │       └── {entity}_dtos.py
│       │
│       ├── domain/              # Доменный слой (ядро)
│       │   ├── __init__.py
│       │   ├── entities/        # Доменные сущности
│       │   │   ├── __init__.py
│       │   │   └── {entity}.py
│       │   ├── value_objects/   # Value Objects
│       │   │   └── __init__.py
│       │   └── services/        # Domain services
│       │       └── __init__.py
│       │
│       ├── infrastructure/      # Исходящие адаптеры
│       │   ├── __init__.py
│       │   └── http/            # HTTP клиенты
│       │       ├── __init__.py
│       │       ├── base_client.py
│       │       └── data_api_client.py
│       │
│       ├── schemas/             # Pydantic схемы
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {entity}_schemas.py
│       │
│       └── core/                # Общие компоненты
│           ├── __init__.py
│           ├── config.py        # Конфигурация
│           ├── logging.py       # Настройка логирования
│           └── exceptions.py    # Кастомные исключения
│
└── tests/
    ├── __init__.py
    ├── conftest.py              # Фикстуры
    ├── unit/
    │   ├── __init__.py
    │   └── test_{entity}_service.py
    └── integration/
        ├── __init__.py
        └── test_{entity}_api.py
```

---

## Структура Data API

```
services/{context}_data/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── alembic.ini                  # Конфигурация миграций
│
├── migrations/                  # Alembic миграции
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
│       │       └── {entity}.py  # ORM модели
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

## Структура Telegram Bot

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
│       ├── handlers/            # Обработчики сообщений
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── start.py
│       │   └── {feature}_handlers.py
│       │
│       ├── keyboards/           # Клавиатуры
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {feature}_keyboards.py
│       │
│       ├── states/              # FSM состояния
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

## Структура Background Worker

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
│       ├── tasks/               # Обработчики задач
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {task_name}_task.py
│       │
│       ├── scheduler/           # Планировщик
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

## Ключевые файлы

### main.py (Business API)

```python
"""Точка входа Business API."""

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
"""Конфигурация сервиса."""

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
