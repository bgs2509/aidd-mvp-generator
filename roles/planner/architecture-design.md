# Function: Architecture Design

> **Purpose**: Creating an architectural solution based on the PRD.

---

## Goal

Design a system architecture that satisfies
the functional and non-functional requirements from the PRD.

---

## Input Data

| Artifact | Path | Description |
|----------|------|-------------|
| PRD | `ai-docs/docs/_analysis/{name}-prd.md` | Requirements |
| Code Analysis | `ai-docs/docs/research/{name}-research.md` | For FEATURE mode |
| Gates | PRD_READY | Must be passed |

---

## AIDD-MVP Architectural Principles

### 1. HTTP-only Data Access

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│  Business API   │ ───────────▶  │    Data API     │
│  (FastAPI)      │               │  (PostgreSQL)   │
└─────────────────┘               └─────────────────┘

RULE: Business services NEVER access the database directly.
      Only through HTTP calls to the Data API.
```

### 2. DDD + Hexagonal Architecture

```
┌────────────────────────────────────────────────────┐
│                     SERVICE                         │
├────────────────────────────────────────────────────┤
│  api/              ← Incoming adapters (REST)       │
│  ├── v1/                                           │
│  │   └── routes.py                                 │
│  └── dependencies.py                               │
├────────────────────────────────────────────────────┤
│  application/      ← Application services           │
│  ├── services/                                     │
│  └── dtos/                                         │
├────────────────────────────────────────────────────┤
│  domain/           ← Business logic (core)          │
│  ├── entities/                                     │
│  ├── value_objects/                                │
│  └── services/                                     │
├────────────────────────────────────────────────────┤
│  infrastructure/   ← Outgoing adapters              │
│  ├── http/         (HTTP clients)                  │
│  └── messaging/    (queues)                        │
└────────────────────────────────────────────────────┘
```

### 3. One Event Loop per Service

```
RULE: Each service owns ONE event loop.
      Creating additional event loops is not allowed.

FastAPI/Aiogram/Worker → asyncio.run() → one loop
```

---

## Design Process

### Step 1: Identify Components

Based on the PRD, identify the required services:

```markdown
| Component | Needed? | Justification |
|-----------|---------|---------------|
| Business API | ? | Are there REST endpoints in FR? |
| Data API (PG) | ? | Is there relational data? |
| Data API (Mongo) | ? | Are there documents/logs? |
| Telegram Bot | ? | Are there FR for the bot? |
| Background Worker | ? | Are there background tasks? |
| Redis | ? | Is cache/sessions needed? |
```

### Step 2: Design the Data Model

```markdown
## Data Models

### Entity: {Name}

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Identifier | PK |
| ... | ... | ... | ... |

### Relationships

{Entity1} 1──N {Entity2}
```

### Step 3: Define API Contracts

```markdown
## API Contracts

### {Service} API

| Method | Path | Description | Req ID |
|--------|------|-------------|--------|
| POST | /api/v1/{resource} | Create | FR-001 |
| GET | /api/v1/{resource}/{id} | Retrieve | FR-002 |
```

### Step 4: Define Interactions

```markdown
## Interaction Diagram

User ──▶ Business API ──▶ Data API ──▶ PostgreSQL
              │
              └──▶ Telegram Bot ──▶ User (notifications)
```

---

## Architecture Document Template

```markdown
# Architecture: {Project Name}

**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Author**: AI Agent (Planner)

---

## 1. Overview

### 1.1 Context
{Brief system description}

### 1.2 Architecture Goals
- {Goal 1}
- {Goal 2}

---

## 2. System Components

| Component | Type | Port | Description |
|-----------|------|------|-------------|
| {name}_api | Business API | 8000 | REST API |
| {name}_data | Data API | 8001 | PostgreSQL access |
| {name}_bot | Telegram Bot | — | Notifications |

---

## 3. Data Models

### 3.1 ER Diagram

{Text diagram}

### 3.2 Model Descriptions

{Tables with field descriptions}

---

## 4. API Contracts

### 4.1 Business API

{Endpoints table}

### 4.2 Data API

{Endpoints table}

---

## 5. Interactions

### 5.1 Main Flows

{Sequence diagrams}

---

## 6. Infrastructure

### 6.1 Docker Services

| Service | Image | Port | Dependencies |
|---------|-------|------|--------------|

### 6.2 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|

---

## 7. Decisions and Justifications

| # | Decision | Alternatives | Justification |
|---|----------|--------------|---------------|
| 1 | {Decision} | {Alternatives} | {Why chosen} |
```

---

## Quality Gates: ARCHITECTURE_READY

### Checklist

- [ ] All required components are identified
- [ ] HTTP-only data access principle is followed
- [ ] Data models are defined
- [ ] API contracts are defined
- [ ] Contracts cover all FRs
- [ ] Interactions between components are defined
- [ ] Document is saved to `ai-docs/docs/_plans/mvp/`

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/architecture/improved-hybrid.md` | Hybrid architecture |
| `knowledge/architecture/ddd-hexagonal.md` | DDD principles |
| `knowledge/architecture/data-access.md` | HTTP-only access |
