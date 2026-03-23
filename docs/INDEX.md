# AIDD-MVP Generator File Index


> **Purpose**: Navigation through FRAMEWORK (generator) files.
> For Target Project structure see [target-project-structure.md](target-project-structure.md)

---

## Entry Points

| File | Purpose | When to read |
|------|---------|--------------|
| [CLAUDE.md](../CLAUDE.md) | Main Entry Point | First |
| [initialization.md](initialization.md) | Initialization algorithm (4 phases) | When running a command |
| [conventions.md](../conventions.md) | Code conventions | When writing code |
| [workflow.md](../workflow.md) | Pipeline (stages 0-5) | When working with the pipeline |
| [artifact-naming.md](artifact-naming.md) | Artifact naming system (FID) | When creating artifacts |

---

## Agent Roles

| File | Role | Stages | Gates |
|------|------|--------|-------|
| [.claude/agents/analyst.md](../.claude/agents/analyst.md) | Analyst | 1 | PRD_READY |
| [.claude/agents/researcher.md](../.claude/agents/researcher.md) | Researcher | 2 | RESEARCH_DONE |
| [.claude/agents/planner.md](../.claude/agents/planner.md) | Planner | 3 | PLAN_APPROVED |
| [.claude/agents/coder.md](../.claude/agents/coder.md) | Coder | 4 | IMPLEMENT_OK |
| [.claude/agents/validator.md](../.claude/agents/validator.md) | Validator | 5 | REVIEW_OK, QA_PASSED, ALL_GATES_PASSED, DEPLOYED |

---

## Slash Commands

| Command | File | Description |
|---------|------|-------------|
| `/aidd-init` | [.claude/commands/aidd-init.md](../.claude/commands/aidd-init.md) | Bootstrap (Target Project initialization) |
| `/aidd-analyze` | [.claude/commands/aidd-analyze.md](../.claude/commands/aidd-analyze.md) | PRD creation |
| `/aidd-research` | [.claude/commands/aidd-research.md](../.claude/commands/aidd-research.md) | Research |
| `/aidd-plan` | [.claude/commands/aidd-plan.md](../.claude/commands/aidd-plan.md) | Architecture (CREATE) |
| `/aidd-plan-feature` | [.claude/commands/aidd-plan-feature.md](../.claude/commands/aidd-plan-feature.md) | Feature plan (FEATURE) |
| `/aidd-code` | [.claude/commands/aidd-code.md](../.claude/commands/aidd-code.md) | Code generation |
| `/aidd-validate` | [.claude/commands/aidd-validate.md](../.claude/commands/aidd-validate.md) | Quality & Deploy (Review → Test → Validate → Deploy) |

