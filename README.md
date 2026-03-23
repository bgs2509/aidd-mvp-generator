# AIDD-MVP Generator

> A framework for rapid generation of production-ready MVP projects
> using the AI-Driven Development (AIDD) methodology

---

## What is it?

**AIDD-MVP Generator** combines:
- **AIDD Methodology** — a structured development process with AI agents
- **Architectural Templates** — ready-made patterns for microservices
- **Quality Gates** — automatic quality checks at every stage

**Result**: Production-ready MVP in ~10 minutes.

---

## Characteristics

| Parameter | Value |
|-----------|-------|
| Maturity Level | Level 2 (MVP) |
| Test Coverage | ≥75% |
| Architecture | DDD/Hexagonal, HTTP-only |
| Services | FastAPI, Aiogram, AsyncIO Workers |
| Databases | PostgreSQL, MongoDB |
| Infrastructure | Docker, Nginx, CI/CD |

---

## Quick Start

### Requirements

- Python 3.11+
- Docker & Docker Compose
- Claude Code CLI
- Git 2.40+

### Framework Installation (recommended)

```bash
# 1. Create and initialize the target project
mkdir restaurant-booking && cd restaurant-booking
git init

# 2. Add the framework as a Git Submodule
git submodule add git@github.com:bgs2509/aidd-mvp-generator.git .aidd
git submodule update --init --recursive

# 3. Launch Claude Code
claude
```

```bash
# 4. Initialize the framework (creates CLAUDE.md, registers /aidd-* commands)
/aidd-init

# /aidd-init performs:
#   - Creates CLAUDE.md with AI instructions
#   - Copies commands to .claude/commands/
#   - Creates project structure (ai-docs/, .pipeline-state.json)
```

```bash
# 5. Follow the 6-stage process (stages 0-5)
/aidd-analyze "Create a restaurant table booking service"
/aidd-research
/aidd-plan
# ... approve the plan ...
/aidd-code
/aidd-validate

# 6. Run the generated project
make build && make up
```

### Adding a Feature to an Existing Project

```bash
# 1. Navigate to the project directory (where .aidd/ already exists)
cd my-existing-project

# 2. Launch Claude Code
claude

# 3. If /aidd-* commands are not yet registered — initialize
/aidd-init

# 4. Describe the feature (Claude automatically detects FEATURE mode)
/aidd-analyze "Add email notification system"

# 5. Follow the pipeline: /aidd-research → /aidd-plan-feature → /aidd-code → ...
```

---

## Development Process

A 6-stage pipeline (stages 0-5) with quality gates.

**Stage 0 — Bootstrap (`/aidd-init`)**: Registers `/aidd-*` commands, creates the project structure.
Without this stage, the remaining commands **will not work**.

```
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│   IDEA    │─▶│ RESEARCH  │─▶│ARCHITEC-  │─▶│IMPLEMEN-  │
│           │  │           │  │   TURE    │  │  TATION   │
│/aidd-analyze │  │ /aidd-    │  │  /aidd-   │  │  /aidd-   │
│           │  │ research  │  │   plan    │  │ generate  │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │              │
┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
│ PRD_READY │  │ RESEARCH  │  │   PLAN    │  │IMPLEMENT  │
│           │  │   _DONE   │  │ APPROVED  │  │   _OK     │
└───────────┘  └───────────┘  └───────────┘  └───────────┘
                                                    │
                                                    ▼
                     ┌──────────────────────────────────────┐
                     │      QUALITY & DEPLOY                │
                     │      /aidd-validate                  │
                     │                                      │
                     │  Review → Test → Validate → Deploy   │
                     └───────────────┬──────────────────────┘
                                     │
                          ┌──────────▼───────────┐
                          │  REVIEW_OK           │
                          │  QA_PASSED           │
                          │  ALL_GATES_PASSED    │
                          │  DEPLOYED            │
                          └──────────────────────┘
```

---

## 5 AI Roles

| Role | Command | Task |
|------|---------|------|
| **Analyst** | `/aidd-analyze` | Create PRD from an idea |
| **Researcher** | `/aidd-research` | Analyze code and technologies |
| **Planner** | `/aidd-plan` | System design |
| **Coder** | `/aidd-code` | Code generation |
| **Validator** | `/aidd-validate` | Quality & Deploy (Review → Test → Validate → Deploy) |

---

## Generated Service Types

| Type | Technology | Description |
|------|------------|-------------|
| **Business API** | FastAPI | REST API |
| **Business Bot** | Aiogram | Telegram bot |
| **Background Worker** | AsyncIO | Background tasks |
| **Data API PostgreSQL** | FastAPI + SQLAlchemy | CRUD for PostgreSQL |
| **Data API MongoDB** | FastAPI + Motor | CRUD for MongoDB |

---

## Project Structure

```
aidd-mvp-generator/
│
├── CLAUDE.md              # Entry point for AI
├── conventions.md         # Code conventions
├── workflow.md            # Development process
├── README.md              # This file
│
├── .claude/               # Claude Code integration
│   ├── agents/            # 7 AI roles
│   └── commands/          # 9 slash commands
│
├── roles/                 # Detailed role instructions
├── knowledge/             # Knowledge base
├── templates/             # Service templates
│   ├── services/          # FastAPI, Aiogram, Workers
│   ├── shared/            # Shared components
│   └── infrastructure/    # Docker, Nginx, CI/CD
│
└── docs/                  # Document templates
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [CLAUDE.md](CLAUDE.md) | Main entry point for AI agents |
| [conventions.md](conventions.md) | Code and style conventions |
| [workflow.md](workflow.md) | 6-stage development process (stages 0-5) |

---

## Architectural Principles

- **HTTP-only data access** — business services never access the database directly
- **DDD/Hexagonal** — layered separation (api/application/domain/infrastructure)
- **Async-First** — all I/O operations are asynchronous
- **Type Safety** — full type hints for all functions

---

## License

MIT

---

## Authors

Created using the AIDD methodology
(AI-Driven Development)
