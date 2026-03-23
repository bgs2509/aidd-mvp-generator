# AIDD-MVP Generator Navigation Matrix

**Note:** This document may contain outdated commands `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Current commands: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Purpose**: Explicit table "role → which documents to read → which to create"
> for each pipeline stage.

---

## Initialization Principle

> **First WHERE we are, then HOW to act.**
>
> **Detailed algorithm**: [initialization.md](initialization.md)

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: Target Project (TP) context                           │
│  ./CLAUDE.md → ./.pipeline-state.json → ./ai-docs/docs/        │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2: Precondition check                                    │
│  .pipeline-state.json → gates.{GATE}.passed == true             │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3: Framework instructions                                │
│  .aidd/CLAUDE.md → workflow.md → commands → agents              │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 4: Templates (only if artifact does NOT exist)           │
│  .aidd/templates/documents/*.md                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Matrix Structure

For each stage the following is specified:
- **Read (in TP)** — Target Project files
- **Read (in framework)** — files from `.aidd/`
- **Create (in TP)** — artifacts in `{project-name}/`

---

## Stage 0: Bootstrap (Initialization)

**Command**: `/aidd-init` (manual) or auto with `/aidd-analyze`
**Agent**: — (system)
**Gates**: `BOOTSTRAP_READY`

| Phase | # | Check/Read | Condition |
|-------|---|------------|-----------|
| **Checks** | 1 | `git rev-parse --git-dir` | Must be a git repo |
| **Checks** | 2 | `.aidd/CLAUDE.md` | Framework is connected |
| **Checks** | 3 | `python3 --version` | >= 3.11 |
| **Checks** | 4 | `docker --version` | Docker installed |
| **Framework** | 5 | `.aidd/.claude/commands/aidd-init.md` | Always |
| **Framework** | 6 | `.aidd/docs/target-project-structure.md` | For creating structure |

**Create (in TP)**:
- `ai-docs/docs/{prd,architecture,plans,reports,research}/`
- `.claude/` (local Claude Code settings)
- `.pipeline-state.json`
- `CLAUDE.md`

**BOOTSTRAP_READY gates checklist**:
- [ ] Git repository initialized
- [ ] Framework `.aidd/` connected
- [ ] Python version >= 3.11
- [ ] Docker installed
- [ ] `ai-docs/docs/` structure created
- [ ] `.claude/` folder created
- [ ] `.pipeline-state.json` created

---

## Stage 1: Idea → PRD

**Command**: `/aidd-analyze`
**Agent**: Analyst
**Gates**: `PRD_READY`

| Phase | # | Read | Condition |
|-------|---|------|-----------|
| **1. TP** | 1 | `./CLAUDE.md` | If exists |
| **1. TP** | 2 | `./.pipeline-state.json` | If exists |
| **1. TP** | 3 | `./ai-docs/docs/_analysis/` | For FEATURE mode |
| **2. Gates** | — | No preconditions | First stage |
| **3. Framework** | 4 | `.aidd/CLAUDE.md` | Always |
| **3. Framework** | 5 | `.aidd/workflow.md` | Always |
| **3. Framework** | 6 | `.aidd/.claude/commands/aidd-analyze.md` | Always |
| **3. Framework** | 7 | `.aidd/.claude/agents/analyst.md` | Always |
| **4. Templates** | 8 | `.aidd/templates/documents/prd-template.md` | If PRD does not exist |

**Create (in TP)**:
- `ai-docs/docs/_analysis/{name}-prd.md`
- `.pipeline-state.json`

**PRD_READY gates checklist**:
- [ ] All PRD sections filled
- [ ] Requirements have IDs (FR-*, NF-*, UI-*, INT-*)
- [ ] Must/Should/Could priorities specified
- [ ] No blocking questions
- [ ] `.pipeline-state.json` updated

---

## Stage 2: Research

**Command**: `/aidd-research`
**Agent**: Researcher
**Gates**: `RESEARCH_DONE`

| Phase | # | Read | Condition |
|-------|---|------|-----------|
| **1. TP** | 1 | `./CLAUDE.md` | If exists |
| **1. TP** | 2 | `./.pipeline-state.json` | Required |
| **1. TP** | 3 | `./ai-docs/docs/_analysis/*.md` | Required |
| **1. TP** | 4 | `./services/` | For FEATURE mode |
| **2. Gates** | — | `gates.PRD_READY.passed == true` | Required |
| **3. Framework** | 5 | `.aidd/CLAUDE.md` | Always |
| **3. Framework** | 6 | `.aidd/workflow.md` | Always |
| **3. Framework** | 7 | `.aidd/.claude/commands/aidd-research.md` | Always |
| **3. Framework** | 8 | `.aidd/.claude/agents/researcher.md` | Always |
| **4. Knowledge Base** | 9 | `.aidd/knowledge/architecture/*.md` | As needed |

**Create (in TP)**:
- `ai-docs/docs/research/{name}-research.md`
- Updated `.pipeline-state.json`

**RESEARCH_DONE gates checklist**:
- [ ] Existing code analyzed (for FEATURE)
- [ ] Architectural patterns and constraints described in report
- [ ] Integration recommendations documented
- [ ] Report saved to `ai-docs/docs/research/{name}-research.md`
- [ ] `.pipeline-state.json` updated

---

## Stage 3: Architecture

**Command**: `/aidd-plan` (CREATE) or `/aidd-plan-feature` (FEATURE)
**Agent**: Planner
**Gates**: `PLAN_APPROVED`

### CREATE Mode (`/aidd-plan`)

| Phase | # | Read | Condition |
|-------|---|------|-----------|
| **1. TP** | 1 | `./CLAUDE.md` | If exists |
| **1. TP** | 2 | `./.pipeline-state.json` | Required |
| **1. TP** | 3 | `./ai-docs/docs/_analysis/*.md` | Required |
| **1. TP** | 4 | `./ai-docs/docs/research/*.md` | Required |
| **2. Gates** | — | `gates.PRD_READY + RESEARCH_DONE` | Required |
| **3. Framework** | 5 | `.aidd/.claude/commands/aidd-plan.md` | Always |
| **3. Framework** | 6 | `.aidd/.claude/agents/planner.md` | Always |
| **4. Templates** | 7 | `.aidd/templates/documents/architecture-template.md` | Always |
| **4. Knowledge Base** | 8 | `.aidd/knowledge/architecture/*.md` | Always |

### FEATURE Mode (`/aidd-plan-feature`)

| Phase | # | Read | Condition |
|-------|---|------|-----------|
| **1. TP** | 1 | `./CLAUDE.md` | If exists |
| **1. TP** | 2 | `./.pipeline-state.json` | Required |
| **1. TP** | 3 | `./ai-docs/docs/_analysis/*.md` | Required |
| **1. TP** | 4 | `./ai-docs/docs/research/*.md` | Required |
| **1. TP** | 5 | `./ai-docs/docs/_plans/mvp/*.md` | Required |
| **1. TP** | 6 | `./services/` | Required |
| **2. Gates** | — | `mode == FEATURE + gates` | Required |
| **3. Framework** | 7 | `.aidd/.claude/commands/aidd-plan-feature.md` | Always |
| **3. Framework** | 8 | `.aidd/.claude/agents/planner.md` | Always |

**Create (in TP)**:
- CREATE: `ai-docs/docs/_plans/mvp/{name}-plan.md`
- FEATURE: `ai-docs/docs/_plans/features/{feature}-plan.md`

**PLAN_APPROVED gates checklist**:
- [ ] System components described
- [ ] API contracts defined
- [ ] NFR accounted for
- [ ] **Plan approved by user**
- [ ] `.pipeline-state.json` updated

---

## Stage 4: Implementation

**Command**: `/aidd-code`
**Agent**: Coder
**Gates**: `IMPLEMENT_OK`

| Phase | # | Read | Condition |
|-------|---|------|-----------|
| **1. TP** | 1 | `./CLAUDE.md` | If exists |
| **1. TP** | 2 | `./.pipeline-state.json` | Required |
| **1. TP** | 3 | `./ai-docs/docs/_analysis/*.md` | Required |
| **1. TP** | 4 | `./ai-docs/docs/_plans/mvp/*.md` | For CREATE |
| **1. TP** | 5 | `./ai-docs/docs/_plans/features/*.md` | For FEATURE |
| **1. TP** | 6 | `./services/` | For FEATURE |
| **2. Gates** | — | `gates.PLAN_APPROVED.passed + approved_by` | Required |
| **3. Framework** | 7 | `.aidd/conventions.md` | Always |
| **3. Framework** | 8 | `.aidd/.claude/commands/aidd-code.md` | Always |
| **3. Framework** | 9 | `.aidd/.claude/agents/coder.md` | Always |
| **4. Templates** | 10 | `.aidd/templates/services/*.md` | Always |
| **4. Templates** | 11 | `.aidd/templates/infrastructure/*.md` | Always |

**Create (in TP)**:
- `docker-compose.yml`, `Makefile`
- `services/{name}_data/`, `services/{name}_api/`
- `services/{name}_bot/`, `services/{name}_worker/` (optional)
- `services/*/tests/`

**IMPLEMENT_OK gates checklist**:
- [ ] Code written according to plan
- [ ] Unit tests pass
- [ ] DDD/Hexagonal structure followed
- [ ] Type hints everywhere
- [ ] `.pipeline-state.json` updated

---

## Stage 5: Quality & Deploy

**Command**: `/aidd-validate` (or `/aidd-validate` in v2.4+)
**Role**: Validator (`.claude/agents/validator.md`)
**Precondition**: `IMPLEMENT_OK` ✓
**Artifact**: `ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}-completion.md`

### Description

The Quality & Deploy stage performs a full quality check and deploy cycle in 4 sequential steps:

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1: Code Review → REVIEW_OK                              │
│  Step 2: Testing → QA_PASSED                                  │
│  Step 3: Validation → ALL_GATES_PASSED                        │
│  Step 4: Deploy & Completion Report → DEPLOYED                │
└──────────────────────────────────────────────────────────────┘
```

