# AIDD-MVP Artifact Catalog

> **Purpose**: Complete catalog of all artifacts created during MVP generation.
> For each artifact the template, path, and readiness criteria are specified.

---

## Overview

```
GENERATOR (templates)                →    TARGET PROJECT (artifacts)
templates/documents/prd-template.md  →    ai-docs/docs/_analysis/{name}-prd.md
templates/documents/research-report-template.md →    ai-docs/docs/research/{name}-research.md
templates/documents/architecture-*.md →    ai-docs/docs/_plans/mvp/{name}-plan.md
templates/services/*                 →    services/{name}_{type}/
```

---

## Stage 1: Idea (PRD)

### PRD Document

| Parameter | Value |
|-----------|-------|
| **Command** | `/idea` |
| **Agent** | Analyst |
| **Template (generator)** | `templates/documents/prd-template.md` |
| **Path (Target Project)** | `ai-docs/docs/_analysis/{name}-prd.md` |
| **Gates** | `PRD_READY` |

**Readiness criteria**:
- [ ] All sections filled
- [ ] Requirements have IDs (FR-*, NF-*, UI-*)
- [ ] Acceptance criteria defined
- [ ] No blocking Open questions

**Example file name**: `booking-restaurant-prd.md`

---

## Stage 2: Research

### Research Report

| Parameter | Value |
|-----------|-------|
| **Command** | `/research` |
| **Agent** | Researcher |
| **Template (generator)** | `templates/documents/research-report-template.md` |
| **Path (Target Project)** | `ai-docs/docs/research/{name}-research.md` |
| **Gates** | `RESEARCH_DONE` |

**Readiness criteria**:
- [ ] Code and/or requirements analyzed
- [ ] Patterns and constraints described in report
- [ ] Integration recommendations formulated
- [ ] `.pipeline-state.json` updated (`RESEARCH_DONE`)

---

## Stage 3: Architecture

### Architecture Plan (CREATE)

| Parameter | Value |
|-----------|-------|
| **Command** | `/plan` |
| **Agent** | Planner |
| **Template (generator)** | `templates/documents/architecture-template.md` |
| **Path (Target Project)** | `ai-docs/docs/_plans/mvp/{name}-plan.md` |
| **Gates** | `PLAN_APPROVED` |

### Feature Plan (FEATURE)

| Parameter | Value |
|-----------|-------|
| **Command** | `/feature-plan` |
| **Agent** | Planner |
| **Template (generator)** | `templates/documents/feature-plan-template.md` |
| **Path (Target Project)** | `ai-docs/docs/_plans/features/{feature}-plan.md` |
| **Gates** | `PLAN_APPROVED` |

**Readiness criteria**:
- [ ] System components defined
- [ ] API contracts described
- [ ] NFR accounted for
- [ ] **Plan approved by user**

**Example file name**: `booking-restaurant-plan.md`, `notifications-plan.md`

---

## Stage 4: Implementation

### Infrastructure

| Artifact | Template (generator) | Path (Target Project) |
|----------|---------------------|-----------------------|
| Docker Compose | `templates/infrastructure/docker-compose.yml` | `docker-compose.yml` |
| Docker Dev | `templates/infrastructure/docker-compose.dev.yml` | `docker-compose.dev.yml` |
| Makefile | `templates/infrastructure/Makefile` | `Makefile` |
| .env | `templates/infrastructure/.env.example` | `.env.example` |

### Services

| Service Type | Template (generator) | Path (Target Project) |
|-------------|---------------------|-----------------------|
| Business API | `templates/services/fastapi_business_api/` | `services/{name}_api/` |
| Telegram Bot | `templates/services/aiogram_bot/` | `services/{name}_bot/` |
| Background Worker | `templates/services/asyncio_worker/` | `services/{name}_worker/` |
| Data API (PostgreSQL) | `templates/services/postgres_data_api/` | `services/{name}_data/` |
| Data API (MongoDB) | `templates/services/mongo_data_api/` | `services/{name}_data/` |

