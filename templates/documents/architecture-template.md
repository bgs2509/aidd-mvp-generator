---
# === YAML Frontmatter (machine-readable metadata) ===
feature_id: "{FID}"
feature_name: "{slug}"
title: "Architecture: {Project Name}"
created: "{YYYY-MM-DD}"
author: "AI (Architect)"
type: "architecture"
status: "PLAN_APPROVED"                # Draft → PLAN_APPROVED
version: 1
mode: "CREATE"

# Links to related artifacts
prd_ref: "prd/{YYYY-MM-DD}_{FID}_{slug}-prd.md"
research_ref: "research/{YYYY-MM-DD}_{FID}_{slug}-research.md"

# Services
services:
  - "{context}_api"
  - "{context}_data"

# Technologies
technologies:
  backend: "FastAPI"
  database: "PostgreSQL"
  cache: "Redis"

# Optional
approved_by: null
approved_at: null
---

# Architecture Plan: {Project Name}

**Feature ID**: {FID}
**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Author**: AI Agent (Planner)
**Status**: Draft | Review | Approved
**Related PRD**: {prd-name}-prd.md

---

## 1. Architecture Overview

### 1.1 Architectural Style

- **Core pattern**: Hexagonal Architecture (Ports & Adapters)
- **Data access principle**: HTTP-only (Data API)
- **Maturity Level**: Level 2 (MVP)

### 1.2 High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           Clients                                │
│  [Web App]  [Mobile App]  [Telegram Bot]  [External Systems]    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (Nginx)                         │
│              Rate Limiting, SSL Termination                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│  {context}_api  │ │  {bot}_bot  │ │ {worker}_worker │
│  Business API   │ │ Telegram Bot│ │ Background Jobs │
│    (FastAPI)    │ │  (Aiogram)  │ │   (asyncio)     │
└────────┬────────┘ └──────┬──────┘ └────────┬────────┘
         │                 │                  │
         └─────────────────┼──────────────────┘
                           │ HTTP
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    {context}_data                                │
│                    Data API (FastAPI)                            │
│              Repository Pattern, CRUD Operations                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ SQL
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       PostgreSQL                                 │
│                     Primary Database                             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Key Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Data access | HTTP-only through Data API | Isolation, independent scaling |
| Authentication | JWT tokens | Stateless, scalability |
| Communication | Synchronous HTTP | Simplicity for MVP |
| Logging | structlog JSON | Structured, ELK ready |

---

## 2. System Components

### 2.1 Services

#### {context}_api — Business API

**Purpose**: Main API for business logic

**Technologies**:
- FastAPI 0.100+
- Python 3.11+
- httpx (HTTP client)

**Structure**:
```
{context}_api/
├── src/
│   ├── api/                 # Endpoints
│   │   ├── v1/
│   │   │   ├── router.py
│   │   │   └── {domain}.py
│   │   └── dependencies.py
│   ├── application/         # Use cases
│   │   ├── services/
│   │   └── dtos/
│   ├── domain/              # Business logic
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   ├── infrastructure/      # External adapters
│   │   └── http/
│   ├── core/                # Config, logging
│   └── main.py
└── tests/
```

**Endpoints**:

| Method | Path | Description | Requirement |
|--------|------|-------------|-------------|
| GET | /api/v1/{entities} | List entities | FR-001 |
| POST | /api/v1/{entities} | Create | FR-002 |
| GET | /api/v1/{entities}/{id} | Get by ID | FR-001 |
| PUT | /api/v1/{entities}/{id} | Update | FR-003 |
| DELETE | /api/v1/{entities}/{id} | Delete | FR-004 |

---

#### {context}_data — Data API

**Purpose**: Single point of data access

**Technologies**:
- FastAPI 0.100+
- SQLAlchemy 2.0+ (async)
- Alembic (migrations)
- asyncpg

**Structure**:
```
{context}_data/
├── src/
│   ├── api/
│   │   └── v1/
│   ├── domain/
│   │   └── entities/       # SQLAlchemy models
│   ├── repositories/       # Data access
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   └── main.py
├── alembic/
│   └── versions/
└── tests/
```

---

### 2.2 Databases

#### PostgreSQL

**Version**: 15+

**Data schema**:

```sql
-- Example table
CREATE TABLE {entities} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    {field_1} VARCHAR(255) NOT NULL,
    {field_2} TEXT,
    {field_3} INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_{entities}_{field_1} ON {entities}({field_1});
CREATE INDEX idx_{entities}_created_at ON {entities}(created_at);
```

**ER Diagram**:

```
┌─────────────────┐       ┌─────────────────┐
│    {entity_1}   │       │    {entity_2}   │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │──┐    │ id (PK)         │
│ name            │  │    │ {entity_1}_id(FK)│──┐
│ ...             │  └────│ ...             │  │
│ created_at      │       │ created_at      │  │
└─────────────────┘       └─────────────────┘  │
                                               │
                          ┌─────────────────┐  │
                          │    {entity_3}   │  │
                          ├─────────────────┤  │
                          │ id (PK)         │  │
                          │ {entity_2}_id(FK)│◄─┘
                          │ ...             │
                          └─────────────────┘
```

