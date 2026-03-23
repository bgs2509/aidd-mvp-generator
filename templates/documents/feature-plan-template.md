---
# === YAML Frontmatter (machine-readable metadata) ===
feature_id: "{FID}"
feature_name: "{slug}"
title: "Feature Plan: {Feature Name}"
created: "{YYYY-MM-DD}"
author: "AI (Architect)"
type: "feature-plan"
status: "PLAN_APPROVED"
version: 1
mode: "FEATURE"

# Links to related artifacts
prd_ref: "prd/{YYYY-MM-DD}_{FID}_{slug}-prd.md"
research_ref: "research/{YYYY-MM-DD}_{FID}_{slug}-research.md"

# Affected services
affected_services:
  modified: []                         # Existing services to modify
  created: []                          # New services to create

# Optional
related_features: []
approved_by: null
approved_at: null
---

# Feature Integration Plan: {Feature Name}

**Feature ID**: {FID}
**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Author**: AI Agent (Planner)
**Status**: Draft | Review | Approved
**Mode**: FEATURE
**Related PRD**: {prd-name}-prd.md

---

## 1. Feature Overview

### 1.1 Goal

{Brief description of what will be added to the existing project}

### 1.2 Scope

**In scope:**
- {Included item 1}
- {Included item 2}
- {Included item 3}

**Out of scope:**
- {Excluded item 1}
- {Excluded item 2}

---

## 2. Existing Architecture Analysis

### 2.1 Current Project Structure

```
{project_name}/
├── services/
│   ├── {existing_service_1}/    ← Will be modified
│   ├── {existing_service_2}/    ← No changes
│   └── {new_service}/           ← Will be created (if needed)
├── docker-compose.yml           ← Will be modified
└── ...
```

### 2.2 Affected Services

| Service | Change Type | Impact |
|---------|-------------|--------|
| {service_1} | Modification | High |
| {service_2} | No changes | — |
| {new_service} | Creation | — |

### 2.3 Existing Patterns

**Architectural patterns in the project:**
- {Pattern 1, e.g.: HTTP-only data access}
- {Pattern 2, e.g.: DDD/Hexagonal structure}
- {Pattern 3, e.g.: Async-first approach}

**Code conventions:**
- {Convention 1}
- {Convention 2}

**Important**: New code MUST follow existing patterns.

---

## 3. Impact Matrix

### 3.1 Impact on Existing Components

| Component | Impact Type | Risk | Description |
|-----------|-------------|------|-------------|
| {Data model X} | Extension | Low | Adding new fields |
| {API endpoint Y} | Modification | Medium | Changing response |
| {Service Z} | No changes | — | Not affected |

### 3.2 Dependencies

| Dependency | Type | Status | Action |
|------------|------|--------|--------|
| {Existing service} | Internal | Ready | Use existing API |
| {External API} | External | Pending | Set up integration |
| {New library} | Package | Pending | Add to requirements.txt |

### 3.3 Backward Compatibility

| Aspect | Compatible? | Action if Not |
|--------|-------------|---------------|
| API contracts | Yes/No | {Action} |
| DB schema | Yes/No | {Migration} |
| Configuration | Yes/No | {Update .env.example} |

---

## 4. Integration Plan

### Stage 4.1: Infrastructure Preparation (if required)

**Goal**: Prepare the environment for the new feature

**Tasks**:

| # | Task | Files | Change |
|---|------|-------|--------|
| 4.1.1 | Update docker-compose.yml | docker-compose.yml | Add service |
| 4.1.2 | Update .env.example | .env.example | New variables |
| 4.1.3 | Update requirements.txt | requirements.txt | New dependencies |

**Completion criteria**:
- [ ] `docker compose up` starts without errors
- [ ] All existing services work
- [ ] New environment variables documented

---

### Stage 4.2: Data API Extension

**Goal**: Add new data models or extend existing ones

**Tasks**:

| # | Task | Files | Requirement |
|---|------|-------|-------------|
| 4.2.1 | Create/extend models | domain/entities/{entity}.py | FR-* |
| 4.2.2 | Create migration | alembic/versions/{xxx}_add_{feature}.py | — |
| 4.2.3 | Extend repository | repositories/{entity}_repository.py | — |
| 4.2.4 | Add/extend endpoints | api/v1/{entity}.py | FR-* |
| 4.2.5 | Write tests | tests/unit/test_{entity}.py | — |

**Model changes**:

```python
# Extending existing model
class {Entity}(Base):
    # Existing fields...

    # New fields for the feature:
    {new_field_1}: Mapped[str | None] = mapped_column(String(255))
    {new_field_2}: Mapped[int] = mapped_column(default=0)
```

**New/modified endpoints**:

```
# New endpoints:
GET    /api/v1/{entities}/{id}/{feature}    → Get feature data
POST   /api/v1/{entities}/{id}/{feature}    → Create feature data

# Modified endpoints:
GET    /api/v1/{entities}/{id}              → Added {feature} to response
```

**Completion criteria**:
- [ ] Migration applies successfully (up and down)
- [ ] Existing tests are NOT broken
- [ ] New tests cover new functionality
- [ ] Coverage >= 75%

---

### Stage 4.3: Business API Extension

**Goal**: Add business logic for the feature

**Tasks**:

