# AIDD-MVP Generator Links Reference

**Note:** This document may contain outdated commands `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Current commands: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Purpose**: Centralized reference of all important links in the generator.
> Use this file to quickly find the needed document.

---

## Entry Points

| File | Description | When to read |
|------|-------------|--------------|
| [CLAUDE.md](../CLAUDE.md) | Main Entry Point | First of all |
| [conventions.md](../conventions.md) | Code conventions | When writing code |
| [workflow.md](../workflow.md) | 9-stage process (0-8) | When executing commands |

---

## Indexes and Navigation

| File | Description |
|------|-------------|
| [docs/INDEX.md](INDEX.md) | Full generator file index |
| [docs/NAVIGATION.md](NAVIGATION.md) | "Read → Create" matrix |
| [docs/target-project-structure.md](target-project-structure.md) | Target Project structure |

---

## Agents (Roles)

| File | Role | Stage |
|------|------|-------|
| [.claude/agents/analyst.md](../.claude/agents/analyst.md) | Analyst | 1 |
| [.claude/agents/researcher.md](../.claude/agents/researcher.md) | Researcher | 2 |
| [.claude/agents/planner.md](../.claude/agents/planner.md) | Planner | 3 |
| [.claude/agents/coder.md](../.claude/agents/coder.md) | Coder | 4 |
| [.claude/agents/validator.md](../.claude/agents/validator.md) | Validator | 5 |

**Supporting instruction libraries** (used inside Validator):

| File | Purpose |
|------|---------|
| [.claude/agents/code-review-library.md](../.claude/agents/code-review-library.md) | Detailed instructions for Code Review (Step 1) |
| [.claude/agents/testing-library.md](../.claude/agents/testing-library.md) | Detailed instructions for Testing (Step 2) |

---

## Commands

| File | Command | Stage |
|------|---------|-------|
| [.claude/commands/aidd-analyze.md](../.claude/commands/aidd-analyze.md) | `/aidd-analyze` | 1 |
| [.claude/commands/aidd-research.md](../.claude/commands/aidd-research.md) | `/aidd-research` | 2 |
| [.claude/commands/aidd-plan.md](../.claude/commands/aidd-plan.md) | `/aidd-plan` | 3 (CREATE) |
| [.claude/commands/aidd-plan-feature.md](../.claude/commands/aidd-plan-feature.md) | `/aidd-plan-feature` | 3 (FEATURE) |
| [.claude/commands/aidd-code.md](../.claude/commands/aidd-code.md) | `/aidd-code` | 4 |
| [.claude/commands/aidd-validate.md](../.claude/commands/aidd-validate.md) | `/aidd-validate` | 7 |

---

## Document Templates

| Template (in generator) | Creates (in Target Project) |
|-------------------------|-----------------------------|
| [templates/documents/prd-template.md](../templates/documents/prd-template.md) | `ai-docs/docs/_analysis/{name}-prd.md` |
| [templates/documents/research-report-template.md](../templates/documents/research-report-template.md) | `ai-docs/docs/research/{name}-research.md` |
| [templates/documents/architecture-template.md](../templates/documents/architecture-template.md) | `ai-docs/docs/_plans/mvp/{name}-plan.md` |
| [templates/documents/feature-plan-template.md](../templates/documents/feature-plan-template.md) | `ai-docs/docs/_plans/features/{feature}-plan.md` |
| [templates/documents/completion-report-template.md](../templates/documents/completion-report-template.md) | `ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}-completion.md` |
| [templates/documents/pipeline-state-template.json](../templates/documents/pipeline-state-template.json) | `.pipeline-state.json` |

---

## Knowledge Base

### Architecture

| File | Description |
|------|-------------|
| [knowledge/architecture/improved-hybrid.md](../knowledge/architecture/improved-hybrid.md) | Hybrid architecture |
| [knowledge/architecture/ddd-hexagonal.md](../knowledge/architecture/ddd-hexagonal.md) | DDD and Hexagonal |
| [knowledge/architecture/project-structure.md](../knowledge/architecture/project-structure.md) | Project structure |

### Services

| Directory | Description |
|-----------|-------------|
| [knowledge/services/fastapi/](../knowledge/services/fastapi/) | FastAPI services |
| [knowledge/services/aiogram/](../knowledge/services/aiogram/) | Telegram bots |
| [knowledge/services/asyncio-workers/](../knowledge/services/asyncio-workers/) | Background workers |
| [knowledge/services/data-services/](../knowledge/services/data-services/) | Data API services |

### Quality

| File | Description |
|------|-------------|
| [knowledge/quality/quality-cascade.md](../knowledge/quality/quality-cascade.md) | **Quality Cascade v2** — cascading checks |
| [knowledge/quality/testing/](../knowledge/quality/testing/) | Testing |
| [knowledge/quality/dry-kiss-yagni.md](../knowledge/quality/dry-kiss-yagni.md) | Quality principles |

---

## Service Templates

| Template | Service Type | Port |
|----------|-------------|------|
| [templates/services/fastapi_business_api/](../templates/services/fastapi_business_api/) | Business API | 8000+ |
| [templates/services/aiogram_bot/](../templates/services/aiogram_bot/) | Telegram Bot | — |
| [templates/services/asyncio_worker/](../templates/services/asyncio_worker/) | Background Worker | — |
| [templates/services/postgres_data_api/](../templates/services/postgres_data_api/) | Data API (PostgreSQL) | 8001 |
| [templates/services/mongo_data_api/](../templates/services/mongo_data_api/) | Data API (MongoDB) | 8002 |

---

## Infrastructure

| File | Description |
|------|-------------|
| [templates/infrastructure/docker-compose.yml](../templates/infrastructure/docker-compose.yml) | Docker Compose |
| [templates/infrastructure/Makefile](../templates/infrastructure/Makefile) | Makefile |
| [templates/infrastructure/nginx/](../templates/infrastructure/nginx/) | Nginx configuration |

---

## Reference Materials

| File | Description |
|------|-------------|
| [templates/documents/template-map.md](../templates/documents/template-map.md) | Template map |
| [docs/reference/deliverables-catalog.md](reference/deliverables-catalog.md) | Artifact catalog |

---

**Version**: 1.0
**Created**: 2025-12-21