### Reading Table

| Phase | # | Read | Condition |
|-------|---|------|-----------|
| **1. TP** | 1 | `./CLAUDE.md` | If exists |
| **1. TP** | 2 | `./.pipeline-state.json` | Required |
| **1. TP** | 3 | `./ai-docs/docs/_analysis/*.md` | Required |
| **1. TP** | 4 | `./ai-docs/docs/_plans/mvp/*.md` | Required |
| **1. TP** | 5 | `./services/` | Required |
| **1. TP** | 6 | `./docker-compose.yml`, `./Makefile` | For step 4 (Deploy) |
| **2. Gates** | — | Check `IMPLEMENT_OK` | Required (for Full mode) |
| **3. Framework** | 7 | `.aidd/CLAUDE.md` | Always |
| **3. Framework** | 8 | `.aidd/workflow.md` | Always |
| **3. Framework** | 9 | `.aidd/.claude/commands/aidd-validate.md` | Main instructions |
| **3. Framework** | 10 | `.aidd/.claude/agents/validator.md` | Validator role |
| **3. Framework** | 11 | `.aidd/.claude/agents/code-review-library.md` | Library for step 1 |
| **3. Framework** | 12 | `.aidd/.claude/agents/testing-library.md` | Library for step 2 |
| **3. Framework** | 13 | `.aidd/conventions.md` | Code conventions |
| **4. Templates** | 14 | `.aidd/templates/documents/completion-report-template.md` | For creating the final report |
| **4. Knowledge Base** | 15 | `.aidd/knowledge/quality/quality-cascade.md` | Quality Cascade (17 checks) |
| **4. Knowledge Base** | 16 | `.aidd/knowledge/security/security-checklist.md` | Security checklist |

