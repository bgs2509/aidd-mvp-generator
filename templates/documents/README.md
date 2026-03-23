# AIDD-MVP Document Templates

Templates for generating documentation at each stage of the development pipeline.

## Contents

| Template | Purpose | Stage | Agent |
|----------|---------|-------|-------|
| `prd-template.md` | Product Requirements Document | Stage 1 | Analyst |
| `research-report-template.md` | Research Report | Stage 2 | Researcher |
| `architecture-template.md` | Architecture plan (CREATE mode) | Stage 3 | Planner |
| `feature-plan-template.md` | Feature plan (FEATURE mode) | Stage 3 | Planner |
| `implementation-plan-template.md` | Implementation plan | Stage 3 | Planner |
| `completion-report-template.md` | Completion Report (Review + Test + Validation) | Stage 5 | Validator |

> **Note**: Consolidation Stage 5 — the Reviewer, QA, and legacy Validator roles are merged into a single **Validator** role that performs 4 steps: Review → Test → Validate → Deploy. Three separate reports (`review-report`, `qa-report`, `validation-report`) are replaced by a single **Completion Report**.

## Usage

### 1. PRD Template

Used by the Analyst to formulate requirements:

```bash
/aidd-analyze "Project or feature description"
# or (migration mode v2.4+)
/aidd-analyze "Project or feature description"
```

**Output file** (Target Project):
- **naming v2** (default): `ai-docs/docs/_analysis/{date}_{FID}_{slug}-prd.md`
- **naming v3**: `ai-docs/docs/_analysis/{date}_{FID}_{slug}.md`

### 2. Research Report Template

Used by the Researcher after analyzing requirements/code:

```bash
/aidd-research
```

**Output file** (Target Project):
- **naming v2**: `ai-docs/docs/research/{date}_{FID}_{slug}-research.md`
- **naming v3**: `ai-docs/docs/_research/{date}_{FID}_{slug}.md`

### 3. Architecture Template

Used by the Planner for design (CREATE mode):

```bash
/aidd-plan
```

**Output file** (Target Project):
- **naming v2**: `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}-plan.md`
- **naming v3**: `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}.md`

### 4. Feature Plan Template

Used by the Planner for feature planning (FEATURE mode):

```bash
/aidd-plan-feature
# or (migration mode v2.4+)
/aidd-plan-feature
```

**Output file** (Target Project):
- **naming v2**: `ai-docs/docs/_plans/features/{date}_{FID}_{slug}-plan.md`
- **naming v3**: `ai-docs/docs/_plans/features/{date}_{FID}_{slug}.md`

### 5. Implementation Plan Template

Used by the Planner for detailed implementation planning:

```bash
/aidd-plan
# or
/aidd-plan-feature  # for FEATURE mode
```

**Output file** (Target Project):
- **naming v2**: `ai-docs/docs/_plans/features/{date}_{FID}_{slug}-implementation.md`
- **naming v3**: `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}-implementation.md` or `_plans/features/{date}_{FID}_{slug}-implementation.md`

### 6. Completion Report Template

Used by the Validator for comprehensive Quality & Deploy (Stage 5):

```bash
/aidd-validate
# or (migration mode v2.4+)
/aidd-validate
```

**Modes**:
- **Full** (default): Review → Test → Validate → Deploy → Production-ready MVP
- **Quick**: Draft Completion Report + Static Analysis (for documentation/incomplete features)

**Output file** (Target Project):
- **naming v2**: `ai-docs/docs/_validation/{date}_{FID}_{slug}-completion.md`
- **naming v3**: `ai-docs/docs/_validation/{date}_{FID}_{slug}.md`

**Completion Report contents**:
1. Executive Summary — what was done (2-3 sentences)
2. Code Review Summary — quality review results
3. Testing Summary — testing results
4. Requirements Traceability — requirements compliance
5. ADR — architectural decisions
6. Scope Changes — deviations from plan
7. Known Limitations — limitations and workarounds
8. Metrics — coverage, tests, security
9. Links — to all artifacts

## ai-docs Directory Structure (in Target Project)

### naming v2 (default)

