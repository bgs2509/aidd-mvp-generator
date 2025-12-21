# Template Map — Карта соответствия шаблонов

> **Назначение**: Связь между шаблонами генератора и результатом в целевом проекте.
> Помогает понять, что получится из каждого шаблона.

---

## Обзор

```
ГЕНЕРАТОР (templates/)           →         ЦЕЛЕВОЙ ПРОЕКТ
─────────────────────────────────────────────────────────
templates/services/              →    services/{name}_{type}/
templates/shared/                →    services/{name}_api/src/shared/
templates/infrastructure/        →    {project-name}/
templates/documents/                  →    ai-docs/docs/
```

---

## Шаблоны сервисов

### fastapi_business_api/

| Шаблон | Результат | Описание |
|--------|-----------|----------|
| `src/api/` | `services/{name}_api/src/api/` | REST API роутеры |
| `src/application/` | `services/{name}_api/src/application/` | Application services |
| `src/domain/` | `services/{name}_api/src/domain/` | Domain entities |
| `src/infrastructure/` | `services/{name}_api/src/infrastructure/` | HTTP клиенты |
| `src/schemas/` | `services/{name}_api/src/schemas/` | Pydantic schemas |
| `src/core/` | `services/{name}_api/src/core/` | Config, logging |
| `tests/` | `services/{name}_api/tests/` | Unit + Integration |
| `Dockerfile` | `services/{name}_api/Dockerfile` | Сборка контейнера |

**Пример**: `booking_api/`

### postgres_data_api/

| Шаблон | Результат | Описание |
|--------|-----------|----------|
| `src/api/` | `services/{name}_data/src/api/` | CRUD endpoints |
| `src/domain/entities/` | `services/{name}_data/src/domain/entities/` | SQLAlchemy models |
| `src/repositories/` | `services/{name}_data/src/repositories/` | DB repositories |
| `alembic/` | `services/{name}_data/alembic/` | Миграции |
| `Dockerfile` | `services/{name}_data/Dockerfile` | Сборка контейнера |

**Пример**: `booking_data/`

### aiogram_bot/

| Шаблон | Результат | Описание |
|--------|-----------|----------|
| `src/handlers/` | `services/{name}_bot/src/handlers/` | Telegram handlers |
| `src/keyboards/` | `services/{name}_bot/src/keyboards/` | Inline/Reply keyboards |
| `src/states/` | `services/{name}_bot/src/states/` | FSM states |
| `src/middlewares/` | `services/{name}_bot/src/middlewares/` | Bot middlewares |

**Пример**: `booking_bot/`

### asyncio_worker/

| Шаблон | Результат | Описание |
|--------|-----------|----------|
| `src/tasks/` | `services/{name}_worker/src/tasks/` | Task handlers |
| `src/processor.py` | `services/{name}_worker/src/processor.py` | Task processor |
| `src/scheduler.py` | `services/{name}_worker/src/scheduler.py` | Task scheduler |

**Пример**: `booking_worker/`

---

## Шаблоны инфраструктуры

### infrastructure/

| Шаблон | Результат | Описание |
|--------|-----------|----------|
| `docker-compose.yml` | `docker-compose.yml` | Оркестрация |
| `docker-compose.dev.yml` | `docker-compose.dev.yml` | Dev окружение |
| `.env.example` | `.env.example` | Переменные окружения |
| `Makefile` | `Makefile` | Команды сборки |

### github-actions/

| Шаблон | Результат | Описание |
|--------|-----------|----------|
| `ci.yml` | `.github/workflows/ci.yml` | CI pipeline |
| `cd.yml` | `.github/workflows/cd.yml` | CD pipeline |

### nginx/

| Шаблон | Результат | Описание |
|--------|-----------|----------|
| `nginx.conf` | `nginx/nginx.conf` | API Gateway |
| `Dockerfile` | `nginx/Dockerfile` | Nginx контейнер |

---

## Шаблоны документов

### templates/documents/

| Шаблон генератора | Результат в целевом проекте | Этап |
|-------------------|----------------------------|------|
| `prd-template.md` | `ai-docs/docs/prd/{name}-prd.md` | 1 (Идея) |
| `architecture-template.md` | `ai-docs/docs/architecture/{name}-plan.md` | 3 (Архитектура) |
| `feature-plan-template.md` | `ai-docs/docs/plans/{feature}-plan.md` | 3 (FEATURE) |
| `rtm-template.md` | `ai-docs/docs/rtm.md` | 7 (Валидация) |
| `pipeline-state-template.json` | `.pipeline-state.json` | 1 (Идея) |

---

## Общие компоненты

### shared/

| Шаблон | Результат | Используется в |
|--------|-----------|---------------|
| `http_client/` | `services/{name}_api/src/infrastructure/http/` | Business API |
| `logging/` | `services/*/src/core/logging.py` | Все сервисы |
| `health/` | `services/*/src/api/health.py` | Все сервисы |
| `exceptions/` | `services/*/src/core/exceptions.py` | Все сервисы |

---

## Трансформации при копировании

### Замены в файлах

| Плейсхолдер | Заменяется на | Пример |
|-------------|---------------|--------|
| `{context}` | Контекст проекта | `booking` |
| `{domain}` | Домен | `restaurant` |
| `{name}` | Полное имя | `booking_restaurant` |
| `{type}` | Тип сервиса | `api`, `data`, `bot` |
| `{entity}` | Название сущности | `Restaurant`, `Booking` |

### Пример трансформации

```
templates/services/fastapi_business_api/src/api/v1/{entity}_router.py
                                        ↓
services/booking_api/src/api/v1/restaurants_router.py
```

---

## Визуальная карта

```
templates/
├── services/
│   ├── fastapi_business_api/  ─────→  services/{name}_api/
│   ├── postgres_data_api/     ─────→  services/{name}_data/
│   ├── aiogram_bot/           ─────→  services/{name}_bot/
│   └── asyncio_worker/        ─────→  services/{name}_worker/
│
├── shared/
│   ├── http_client/           ─────→  */infrastructure/http/
│   ├── logging/               ─────→  */core/logging.py
│   └── health/                ─────→  */api/health.py
│
├── infrastructure/
│   ├── docker-compose.yml     ─────→  docker-compose.yml
│   ├── Makefile               ─────→  Makefile
│   └── github-actions/        ─────→  .github/workflows/
│
└── templates/documents/
    ├── prd-template.md        ─────→  ai-docs/docs/prd/*.md
    ├── architecture-template.md ───→  ai-docs/docs/architecture/*.md
    └── rtm-template.md        ─────→  ai-docs/docs/rtm.md
```

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| [CLAUDE.md](../../CLAUDE.md) | Главная точка входа |
| [workflow.md](../../workflow.md) | Процесс разработки |
| [target-project-structure.md](../target-project-structure.md) | Структура целевого проекта |
