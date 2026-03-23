---
# === YAML Frontmatter (machine-readable metadata) ===
feature_id: "{FID}"
feature_name: "{slug}"
title: "Implementation Plan: {Feature/Project Name}"
created: "{YYYY-MM-DD}"
author: "AI (Architect)"
type: "plan"
status: "PLAN_APPROVED"
version: 1
mode: "CREATE"

# Links to related artifacts
prd_ref: "prd/{YYYY-MM-DD}_{FID}_{slug}-prd.md"
research_ref: "research/{YYYY-MM-DD}_{FID}_{slug}-research.md"
architecture_ref: "architecture/{YYYY-MM-DD}_{FID}_{slug}-architecture.md"

# Services to create
services:
  - "{context}_api"
  - "{context}_data"

# Optional
approved_by: null
approved_at: null
stages_count: 0
tasks_count: 0
---

# Implementation Plan: {Feature/Project Name}

**Feature ID**: {FID}
**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Author**: AI Agent (Planner)
**Status**: Draft | Review | Approved
**Related PRD**: {prd-name}-prd.md
**Architecture**: {architecture-name}.md

---

## 1. Overview

### 1.1 Goal

{Brief description of what will be implemented}

### 1.2 Scope

**In scope:**
- {Included item 1}
- {Included item 2}
- {Included item 3}

**Out of scope:**
- {Excluded item 1}
- {Excluded item 2}

### 1.3 Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| {Dependency 1} | Blocking | Ready/Pending |
| {Dependency 2} | Desirable | Ready/Pending |

---

## 2. Implementation Stages

### Stage 4.1: Infrastructure

**Goal**: Prepare the project's base infrastructure

**Tasks**:

| # | Task | Files | Requirement |
|---|------|-------|-------------|
| 4.1.1 | Create project structure | All directories | — |
| 4.1.2 | Set up docker-compose.yml | docker-compose.yml | — |
| 4.1.3 | Create .env.example | .env.example | — |
| 4.1.4 | Set up CI pipeline (optional) | {specify path} | — |
| 4.1.5 | Create Makefile | Makefile | — |

**Completion criteria**:
- [ ] `docker compose up` starts without errors
- [ ] All services pass health check
- [ ] CI pipeline passes (if configured)

---

### Stage 4.2: Data API

**Goal**: Implement data access through HTTP API

**Tasks**:

| # | Task | Files | Requirement |
|---|------|-------|-------------|
| 4.2.1 | Create SQLAlchemy models | domain/entities/*.py | FR-001 |
| 4.2.2 | Set up Alembic migrations | alembic/versions/*.py | — |
| 4.2.3 | Implement repositories | repositories/*.py | — |
| 4.2.4 | Create CRUD endpoints | api/v1/*.py | FR-001-004 |
| 4.2.5 | Write tests | tests/unit/*.py | — |

**Data models**:

```python
# {Entity} model
class {Entity}(Base):
    __tablename__ = "{entities}"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    {field_1}: Mapped[str] = mapped_column(String(255))
    {field_2}: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())
```

**Endpoints**:

```
GET    /api/v1/{entities}           → List with pagination
POST   /api/v1/{entities}           → Create
GET    /api/v1/{entities}/{id}      → Get by ID
PUT    /api/v1/{entities}/{id}      → Update
DELETE /api/v1/{entities}/{id}      → Delete
```

**Completion criteria**:
- [ ] Migrations apply successfully
- [ ] All CRUD operations work
- [ ] Tests pass with coverage >= 75%

---

### Stage 4.3: Business API

**Goal**: Implement business logic

**Tasks**:

| # | Task | Files | Requirement |
|---|------|-------|-------------|
| 4.3.1 | Create HTTP client for Data API | infrastructure/http/data_client.py | — |
| 4.3.2 | Implement domain services | domain/services/*.py | FR-* |
| 4.3.3 | Implement application services | application/services/*.py | FR-* |
| 4.3.4 | Create API endpoints | api/v1/*.py | FR-* |
| 4.3.5 | Add validation | schemas/*.py | — |
| 4.3.6 | Write tests | tests/*.py | — |

**Business logic**:

```python
# {UseCase} use case
class {UseCase}Service:
    def __init__(self, data_client: DataAPIClient):
        self._data_client = data_client

    async def execute(self, request: {UseCase}Request) -> {UseCase}Response:
        # 1. Validate business rules
        # 2. Execute operation
        # 3. Return result
        pass
```

**Completion criteria**:
- [ ] Business API communicates with Data API
- [ ] Business rules implemented
- [ ] API documentation generated (OpenAPI)
- [ ] Tests pass

---

### Stage 4.4: Background Worker (if required)

**Goal**: Implement background tasks

**Tasks**:

| # | Task | Files | Requirement |
|---|------|-------|-------------|
| 4.4.1 | Create base worker | main.py, scheduler.py | — |
| 4.4.2 | Implement tasks | tasks/*.py | FR-* |
| 4.4.3 | Set up graceful shutdown | — | — |

**Completion criteria**:
- [ ] Worker starts and stops correctly
- [ ] Tasks execute on schedule

---

### Stage 4.5: Telegram Bot (if required)

**Goal**: Implement Telegram interface

**Tasks**:

| # | Task | Files | Requirement |
|---|------|-------|-------------|
| 4.5.1 | Set up bot | main.py, bot/ | — |
| 4.5.2 | Implement handlers | handlers/*.py | UI-* |
| 4.5.3 | Add FSM (if needed) | states/*.py | — |
| 4.5.4 | Create keyboards | keyboards/*.py | UI-* |

**Completion criteria**:
- [ ] Bot responds to /start
- [ ] Main scenarios work

---

### Stage 4.6: Testing

**Goal**: Ensure code quality

**Tasks**:

| # | Task | Files | Coverage |
|---|------|-------|----------|
| 4.6.1 | Data API unit tests | tests/unit/*.py | >= 75% |
| 4.6.2 | Business API unit tests | tests/unit/*.py | >= 75% |
| 4.6.3 | Integration tests | tests/integration/*.py | Key flows |
| 4.6.4 | E2E tests (optional) | tests/e2e/*.py | Happy path |

**Completion criteria**:
- [ ] Coverage >= 75% for each service
- [ ] All tests pass in CI
- [ ] Critical paths covered

---

## 3. Execution Order

```
Stage 4.1 (Infrastructure)
    │
    ▼
Stage 4.2 (Data API)
    │
    ├──────────────────┐
    ▼                  ▼
Stage 4.3          Stage 4.4/4.5
(Business API)     (Worker/Bot)
    │                  │
    └────────┬─────────┘
             ▼
      Stage 4.6 (Tests)
```

---

## 4. Files to Create

### 4.1 Data API ({context}_data)

```
services/{context}_data/
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── {entities}.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── logging.py
│   ├── domain/
│   │   ├── __init__.py
│   │   └── entities/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       └── {entity}.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── {entity}_repository.py
│   └── schemas/
│       ├── __init__.py
│       └── {entity}.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── unit/
        └── test_{entity}_repository.py
```

### 4.2 Business API ({context}_api)

```
services/{context}_api/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── {domain}.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   └── {use_case}_service.py
│   │   └── dtos/
│   │       └── {domain}.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── http/
│   │       ├── __init__.py
│   │       └── data_client.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   └── schemas/
│       └── {domain}.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── unit/
        └── test_{use_case}_service.py
```

---

## 5. Requirements Traceability

| Requirement | Stage | Task | File | Test |
|-------------|-------|------|------|------|
| FR-001 | 4.2 | 4.2.1, 4.2.4 | entities.py | test_*.py |
| FR-002 | 4.3 | 4.3.3, 4.3.4 | service.py | test_*.py |
| NF-001 | 4.6 | 4.6.3 | — | integration |

---

## 6. Implementation Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| {Risk 1} | Medium | High | {Action} |
| {Risk 2} | Low | Medium | {Action} |

---

## Quality Gates

### IMPLEMENTATION_READY Checklist

- [ ] All stages defined
- [ ] Tasks detailed
- [ ] Files to create listed
- [ ] Requirements traced to tasks
- [ ] Execution order defined
- [ ] Completion criteria for each stage are clear