### Two Operating Modes

| Mode | When to use | Gates |
|------|------------|-------|
| **Full** (recommended) | Production-ready MVP | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` |
| **Quick** | Documentation, stalled feature | `DOCUMENTED` (static analysis only) |

**Quick Mode**:
- Runs only mypy, ruff, bandit (no tests)
- Creates a DRAFT Completion Report marked "⚠️ DRAFT — QA not performed"
- Feature stays in `active_pipelines` (NOT moved to `features_registry`)
- Allows switching to another feature without completing the current one

### Created Artifact (single)

- `ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}-completion.md`

**Completion Report** contains:
- Executive Summary
- Code Review Summary (instead of a separate review-report.md)
- Testing Summary (instead of a separate qa-report.md)
- Requirements Traceability (instead of a separate rtm.md)
- ADR (Architecture Decision Records)
- Scope Changes (plan vs actual)
- Known Limitations
- Quality metrics

### Instruction Libraries

The Validator uses two supporting libraries:

| Library | File | Content |
|---------|------|---------|
| **Code Review** | `.claude/agents/code-review-library.md` | Quality Cascade (17 checks), Log-Driven Design, Security |
| **Testing** | `.claude/agents/testing-library.md` | Test scenarios, Coverage, Requirements verification |

### Gates Checklist

**REVIEW_OK** (after step 1):
- [ ] Architecture matches the plan (DDD, HTTP-only)
- [ ] Security checklist passed (no vulnerabilities)
- [ ] Code style followed (conventions.md)
- [ ] Log-Driven Design verified
- [ ] Quality Cascade (QC-1 to QC-17) passed

**QA_PASSED** (after step 2):
- [ ] All tests pass (0 failed)
- [ ] Coverage ≥ 75%
- [ ] Integration tests passed
- [ ] All FR-* requirements verified

**ALL_GATES_PASSED** (after step 3):
- [ ] PRD_READY ✓
- [ ] RESEARCH_DONE ✓
- [ ] PLAN_APPROVED ✓
- [ ] IMPLEMENT_OK ✓
- [ ] REVIEW_OK ✓ (from step 1)
- [ ] QA_PASSED ✓ (from step 2)
- [ ] Security BLOCKER issues = 0
- [ ] Security CRITICAL issues = 0
- [ ] All artifacts exist and are up to date

**DEPLOYED** (after step 4):
- [ ] Docker containers built and running
- [ ] Health-check passes
- [ ] Basic scenarios work (API requests succeed)
- [ ] Logs verified (no errors)
- [ ] **Completion Report created** ← REQUIRED!
- [ ] Feature moved to `features_registry`

---

## Summary Table

| # | Stage | Command | Agent | Reads | Creates | Gates |
|---|-------|---------|-------|-------|---------|-------|
| 0 | Bootstrap | `/aidd-init` | — | init.md, target-structure | TP Structure | BOOTSTRAP_READY |
| 1 | Idea | `/aidd-analyze` | Analyst | CLAUDE, workflow, analyst, prd-template | PRD, state | PRD_READY |
| 2 | Research | `/aidd-research` | Researcher | researcher, knowledge | (state) | RESEARCH_DONE |
| 3 | Architecture | `/aidd-plan` | Planner | planner, ddd, http-only | Plan | PLAN_APPROVED |
| 4 | Implementation | `/aidd-code` | Coder | coder, conventions, templates | Code, tests | IMPLEMENT_OK |
| 5 | Quality & Deploy | `/aidd-validate` | Validator | validator, code-review-library, testing-library, completion-report-template | Completion Report | REVIEW_OK → QA_PASSED → ALL_GATES_PASSED → DEPLOYED |

> **Note (v2.4+)**: Naming conventions unification:
>
> | Old | New | Status |
> |-----|-----|--------|
> | `/aidd-analyze` | `/aidd-analyze` | ✅ Both work |
> | `/aidd-plan-feature` | `/aidd-plan-feature` | ✅ Both work |
> | `/aidd-code` | `/aidd-code` | ✅ Both work |
> | `/aidd-validate` | `/aidd-validate` | ✅ Both work |
> | `planner.md` | `planner.md` | ✅ Both available |
> | `coder.md` | `coder.md` | ✅ Both available |
>
> **Important**: `/aidd-validate` (or `/aidd-validate`) combines stages 5-8 into a single Quality & Deploy cycle.

---

## See Also

- [initialization.md](initialization.md) — Initialization algorithm (4 phases)
- [INDEX.md](INDEX.md) — Full generator file index
- [PIPELINE-TREE.md](PIPELINE-TREE.md) — All pipelines tree
- [target-project-structure.md](target-project-structure.md) — Target Project structure
- [workflow.md](../workflow.md) — Detailed process description

---

**Version**: 2.0
**Updated**: 2025-12-21
