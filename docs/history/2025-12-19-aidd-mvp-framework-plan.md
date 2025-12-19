# Plan: AIDD-MVP Generator Framework

**Created**: 2025-12-19
**Status**: In Development

---

## Overview

Creating a framework for rapid MVP project generation, combining:
- **AIDD methodology** (roles, quality gates, artifacts) from Habr article
- **Architecture from .ai-framework** (templates, patterns, infrastructure)

**Quality**: Production-ready immediately (no intermediate stages)
- Full AIDD process with quality gates
- Production-grade code from first run
- Full stack: Nginx, SSL, tests, CI/CD, logging

---

# PART 1: SOURCE DATA FROM AIDD ARTICLE

**Source**: https://habr.com/ru/articles/974924/
**Title**: AI-Driven Development (AIDD): Complete Guide

## 1.1 AIDD Concept

AIDD transforms LLM from "one big brain" into "team of roles" for managed development.
Instead of "vibe-coding", it proposes a structured process with quality gates.

**Key idea**: Artifacts are stored in repository as "structured memory", not relying on "chat memory".

## 1.2 AIDD Roles

| Role | Task | Artifact |
|------|------|----------|
| **Analyst** | Forms requirements | PRD document |
| **Researcher** | Researches codebase | Research notes |
| **Planner** | Designs architecture | Architecture plan |
| **Implementer** | Writes code iteratively | Source code |
| **Reviewer** | Conducts code review | Review comments |
| **QA** | Tests and evaluates readiness | QA report |
| **Tech Writer** | Updates documentation | Docs update |
| **Validator** | Tracks quality gates | Gate status |

## 1.3 Repository Structure (from article)

```
project/
├── conventions.md          # Project conventions (code, style, naming)
├── CLAUDE.md              # Instructions for Claude Code
├── workflow.md            # Development process description
│
├── .claude/               # Claude Code configuration
│   ├── agents/            # AI agent role definitions
│   │   ├── analyst.md
│   │   ├── researcher.md
│   │   ├── planner.md
│   │   ├── implementer.md
│   │   ├── reviewer.md
│   │   ├── qa.md
│   │   ├── tech-writer.md
│   │   └── validator.md
│   │
│   ├── commands/          # Slash commands
│   │   ├── idea.md        # /idea → PRD
│   │   ├── researcher.md  # /researcher → code analysis
│   │   ├── plan.md        # /plan → architecture
│   │   ├── tasks.md       # /tasks → breakdown
│   │   ├── implement.md   # /implement → code
│   │   ├── review.md      # /review → review
│   │   ├── qa.md          # /qa → testing
│   │   ├── docs-update.md # /docs-update → documentation
│   │   └── validate.md    # /validate → gate check
│   │
│   └── hooks/             # Pre/Post handlers
│       └── settings.json  # Violation blocking
│
├── docs/                  # Development artifacts
│   ├── prd/              # Product Requirements Documents
│   ├── plan/             # Architecture plans
│   ├── tasklist/         # Task checklists
│   └── research/         # Technical research
│
└── reports/
    └── qa/               # QA reports
```

## 1.4 Quality Gates (from article)

| Stage | Gate ID | Passing Criteria |
|-------|---------|------------------|
| Project | `AGREEMENTS_ON` | conventions.md, workflow.md, base agents present |
| PRD | `PRD_READY` | All sections filled, metrics defined, no blocking questions |
| Architecture | `PLAN_APPROVED` | Components described, contracts defined, NFR considered |
| Tasks | `TASKLIST_READY` | Small tasks with acceptance criteria |
| Implementation | `IMPLEMENT_STEP_OK` | Code written + tests passed |
| Review | `REVIEW_OK` | CI green, no blocking comments |
| QA | `RELEASE_READY` | No critical bugs |
| Docs | `DOCS_UPDATED` | Architecture and runbook up-to-date |

## 1.5 Three Levels of AIDD Adoption