---

### 2.3 Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Reverse Proxy | Nginx | SSL, Rate Limiting |
| Containerization | Docker | Service isolation |
| Orchestration | Docker Compose | Local development |
| CI/CD | {tool} | Automation |
| Registry | GHCR | Docker images |

---

## 3. API Contracts

### 3.1 General Conventions

- **Format**: JSON
- **Versioning**: URL path (/api/v1/)
- **Authentication**: Bearer JWT token
- **Pagination**: page + page_size
- **Sorting**: sort_by + sort_order

### 3.2 Response Format

**Successful response (single object)**:
```json
{
  "id": "uuid",
  "field_1": "value",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Successful response (list with pagination)**:
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

**Error response**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": {}
  }
}
```

### 3.3 Error Codes

| HTTP | Code | Description |
|------|------|-------------|
| 400 | VALIDATION_ERROR | Validation error |
| 401 | UNAUTHORIZED | Not authorized |
| 403 | FORBIDDEN | Access denied |
| 404 | NOT_FOUND | Not found |
| 409 | CONFLICT | Conflict |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Internal error |

---

## 4. Security

### 4.1 Authentication

```
┌──────────┐        ┌──────────┐        ┌──────────┐
│  Client  │──(1)──▶│   API    │──(2)──▶│  Auth    │
│          │◀──(4)──│ Gateway  │◀──(3)──│ Service  │
└──────────┘        └──────────┘        └──────────┘

(1) POST /auth/login {credentials}
(2) Validate credentials
(3) Generate JWT
(4) Return {access_token, refresh_token}
```

### 4.2 Authorization

- **Model**: RBAC (Role-Based Access Control)
- **Roles**: admin, user, guest
- **Enforcement**: Middleware + Dependencies

### 4.3 Data Protection

| Aspect | Measure |
|--------|---------|
| Transport | TLS 1.3 |
| Password storage | bcrypt/argon2 |
| Sensitive data | Encryption at rest |
| API keys | Vault/Secrets Manager |

---

## 5. Observability

### 5.1 Logging

- **Format**: JSON (structlog)
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Correlation**: X-Request-ID

### 5.2 Metrics (Level 3+)

- Request rate
- Response time (p50, p95, p99)
- Error rate
- Database connections
- Cache hit ratio

### 5.3 Health Checks

| Endpoint | Checks |
|----------|--------|
| /health | Service is running |
| /health/ready | All dependencies available |
| /health/live | Service is responding |

---

## 6. Scaling

### 6.1 Strategy

| Service | Type | Method |
|---------|------|--------|
| API | Stateless | Horizontal (replicas) |
| Data API | Stateless | Horizontal (replicas) |
| PostgreSQL | Stateful | Vertical / Read replicas |
| Redis | Stateful | Cluster mode |

### 6.2 Bottlenecks

| Component | Risk | Mitigation |
|-----------|------|------------|
| PostgreSQL | Connection limit | Connection pooling |
| API | CPU bound | Horizontal scaling |
| External API | Rate limits | Caching, queuing |

---

## 7. Deployment

### 7.1 Environments

| Environment | Purpose | URL |
|-------------|---------|-----|
| Development | Local development | localhost |
| Staging | Testing | staging.domain.com |
| Production | Live | domain.com |

### 7.2 Configuration

All settings via environment variables:

| Variable | Development | Production |
|----------|-------------|------------|
| DEBUG | true | false |
| LOG_LEVEL | DEBUG | INFO |
| DATABASE_URL | localhost | {secret} |

---

## 8. Requirements Traceability

| Requirement | Component | API | Table |
|-------------|-----------|-----|-------|
| FR-001 | {context}_api | GET /entities | {entities} |
| FR-002 | {context}_api | POST /entities | {entities} |
| FR-003 | {context}_api | PUT /entities/{id} | {entities} |
| NF-001 | All | — | — |

---

## 9. Test Plan

### 9.1 Smoke Tests (mandatory, inside services)

| Service | Endpoint | Test | Status |
|---------|----------|------|--------|
| {api} | GET /health | test_health_check | Planned |
| {api} | POST /users | test_create_user_happy | Planned |

### 9.2 Unit Tests (if TRQ-005 = Yes)

| Module | Function | Test | Mocks |
|--------|----------|------|-------|
| services/user | create_user() | test_create_user | DataApiClient |

### 9.3 Integration Tests (if TRQ-006 = Yes)

| Pipeline | Test | Test DB |
|----------|------|---------|
| User registration | test_registration_flow | testcontainers for {DB from PRD} |

### 9.4 E2E Tests (if TRQ-007 = Yes, global)

| Scenario | Test | Description |
|----------|------|-------------|
| {scenario} | test_{name}_e2e | {description} |

---

## Quality Gates

### PLAN_APPROVED Checklist

- [ ] Architecture conforms to framework principles
- [ ] All components defined
- [ ] API contracts specified
- [ ] DB schema designed
- [ ] Security requirements covered
- [ ] Scaling strategy defined
- [ ] Requirements traced to components
