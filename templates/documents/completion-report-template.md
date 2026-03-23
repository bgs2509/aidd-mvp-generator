---
# === YAML Frontmatter (machine-readable metadata) ===
feature_id: "{FID}"
feature_name: "{slug}"
title: "Completion Report: {Project/Feature Name}"
created: "{YYYY-MM-DD}"
deployed: "{YYYY-MM-DD}"
author: "AI (Validator)"
type: "completion"
status: "DEPLOYED"
version: 1

# Quality metrics (final)
metrics:
  coverage_percent: 0
  tests_passed: 0
  tests_total: 0
  security_issues: 0

# Implemented services
services: []

# Number of ADRs
adr_count: 0

# Links to ALL feature artifacts
artifacts:
  prd: "prd/{YYYY-MM-DD}_{FID}_{slug}-prd.md"
  research: "research/{YYYY-MM-DD}_{FID}_{slug}-research.md"
  plan: "architecture/{YYYY-MM-DD}_{FID}_{slug}-plan.md"
  # completion report — the only artifact of the Quality & Deploy stage

# Dependencies
depends_on: []           # FIDs of features this one depends on
enables: []              # Potential features that may use this one
---

# Completion Report: {Project/Feature Name}

> **Feature ID**: {FID}
> **Status**: DEPLOYED
> **Created**: {YYYY-MM-DD}
> **Deployed**: {YYYY-MM-DD}
> **Author**: AI Agent (Validator)

---

## 1. Executive Summary

{2-3 sentences about what was created, what problem it solves, and who it is intended for}

### 1.1 Key Results

| Metric | Value |
|--------|-------|
| Services created | {N} |
| Test coverage | {XX}% |
| Requirements implemented | {N}/{M} |
| ADRs documented | {N} |
| All gates passed | ✅ |

### 1.2 Created Services

- **{context}_{domain}_api** — {brief description}
- **{context}_{domain}_data** — {brief description}

---

## 2. Implemented Components

### 2.1 Services

| Service | Type | Purpose | Port | Key endpoints |
|---------|------|---------|------|---------------|
| {context}_{domain}_api | Business API | {description} | 8000 | `GET/POST /api/v1/{resource}` |
| {context}_{domain}_data | Data API | {description} | 8001 | `CRUD /api/v1/{entity}` |

### 2.2 Data Models

| Entity | DB Table | Key Fields | Relations |
|--------|----------|------------|-----------|
| {EntityName} | {table_name} | id, name, created_at, ... | FK → {other_table} |

### 2.3 API Endpoints

#### Business API ({context}_{domain}_api)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/{resource}` | {description} | {JWT/API Key/None} |
| POST | `/api/v1/{resource}` | {description} | {JWT/API Key/None} |

#### Data API ({context}_{domain}_data)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/{entity}` | Get list |
| GET | `/api/v1/{entity}/{id}` | Get by ID |
| POST | `/api/v1/{entity}` | Create |
| PUT | `/api/v1/{entity}/{id}` | Update |
| DELETE | `/api/v1/{entity}/{id}` | Delete |

### 2.4 Integrations

```
┌─────────────────┐      HTTP/JSON      ┌─────────────────┐      SQL      ┌──────────┐
│  Business API   │ ──────────────────► │    Data API     │ ────────────► │ Database │
│  (FastAPI)      │                     │    (FastAPI)    │               │(Postgres)│
└─────────────────┘                     └─────────────────┘               └──────────┘
```

- **Business API → Data API**: HTTP REST (JSON)
- **Data API → PostgreSQL**: SQLAlchemy async
- **External integrations**: {list if any}

---

## 3. Architecture Decision Records (ADR)

> **Purpose**: Documenting key architectural decisions and their rationale.
> This section is critically important for understanding **WHY** the system is built this way.

### ADR-001: {Decision Name}

| Aspect | Description |
|--------|-------------|
| **Decision** | {What was chosen — specific technical decision} |
| **Context** | {Why it was needed — business/technical context} |
| **Alternatives** | {What was considered and why it was rejected} |
| **Consequences** | **Pros**: ... / **Cons**: ... |
| **Status** | Accepted |
| **Date** | {YYYY-MM-DD} |

### ADR-002: HTTP-only Data Access

| Aspect | Description |
|--------|-------------|
| **Decision** | Business API accesses data only through Data API (HTTP), not directly to the DB |
| **Context** | DDD/Hexagonal architecture requirement, layer isolation |
| **Alternatives** | Direct DB access (rejected: violates boundaries), Shared DB (rejected: coupling) |
| **Consequences** | **Pros**: clean architecture, scalability / **Cons**: +1 network hop |
| **Status** | Accepted |
| **Date** | {YYYY-MM-DD} |

### ADR-003: {Next Decision}

{Continue using ADR-001 template}

---

## 4. Deviations from Plan (Scope Changes)

### 4.1 What Was Planned vs What Was Done

| Requirement | Plan | Actual | Reason for Change |
|-------------|------|--------|-------------------|
| {FR-XXX} | {What was planned} | {What was actually done} | {Why it changed} |
| {FR-YYY} | {Description} | Implemented as planned | — |

### 4.2 Deferred Items (postponed for the future)

> These requirements were consciously deferred and are NOT bugs or deficiencies.

| ID | Description | Reason for Deferral | Priority for Next Iteration |
|----|-------------|---------------------|----------------------------|
| {FR-XXX} | {what was deferred} | {why} | High / Medium / Low |