### Minimal AIDD
- `CLAUDE.md` + `conventions.md`
- PRD and tasklist templates
- Basic workflow without automation

### Full AIDD
- Full set of agents in `.claude/agents/`
- Slash commands for each stage
- Validator and orchestrator

### Strict AIDD
- Hooks in `.claude/settings.json` block gate violations
- Headless CI integration
- Automatic pre-release checks

## 1.6 Example Workflow by Ticket (T-104)

```
1. /idea T-104      → PRD creation by analyst
2. /researcher T-104 → codebase analysis
3. /plan T-104      → architecture design
4. /tasks T-104     → task breakdown
5. /implement T-104 → implementation in small steps (with confirmation)
6. /review T-104    → code review with compliance check
7. /qa T-104        → final QA testing
8. /docs-update T-104 → documentation update
9. /validate T-104  → all gates check
```

## 1.7 Key Principles from Article

1. **Artifacts = memory**: Don't rely on chat memory, everything in files
2. **Independent tasks**: Each task must have verifiable acceptance criteria
3. **Early validation**: Validator helps identify "hallucinations" early
4. **Hooks for control**: Prevent stage bypass, block Edit/Write without completed gates
5. **Managed process**: "Not vibe-coding, but managed process integrated into SDLC"

---

# PART 2: SOURCE DATA FROM .ai-framework

**Source**: /home/bgs/Henry_Bud_GitHub/aidd-mvp-generator/.ai-framework/
**Title**: AI Generator for Async Microservices

## 2.1 Architecture: Improved Hybrid Approach

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Business API │  │ Business Bot │  │    Worker    │      │
│  │   (FastAPI)  │  │   (Aiogram)  │  │   (AsyncIO)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   HTTP ONLY (no direct DB access)            │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                     ┌───────┴───────┐
                     │               │
         ┌───────────▼─────┐  ┌──────▼───────────┐
         │  Data Service   │  │  Data Service    │
         │  PostgreSQL API │  │   MongoDB API    │
         │  (Port: 8001)   │  │   (Port: 8002)   │
         └─────────────────┘  └──────────────────┘
                 │                      │
         ┌───────▼─────────┐    ┌──────▼──────────┐
         │   PostgreSQL    │    │    MongoDB      │
         │    Database     │    │    Database     │
         └─────────────────┘    └─────────────────┘
```

## 2.2 Key Architecture Principles

| Principle | Description |
|-----------|-------------|
| **HTTP-Only Data Access** | Business services NEVER access DB directly |
| **Single Event Loop** | Each service owns its event loop (no sharing) |
| **Async-First** | All I/O operations use async/await |
| **Type Safety** | Full type hints, mypy strict mode |
| **DDD & Hexagonal** | Domain-Driven Design with ports/adapters |
| **Service Separation** | FastAPI, Aiogram, Workers in separate processes |

## 2.3 Service Types

### Business API (FastAPI)
- REST API endpoints
- Port 8000-8099
- Calls Data Services via HTTP
- NO database access

### Business Bot (Aiogram)
- Telegram Bot API
- Event-driven handlers
- Calls Data Services via HTTP
- NO database access

### Business Worker (AsyncIO)
- Background task processing
- Async processing
- Calls Data Services via HTTP
- NO database access

### Data API PostgreSQL
- CRUD operations
- Port 8001
- Direct PostgreSQL access
- SQLAlchemy + Alembic

### Data API MongoDB
- Document operations
- Port 8002
- Direct MongoDB access
- Motor async driver

## 2.4 Service Structure (DDD/Hexagonal)

```
service/
├── src/
│   ├── api/              # API Layer (FastAPI routes)
│   │   ├── v1/
│   │   │   ├── health.py
│   │   │   └── {domain}_router.py
│   │   └── dependencies.py
│   │
│   ├── application/      # Application Layer (Use cases)
│   │   ├── services/
│   │   └── dtos/
│   │
│   ├── domain/           # Domain Layer (Pure business logic)
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   │
│   ├── infrastructure/   # Infrastructure Layer (External)
│   │   ├── http/         # HTTP clients to data services
│   │   ├── database/     # Only for Data APIs
│   │   └── messaging/    # Redis, etc.
│   │
│   ├── schemas/          # Pydantic schemas
│   │   └── base.py
│   │
│   ├── core/             # Core utilities
│   │   ├── config.py
│   │   └── logging.py
│   │
│   └── main.py           # Application entry point
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── Dockerfile
├── requirements.txt
└── README.md
```

## 2.5 Templates in .ai-framework/templates/

### services/
```
template_business_api/          # FastAPI template
├── src/
│   ├── api/v1/health.py
│   ├── schemas/base.py
│   └── main.py
├── tests/
├── Dockerfile
└── requirements.txt