### Tests

| Artifact | Path (Target Project) |
|----------|-----------------------|
| Unit tests | `services/{name}/tests/unit/` |
| Integration tests | `services/{name}/tests/integration/` |
| conftest.py | `services/{name}/tests/conftest.py` |

**Readiness criteria (IMPLEMENT_OK)**:
- [ ] Code written according to plan
- [ ] Structure follows DDD/Hexagonal
- [ ] Type hints present
- [ ] All unit tests pass

---

## Stage 5: Review

### Review Report

| Parameter | Value |
|-----------|-------|
| **Command** | `/review` |
| **Agent** | Reviewer |
| **Path (Target Project)** | `ai-docs/docs/_validation/review-report.md` |
| **Gates** | `REVIEW_OK` |

**Readiness criteria**:
- [ ] Code follows conventions.md
- [ ] Architecture matches the plan
- [ ] No Blocker/Critical findings
- [ ] DRY/KISS/YAGNI followed

---

## Stage 6: QA

### QA Report

| Parameter | Value |
|-----------|-------|
| **Command** | `/test` |
| **Agent** | QA |
| **Path (Target Project)** | `ai-docs/docs/_validation/qa-report.md` |
| **Gates** | `QA_PASSED` |

**Readiness criteria**:
- [ ] All tests pass
- [ ] Coverage ≥75%
- [ ] No Critical/Blocker bugs
- [ ] PRD requirements verified

---

## Stage 7: Validation

### Validation Report

| Parameter | Value |
|-----------|-------|
| **Command** | `/validate` |
| **Agent** | Validator |
| **Path (Target Project)** | `ai-docs/docs/_validation/validation-report.md` |
| **Gates** | `ALL_GATES_PASSED` |

### RTM (Requirements Traceability Matrix)

| Parameter | Value |
|-----------|-------|
| **Template (generator)** | `templates/documents/rtm-template.md` |
| **Path (Target Project)** | `ai-docs/docs/rtm.md` |

**Readiness criteria**:
- [ ] All previous gates passed
- [ ] All artifacts exist
- [ ] RTM is up to date
- [ ] Project ready for deploy

---

## Stage 8: Deploy

### Running Application

| Parameter | Value |
|-----------|-------|
| **Command** | `/deploy` |
| **Agent** | Validator |
| **Gates** | `DEPLOYED` |

**Readiness criteria**:
- [ ] Docker containers built
- [ ] Application running
- [ ] Health-check passes
- [ ] Basic scenarios work

---

## Service Artifacts

### Pipeline State

| Parameter | Value |
|-----------|-------|
| **Template (generator)** | `templates/documents/pipeline-state-template.json` |
| **Path (Target Project)** | `.pipeline-state.json` |

**Purpose**: Stores the current pipeline state, passed gates, artifact paths.

---

## Summary Table

| Stage | Artifact | Path in Target Project | Gates |
|-------|----------|------------------------|-------|
| 1 | PRD | `ai-docs/docs/_analysis/{name}-prd.md` | PRD_READY |
| 2 | Research Report | `ai-docs/docs/research/{name}-research.md` | RESEARCH_DONE |
| 3 | Plan | `ai-docs/docs/_plans/mvp/{name}-plan.md` | PLAN_APPROVED |
| 4 | Code | `services/`, `docker-compose.yml` | IMPLEMENT_OK |
| 5 | Review | `ai-docs/docs/_validation/review-report.md` | REVIEW_OK |
| 6 | QA | `ai-docs/docs/_validation/qa-report.md` | QA_PASSED |
| 7 | Validation | `ai-docs/docs/_validation/validation-report.md`, `rtm.md` | ALL_GATES_PASSED |
| 8 | Deploy | Running application | DEPLOYED |

---

**Version**: 1.0
**Created**: 2025-12-21