> Pipeline overview: [CLAUDE.md](../CLAUDE.md#6-этапный-пайплайн)

---

## Knowledge Base

> Knowledge base index: [knowledge/README.md](../knowledge/README.md)

### Architecture
| File | Topic |
|------|-------|
| [knowledge/architecture/ddd-hexagonal.md](../knowledge/architecture/ddd-hexagonal.md) | DDD/Hexagonal architecture |
| [knowledge/architecture/project-structure.md](../knowledge/architecture/project-structure.md) | Project structure |
| [knowledge/architecture/service-separation.md](../knowledge/architecture/service-separation.md) | Service separation |
| [knowledge/architecture/data-access.md](../knowledge/architecture/data-access.md) | Data access |

### Services
| Folder | Topic |
|--------|-------|
| [knowledge/services/fastapi/](../knowledge/services/fastapi/) | FastAPI services (5 files) |
| [knowledge/services/aiogram/](../knowledge/services/aiogram/) | Telegram bots (4 files) |
| [knowledge/services/asyncio-workers/](../knowledge/services/asyncio-workers/) | Background workers (3 files) |
| [knowledge/services/data-services/](../knowledge/services/data-services/) | Data Services (2 files) |

### Integrations
| Folder | Topic |
|--------|-------|
| [knowledge/integrations/http/](../knowledge/integrations/http/) | HTTP clients (3 files) |
| [knowledge/integrations/redis/](../knowledge/integrations/redis/) | Redis integration (2 files) |

### Infrastructure
| File | Topic |
|------|-------|
| [knowledge/infrastructure/docker-compose.md](../knowledge/infrastructure/docker-compose.md) | Docker Compose |
| [knowledge/infrastructure/dockerfile.md](../knowledge/infrastructure/dockerfile.md) | Dockerfile |
| [knowledge/infrastructure/nginx.md](../knowledge/infrastructure/nginx.md) | Nginx gateway |
| [knowledge/infrastructure/ci-cd.md](../knowledge/infrastructure/ci-cd.md) | CI/CD |

### Quality
| Path | Topic |
|------|-------|
| [knowledge/quality/quality-cascade.md](../knowledge/quality/quality-cascade.md) | **Quality Cascade v2** — cascading quality checks |
| [knowledge/quality/testing/](../knowledge/quality/testing/) | Testing (5 files) |
| [knowledge/quality/logging/](../knowledge/quality/logging/) | Logging (2 files) |
| [knowledge/quality/dry-kiss-yagni.md](../knowledge/quality/dry-kiss-yagni.md) | DRY/KISS/YAGNI principles |
| [knowledge/quality/production-requirements.md](../knowledge/quality/production-requirements.md) | Production requirements |

---

## Document Templates

| Template | Path in generator | Creates in Target Project |
|----------|-------------------|--------------------------|
| PRD | [templates/documents/prd-template.md](../templates/documents/prd-template.md) | `ai-docs/docs/_analysis/{name}.md` |
| Research Report | [templates/documents/research-report-template.md](../templates/documents/research-report-template.md) | `ai-docs/docs/_research/{name}.md` |
| Architecture | [templates/documents/architecture-template.md](../templates/documents/architecture-template.md) | `ai-docs/docs/_plans/mvp/{name}.md` |
| Feature Plan (FEATURE) | [templates/documents/feature-plan-template.md](../templates/documents/feature-plan-template.md) | `ai-docs/docs/_plans/features/{name}.md` |
| Implementation Plan | [templates/documents/implementation-plan-template.md](../templates/documents/implementation-plan-template.md) | `ai-docs/docs/_plans/mvp/{name}-impl.md` |
| **Completion Report** | [templates/documents/completion-report-template.md](../templates/documents/completion-report-template.md) | `ai-docs/docs/_validation/{date}_{FID}_{slug}.md` |
| Pipeline State | [templates/documents/pipeline-state-template.json](../templates/documents/pipeline-state-template.json) | `.pipeline-state.json` |

---

## Service Templates

| Service Type | Template Path | Port |
|--------------|--------------|------|
| Business API | [templates/services/fastapi_business_api/](../templates/services/fastapi_business_api/) | 8000-8099 |
| Data API (PostgreSQL) | [templates/services/postgres_data_api/](../templates/services/postgres_data_api/) | 8001 |
| Data API (MongoDB) | [templates/services/mongo_data_api/](../templates/services/mongo_data_api/) | 8002 |
| Telegram Bot | [templates/services/aiogram_bot/](../templates/services/aiogram_bot/) | — |
| Background Worker | [templates/services/asyncio_worker/](../templates/services/asyncio_worker/) | — |

---

## Infrastructure Templates

| Component | Path |
|-----------|------|
| Docker | [templates/infrastructure/docker/](../templates/infrastructure/docker/) |
| Nginx | [templates/infrastructure/nginx/](../templates/infrastructure/nginx/) |

---

## Project Templates (TP root files)

> Files created in the Target Project root during `/aidd-init`.

| Template | Path in generator | Creates in TP | Purpose |
|----------|-------------------|---------------|---------|
| CLAUDE.md | [templates/project/CLAUDE.md.template](../templates/project/CLAUDE.md.template) | `./CLAUDE.md` | Entry Point for AI |
| README.md | [templates/project/README.md.template](../templates/project/README.md.template) | `./README.md` | Project documentation |
| .gitignore | [templates/project/.gitignore.template](../templates/project/.gitignore.template) | `./.gitignore` | Ignored files |
| .env.example | [templates/project/.env.example.template](../templates/project/.env.example.template) | `./.env.example` | Environment variables example |
| settings.local | [templates/project/.claude/settings.local.json.example](../templates/project/.claude/settings.local.json.example) | `./.claude/settings.local.json.example` | Local Claude Code settings |

---

## Detailed Instructions (roles/)

### Analyst
| File | Function |
|------|----------|
| [roles/analyst/initialization.md](../roles/analyst/initialization.md) | Initialization |
| [roles/analyst/prompt-validation.md](../roles/analyst/prompt-validation.md) | Prompt validation |
| [roles/analyst/requirements-gathering.md](../roles/analyst/requirements-gathering.md) | Requirements gathering |
| [roles/analyst/prd-formation.md](../roles/analyst/prd-formation.md) | PRD formation |

### Researcher
| File | Function |
|------|----------|
| [roles/researcher/codebase-analysis.md](../roles/researcher/codebase-analysis.md) | Codebase analysis |
| [roles/researcher/pattern-identification.md](../roles/researcher/pattern-identification.md) | Pattern identification |
| [roles/researcher/constraint-identification.md](../roles/researcher/constraint-identification.md) | Constraints |

### Planner
| File | Function |
|------|----------|
| [roles/planner/architecture-design.md](../roles/planner/architecture-design.md) | Design |
| [roles/planner/maturity-level-selection.md](../roles/planner/maturity-level-selection.md) | Level selection |
| [roles/planner/service-naming.md](../roles/planner/service-naming.md) | Naming |
| [roles/planner/api-contracts.md](../roles/planner/api-contracts.md) | API contracts |

### Coder
| File | Function |
|------|----------|
| [roles/coder/infrastructure-setup.md](../roles/coder/infrastructure-setup.md) | Infrastructure |
| [roles/coder/data-service.md](../roles/coder/data-service.md) | Data Service |
| [roles/coder/business-api.md](../roles/coder/business-api.md) | Business API |
| [roles/coder/testing.md](../roles/coder/testing.md) | Testing |

### Reviewer
| File | Function |
|------|----------|
| [roles/reviewer/architecture-compliance.md](../roles/reviewer/architecture-compliance.md) | Architecture |
| [roles/reviewer/convention-compliance.md](../roles/reviewer/convention-compliance.md) | Conventions |

### QA
| File | Function |
|------|----------|
| [roles/qa/test-execution.md](../roles/qa/test-execution.md) | Test execution |
| [roles/qa/coverage-verification.md](../roles/qa/coverage-verification.md) | Coverage |

### Validator
| File | Function |
|------|----------|
| [roles/validator/quality-gates.md](../roles/validator/quality-gates.md) | Quality Gates check |
| [roles/validator/artifact-verification.md](../roles/validator/artifact-verification.md) | Verification |

---

## Quick Search

| Looking for | Where to look |
|-------------|---------------|
| How to start a project | [CLAUDE.md](../CLAUDE.md) → Quick Start |
| Initialization algorithm | [initialization.md](initialization.md) |
| What files to create | [target-project-structure.md](target-project-structure.md) |
| Code rules | [conventions.md](../conventions.md) |
| Process stages | [workflow.md](../workflow.md) |
| File reading order | [initialization.md](initialization.md) → "Reading Order Table" |
| TP vs Framework criteria | [initialization.md](initialization.md) → "Source Determination Criteria" |
| Role instructions | `.claude/agents/{role}.md` |
| Document template | `templates/documents/*.md` |
| Service template | `templates/services/*/` |
| TP file templates | `templates/project/*.template` |

---

## Documentation Audit

| Template | Purpose |
|----------|---------|
| [audit/templates/comprehensive-audit.md](audit/templates/comprehensive-audit.md) | Comprehensive audit (12 smoke tests, 16 objectives) |

---

## See Also

- [initialization.md](initialization.md) — Initialization algorithm (4 phases)
- [NAVIGATION.md](NAVIGATION.md) — Navigation matrix by stages
- [PIPELINE-TREE.md](PIPELINE-TREE.md) — All pipelines tree
- [target-project-structure.md](target-project-structure.md) — Target Project structure

---

**Version**: 2.0
**Updated**: 2025-12-21
