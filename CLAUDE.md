# CLAUDE.md — Main Entry Point for AI Agents

> **Philosophy**: VERIFY BEFORE ACT — Verify before acting.
> **Principle**: Artifacts = Memory. Do not rely on chat context.
>
> Full list of artifacts: [docs/NAVIGATION.md](docs/NAVIGATION.md#summary-table)

---

## TL;DR (30 seconds)

| Question | Answer |
|----------|--------|
| **What is it?** | Framework for generating production-ready MVPs in ~10 minutes |
| **How does it work?** | 6-stage pipeline with quality gates |
| **How to start?** | `/aidd-analyze "project description"` |
| **Result** | Working MVP: FastAPI + PostgreSQL + Docker |

---

## What is AIDD-MVP Generator

**AIDD-MVP Generator** — a framework for rapid generation of production-ready MVP projects,
combining AI-Driven Development (AIDD) methodology with architectural templates.

### Key Characteristics

| Parameter | Value |
|-----------|-------|
| Maturity Level | **Level 2 (MVP)** — always |
| Test Coverage | ≥75% |
| Architecture | DDD/Hexagonal, HTTP-only data access |
| Quality Gates | 6 stages (0-5), 6 gates |
| Service Types | Business API, Data API, Bot, Worker |

---

## Uniqueness: Git Submodule Approach

> **KEY IDEA**: Framework ≠ template. Framework = Knowledge Base.

```
┌────────────────────────────────────────────────────────────────────┐
│                        USAGE MODEL                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  my-project/                    ← TARGET PROJECT (your code)       │
│  │                                                                 │
│  ├── .aidd/                     ← Git Submodule (READ ONLY!)       │
│  │   ├── CLAUDE.md              ← Instructions                     │
│  │   ├── .claude/agents/        ← AI Roles                         │
│  │   ├── .claude/commands/      ← Slash commands                   │
│  │   ├── templates/             ← Service Templates                │
│  │   └── knowledge/             ← Knowledge Base                   │
│  │                                                                 │
│  ├── ai-docs/docs/              ← AI-GENERATED ARTIFACTS           │
│  │   ├── _analysis/{name}.md                                       │
│  │   ├── _plans/mvp/{name}.md                                      │
│  │   └── _validation/                                              │
│  │                                                                 │
│  ├── services/                  ← AI-GENERATED CODE                │
│  │   ├── {context}_{domain}_api/                                   │
│  │   └── {context}_{domain}_data/                                  │
│  │                                                                 │
│  ├── .pipeline-state.json       ← Pipeline State                   │
│  └── docker-compose.yml         ← Infrastructure                   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Critical Rule

```
┌─────────────────────────────────────────────────────────────────┐
│  ⛔ NEVER MODIFY FILES IN .aidd/                                 │
├─────────────────────────────────────────────────────────────────┤
│  • Framework = Knowledge Base (read only)                       │
│  • All code is generated OUTSIDE the submodule                  │
│  • To update: git submodule update --remote                     │
└─────────────────────────────────────────────────────────────────┘
```

### Command Handling Details

**Problem**: Claude Code looks for slash commands only in `{project}/.claude/commands/`.
When the framework is connected as a submodule (`.aidd/`), commands from `.aidd/.claude/commands/`
**are not registered automatically**.

**Solution**: The `/aidd-init` command automatically copies command files:

```bash
# During /aidd-init the following is executed:
mkdir -p .claude/commands
cp .aidd/.claude/commands/*.md .claude/commands/
```

After `/aidd-init`, commands are available in CLI autocompletion:
```
/aidd-analyze, /aidd-research, /aidd-plan, /aidd-plan-feature, /aidd-code, /aidd-validate
```

**Updating commands**: When updating the submodule (`.aidd/`), re-run `/aidd-init` —
modified files will be updated, already current files will be skipped.

**How AI executes a command**:
```
User: /aidd-analyze "description"
     ↓
Claude Code loads: ./.claude/commands/aidd-analyze.md (copy from .aidd/)
     ↓
AI reads: ./.aidd/.claude/agents/analyst.md (role)
     ↓
AI executes the command according to instructions
```

---

## Two Operating Modes

| Mode | When to use | Differences |
|------|-------------|-------------|
| **CREATE** | New MVP from scratch | `/aidd-plan` → full architecture |
| **FEATURE** | Adding a feature to an existing project | `/aidd-plan-feature` → integration plan |

### Auto-detection of Mode

| Indicator | Mode |
|-----------|------|
| `services/` or `docker-compose.yml` exists | **FEATURE** |
| Empty directory | **CREATE** |

Explicit override: `/aidd-analyze --mode=FEATURE "description"`

### Parallel Pipelines (Pipeline State v2)

The framework supports simultaneous development of multiple features:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PARALLEL PIPELINES                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  main                                                                   │
│    │                                                                    │
│    ├──┬── feature/F042-oauth ─────────────────────────▶ merge           │
│    │  │     ├── /aidd-analyze → PRD_READY                                 │
│    │  │     ├── /aidd-research → RESEARCH_DONE                         │
│    │  │     ├── /aidd-plan → PLAN_APPROVED                             │
│    │  │     └── ... → DEPLOYED                                          │
│    │  │                                                                 │
│    │  └── feature/F043-payments ──────────────────────▶ merge           │
│    │        ├── /aidd-analyze (in parallel!)                              │
│    │        └── ...                                                     │
│    ▼                                                                    │
│  main (with both features)                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key features**:
- Each feature is developed in a separate git branch `feature/{FID}-{slug}`
- Gates are isolated: `active_pipelines[FID].gates` instead of shared `gates`
- Feature context is determined automatically by the current git branch
- Upon `/aidd-validate` (DEPLOYED), the feature is moved to `features_registry`

**Parallel development rules**:
- ✅ **Allowed** to start a new feature even if the previous one is not completed (DEPLOYED)
- ✅ **Allowed** to develop multiple features simultaneously in different branches
- ⚠️ **Recommended** to track conflicts: `python3 scripts/git_helpers.py conflicts F042 F043`
- ⚠️ **Avoid** modifying the same files in different active features

**Documentation**: [knowledge/pipeline/git-integration.md](knowledge/pipeline/git-integration.md)

### Initialization Modes (`/aidd-init`)

The `/aidd-init` command automatically detects the project type and launches the corresponding mode:

| Mode | Condition | Behavior |
|------|-----------|----------|
| **NEW_PROJECT** | Project is empty | Standard initialization — creating all files |
| **EXISTING_PROJECT** | Has significant files | Interactive mode — AI asks for each file |

**Existing project criteria** (any of):
- `services/`, `src/`, `app/` — code directories
- `docker-compose.yml` — infrastructure
- `CLAUDE.md` — project documentation
- `README.md` larger than 500 bytes
- More than 2 Python files in root

**Interactive EXISTING_PROJECT mode**:

```
┌─────────────────────────────────────────────────────────────────┐
│  For each file/folder AI asks a question:                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  File exists and differs from template:                          │
│  • [1] Keep current version (recommended)                       │
│  • [2] Replace with template                                     │
│  • [3] Merge (add sections from template)                       │
│                                                                  │
│  File/folder does not exist:                                     │
│  • Create? [Y/n] or [y/N]                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

All decisions are recorded in `.pipeline-state.json`:
```json
{
  "init_mode": "EXISTING_PROJECT",
  "init_decisions": {
    "CLAUDE.md": "kept_existing",
    "README.md": "kept_existing",
    ".pipeline-state.json": "created",
    "ai-docs/": "skipped"
  }
}
```

---

## 6-Stage Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AIDD-MVP DEVELOPMENT PIPELINE (v2.0)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────┐                                                               │
│  │ BOOTSTRAP │  Stage 0: Target Project Initialization                      │
│  │/aidd-init │  ─────────────────────────────────────────────────────────── │
│  └─────┬─────┘                                                               │
│        │ BOOTSTRAP_READY                                                     │
│        ▼                                                                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────────┐             │
│  │  IDEA   │───▶│RESEARCH │───▶│ARCHITEC-│───▶│IMPLEMENTA-   │             │
│  │         │    │         │    │  TURE   │    │    TION       │             │
│  └────┬────┘    └────┬────┘    └────┬────┘    └──────┬───────┘             │
│       │              │              │                 │                     │
│  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌──────▼───────┐             │
│  │PRD_READY│    │RESEARCH │    │  PLAN   │    │  IMPLEMENT   │             │
│  │         │    │  RESEARCH_DONE  │    │APPROVED │    │     IMPLEMENT_OK      │             │
│  └─────────┘    └─────────┘    └─────────┘    └──────────────┘             │
│                                      ⚠️                                      │
│                                Requires user                                │
│                                confirmation!                                 │
│                                                                              │
│                                     ▼                                        │
│  ┌───────────────────────────────────────────────────────────────┐          │
│  │            QUALITY & DEPLOY (/aidd-validate)                  │          │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────────────┐      │          │
│  │  │ Review │─▶│  Test  │─▶│Validate│─▶│Deploy + Report │      │          │
│  │  └────┬───┘  └────┬───┘  └────┬───┘  └────┬───────────┘      │          │
│  │       │           │           │            │                  │          │
│  │  REVIEW_OK    QA_PASSED  ALL_GATES     DEPLOYED              │          │
│  │                                 PASSED                        │          │
│  └───────────────────────────────────────────────────────────────┘          │
│                                                                              │
│  Artifact: 1 Completion Report (instead of 4 files)                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Commands and Gates Table

| # | Stage | Command | Agent | Gate | Artifact |
|---|-------|---------|-------|------|----------|
| 0 | Bootstrap | `/aidd-init` | — | `BOOTSTRAP_READY` | TP Structure |
| 1 | Idea | `/aidd-analyze` | Analyst | `PRD_READY` | `_analysis/{name}.md` |
| 2 | Research | `/aidd-research` | Researcher | `RESEARCH_DONE` | `_research/{name}.md` |
| 3 | Architecture (CREATE) | `/aidd-plan` | Planner | `PLAN_APPROVED` | `_plans/mvp/{name}.md` |
| 3 | Architecture (FEATURE) | `/aidd-plan-feature` | Planner | `PLAN_APPROVED` | `_plans/features/{name}.md` |
| 4 | Implementation | `/aidd-code` | Coder | `IMPLEMENT_OK` | `services/`, tests |
| 5 | Quality & Deploy | `/aidd-validate` | Validator | **Full**: `REVIEW_OK`, `QA_PASSED`, `ALL_GATES_PASSED`, `DEPLOYED` <br> **Quick**: `DOCUMENTED` | `_validation/{name}.md` |

> **Note**: `/aidd-validate` supports two modes:
> - **Full (recommended)**: Review → Test → Validate → Deploy → Production-ready MVP
> - **Quick**: Only DRAFT Completion Report + Static Analysis → for documentation or stalled features
>
> Command files: [docs/INDEX.md](docs/INDEX.md#slash-commands)

### Blocking Principle

```
❌ Gate not passed → Transition to next stage is BLOCKED
✅ Gate passed → May proceed
```

**Example**: Cannot execute `/aidd-code` without `PLAN_APPROVED`.

### Completion Report (Final Report)

After `DEPLOYED`, each feature receives a **Completion Report** — a single document
containing everything you need to know about the implemented feature.

#### Why It Is Needed

| Problem | Solution |
|---------|----------|
| AI loses context between sessions | Single source of truth |
| Decisions are not documented | ADR in each report |
| Scope changes are not tracked | Plan vs Actual |
| Known issues get lost | Explicit limitations section |

#### What It Contains

1. **Executive Summary** — what was done (2-3 sentences)
2. **Code Review Summary** — quality check results
3. **Testing Summary** — testing results
4. **Requirements Traceability** — requirements compliance
5. **ADR** — architectural decisions with rationale
6. **Scope Changes** — deviations from the plan
7. **Known Limitations** — limitations and workarounds
8. **Metrics** — coverage, tests, security
9. **References** — to all artifacts

#### When AI MUST Read

```
┌─────────────────────────────────────────────────────────────┐
│  When working in FEATURE mode AI MUST:                       │
│                                                             │
│  1. Read .pipeline-state.json                               │
│  2. For each feature in features_registry:                   │
│     → Read artifacts.completion                              │
│  3. Understand dependencies and integration possibilities    │
└─────────────────────────────────────────────────────────────┘
```

#### File Path

```
ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}-completion.md
```

---

### CHANGELOG.md (Change Log)

Each target project automatically receives `CHANGELOG.md` — a **single entry point** for understanding project history.

#### Why It Is Needed

| Problem | Solution |
|---------|----------|
| AI loses context in a new session | Quick overview of all features in 30 seconds |
| Project history is scattered | Single file with chronology |
| Critical changes are not tracked | Manual entries between features |

#### What It Contains

1. **[Unreleased]** — active features and recent changes
2. **Completed features** — automatically from Completion Reports
3. **Critical changes** — hotfix, breaking changes, security fixes (manually by AI)

#### Automatic Update

| Event | Action |
|-------|--------|
| `/aidd-init` | Created from template or generated from `features_registry` |
| `/aidd-validate` → DEPLOYED | Feature section is automatically added |
| Critical changes | AI manually adds entries (see rules in TP CLAUDE.md) |

#### When AI MUST Read

```
┌─────────────────────────────────────────────────────────────┐
│  AI MUST read CHANGELOG.md BEFORE:                           │
│  • Planning any changes                                      │
│  • Adding new functionality                                  │
│  • Fixing bugs                                               │
│  • Refactoring code                                          │
└─────────────────────────────────────────────────────────────┘
```

**More details**: See TP CLAUDE.md → section "CHANGELOG.md Maintenance Rules"

---

## 5 Core AI Agent Roles (7 files)

| Role | File | Stages | Responsibility |
|------|------|--------|----------------|
| **Analyst** | `analyst.md` | 1 | PRD, requirements |
| **Researcher** | `researcher.md` | 2 | Code/requirements analysis |
| **Planner** | `planner.md` | 3 | Design |
| **Coder** | `coder.md` | 4 | Code generation |
| **Validator** | `validator.md` | 5 | Quality & Deploy (4 steps) |

**Auxiliary instruction libraries** (used within the Validator):
- `code-review-library.md` — detailed instructions for Code Review (Step 1)
- `testing-library.md` — detailed instructions for Testing (Step 2)

---

## User Interaction with the Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│  USER                                   AI AGENT                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Connects .aidd/ as submodule                                    │
│  2. Launches Claude Code                                            │
│                                                                     │
│  3. /aidd-analyze "description"    ───▶    Creates PRD                 │
│                                         Asks clarifying questions    │
│                                                                     │
│  4. Answers questions              ◀───    PRD_READY ✓              │
│                                                                     │
│  5. /aidd-research                 ───▶    Analyzes                  │
│                                         RESEARCH_DONE ✓             │
│                                                                     │
│  6. /aidd-plan                     ───▶    Creates architecture plan │
│                                                                     │
│  7. ⚠️ APPROVES PLAN               ◀───    Awaits confirmation       │
│     "Yes, I approve the plan"              PLAN_APPROVED ✓          │
│                                                                     │
│  8. /aidd-code                     ───▶    Generates code            │
│                                         IMPLEMENT_OK ✓              │
│                                                                     │
│  9. /aidd-validate                 ───▶    Quality & Deploy:         │
│                                         • Review → REVIEW_OK ✓      │
│                                         • Test → QA_PASSED ✓        │
│                                         • Validate → ALL_GATES ✓    │
│                                         • Deploy → DEPLOYED ✓       │
│                                         • Completion Report         │
│                                                                     │
│  🎉 MVP is ready!                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Architectural Principles

| Principle | Rule |
|-----------|------|
| **HTTP-only** | Business services NEVER access the DB directly. Only through Data API. |
| **DDD/Hexagonal** | Separation into `api/application/domain/infrastructure` |
| **Async-First** | All I/O operations use `async/await` |
| **Type Safety** | Full type hints for all functions |
| **Level 2 (MVP)** | Production-ready, but without complex scalability |

### HTTP-only Architecture

```
┌─────────────┐      HTTP       ┌─────────────┐      SQL      ┌─────────┐
│ Business API│ ──────────────▶ │  Data API   │ ────────────▶ │   DB    │
│  (FastAPI)  │                 │  (FastAPI)  │               │(Postgres)│
└─────────────┘                 └─────────────┘               └─────────┘
      ▲
      │ HTTP
      │
┌─────────────┐
│  Telegram   │
│    Bot      │
└─────────────┘
```

---

## Critical Rules (VERIFY BEFORE ACT)

```
┌─────────────────────────────────────────────────────────────────┐
│  BEFORE ANY ACTION AI MUST:                                      │
├─────────────────────────────────────────────────────────────────┤
│  1. CREATING A FILE  → Verify that the file does NOT exist       │
│  2. EDITING          → First read the current contents           │
│  3. DELETING         → Check all dependencies and references     │
│  4. ADDING A LINK    → Verify that the target exists             │
│  5. WRITING CODE     → Check if similar code exists (DRY)        │
│  6. ADDING A FEATURE → Verify it is needed NOW (YAGNI)           │
└─────────────────────────────────────────────────────────────────┘

NEVER ASSUME → ALWAYS VERIFY → THEN ACT
```

```
┌─────────────────────────────────────────────────────────────────┐
│  ⛔ AI NEVER READS .env FILES                                    │
├─────────────────────────────────────────────────────────────────┤
│  • Files .env, .env.*, *.env, .env.local contain SECRETS        │
│  • ALL tools are prohibited: Read, Bash (cat/grep/less/...)     │
│  • Alternative: .env.example (WITHOUT real values)               │
│  • NO exceptions — even for other projects                       │
│                                                                 │
│  Violation = BLOCKER for any task                                │
└─────────────────────────────────────────────────────────────────┘
```

**Why it is prohibited**:
- .env contains API keys, DB passwords, tokens
- Reading .env = potential leak into logs/context
- Even reading without showing to user = violation

**Prohibited file patterns**:
- `.env*` — any env files
- `*.pem`, `*.key` — encryption keys
- `credentials.json` — credentials
- `*secret*` — files with the word secret
- More details: knowledge/security/secrets-management.md

---

## Executing /aidd-* Commands

> **Lesson Learned**: F007 (2026-01-14) — missed Completion Report during `/aidd-validate`

### Mandatory Algorithm

When executing any `/aidd-*` command, AI MUST:

1. **Read the ENTIRE** command file `.aidd/.claude/commands/{cmd}.md`
2. **Find** the "Gate Checklist" section at the end of the file
3. **Create a TodoWrite** with ALL checklist items
4. **Execute** each item and mark it completed
5. **Complete** the command ONLY when ALL 🔴 items are done

### Criticality Markers

| Marker | Meaning | Rule |
|--------|---------|------|
| 🔴 | **BLOCKER** | Without this the command is NOT complete |
| 🟡 | **REQUIRED** | Must be executed |
| ⚪ | **OPTIONAL** | Recommended |

### Prohibited

```
┌─────────────────────────────────────────────────────────────────┐
│  ❌ Consider command complete with unfulfilled 🔴 items          │
│  ❌ Skip "documentation" steps (reports, artifacts)              │
│  ❌ Selectively read command files (only technical sections)     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Reading Order for AI Agent

### When Working in the Target Project (TP)

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: Target Project Context (FIRST!)                            │
├─────────────────────────────────────────────────────────────────────┤
│  1. ./CLAUDE.md              ← TP Entry Point                        │
│  2. ./.pipeline-state.json   ← State, mode, passed gates            │
│  3. ./ai-docs/docs/          ← Existing artifacts                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: Precondition Check                                         │
├─────────────────────────────────────────────────────────────────────┤
│  4. Check required gates for the command                             │
│  5. If not passed → notify the user                                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3: Framework Instructions                                     │
├─────────────────────────────────────────────────────────────────────┤
│  6. .aidd/workflow.md        ← Process and gates                     │
│  7. .aidd/.claude/commands/  ← Command instructions                  │
│  8. .aidd/.claude/agents/    ← Role instructions                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 4: Templates (only if artifact does NOT exist)                │
├─────────────────────────────────────────────────────────────────────┤
│  9. .aidd/templates/documents/  ← Document Templates                 │
│  10. .aidd/knowledge/           ← Knowledge Base by topic            │
└─────────────────────────────────────────────────────────────────────┘
```

**Detailed algorithm**: [docs/initialization.md](docs/initialization.md)

### When Developing the Framework Itself

```
CLAUDE.md → docs/INDEX.md → conventions.md → workflow.md
```

---

## Quick Start

### New Project (CREATE)

```bash
# 1. Create project and connect framework
mkdir my-mvp && cd my-mvp
git init
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd

# 2. Launch Claude Code
claude

# 3. Start working
/aidd-analyze "Create a restaurant table booking service"

# 4. Follow the pipeline (stages 0-5)
/aidd-init → /aidd-analyze → /aidd-research → /aidd-plan → /aidd-code → /aidd-validate
```

### Adding a Feature (FEATURE)

```bash
cd existing-project
claude

# Start working
/aidd-analyze "Add email notification system"

# Pipeline
/aidd-analyze → /aidd-research → /aidd-plan-feature → /aidd-code → /aidd-validate
```

---

## Generated Service Types

| Type | Template | Port | Description |
|------|----------|------|-------------|
| **Business API** | `fastapi_business_api/` | 8000-8099 | REST API on FastAPI |
| **Data API (PostgreSQL)** | `postgres_data_api/` | 8001 | CRUD for PostgreSQL |
| **Data API (MongoDB)** | `mongo_data_api/` | 8002 | CRUD for MongoDB |
| **Telegram Bot** | `aiogram_bot/` | — | Bot on Aiogram |
| **Background Worker** | `asyncio_worker/` | — | Background tasks |

### Service Naming

```
{context}_{domain}_{type}

Examples:
- finance_lending_api      — Business API
- finance_lending_data     — Data API
- finance_lending_bot      — Telegram Bot
```

---

## Framework Structure

```
aidd-mvp-generator/
│
├── CLAUDE.md              ← YOU ARE HERE — entry point
├── conventions.md         ← Code Conventions
├── workflow.md            ← 6-stage process description
│
├── .claude/               ← Claude Code Integration
│   ├── settings.json      ← Permissions and hooks (committed)
│   ├── settings.local.json← Local permissions (DO NOT commit!)
│   ├── agents/            ← 5 roles + aliases + libraries (9 files)
│   └── commands/          ← 11 command files (6 unique)
│
├── roles/                 ← Detailed role instructions
├── knowledge/             ← Knowledge Base (architecture, services, quality)
├── templates/             ← Templates (services, documents, infrastructure)
└── docs/                  ← Generator documentation
```

**Full index**: [docs/INDEX.md](docs/INDEX.md)

---

## Documentation Navigation

| Looking for | Document |
|-------------|----------|
| Full file index | [docs/INDEX.md](docs/INDEX.md) |
| Navigation matrix | [docs/NAVIGATION.md](docs/NAVIGATION.md) |
| Initialization algorithm | [docs/initialization.md](docs/initialization.md) |
| 6-stage process | [workflow.md](workflow.md) |
| Code Conventions | [conventions.md](conventions.md) |
| Target Project structure | [docs/target-project-structure.md](docs/target-project-structure.md) |
| **Parallel pipelines** | [knowledge/pipeline/git-integration.md](knowledge/pipeline/git-integration.md) |
| Pipeline State v2 | [knowledge/pipeline/state-v2.md](knowledge/pipeline/state-v2.md) |
| Role instructions | `.claude/agents/{role}.md` |
| Command instructions | `.claude/commands/{command}.md` |
| Document Templates | `templates/documents/*.md` |
| Service Templates | `templates/services/*/` |
| Knowledge Base | `knowledge/` |

---

**Document version**: 2.3
**Updated**: 2025-12-25
**Purpose**: Main Entry Point for AI agents of AIDD-MVP Generator
