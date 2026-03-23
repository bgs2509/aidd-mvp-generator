# Function: Creating an Implementation Plan

> **Purpose**: Forming an implementation plan for the Coder.

---

## Goal

Create a detailed implementation plan that the Coder
can execute sequentially, stage by stage.

---

## Implementation Plan Structure

```markdown
# Implementation Plan: {Project Name}

**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Author**: AI Agent (Planner)
**Mode**: CREATE | FEATURE

---

## 1. Overview

### 1.1 Implementation Goal
{What will be created}

### 1.2 Components
{List of components to implement}

### 1.3 Dependencies
{External dependencies}

---

## 2. Implementation Stages

### Stage 4.1: Infrastructure

| # | Task | Files | Depends on |
|---|------|-------|------------|
| 4.1.1 | Create project structure | — | — |
| 4.1.2 | Create docker-compose.yml | docker-compose.yml | 4.1.1 |
| 4.1.3 | Create .env.example | .env.example | 4.1.1 |
| 4.1.4 | Create Makefile | Makefile | 4.1.2 |
| 4.1.5 | Set up CI pipeline (optional) | {specify path} | 4.1.1 |

### Stage 4.2: Data Service

| # | Task | Files | Depends on |
|---|------|-------|------------|
| 4.2.1 | Create service structure | services/{context}_data/ | 4.1.1 |
| 4.2.2 | Create Dockerfile | Dockerfile | 4.2.1 |
| 4.2.3 | Create models | domain/entities/ | 4.2.1 |
| 4.2.4 | Create repositories | infrastructure/repositories/ | 4.2.3 |
| 4.2.5 | Create API routes | api/v1/ | 4.2.4 |
| 4.2.6 | Create main.py | main.py | 4.2.5 |

### Stage 4.3: Business API

| # | Task | Files | Depends on |
|---|------|-------|------------|
| 4.3.1 | Create service structure | services/{context}_api/ | 4.1.1 |
| 4.3.2 | Create Dockerfile | Dockerfile | 4.3.1 |
| 4.3.3 | Create HTTP client | infrastructure/http/ | 4.3.1 |
| 4.3.4 | Create services | application/services/ | 4.3.3 |
| 4.3.5 | Create schemas | schemas/ | 4.3.1 |
| 4.3.6 | Create API routes | api/v1/ | 4.3.4, 4.3.5 |
| 4.3.7 | Create main.py | main.py | 4.3.6 |

### Stage 4.4: Telegram Bot (if needed)

| # | Task | Files | Depends on |
|---|------|-------|------------|
| 4.4.1 | Create service structure | services/{context}_bot/ | 4.1.1 |
| 4.4.2 | Create Dockerfile | Dockerfile | 4.4.1 |
| 4.4.3 | Create HTTP client | infrastructure/http/ | 4.4.1 |
| 4.4.4 | Create handlers | handlers/ | 4.4.3 |
| 4.4.5 | Create keyboards | keyboards/ | 4.4.1 |
| 4.4.6 | Create states | states/ | 4.4.1 |
| 4.4.7 | Create main.py | main.py | 4.4.4, 4.4.5, 4.4.6 |

### Stage 4.5: Background Worker (if needed)

| # | Task | Files | Depends on |
|---|------|-------|------------|
| 4.5.1 | Create service structure | services/{context}_worker/ | 4.1.1 |
| 4.5.2 | Create Dockerfile | Dockerfile | 4.5.1 |
| 4.5.3 | Create task handlers | tasks/ | 4.5.1 |
| 4.5.4 | Create scheduler | scheduler.py | 4.5.3 |
| 4.5.5 | Create main.py | main.py | 4.5.4 |

### Stage 4.6: Testing

| # | Task | Files | Depends on |
|---|------|-------|------------|
| 4.6.1 | Create conftest.py | tests/conftest.py | 4.2-4.5 |
| 4.6.2 | Unit tests for Data Service | tests/unit/ | 4.2.6 |
| 4.6.3 | Unit tests for Business API | tests/unit/ | 4.3.7 |
| 4.6.4 | Integration tests | tests/integration/ | 4.6.2, 4.6.3 |

---

## 3. Requirements Traceability

| Req ID | Description | Stage | Files |
|--------|-------------|-------|-------|
| FR-001 | {Description} | 4.3.6 | api/v1/routes.py |
| FR-002 | {Description} | 4.2.5 | api/v1/routes.py |

---

## 4. Templates to Use

| Component | Template |
|-----------|----------|
| Business API | templates/services/fastapi_business_api/ |
| Data API | templates/services/postgres_data_api/ |
| Telegram Bot | templates/services/aiogram_bot/ |
| Worker | templates/services/asyncio_worker/ |

---

## 5. Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| DATABASE_URL | Data API | PostgreSQL connection |
| DATA_API_URL | Business API | Data API URL |
| BOT_TOKEN | Bot | Telegram bot token |

---

## Quality Gates: PLAN_APPROVED

- [ ] All stages are defined
- [ ] Dependencies between tasks are specified
- [ ] All FRs are covered in traceability
- [ ] Templates are specified for all components
- [ ] Environment variables are defined
```

---

## Plan Formation Rules

### 1. Stage Order

```
RULE: Stages are executed strictly sequentially.

4.1 Infrastructure → always first
4.2 Data Service → before Business API
4.3 Business API → after Data Service
4.4 Bot / 4.5 Worker → after Business API
4.6 Tests → last stage
```

### 2. Dependencies

```
RULE: Each task specifies its dependencies.

Example:
- 4.2.5 (API routes) depends on 4.2.4 (repositories)
- 4.3.4 (services) depends on 4.3.3 (HTTP client)
```

### 3. Traceability

```
RULE: Each FR must be covered by at least one task.

FR-001 → 4.3.6 (Business API routes)
FR-002 → 4.2.5 (Data API routes)
```

### 4. Templates

```
RULE: Specify a template for each component.

Business API → templates/services/fastapi_business_api/
Data API PG → templates/services/postgres_data_api/
```

---

## FEATURE Mode

For adding functionality, the plan is simplified:

```markdown
# Feature Implementation Plan: {Feature Name}

## 1. Changes in Existing Services

### Data Service

| # | Task | Files |
|---|------|-------|
| 1.1 | Add model | domain/entities/new_entity.py |
| 1.2 | Add migration | migrations/ |
| 1.3 | Add repository | infrastructure/repositories/ |
| 1.4 | Add endpoints | api/v1/new_routes.py |

### Business API

| # | Task | Files |
|---|------|-------|
| 2.1 | Update HTTP client | infrastructure/http/client.py |
| 2.2 | Add service | application/services/new_service.py |
| 2.3 | Add endpoints | api/v1/new_routes.py |

## 2. New Tests

| # | Task | Files |
|---|------|-------|
| 3.1 | Unit tests | tests/unit/test_new_feature.py |
| 3.2 | Integration tests | tests/integration/test_new_feature.py |
```

---

## Save Path

```
ai-docs/docs/_plans/features/{name}-implementation-plan.md

Examples:
- ai-docs/docs/_plans/features/booking-implementation-plan.md
- ai-docs/docs/_plans/features/notifications-feature-plan.md
```

---

## References

| Document | Description |
|----------|-------------|
| `workflow.md` | Stage descriptions |
| `knowledge/architecture/project-structure.md` | Project structure |
| `roles/coder/` | Coder instructions |
