# PIPELINE-TREE.md — AIDD-MVP Pipeline Tree

**Note:** This document may contain outdated commands `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Current commands: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Purpose**: Complete map of all framework pipelines.
> For each pipeline the following is specified: command, agent, gates, artifacts, file sources.

---

## Visual Pipeline Tree

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          AIDD-MVP PIPELINE TREE                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────┐                                                                │
│  │   STAGE 0    │  Bootstrap Pipeline                                            │
│  │   /aidd-init │  ──────────────────────────────────────────────────────────── │
│  │              │  Target Project initialization                                │
│  └──────┬───────┘                                                                │
│         │ BOOTSTRAP_READY                                                        │
│         ▼                                                                        │
│  ┌──────────────┐                                                                │
│  │   STAGE 1    │  Idea Pipeline                                                 │
│  │ /aidd-analyze│  ──────────────────────────────────────────────────────────── │
│  │              │  PRD document creation                                         │
│  └──────┬───────┘                                                                │
│         │ PRD_READY                                                              │
│         ▼                                                                        │
│  ┌──────────────┐                                                                │
│  │   STAGE 2    │  Research Pipeline                                             │
│  │/aidd-research│  ──────────────────────────────────────────────────────────── │
│  │              │  Research and analysis                                          │
│  └──────┬───────┘                                                                │
│         │ RESEARCH_DONE                                                          │
│         ▼                                                                        │
│  ┌──────────────┐                                                                │
│  │   STAGE 3    │  Architecture Pipeline                                         │
│  │ /aidd-plan or│  ──────────────────────────────────────────────────────────── │
│  │ /feature-plan│  Architecture design                                           │
│  └──────┬───────┘                                                                │
│         │ PLAN_APPROVED (requires user confirmation)                              │
│         ▼                                                                        │
│  ┌──────────────┐                                                                │
│  │   STAGE 4    │  Implementation Pipeline                                       │
│  │   /aidd-code │  ──────────────────────────────────────────────────────────── │
│  │              │  Code generation                                               │
│  └──────┬───────┘                                                                │
│         │ IMPLEMENT_OK                                                           │
│         ▼                                                                        │
│  ┌───────────────────────────────────────────────────────────────┐              │
│  │   STAGE 5: Quality & Deploy Pipeline (/aidd-validate)         │              │
│  │  ──────────────────────────────────────────────────────────── │              │
│  │                                                                │              │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────────────┐      │              │
│  │  │ Review │─▶│  Test  │─▶│Validate│─▶│Deploy + Report │      │              │
│  │  └────┬───┘  └────┬───┘  └────┬───┘  └────┬───────────┘      │              │
│  │       │           │           │            │                  │              │
│  │  REVIEW_OK    QA_PASSED  ALL_GATES     DEPLOYED              │              │
│  │                                 PASSED                        │              │
│  │                                                                │              │
│  │  Artifact: 1 Completion Report (instead of 4 files)           │              │
│  └────────────────────────────────┬───────────────────────────────┘              │
│                                   │                                              │
│                                   ▼                                              │
│                              ✅ MVP READY                                        │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Pipeline Description

### Stage 0: Bootstrap Pipeline

| Parameter | Value |
|-----------|-------|
| **Command** | `/aidd-init` (manual) or auto with `/aidd-analyze` |
| **Agent** | — (system) |
| **Preconditions** | — |
| **Quality Gates** | `BOOTSTRAP_READY` |

#### Checks

| # | Check | Command/File | Criterion |
|---|-------|--------------|-----------|
| 1 | Git repository | `git rev-parse --git-dir` | Exit 0 |
| 2 | Framework connected | `.aidd/CLAUDE.md` | File exists |
| 3 | Python version | `python3 --version` | >= 3.11 |
| 4 | Docker | `docker --version` | Installed |

#### Actions

| # | Action | Result |
|---|--------|--------|
| 1 | Create folder structure | `ai-docs/docs/{prd,architecture,plans,reports,research}` |
| 2 | Create pipeline state | `.pipeline-state.json` |
| 3 | Create CLAUDE.md | `./CLAUDE.md` → link to `.aidd/CLAUDE.md` |

#### File Sources

| File | Source | Path |
|------|--------|------|
| Command instructions | Framework | `.aidd/.claude/commands/aidd-init.md` |
| CLAUDE.md (template) | Framework | `.aidd/CLAUDE.md` |
| TP structure | Framework | `.aidd/docs/target-project-structure.md` |
| **Result** | TP | `./CLAUDE.md`, `./ai-docs/docs/`, `./.pipeline-state.json` |

---

### Stage 1: Idea Pipeline (PRD)

| Parameter | Value |
|-----------|-------|
| **Command** | `/aidd-analyze "description"` |
| **Agent** | Analyst |
| **Preconditions** | `BOOTSTRAP_READY` (or auto-bootstrap) |
| **Quality Gates** | `PRD_READY` |

#### Input Artifacts

| Artifact | Source | Path |
|----------|--------|------|
| Idea description | User | Command argument |
| PRD Template | Framework | `.aidd/templates/documents/prd-template.md` |

#### Output Artifacts

| Artifact | Path in TP |
|----------|------------|
| PRD document | `ai-docs/docs/_analysis/{name}-prd.md` |
| State | `.pipeline-state.json` (updated) |

#### File Sources

| File | Source | Path |
|------|--------|------|
| Command instructions | Framework | `.aidd/.claude/commands/aidd-analyze.md` |
| Agent instructions | Framework | `.aidd/.claude/agents/analyst.md` |
| PRD Template | Framework | `.aidd/templates/documents/prd-template.md` |
| Workflow | Framework | `.aidd/workflow.md` |
| **Result** | TP | `ai-docs/docs/_analysis/{name}-prd.md` |

---

### Stage 2: Research Pipeline

| Parameter | Value |
|-----------|-------|
| **Command** | `/aidd-research` |
| **Agent** | Researcher |
| **Preconditions** | `PRD_READY` |
| **Quality Gates** | `RESEARCH_DONE` |

#### Input Artifacts

| Artifact | Source | Path |
|----------|--------|------|
| PRD | TP | `ai-docs/docs/_analysis/{name}-prd.md` |
| Existing code | TP | `services/` (for FEATURE) |

#### Output Artifacts

| Artifact | Path in TP |
|----------|------------|
| Research report | `ai-docs/docs/research/{name}-research.md` |
| State | `.pipeline-state.json` (updated) |

#### File Sources

| File | Source | Path |
|------|--------|------|
| Command instructions | Framework | `.aidd/.claude/commands/aidd-research.md` |
| Agent instructions | Framework | `.aidd/.claude/agents/researcher.md` |
| Detailed instructions | Framework | `.aidd/roles/researcher/*.md` |
| Report template | Framework | `.aidd/templates/documents/research-report-template.md` |
| PRD | TP | `ai-docs/docs/_analysis/{name}-prd.md` |

---

### Stage 3: Architecture Pipeline

| Parameter | CREATE Value | FEATURE Value |
|-----------|-------------|---------------|
| **Command** | `/aidd-plan` | `/aidd-plan-feature` |
| **Agent** | Planner | Planner |
| **Preconditions** | `PRD_READY`, `RESEARCH_DONE` | `PRD_READY`, `RESEARCH_DONE` |
| **Quality Gates** | `PLAN_APPROVED` | `PLAN_APPROVED` |

#### Input Artifacts

| Artifact | Source | Path |
|----------|--------|------|
| PRD | TP | `ai-docs/docs/_analysis/{name}-prd.md` |
| Research report | TP | `ai-docs/docs/research/{name}-research.md` |
| Architecture template | Framework | `.aidd/templates/documents/architecture-template.md` |

#### Output Artifacts

| Artifact | Path in TP (CREATE) | Path in TP (FEATURE) |
|----------|--------------------|-----------------------|
| Architecture plan | `ai-docs/docs/_plans/mvp/{name}-plan.md` | — |
| Feature plan | — | `ai-docs/docs/_plans/features/{feature}-plan.md` |

#### File Sources

| File | Source | Path |
|------|--------|------|
| Command instructions | Framework | `.aidd/.claude/commands/aidd-plan.md` or `aidd-feature-plan.md` |
| Agent instructions | Framework | `.aidd/.claude/agents/planner.md` |
| Detailed instructions | Framework | `.aidd/roles/architect/*.md` |
| Knowledge Base | Framework | `.aidd/knowledge/architecture/*.md` |
| **Result** | TP | `ai-docs/docs/_plans/mvp/` or `ai-docs/docs/_plans/features/` |

---

### Stage 4: Implementation Pipeline

| Parameter | Value |
|-----------|-------|
| **Command** | `/aidd-code` |
| **Agent** | Coder |
| **Preconditions** | `PLAN_APPROVED` |
| **Quality Gates** | `IMPLEMENT_OK` |

#### Input Artifacts

| Artifact | Source | Path |
|----------|--------|------|
| Plan | TP | `ai-docs/docs/_plans/mvp/{name}-plan.md` |
| Service templates | Framework | `.aidd/templates/services/` |
| Infrastructure templates | Framework | `.aidd/templates/infrastructure/` |
| Shared components | Framework | `.aidd/templates/shared/` |

#### Output Artifacts

| Artifact | Path in TP |
|----------|------------|
| Business API | `services/{name}_api/` |
| Data API | `services/{name}_data/` |
| Telegram Bot | `services/{name}_bot/` |
| Background Worker | `services/{name}_worker/` |
| Docker Compose | `docker-compose.yml` |
| Makefile | `Makefile` |
| Nginx | `nginx/` |

#### File Sources

| File | Source | Path |
|------|--------|------|
| Command instructions | Framework | `.aidd/.claude/commands/aidd-code.md` |
| Agent instructions | Framework | `.aidd/.claude/agents/coder.md` |
| Detailed instructions | Framework | `.aidd/roles/implementer/*.md` |
| FastAPI Template | Framework | `.aidd/templates/services/fastapi_business_api/` |
| Data API Template | Framework | `.aidd/templates/services/postgres_data_api/` |
| Bot Template | Framework | `.aidd/templates/services/aiogram_bot/` |
| Worker Template | Framework | `.aidd/templates/services/asyncio_worker/` |
| Knowledge Base | Framework | `.aidd/knowledge/services/*.md` |
| Conventions | Framework | `.aidd/conventions.md` |
| **Result** | TP | `services/`, `docker-compose.yml`, `Makefile` |

---

### Stage 5: Quality & Deploy Pipeline

| Parameter | Value |
|-----------|-------|
| **Command** | `/aidd-validate` (or `/aidd-validate` in v2.4+) |
| **Agent** | Validator |
| **Preconditions** | `IMPLEMENT_OK` |
| **Quality Gates** | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` |

#### Description

The Quality & Deploy stage performs a full quality check and deploy cycle in 4 sequential steps:

1. **Code Review** → `REVIEW_OK`
2. **Testing** → `QA_PASSED`
3. **Validation** → `ALL_GATES_PASSED`
4. **Deploy & Completion Report** → `DEPLOYED`

#### Input Artifacts

| Artifact | Source | Path |
|----------|--------|------|
| Service code | TP | `services/` |
| PRD | TP | `ai-docs/docs/_analysis/{name}-prd.md` |
| Plan | TP | `ai-docs/docs/_plans/mvp/{name}-plan.md` |
| Docker Compose | TP | `docker-compose.yml` |
| Makefile | TP | `Makefile` |
| State | TP | `.pipeline-state.json` |

#### Output Artifacts

| Artifact | Path in TP |
|----------|------------|
| **Completion Report** | `ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}-completion.md` |

**Completion Report contains** (single artifact instead of 4 files):
- Executive Summary
- Code Review Summary
- Testing Summary
- Requirements Traceability
- ADR (Architecture Decision Records)
- Scope Changes
- Known Limitations
- Quality metrics

#### Two Operating Modes

| Mode | Gates | Artifact |
|------|-------|----------|
| **Full** (recommended) | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` | Production-ready Completion Report |
| **Quick** | `DOCUMENTED` | DRAFT Completion Report (static analysis only) |

#### Actions (Full mode)

| Step | Actions | Checks |
|------|---------|--------|
| 1. Review | Quality Cascade (17 checks), Security checklist | DDD, HTTP-only, conventions.md |
| 2. Test | `pytest --cov --cov-fail-under=75` | Coverage ≥75%, all FR-* |
| 3. Validate | Check all gates, final security check | ALL_GATES_PASSED |
| 4. Deploy | `make build && make up && make health` | Containers running, Completion Report created |

#### File Sources

| File | Source | Path |
|------|--------|------|
| Command instructions | Framework | `.aidd/.claude/commands/aidd-validate.md` |
| Agent instructions | Framework | `.aidd/.claude/agents/validator.md` |
| **Code Review Library** | Framework | `.aidd/.claude/agents/code-review-library.md` |
| **Testing Library** | Framework | `.aidd/.claude/agents/testing-library.md` |
| Conventions | Framework | `.aidd/conventions.md` |
| Quality Cascade | Framework | `.aidd/knowledge/quality/quality-cascade.md` |
| Security Checklist | Framework | `.aidd/knowledge/security/security-checklist.md` |
| Completion Report Template | Framework | `.aidd/templates/documents/completion-report-template.md` |
| **Result** | TP | `ai-docs/docs/_validation/{date}_{FID}_{slug}-completion.md` |

---

## Pipeline Summary Table

| # | Stage | Command | Agent | Gates | Output Artifact |
|---|-------|---------|-------|-------|-----------------|
| 0 | Bootstrap | `/aidd-init` | — | `BOOTSTRAP_READY` | TP Structure |
| 1 | Idea | `/aidd-analyze` | Analyst | `PRD_READY` | PRD document |
| 2 | Research | `/aidd-research` | Researcher | `RESEARCH_DONE` | Research Report (`ai-docs/docs/research/{name}-research.md`) |
| 3 | Architecture | `/aidd-plan` | Planner | `PLAN_APPROVED` | Architecture plan |
| 3 | Architecture | `/aidd-plan-feature` | Planner | `PLAN_APPROVED` | Feature plan |
| 4 | Implementation | `/aidd-code` | Coder | `IMPLEMENT_OK` | Service code |
| 5 | Quality & Deploy | `/aidd-validate` | Validator | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` | **Completion Report** (`ai-docs/docs/_validation/{date}_{FID}_{slug}-completion.md`) |

---

## File Source Matrix

| Category | Source | Example Paths |
|----------|--------|---------------|
| **Command instructions** | Framework | `.aidd/.claude/commands/*.md` |
| **Agent instructions** | Framework | `.aidd/.claude/agents/*.md` |
| **Detailed roles** | Framework | `.aidd/roles/*/*.md` |
| **Document templates** | Framework | `.aidd/templates/documents/*.md` |
| **Service templates** | Framework | `.aidd/templates/services/*/` |
| **Infrastructure templates** | Framework | `.aidd/templates/infrastructure/*/` |
| **Knowledge Base** | Framework | `.aidd/knowledge/*/*.md` |
| **Conventions** | Framework | `.aidd/conventions.md` |
| **Workflow** | Framework | `.aidd/workflow.md` |
| **PRD** | TP | `ai-docs/docs/_analysis/*.md` |
| **Plans** | TP | `ai-docs/docs/_plans/mvp/*.md`, `ai-docs/docs/_plans/features/*.md` |
| **Research reports** | TP | `ai-docs/docs/research/*.md` |
| **Reports** | TP | `ai-docs/docs/_validation/*.md` |
| **RTM** | TP | `ai-docs/docs/rtm.md` |
| **Service code** | TP | `services/*/` |
| **Infrastructure** | TP | `docker-compose.yml`, `Makefile`, `nginx/` |
| **State** | TP | `.pipeline-state.json` |

---

## See Also

- [workflow.md](../workflow.md) — Detailed process description
- [initialization.md](initialization.md) — Initialization algorithm
- [INDEX.md](INDEX.md) — Framework file index
- [NAVIGATION.md](NAVIGATION.md) — Navigation matrix

---

**Version**: 1.0
**Created**: 2025-12-21
**Purpose**: Complete map of AIDD-MVP Generator pipelines