template_business_bot/          # Aiogram template
├── src/
│   ├── bot/
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   ├── middlewares/
│   │   └── states/
│   └── main.py
├── tests/
├── Dockerfile
└── requirements.txt

template_business_worker/       # AsyncIO Worker template
├── src/
│   ├── worker/
│   │   ├── handlers/
│   │   └── task_processor.py
│   └── main.py
├── tests/
├── Dockerfile
└── requirements.txt

template_data_postgres_api/     # PostgreSQL Data API
├── src/
│   ├── api/v1/health.py
│   ├── models/base.py
│   ├── repositories/base_repository.py
│   ├── schemas/base.py
│   └── main.py
├── alembic/
├── tests/
├── Dockerfile
└── requirements.txt

template_data_mongo_api/        # MongoDB Data API
├── src/
│   ├── api/v1/health.py
│   ├── models/base.py
│   ├── repositories/base_repository.py
│   ├── schemas/base.py
│   └── main.py
├── tests/
├── Dockerfile
└── requirements.txt
```

### infrastructure/
```
docker-compose.yml          # Development
docker-compose.dev.yml      # Dev overrides
docker-compose.prod.yml     # Production
.env.example                # Environment template
```

### nginx/
```
nginx.conf                  # API Gateway config
Dockerfile                  # Nginx image
```

### ci-cd/
```
.github/workflows/
├── ci.yml                  # Continuous Integration
└── cd.yml                  # Continuous Deployment
```

## 2.6 Technology Stack .ai-framework

| Category | Technologies |
|----------|-------------|
| **Core** | Python 3.12+, FastAPI 0.115+, Aiogram 3.13+, AsyncIO |
| **Data** | PostgreSQL 16+, MongoDB 7+, Redis 7+, SQLAlchemy 2.0+ |
| **Infrastructure** | Docker 24+, Nginx 1.27+, Docker Compose 2.20+ |
| **Observability** | Prometheus, Grafana, Jaeger, ELK Stack, Sentry |
| **Quality** | pytest 8.3+, mypy 1.11+, Ruff 0.6+, Testcontainers |
| **CI/CD** | GitHub Actions |

## 2.7 7-Stage AI Workflow

| Stage | Name | Actions |
|-------|------|---------|
| **0** | AI Initialization | Framework context loading |
| **1** | Prompt Validation | User prompt completeness check |
| **2** | Requirements Intake | Requirements formalization |
| **3** | Architecture Mapping | Implementation planning |
| **4** | Code Generation | Phased code generation |
| **5** | Quality Verification | Quality check (tests, linting) |
| **6** | QA Report & Handoff | Final report and handoff |

## 2.8 Naming Conventions

**Services**: `{context}_{domain}_{type}`
- `finance_lending_api` - Business API for P2P lending
- `healthcare_telemedicine_bot` - Telegram bot for telemedicine
- `construction_house_worker` - Background worker for construction

**Templates**: `template_{domain}_{type}`
- `template_business_api`
- `template_business_bot`
- `template_data_postgres_api`

---

# PART 3: TRANSFER SCHEMA TO NEW FRAMEWORK

## 3.1 What We Take from AIDD (article)

| Component | Source (AIDD) | Target File | Description |
|-----------|---------------|-------------|-------------|
| **Roles** | 7 roles | `.claude/agents/*.md` | Analyst, Architect, Implementer, Reviewer, QA, Validator |
| **Quality Gates** | 8 gates | `workflow.md` + `validator.md` | PRD_READY, PLAN_APPROVED, REVIEW_OK etc. |
| **Slash Commands** | 9 commands | `.claude/commands/*.md` | /idea, /plan, /generate, /review, /deploy |
| **Artifact Structure** | docs/* | `docs/prd/`, `docs/plans/` | PRD, Architecture, Reports |
| **Hooks** | settings.json | `.claude/settings.json` | Gate violation blocking |
| **conventions.md** | Format | `conventions.md` | Code conventions |
| **CLAUDE.md** | Entry point | `CLAUDE.md` | AI instructions |
| **workflow.md** | Process | `workflow.md` | 5-stage AIDD-MVP process |

## 3.2 What We Take from .ai-framework

| Component | Source | Target File | Description |
|-----------|--------|-------------|-------------|
| **Business API template** | `templates/services/template_business_api/` | `templates/services/fastapi_business_api/` | FastAPI + DDD structure |
| **Bot template** | `templates/services/template_business_bot/` | `templates/services/aiogram_bot/` | Aiogram 3.x + handlers |
| **Worker template** | `templates/services/template_business_worker/` | `templates/services/asyncio_worker/` | AsyncIO workers |
| **PostgreSQL Data API** | `templates/services/template_data_postgres_api/` | `templates/services/postgres_data_api/` | SQLAlchemy + Alembic |
| **MongoDB Data API** | `templates/services/template_data_mongo_api/` | `templates/services/mongo_data_api/` | Motor + repositories |
| **Docker Compose** | `templates/infrastructure/` | `templates/infrastructure/docker-compose/` | Dev + Prod configs |
| **Nginx** | `templates/nginx/` | `templates/infrastructure/nginx/` | API Gateway |
| **CI/CD** | `templates/ci-cd/` | `templates/infrastructure/github-actions/` | GitHub Actions |
| **Architecture principles** | `ARCHITECTURE.md` | `knowledge/architecture/` | HTTP-only, DDD |
| **CLAUDE.md rules** | `CLAUDE.md` | Integrate into `CLAUDE.md` | Pre-action verification |

## 3.3 What We Create New

| Component | File | Description |
|-----------|------|-------------|
| **Unified CLAUDE.md** | `CLAUDE.md` | Combines AIDD roles + .ai-framework rules |
| **AIDD-MVP workflow** | `workflow.md` | 5-stage process instead of 7 |
| **Production requirements** | `knowledge/quality/production-requirements.md` | Requirements for each MVP |
| **Adapted agents** | `.claude/agents/*.md` | 6 roles (Analyst, Architect, Implementer, Reviewer, QA, Validator) |
| **Simplified commands** | `.claude/commands/*.md` | 6 commands (/idea, /plan, /generate, /review, /test, /deploy) |
| **Shared components** | `templates/shared/` | DTOs, Schemas, Utils |
| **Knowledge base** | `knowledge/` | Architecture, services, integrations, quality |

## 3.4 File Mapping: Source → Result

### From AIDD we create:
```
AIDD article                   →  AIDD-MVP Generator
─────────────────────────────────────────────────────────
conventions.md (format)        →  /conventions.md
CLAUDE.md (format)             →  /CLAUDE.md (part)
workflow.md (format)           →  /workflow.md
.claude/agents/analyst.md      →  /.claude/agents/analyst.md
.claude/agents/planner.md      →  /.claude/agents/architect.md
.claude/agents/implementer.md  →  /.claude/agents/implementer.md
.claude/agents/reviewer.md     →  /.claude/agents/reviewer.md
.claude/agents/qa.md           →  /.claude/agents/qa.md
.claude/agents/validator.md    →  /.claude/agents/validator.md
.claude/commands/idea.md       →  /.claude/commands/idea.md
.claude/commands/plan.md       →  /.claude/commands/plan.md
.claude/commands/implement.md  →  /.claude/commands/generate.md
.claude/commands/review.md     →  /.claude/commands/review.md
.claude/commands/qa.md         →  /.claude/commands/test.md
.claude/hooks/settings.json    →  /.claude/settings.json
docs/prd/template              →  /docs/prd/template.md
docs/plan/template             →  /docs/architecture/template.md
reports/qa/template            →  /docs/reports/template.md
```

### From .ai-framework we copy:
```
.ai-framework                              →  AIDD-MVP Generator
─────────────────────────────────────────────────────────────────────
templates/services/template_business_api/  →  /templates/services/fastapi_business_api/
templates/services/template_business_bot/  →  /templates/services/aiogram_bot/
templates/services/template_business_worker/ → /templates/services/asyncio_worker/
templates/services/template_data_postgres_api/ → /templates/services/postgres_data_api/
templates/services/template_data_mongo_api/ →  /templates/services/mongo_data_api/
templates/infrastructure/docker-compose.yml → /templates/infrastructure/docker-compose/
templates/infrastructure/.env.example      →  /templates/infrastructure/docker-compose/
templates/nginx/nginx.conf                 →  /templates/infrastructure/nginx/
templates/ci-cd/.github/workflows/         →  /templates/infrastructure/github-actions/
CLAUDE.md (verification rules)             →  /CLAUDE.md (part)
ARCHITECTURE.md                            →  /knowledge/architecture/improved-hybrid.md
docs/guides/dry-kiss-yagni-principles.md   →  /knowledge/quality/dry-kiss-yagni.md
docs/atomic/services/fastapi/*             →  /knowledge/services/fastapi/
docs/atomic/services/aiogram/*             →  /knowledge/services/aiogram/
docs/atomic/services/asyncio-workers/*     →  /knowledge/services/asyncio-workers/
docs/atomic/integrations/redis/*           →  /knowledge/integrations/redis/
docs/atomic/testing/*                      →  /knowledge/quality/testing/
```

---

## Project Structure

```
aidd-mvp-generator/
├── CLAUDE.md                    # Entry point for AI agent
├── conventions.md               # Code and naming conventions
├── workflow.md                  # AIDD-MVP process description
│
├── .claude/                     # Claude Code integration
│   ├── agents/                  # Role definitions
│   │   ├── analyst.md           # Analyst: PRD generation
│   │   ├── architect.md         # Architect: architecture selection
│   │   ├── implementer.md       # Implementer: code generation
│   │   ├── reviewer.md          # Reviewer: code review
│   │   ├── qa.md                # QA: testing
│   │   └── validator.md         # Validator: quality gates
│   │
│   ├── commands/                # Slash commands
│   │   ├── idea.md              # /idea → PRD
│   │   ├── plan.md              # /plan → architecture
│   │   ├── generate.md          # /generate → code
│   │   ├── review.md            # /review → check
│   │   ├── test.md              # /test → testing
│   │   └── deploy.md            # /deploy → launch
│   │
│   └── settings.json            # Hooks for strict mode
│
├── templates/                   # Service templates
│   ├── services/
│   │   ├── fastapi_business_api/    # REST API service
│   │   ├── aiogram_bot/             # Telegram bot
│   │   ├── asyncio_worker/          # Background worker
│   │   ├── postgres_data_api/       # PostgreSQL Data API
│   │   └── mongo_data_api/          # MongoDB Data API
│   │
│   ├── infrastructure/
│   │   ├── docker/                  # Dockerfiles
│   │   ├── docker-compose/          # Dev/Prod compose files
│   │   ├── nginx/                   # API Gateway config
│   │   └── github-actions/          # CI/CD pipelines
│   │
│   └── shared/                      # Common components
│       ├── dtos/                    # Data Transfer Objects
│       ├── schemas/                 # Common Pydantic schemas
│       └── utils/                   # Utilities (logging, config)
│
├── docs/                        # Project artifacts
│   ├── prd/                     # Product Requirements
│   ├── architecture/            # Architecture decisions
│   ├── plans/                   # Implementation plans
│   ├── tasklists/               # Task checklists
│   └── reports/                 # QA reports
│
├── knowledge/                   # Knowledge base for AI
│   ├── architecture/            # Architecture patterns
│   │   ├── improved-hybrid.md       # HTTP-only data access
│   │   ├── service-separation.md    # Service separation
│   │   └── naming-conventions.md    # Naming
│   │
│   ├── services/                # Service patterns
│   │   ├── fastapi/                 # FastAPI patterns
│   │   ├── aiogram/                 # Aiogram patterns
│   │   └── asyncio-workers/         # AsyncIO patterns
│   │
│   ├── integrations/            # Integrations
│   │   ├── redis/                   # Redis patterns
│   │   └── http-clients/            # HTTP clients
│   │
│   ├── infrastructure/          # Infrastructure
│   │   ├── docker/                  # Docker patterns
│   │   ├── nginx/                   # Nginx configs
│   │   └── logging/                 # Logging
│   │
│   └── quality/                 # Quality
│       ├── testing/                 # Testing
│       ├── linting/                 # Ruff, Mypy
│       └── type-checking/           # Type checking
│
└── generated/                   # Generated projects
    └── {project_name}/          # Each MVP
```

---

## Implementation Phases

### Phase 1: Framework Foundation
**Files:**
- `/CLAUDE.md` - entry point, verification rules
- `/conventions.md` - code conventions (snake_case, docstrings, etc.)
- `/workflow.md` - 5-stage AIDD-MVP process description

### Phase 2: Claude Code Integration (.claude/)
**Files:**
- `/.claude/agents/analyst.md` - analyst role (PRD)
- `/.claude/agents/architect.md` - architect role
- `/.claude/agents/implementer.md` - developer role
- `/.claude/agents/reviewer.md` - reviewer role
- `/.claude/agents/qa.md` - QA role
- `/.claude/agents/validator.md` - validator role (gates)
- `/.claude/commands/idea.md` - /idea command
- `/.claude/commands/plan.md` - /plan command
- `/.claude/commands/generate.md` - /generate command
- `/.claude/commands/review.md` - /review command
- `/.claude/commands/test.md` - /test command
- `/.claude/commands/deploy.md` - /deploy command
- `/.claude/settings.json` - hooks configuration

### Phase 3: Service Templates (templates/)
**Adapt from .ai-framework:**
- `/templates/services/fastapi_business_api/` - FastAPI template
- `/templates/services/aiogram_bot/` - Aiogram template
- `/templates/services/asyncio_worker/` - Worker template
- `/templates/services/postgres_data_api/` - PostgreSQL Data API
- `/templates/services/mongo_data_api/` - MongoDB Data API

### Phase 4: Infrastructure (templates/infrastructure/)
**Files:**
- `/templates/infrastructure/docker/` - Dockerfiles
- `/templates/infrastructure/docker-compose/docker-compose.yml`
- `/templates/infrastructure/docker-compose/docker-compose.dev.yml`
- `/templates/infrastructure/docker-compose/docker-compose.prod.yml`
- `/templates/infrastructure/nginx/nginx.conf`
- `/templates/infrastructure/github-actions/ci.yml`
- `/templates/infrastructure/github-actions/cd.yml`

### Phase 5: Shared Components
**Files:**
- `/templates/shared/dtos/` - base DTO classes
- `/templates/shared/schemas/` - common Pydantic schemas
- `/templates/shared/utils/` - utilities (logging, config, etc.)

### Phase 6: Knowledge Base (knowledge/)
**Adapt from .ai-framework/docs:**
- `/knowledge/architecture/` - architecture principles
- `/knowledge/services/` - service patterns
- `/knowledge/integrations/` - integration patterns (Redis, HTTP)
- `/knowledge/infrastructure/` - Docker, Nginx, logging
- `/knowledge/quality/` - testing, linting

### Phase 7: Document Templates (docs/)
**Document templates:**
- `/docs/prd/template.md` - PRD template
- `/docs/architecture/template.md` - architecture template
- `/docs/plans/template.md` - plan template
- `/docs/tasklists/template.md` - checklist template
- `/docs/reports/template.md` - QA report template

---

## Production Requirements (mandatory for each MVP)

**Infrastructure:**
- ✅ Nginx API Gateway (SSL, rate limiting)
- ✅ Docker multi-stage builds (optimized images)
- ✅ Docker Compose (dev + prod configurations)
- ✅ Health check endpoints (/health, /ready)
- ✅ GitHub Actions CI/CD

**Code Quality:**
- ✅ Ruff linting (strict mode)
- ✅ Mypy type checking (strict)
- ✅ Bandit security scan
- ✅ pytest with coverage ≥85%
- ✅ UV package manager

**Logging and Monitoring:**
- ✅ Structured JSON logging
- ✅ Request ID tracking
- ✅ Error tracking ready (Sentry-ready)

**Architecture:**
- ✅ DDD/Hexagonal structure
- ✅ HTTP-only data access
- ✅ Service separation

---

## Quality Gates

| Gate | Stage | Passing Criteria |
|------|-------|------------------|
| PRD_READY | After /idea | All sections filled, no blocking questions |
| PLAN_APPROVED | After /plan | Architecture selected, components defined |
| TASKLIST_READY | After breakdown | Small tasks, acceptance criteria present |
| IMPLEMENT_OK | After /generate | Code + tests pass, coverage ≥85% |
| REVIEW_OK | After /review | Ruff/Mypy/Bandit passed, 0 errors |
| DEPLOY_READY | After /deploy | Health checks work, nginx responds |

---

## Technology Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python 3.12+, FastAPI, Aiogram 3.x, AsyncIO |
| **Data** | PostgreSQL 16+, MongoDB 7+, Redis 7+ |
| **Infrastructure** | Docker, Docker Compose, Nginx |
| **Quality** | Ruff, Mypy, Bandit, pytest |
| **Package Manager** | UV (uv) |
| **CI/CD** | GitHub Actions |

---

## Critical Files from .ai-framework for Adaptation

**Service Templates:**
1. `.ai-framework/templates/services/template_business_api/`
2. `.ai-framework/templates/services/template_business_bot/`
3. `.ai-framework/templates/services/template_business_worker/`
4. `.ai-framework/templates/services/template_data_postgres_api/`
5. `.ai-framework/templates/services/template_data_mongo_api/`

**Infrastructure:**
6. `.ai-framework/templates/infrastructure/docker-compose.yml`
7. `.ai-framework/templates/nginx/nginx.conf`
8. `.ai-framework/templates/ci-cd/.github/workflows/`

**Documentation (patterns):**
9. `.ai-framework/CLAUDE.md` - verification rules
10. `.ai-framework/AGENTS.md` - workflow
11. `.ai-framework/ARCHITECTURE.md` - architecture (Production Level 4 patterns)

---

## Execution Order

1. Create base directory structure
2. Write CLAUDE.md, conventions.md, workflow.md
3. Create .claude/agents/ with role definitions
4. Create .claude/commands/ with slash commands
5. Adapt service templates from .ai-framework
6. Create infrastructure templates
7. Create shared components
8. Transfer and adapt knowledge from .ai-framework
9. Create document templates in docs/
10. Test workflow on example MVP generation
