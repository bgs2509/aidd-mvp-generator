# Function: Pipeline Refinement

> **Purpose**: Adapting the pipeline for a specific project.

---

## Goal

Based on code analysis and constraints, refine which stages
and components will be required for implementation.

**Artifact**: results are recorded in `ai-docs/docs/research/{name}-research.md`.
Each finding (patterns, constraints, recommendations) must be documented,
so architects and QA can reproduce the reasoning.

---

## Determining Required Components

### For CREATE Mode

```markdown
Based on the PRD, determine:

1. Is a Business API needed?
   → Are there REST endpoints in the requirements?

2. Is a Telegram Bot needed?
   → Are there bot requirements?

3. Is a Background Worker needed?
   → Are there background tasks?

4. What Data API is needed?
   → PostgreSQL for relational data
   → MongoDB for documents
   → Both?

5. Is Redis needed?
   → Caching?
   → Sessions?
   → Queues?
```

### For FEATURE Mode

```markdown
Based on code analysis:

1. Which existing services does the feature affect?
2. Are new services needed?
3. Are Data API changes needed?
4. Are new endpoints needed?
5. Are new data models needed?
```

---

## Component Matrix

### Standard MVP Components

| Component | Port | When needed |
|-----------|------|-------------|
| Business API | 8000 | Almost always (REST API) |
| Data API PG | 8001 | Relational data |
| Data API Mongo | 8002 | Documents, logs |
| Telegram Bot | — | If a bot is needed |
| Background Worker | — | Background tasks |
| Redis | 6379 | Cache, sessions |
| PostgreSQL | 5432 | Primary DB |
| MongoDB | 27017 | Document DB |

### Determination by Requirements

```
FR contains "API", "REST", "endpoint"
  → Business API needed

FR contains "Telegram", "bot", "command"
  → Telegram Bot needed

FR contains "background", "periodically", "scheduled"
  → Background Worker needed

FR contains "store", "save", "data"
  → Data API needed

FR contains "cache", "fast access", "session"
  → Redis needed
```

---

## Refining Implementation Stages

### CREATE Mode

```
Standard order:

1. Infrastructure
   ├── docker-compose.yml
   ├── Makefile
   └── CI/CD

2. Data Service
   ├── Models
   ├── Repositories
   └── API

3. Business API (if needed)
   ├── Services
   ├── Routes
   └── HTTP client

4. Telegram Bot (if needed)
   ├── Handlers
   ├── Keyboards
   └── States

5. Background Worker (if needed)
   ├── Task handlers
   └── Scheduler

6. Tests
   ├── Unit
   └── Integration
```

### FEATURE Mode

```
Adapted order:

1. Data API changes (if needed)
   ├── New models
   ├── Migrations
   └── New endpoints

2. Business Services changes
   ├── New methods
   ├── New routes
   └── HTTP client update

3. UI changes (if needed)
   ├── New handlers
   └── New keyboards

4. Tests
   ├── New feature tests
   └── Regression tests
```

---

## Refinement Result

```markdown
## Required Components

| Component | Needed | Comment |
|-----------|--------|---------|
| Business API | Yes | REST API for clients |
| Telegram Bot | Yes | Restaurant notifications |
| Background Worker | No | No background tasks |
| Data API PG | Yes | Booking storage |
| Redis | Yes | Search caching |

## Implementation Plan

| # | Stage | Components |
|---|-------|------------|
| 1 | Infrastructure | docker-compose, Makefile |
| 2 | Data API | booking_data |
| 3 | Business API | booking_api |
| 4 | Telegram Bot | booking_bot |
| 5 | Tests | unit, integration |

## Dependencies Between Components

booking_api ──HTTP──> booking_data
booking_bot ──HTTP──> booking_api
```

---

## Sources

| Document | Description |
|----------|-------------|
| `.ai-framework/docs/reference/aidd-roles-reference.md` | Roles reference |
| `.ai-framework/docs/guides/conditional-stage-rules.md` | Conditional rules |