```
{target-project}/
└── ai-docs/
    └── docs/
        ├── prd/
        │   ├── {date}_{FID}_{slug}-prd.md
        │   └── ...
        ├── architecture/
        │   └── {date}_{FID}_{slug}-plan.md
        ├── research/
        │   └── {date}_{FID}_{slug}-research.md
        ├── plans/
        │   ├── {date}_{FID}_{slug}-implementation.md
        │   └── {date}_{FID}_{slug}-plan.md  # FEATURE mode
        └── reports/
            └── {date}_{FID}_{slug}-completion.md
```

### naming v3 (after migration)

```
{target-project}/
└── ai-docs/
    └── docs/
        ├── _analysis/
        │   ├── {date}_{FID}_{slug}.md  # PRD (no -prd duplication)
        │   └── ...
        ├── _research/
        │   └── {date}_{FID}_{slug}.md  # Research Report
        ├── _plans/
        │   ├── mvp/
        │   │   ├── {date}_{FID}_{slug}.md  # Architecture (CREATE mode)
        │   │   └── {date}_{FID}_{slug}-implementation.md
        │   └── features/
        │       ├── {date}_{FID}_{slug}.md  # Feature Plan
        │       └── {date}_{FID}_{slug}-implementation.md
        └── _validation/
            └── {date}_{FID}_{slug}.md  # Completion Report (no -completion duplication)
```

> **Migration Mode v2.4+**: The framework supports both structures. The choice is determined by the `naming_version` field in `.pipeline-state.json`.

## Placeholders

Templates contain placeholders for auto-replacement:

| Placeholder | Description |
|-------------|-------------|
| `{Project/Feature Name}` | Name from PRD |
| `{YYYY-MM-DD}` | Current date |
| `{FID}` | Feature ID (e.g., F042) |
| `{slug}` | URL-friendly slug (e.g., oauth-integration) |
| `{context}` | Project context (snake_case) |
| `{entities}` | Entity name (plural) |
| `{entity}` | Entity name (singular) |
| `{domain}` | Domain area |
| `{N}` | Numeric values |
| `{XX}%` | Percentage values |

## Quality Gates

Each template contains a "Quality Gates" section with a checklist of criteria for passing the stage:

| Stage | Gate | Description |
|-------|------|-------------|
| 0 | `BOOTSTRAP_READY` | Target Project initialized |
| 1 | `PRD_READY` | PRD is complete and agreed upon |
| 2 | `RESEARCH_DONE` | Research completed |
| 3 | `PLAN_APPROVED` | Plan approved (requires user confirmation!) |
| 4 | `IMPLEMENT_OK` | Implementation completed |
| 5 (Full) | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` | Production-ready MVP |
| 5 (Quick) | `DOCUMENTED` | Draft Completion Report (bypasses sub-gates) |

> **Note**: Stage 5 supports two modes — **Full** (complete Quality & Deploy cycle) and **Quick** (documentation only).

## Customization

Templates can be customized for project specifics:

1. Copy the template to the Target Project: `ai-docs/templates/`
2. Modify sections to match your requirements
3. Update agent instruction references (optional)

## Best Practices

1. **Always fill in requirement IDs** — FR-XXX, NF-XXX, UI-XXX
2. **Link artifacts** — provide links to related documents (PRD → Research → Plan → Completion)
3. **Update the Completion Report** — record all scope changes, ADRs, limitations
4. **Preserve history** — do not delete old versions of artifacts
5. **Document decisions** — use the ADR section to record reasoning

## Migration to naming v3

To migrate a project from naming v2 to v3:

```bash
cd your-project/
python3 .aidd/scripts/migrate-naming-v3.py
```

The script automatically:
- Renames artifact folders
- Removes name duplication (`-prd.md` → `.md`, `-completion.md` → `.md`)
- Updates `.pipeline-state.json` (sets `naming_version: "v3"`)
- Updates links in documents

## Related Documents

- **Main entry point**: [../../CLAUDE.md](../../CLAUDE.md)
- **Pipeline process**: [../../workflow.md](../../workflow.md)
- **Conventions**: [../../conventions.md](../../conventions.md)
- **Migration Mode v2.4**: [../../contributors/2026-01-19-phase2-completion-summary.md](../../contributors/2026-01-19-phase2-completion-summary.md)
- **Consolidation Stage 5**: [../../contributors/2026-01-19-aidd-finalize-implementation.md](../../contributors/2026-01-19-aidd-finalize-implementation.md)

---

**Document version**: 2.0
**Updated**: 2026-01-20
**Changes**: Synchronized with Migration Mode v2.4 and Consolidation Stage 5