### 4.3 Added Requirements (not in PRD)

| ID | Description | Reason for Addition |
|----|-------------|---------------------|
| {FR-NEW-XXX} | {what was added} | {why it was needed} |

---

## 5. Known Limitations and Technical Debt

### 5.1 Known Limitations

> Limitations that were **consciously accepted** for the MVP. These are NOT bugs.

| ID | Description | Impact | Workaround |
|----|-------------|--------|------------|
| KL-001 | {limitation description} | {what it affects} | {how to work around it if needed} |
| KL-002 | {description} | {impact} | {workaround} |

### 5.2 Technical Debt

> Technical debt that needs to be addressed in future iterations.

| ID | Description | Priority | Recommendation |
|----|-------------|----------|----------------|
| TD-001 | {what needs improvement} | High / Medium / Low | {how to fix} |
| TD-002 | {description} | {priority} | {recommendation} |

### 5.3 Security Considerations

| Aspect | Status | Comment |
|--------|--------|---------|
| Secrets in .env | ✅ | Not in git, .gitignore configured |
| Hardcoded credentials | ✅ | None present |
| Input validation | ✅ | Pydantic schemas |
| SQL Injection | ✅ | SQLAlchemy ORM |
| Auth/AuthZ | {✅/⚠️} | {comment} |

---

## 6. Quality Metrics

### 6.1 Test Coverage

| Service | Unit Tests | Integration Tests | Coverage |
|---------|------------|-------------------|----------|
| {context}_{domain}_api | {N} passed | {N} passed | {XX}% |
| {context}_{domain}_data | {N} passed | {N} passed | {XX}% |
| **TOTAL** | **{N}** | **{N}** | **{XX}%** |

### 6.2 Code Quality

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Test Coverage | {XX}% | >= 75% | ✅/❌ |
| Cyclomatic Complexity (avg) | {X} | <= 10 | ✅/❌ |
| Code Duplication | {X}% | <= 5% | ✅/❌ |
| Type Hints Coverage | {XX}% | >= 90% | ✅/❌ |

### 6.3 Security Scan Results

| Tool | Critical | High | Medium | Low |
|------|----------|------|--------|-----|
| Bandit | 0 | 0 | {N} | {N} |
| Safety | 0 | 0 | {N} | {N} |

---

## 7. Dependencies

### 7.1 Depends On (depends_on)

| FID | Feature Name | How It Is Used |
|-----|--------------|----------------|
| — | — | Independent feature (first in the project) |

*Or if there are dependencies:*

| FID | Feature Name | How It Is Used |
|-----|--------------|----------------|
| F001 | {name} | {integration description} |

### 7.2 Enables (enables)

> What potential features can be built on top of this one.

| Potential Feature | How It Can Use This |
|-------------------|---------------------|
| {feature description} | Through API endpoint `/api/v1/{resource}` |
| {description} | Uses data model {Entity} |

---

## 8. Artifact Links

| Artifact | Path | Status | Description |
|----------|------|--------|-------------|
| PRD | `ai-docs/docs/_analysis/{date}_{FID}_{slug}-prd.md` | ✅ | Requirements |
| Research | `ai-docs/docs/research/{date}_{FID}_{slug}-research.md` | ✅ | Analysis |
| Architecture Plan | `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}-plan.md` | ✅ | Architecture |

---

## 9. Timeline (Development History)

| Date | Stage | Gate | Comment |
|------|-------|------|---------|
| {YYYY-MM-DD} | Idea | PRD_READY | PRD created and approved |
| {YYYY-MM-DD} | Research | RESEARCH_DONE | Analysis completed |
| {YYYY-MM-DD} | Architecture | PLAN_APPROVED | Plan approved by user |
| {YYYY-MM-DD} | Implementation | IMPLEMENT_OK | Code written |
| {YYYY-MM-DD} | Review | REVIEW_OK | Code reviewed |
| {YYYY-MM-DD} | QA | QA_PASSED | Tests passed (coverage >=75%) |
| {YYYY-MM-DD} | Validation | ALL_GATES_PASSED | All checks passed |
| {YYYY-MM-DD} | Deploy | DEPLOYED | Application launched |

**Total development time**: {N} days

---

## 10. Recommendations for Next Iterations

### 10.1 High Priority

1. {Recommendation 1 — what needs to be done first}
2. {Recommendation 2}

### 10.2 Medium Priority

1. {Recommendation — improvements}
2. {Recommendation}

### 10.3 Low Priority (nice-to-have)

1. {Recommendation — optional improvements}

---

## Conclusion

**Feature status**: DEPLOYED

**Summary**:
{1-2 paragraphs with a general description of what was done, what key decisions were made,
what limitations exist, and what is recommended for next iterations}

---

**Document created**: {YYYY-MM-DD}
**Author**: AI Agent (Validator)
**Version**: 1.0

---

## For AI Agents: Quick Reference

> This section is intended for quick context understanding by an AI agent in a new session.

```yaml
# Copy into context when working with this feature:
feature_id: {FID}
feature_name: {slug}
status: DEPLOYED
services:
  - {context}_{domain}_api (port 8000)
  - {context}_{domain}_data (port 8001)
key_endpoints:
  - GET /api/v1/{resource}
  - POST /api/v1/{resource}
key_entities:
  - {EntityName}
depends_on: []
known_limitations:
  - KL-001: {brief description}
technical_debt:
  - TD-001: {brief description}
```
