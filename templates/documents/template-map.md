# Template Map — Template-to-Output Mapping

> **Purpose**: Mapping between generator templates and the result in the Target Project (TP).
> Helps understand what each template produces.

---

## Overview

```
GENERATOR (templates/)           →         TARGET PROJECT
─────────────────────────────────────────────────────────
templates/services/              →    services/{name}_{type}/
templates/shared/                →    services/{name}_api/src/shared/
templates/infrastructure/        →    {project-name}/
templates/documents/                  →    ai-docs/docs/
```

---

## Service Templates

### fastapi_business_api/

| Template | Result | Description |
|----------|--------|-------------|
| `src/api/` | `services/{name}_api/src/api/` | REST API routers |
| `src/application/` | `services/{name}_api/src/application/` | Application services |
| `src/domain/` | `services/{name}_api/src/domain/` | Domain entities |
| `src/infrastructure/` | `services/{name}_api/src/infrastructure/` | HTTP clients |
| `src/schemas/` | `services/{name}_api/src/schemas/` | Pydantic schemas |
| `src/core/` | `services/{name}_api/src/core/` | Config, logging |
| `tests/` | `services/{name}_api/tests/` | Unit + Integration |
| `Dockerfile` | `services/{name}_api/Dockerfile` | Container build |

**Example**: `booking_api/`

### postgres_data_api/

| Template | Result | Description |
|----------|--------|-------------|
| `src/api/` | `services/{name}_data/src/api/` | CRUD endpoints |
| `src/domain/entities/` | `services/{name}_data/src/domain/entities/` | SQLAlchemy models |
| `src/repositories/` | `services/{name}_data/src/repositories/` | DB repositories |
| `alembic/` | `services/{name}_data/alembic/` | Migrations |
| `Dockerfile` | `services/{name}_data/Dockerfile` | Container build |

**Example**: `booking_data/`

### aiogram_bot/

| Template | Result | Description |
|----------|--------|-------------|
| `src/handlers/` | `services/{name}_bot/src/handlers/` | Telegram handlers |
| `src/keyboards/` | `services/{name}_bot/src/keyboards/` | Inline/Reply keyboards |
| `src/states/` | `services/{name}_bot/src/states/` | FSM states |
| `src/middlewares/` | `services/{name}_bot/src/middlewares/` | Bot middlewares |

**Example**: `booking_bot/`

### asyncio_worker/

| Template | Result | Description |
|----------|--------|-------------|
| `src/tasks/` | `services/{name}_worker/src/tasks/` | Task handlers |
| `src/processor.py` | `services/{name}_worker/src/processor.py` | Task processor |
| `src/scheduler.py` | `services/{name}_worker/src/scheduler.py` | Task scheduler |

**Example**: `booking_worker/`

---

## Infrastructure Templates

### infrastructure/

| Template | Result | Description |
|----------|--------|-------------|
| `docker-compose.yml` | `docker-compose.yml` | Orchestration |
| `docker-compose.dev.yml` | `docker-compose.dev.yml` | Dev environment |
| `.env.example` | `.env.example` | Environment variables |
| `Makefile` | `Makefile` | Build commands |

### CI/CD (optional)

CI/CD configuration is not generated automatically. Add it manually for your tool.

### nginx/

| Template | Result | Description |
|----------|--------|-------------|
| `nginx.conf` | `nginx/nginx.conf` | API Gateway |
| `Dockerfile` | `nginx/Dockerfile` | Nginx container |

---

## Document Templates

### templates/documents/

| Generator Template | Result in Target Project | Stage |
|--------------------|--------------------------|-------|
| `prd-template.md` | `ai-docs/docs/_analysis/{name}-prd.md` | 1 (Idea) |
| `research-report-template.md` | `ai-docs/docs/research/{name}-research.md` | 2 (Research) |
| `architecture-template.md` | `ai-docs/docs/_plans/mvp/{name}-plan.md` | 3 (Architecture) |
| `feature-plan-template.md` | `ai-docs/docs/_plans/features/{feature}-plan.md` | 3 (FEATURE) |
| `rtm-template.md` | `ai-docs/docs/rtm.md` | 7 (Validation) |
| `pipeline-state-template.json` | `.pipeline-state.json` | 1 (Idea) |

---

## Shared Components

### shared/

| Template | Result | Used in |
|----------|--------|---------|
| `http_client/` | `services/{name}_api/src/infrastructure/http/` | Business API |
| `logging/` | `services/*/src/core/logging.py` | All services |
| `health/` | `services/*/src/api/health.py` | All services |
| `exceptions/` | `services/*/src/core/exceptions.py` | All services |

---

## Transformations During Copying

### File Replacements

| Placeholder | Replaced with | Example |
|-------------|---------------|---------|
| `{context}` | Project context | `booking` |
| `{domain}` | Domain | `restaurant` |
| `{name}` | Full name | `booking_restaurant` |
| `{type}` | Service type | `api`, `data`, `bot` |
| `{entity}` | Entity name | `Restaurant`, `Booking` |

### Transformation Example

```
templates/services/fastapi_business_api/src/api/v1/{entity}_router.py
                                        ↓
services/booking_api/src/api/v1/restaurants_router.py
```

---

## Visual Map

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
│
└── templates/documents/
    ├── prd-template.md        ─────→  ai-docs/docs/_analysis/*.md
    ├── architecture-template.md ───→  ai-docs/docs/_plans/mvp/*.md
    └── rtm-template.md        ─────→  ai-docs/docs/rtm.md
```

---

## Related Documents

| Document | Description |
|----------|-------------|
| [CLAUDE.md](../../CLAUDE.md) | Main entry point |
| [workflow.md](../../workflow.md) | Development process |
| [target-project-structure.md](../../docs/target-project-structure.md) | Target Project structure |