| # | Task | Files | Requirement |
|---|------|-------|-------------|
| 4.3.1 | Extend HTTP client | infrastructure/http/data_client.py | — |
| 4.3.2 | Create new domain service | domain/services/{feature}_service.py | FR-* |
| 4.3.3 | Create application service | application/services/{feature}_service.py | FR-* |
| 4.3.4 | Add API endpoints | api/v1/{feature}.py | FR-* |
| 4.3.5 | Add validation schemas | schemas/{feature}.py | — |
| 4.3.6 | Write tests | tests/unit/test_{feature}_service.py | — |

**Feature business logic**:

```python
# {Feature}Service
class {Feature}Service:
    def __init__(self, data_client: DataAPIClient):
        self._data_client = data_client

    async def {operation}(self, request: {Feature}Request) -> {Feature}Response:
        # 1. Validate business rules
        # 2. Get data via Data API
        # 3. Execute business logic
        # 4. Save result
        # 5. Return response
        pass
```

**Completion criteria**:
- [ ] New business logic integrated
- [ ] Existing endpoints continue working
- [ ] OpenAPI documentation updated
- [ ] Tests cover new functionality

---

### Stage 4.4: UI Integration (if required)

**Goal**: Update the user interface (Telegram Bot / Web)

**For Telegram Bot**:

| # | Task | Files | Requirement |
|---|------|-------|-------------|
| 4.4.1 | Add new handlers | handlers/{feature}.py | UI-* |
| 4.4.2 | Extend keyboards | keyboards/{feature}.py | UI-* |
| 4.4.3 | Add FSM states (if needed) | states/{feature}.py | — |
| 4.4.4 | Update menu/navigation | handlers/menu.py | — |

**Completion criteria**:
- [ ] New functionality is accessible to the user
- [ ] Navigation is intuitive
- [ ] Edge cases handled

---

### Stage 4.5: Integration Testing

**Goal**: Ensure the feature works in the context of the entire application

**Tasks**:

| # | Task | Files | Coverage |
|---|------|-------|----------|
| 4.5.1 | Unit tests for new functionality | tests/unit/*.py | >= 75% |
| 4.5.2 | Regression tests | tests/regression/*.py | Existing scenarios |
| 4.5.3 | Integration tests | tests/integration/*.py | New scenarios |
| 4.5.4 | Backward compatibility check | — | API contracts |

**Completion criteria**:
- [ ] All existing tests pass (regression)
- [ ] Coverage >= 75% for new code
- [ ] Integration tests cover key flows
- [ ] API is compatible with old clients

---

## 5. Execution Order

```
Stage 4.1 (Infrastructure)
    │
    ▼
Stage 4.2 (Data API)
    │
    ▼
Stage 4.3 (Business API)
    │
    ▼
Stage 4.4 (UI, if needed)
    │
    ▼
Stage 4.5 (Testing)
```

---

## 6. Files to Create/Modify

### 6.1 New Files

```
services/{service_name}/
├── src/
│   ├── domain/
│   │   ├── entities/{new_entity}.py          ← New
│   │   └── services/{feature}_service.py     ← New
│   ├── application/
│   │   └── services/{feature}_service.py     ← New
│   ├── api/v1/{feature}.py                   ← New
│   └── schemas/{feature}.py                  ← New
├── alembic/versions/{xxx}_add_{feature}.py   ← New
└── tests/
    └── unit/test_{feature}.py                ← New
```

### 6.2 Modified Files

```
services/{service_name}/
├── src/
│   ├── api/v1/router.py                      ← Add router
│   ├── infrastructure/http/data_client.py   ← Extend methods
│   └── core/config.py                        ← New settings (if needed)
├── requirements.txt                          ← New dependencies
└── tests/conftest.py                         ← New fixtures

# Project root level:
docker-compose.yml                            ← If new service
.env.example                                  ← New variables
```

---

## 7. Requirements Traceability

| Requirement | Stage | Task | File | Test |
|-------------|-------|------|------|------|
| FR-{XX1} | 4.2 | 4.2.1, 4.2.4 | {entity}.py | test_{entity}.py |
| FR-{XX2} | 4.3 | 4.3.2, 4.3.4 | {feature}_service.py | test_{feature}.py |
| NF-{XX1} | 4.5 | 4.5.3 | — | integration/*.py |

---

## 8. Integration Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing functionality | Medium | High | Full regression testing |
| Migration conflicts | Low | Medium | Check current migrations |
| API incompatibility | Low | High | API versioning (v1, v2) |
| Performance degradation | Low | Medium | Benchmark before and after |

---

## 9. Pre-Implementation Checklist

### FEATURE_PLAN_READY Checklist

**Analysis:**
- [ ] Existing architecture studied
- [ ] Affected services identified
- [ ] Impact matrix filled
- [ ] Backward compatibility verified

**Planning:**
- [ ] All stages defined
- [ ] Tasks detailed
- [ ] New/modified files listed
- [ ] Requirements traced to tasks

**Risks:**
- [ ] Integration risks assessed
- [ ] Mitigations defined

---

## 10. User Confirmation

> **ATTENTION**: The plan requires user confirmation before implementation.

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  USER CONFIRMATION REQUIRED                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Please confirm:                                                │
│                                                                 │
│  1. Feature scope is correct                                    │
│  2. Affected services are identified correctly                  │
│  3. Impact matrix meets expectations                            │
│  4. Risks are acceptable                                        │
│                                                                 │
│  After confirmation, the following will be set:                  │
│  gates.PLAN_APPROVED.passed = true                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
