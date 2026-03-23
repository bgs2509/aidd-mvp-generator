# Target Project Structure

**Note:** This document may contain outdated commands `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Current commands: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Purpose**: Description of the project structure CREATED by the generator.
> **IMPORTANT**: Do NOT confuse with the generator itself (aidd-mvp-generator) structure!

---

## Conceptual Separation

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TWO DIFFERENT PROJECTS                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  aidd-mvp-generator/          {project-name}/                           │
│  ─────────────────────        ─────────────────────                     │
│  FRAMEWORK                    APPLICATION                               │
│  (instructions, templates)    (created by generator)                    │
│                                                                         │
│  Contains:                    Contains:                                 │
│  • CLAUDE.md                  • services/                               │
│  • workflow.md                • ai-docs/docs/                           │
│  • .claude/agents/            • docker-compose.yml                      │
│  • templates/                 • Makefile                                │
│  • knowledge/                 • .pipeline-state.json                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Target Project Structure

```
{project-name}/
│
├── .pipeline-state.json       ← AIDD pipeline state
├── CHANGELOG.md               ← Project changelog
│
├── ai-docs/                   ← AI agent artifacts
│   └── docs/
│       ├── FEATURES.md        ← Feature registry (index)
│       │
│       ├── prd/               ← PRD documents
│       │   └── {YYYY-MM-DD}_{FID}_{slug}-prd.md
│       │
│       ├── architecture/      ← Architecture plans (CREATE)
│       │   └── {YYYY-MM-DD}_{FID}_{slug}-plan.md
│       │
│       ├── plans/             ← Feature plans (FEATURE)
│       │   └── {YYYY-MM-DD}_{FID}_{slug}-plan.md
│       │
│       ├── research/          ← Research reports
│       │   └── {YYYY-MM-DD}_{FID}_{slug}-research.md
│       │
│       └── reports/           ← Completion Reports
│           └── {YYYY-MM-DD}_{FID}_{slug}-completion.md
│
├── services/                  ← Service code (DDD/Hexagonal)
│   ├── {name}_api/            ← Business API
│   │   ├── api/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── {name}_data/           ← Data API
│   │   ├── api/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   ├── {name}_bot/            ← Telegram Bot (optional)
│   │   └── ...
│   │
│   └── {name}_worker/         ← Background Worker (optional)
│       └── ...
│
├── docs/                      ← Public API documentation
│   └── api/
│       └── openapi.yaml
│
├── nginx/                     ← API Gateway configuration
│   ├── nginx.conf
│   └── conf.d/
│       └── api.conf
│
├── .claude/                   ← Local Claude Code settings
│   └── settings.local.json    ← Personal permissions (NOT in git!)
│
├── docker-compose.yml         ← Container orchestration
├── docker-compose.dev.yml     ← For development
├── Makefile                   ← Management commands
├── .env.example               ← Environment variables template
├── .gitignore
└── README.md                  ← Project documentation
```

---

## Artifact Table

> **Name format**: `{YYYY-MM-DD}_{FID}_{slug}-{type}.md`
> Details: [artifact-naming.md](artifact-naming.md)

| Stage | Artifact | Path in Target Project |
|-------|----------|------------------------|
| — | Feature registry | `ai-docs/docs/FEATURES.md` |
| 1. Idea | PRD | `ai-docs/docs/_analysis/{date}_{FID}_{slug}-prd.md` |
| 2. Research | Research report | `ai-docs/docs/research/{date}_{FID}_{slug}-research.md` |
| 3. Architecture (CREATE) | Plan | `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}-plan.md` |
| 3. Architecture (FEATURE) | Feature plan | `ai-docs/docs/_plans/features/{date}_{FID}_{slug}-plan.md` |
| 4. Implementation | Code | `services/*/` |
| 5. Quality & Deploy | Completion Report | `ai-docs/docs/_validation/{date}_{FID}_{slug}-completion.md` |

### File Name Examples

```
2024-12-23_F001_table-booking-prd.md
2024-12-23_F001_table-booking-research.md
2024-12-23_F001_table-booking-plan.md
2024-12-23_F001_table-booking-completion.md
```

---

## Pipeline State

The `.pipeline-state.json` file in the Target Project root:

```json
{
  "version": "2.0",
  "project_name": "booking-service",
  "mode": "CREATE",
  "created_at": "2025-12-21T10:00:00Z",
  "updated_at": "2025-12-21T10:30:00Z",

  "next_feature_id": 3,

  "global_gates": {
    "BOOTSTRAP_READY": { "passed": true, "passed_at": "2025-12-21T09:55:00Z" }
  },

  "active_pipelines": {
    "F002": {
      "branch": "feature/F002-email-notify",
      "name": "email-notify",
      "title": "Booking email notifications",
      "stage": "IMPLEMENT",
      "created": "2025-12-21",
      "gates": {
        "PRD_READY": { "passed": true, "passed_at": "2025-12-21T10:05:00Z" },
        "RESEARCH_DONE": { "passed": true, "passed_at": "2025-12-21T10:10:00Z" },
        "PLAN_APPROVED": { "passed": true, "passed_at": "2025-12-21T10:20:00Z", "approved_by": "user" },
        "IMPLEMENT_OK": { "passed": false }
      },
      "artifacts": {
        "prd": "prd/2025-12-21_F002_email-notify-prd.md",
        "research": "research/2025-12-21_F002_email-notify-research.md",
        "plan": "plans/2025-12-21_F002_email-notify-plan.md"
      }
    }
  },

  "features_registry": {
    "F001": {
      "name": "table-booking",
      "title": "Table booking",
      "status": "DEPLOYED",
      "created": "2025-12-20",
      "deployed": "2025-12-21",
      "artifacts": {
        "prd": "prd/2025-12-20_F001_table-booking-prd.md",
        "research": "research/2025-12-20_F001_table-booking-research.md",
        "plan": "architecture/2025-12-20_F001_table-booking-plan.md",
        "completion": "reports/2025-12-21_F001_table-booking-completion.md"
      },
      "services": ["booking_api", "booking_data"]
    }
  }
}
```

### `active_pipelines[FID]` Structure

| Field | Type | Description |
|-------|------|-------------|
| `branch` | string | Feature git branch (feature/F001-name) |
| `name` | string | Slug for file names (kebab-case) |
| `title` | string | Human-readable title |
| `stage` | string | Current stage (IDEA, RESEARCH, PLAN, IMPLEMENT, ...) |
| `created` | string | Creation date (YYYY-MM-DD) |
| `gates` | object | Feature gates (isolated from other pipelines) |
| `artifacts` | object | Artifact map (type → path) |

### Feature Lifecycle (v2)

```
1. /aidd-analyze creates active_pipelines[FID] with a new Feature ID
2. Each stage updates gates and artifacts in active_pipelines[FID]
3. /aidd-validate moves the feature to features_registry (upon DEPLOYED)
4. Record is removed from active_pipelines
5. Ready for the next feature (or parallel development)
```

---

## Changelog (CHANGELOG.md)

The `CHANGELOG.md` file in the Target Project root:

### Purpose

**Single entry point** for understanding project history. Contains:
- Completed features (automatically from Completion Reports)
- Critical changes between features (manually by AI)
- Reverse chronological order (newest on top)

### Structure

```markdown
# Changelog

> Auto-generated by AIDD-MVP Generator upon `/aidd-validate` (DEPLOYED)
> Manual entries added by AI for critical changes

---

## [Unreleased]

### Active Features (in development)
- **F002** — Email notifications (stage: IMPLEMENT)

### Recent Changes

#### 2025-12-22 - Hotfix: SQL injection in User API
**Security**
- `user_api/repository.py`: parameterized SQL queries

**Impact**: CRITICAL
**Rollback**: `git revert abc123`

---

## [F001] - 2025-12-21 — Table Booking

> **Status**: DEPLOYED
> **Services**: `booking_api`, `booking_data`
> **Completion Report**: [ai-docs/docs/reports/2025-12-21_F001_table-booking-completion.md]

### Added
- Basic booking functionality
- Endpoints: POST /api/v1/bookings, GET /api/v1/bookings

### Architecture Decisions
- ADR-001: HTTP-only Data Access (DDD/Hexagonal)

---

**Version**: 1.0
**Last update**: 2025-12-22
```

### Automatic Updates

| Event | Action |
|-------|--------|
| `/aidd-init` | Created from template (if no history) or generated from `features_registry` |
| `/aidd-validate` → DEPLOYED | Feature section automatically added from Completion Report |
| Critical changes | AI manually adds entries to `[Unreleased]` (see TP CLAUDE.md) |

### Why AI Reads CHANGELOG.md

**CRITICAL**: AI MUST read `CHANGELOG.md` BEFORE starting work (see TP CLAUDE.md).

This allows:
- Understanding project context in 30 seconds
- Not duplicating functionality
- Accounting for known limitations (Known Limitations)
- Understanding dependencies between features
- Following architectural decisions (ADR)

---

## Claude Code Settings (.claude/)

> **IMPORTANT**: The `.claude/` directory contains local Claude Code settings for the Target Project.

### Two Types of Settings Files

| File | Location | In git? | Purpose |
|------|----------|---------|---------|
| `settings.json` | `.aidd/.claude/settings.json` | Yes (in submodule) | Shared framework permissions and hooks |
| `settings.local.json` | `./.claude/settings.local.json` | **No** | Personal local permissions |

### settings.local.json

File for personal developer settings that **MUST NOT be committed to git**.

**Purpose**:
- Additional bash command permissions (npm, cargo, poetry)
- Trusted domains for WebFetch (docs.python.org, etc.)
- Local setting overrides

**Template**:
```json
{
  "permissions": {
    "allow": [
      "WebFetch(domain:docs.python.org)",
      "WebFetch(domain:fastapi.tiangolo.com)",
      "Bash(npm:*)",
      "Bash(poetry:*)"
    ]
  }
}
```

**Creation**:
```bash
# Copy template from framework
mkdir -p .claude
cp .aidd/templates/project/.claude/settings.local.json.example .claude/settings.local.json
```

> **Note**: File is added to the project template's `.gitignore`.

---

## Important Conventions

### Artifact Name Format

```
{YYYY-MM-DD}_{FID}_{slug}-{type}.md

Where:
- YYYY-MM-DD — creation date
- FID — Feature ID (F001, F002, ...)
- slug — kebab-case name (≤30 characters)
- type — artifact type
```

### Type Suffixes

| Type | Suffix | Example |
|------|--------|---------|
| PRD | `-prd.md` | `2024-12-23_F001_table-booking-prd.md` |
| Architecture plan | `-plan.md` | `2024-12-23_F001_table-booking-plan.md` |
| Feature plan | `-plan.md` | `2024-12-23_F042_email-notify-plan.md` |
| Research | `-research.md` | `2024-12-23_F001_table-booking-research.md` |
| Completion Report | `-completion.md` | `2024-12-23_F001_table-booking-completion.md` |

> Detailed specification: [artifact-naming.md](artifact-naming.md)

### Service Naming

```
{context}_{domain}_{type}

Examples:
- booking_restaurant_api      ← Business API
- booking_restaurant_data     ← Data API
- booking_restaurant_bot      ← Telegram Bot
- booking_restaurant_worker   ← Background Worker
```

---

## Bootstrap: Structure Initialization

On first `/aidd-analyze` run in an empty directory:

```bash
mkdir -p ai-docs/docs/{prd,architecture,plans,reports,research}
echo '{"version":"2.0","project_name":"","mode":"CREATE","global_gates":{},"active_pipelines":{},"next_feature_id":1}' > .pipeline-state.json
```

---

## See Also

- [CLAUDE.md](../CLAUDE.md) — Generator structure
- [workflow.md](../workflow.md) — Development process
- [conventions.md](../conventions.md) — Code conventions

---

**Version**: 2.0
**Created**: 2025-12-21
**Updated**: 2025-12-23
