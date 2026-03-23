# placeholder: AIDD-MVP Generator Problem Solutions

**Created**: 2025-12-19
**Author**: AI Agent (Analyzer)
**Status**: To be done
**Source**: Comprehensive project analysis

---

## Summary

| # | Problem | Severity | Status |
|---|---------|----------|--------|
| 1 | Inconsistent artifact paths | CRITICAL | [ ] |
| 2 | Missing metrics.md | CRITICAL | [ ] |
| 3 | Incorrect PRD template links | CRITICAL | [ ] |
| 4 | No working project example | Important | [ ] |
| 5 | Quality Gates not automated | Important | [ ] |
| 6 | No project initialization script | Important | [ ] |
| 7 | RTM path ambiguous | Minor | [ ] |
| 8 | No template versioning | Minor | [ ] |
| 9 | Agent/role information duplication | Minor | [ ] |

---

# CRITICAL PROBLEMS

---

## Problem #1: Inconsistent Artifact Paths

### Problem Description

Different documentation files specify different paths for storing artifacts.
This creates confusion for AI agents and can lead to document loss.

**Conflicting paths:**

| File | Specified Path |
|------|----------------|
| `templates/documents/README.md` | `ai-docs/prd/{name}-prd.md` |
| `templates/documents/README.md` | `ai-docs/architecture/{name}.md` |
| `templates/documents/README.md` | `ai-docs/plans/{name}.md` |
| `templates/documents/README.md` | `ai-docs/reports/` |
| `templates/documents/README.md` | `ai-docs/rtm.md` |
| `.claude/agents/analyst.md` | `docs/prd/{name}-prd.md` |
| `workflow.md` | `docs/prd/{name}-prd.md` |
| `roles/analyst/prd-formation.md` | `docs/prd/` |

**Affected files (16 total):**

```
templates/documents/README.md
templates/documents/validation-report-template.md
knowledge/architecture/project-structure.md
roles/validator/validation-report.md
roles/validator/artifact-verification.md
roles/validator/quality-gates.md
roles/qa/qa-report.md
roles/qa/test-scenarios.md
roles/reviewer/review-report.md
roles/reviewer/architecture-compliance.md
roles/implementer/infrastructure-setup.md
roles/architect/api-contracts.md
roles/architect/implementation-plan.md
roles/architect/architecture-design.md
```

**Impact:**
- AI agent doesn't know where to save files
- Documents may end up in different locations
- Requirements traceability is broken

### Problem #1 Solution

**Standard:** Use `docs/` as the unified root for all artifacts.

**Target structure:**

```
docs/
├── prd/                        # PRD documents
│   ├── {project}-prd.md
│   └── {feature}-feature-prd.md
├── architecture/               # Architecture documents
│   └── {project}-architecture.md
├── plans/                      # Implementation plans
│   ├── {project}-implementation-plan.md
│   └── {feature}-plan.md
├── reports/                    # Reports
│   ├── review-{name}.md
│   ├── qa-{name}.md
│   └── validation-{name}.md
├── templates/                  # Templates (already exists)
│   └── ...
└── rtm.md                      # Traceability matrix
```

**Tasks:**

- [ ] **1.1** Update `templates/documents/README.md`:
  - Replace all `ai-docs/` with `docs/`

- [ ] **1.2** Update files in `roles/`:
  - `roles/validator/validation-report.md`
  - `roles/validator/artifact-verification.md`
  - `roles/validator/quality-gates.md`
  - `roles/qa/qa-report.md`
  - `roles/qa/test-scenarios.md`
  - `roles/reviewer/review-report.md`
  - `roles/reviewer/architecture-compliance.md`
  - `roles/implementer/infrastructure-setup.md`
  - `roles/architect/api-contracts.md`
  - `roles/architect/implementation-plan.md`
  - `roles/architect/architecture-design.md`

- [ ] **1.3** Update `knowledge/architecture/project-structure.md`

- [ ] **1.4** Update `templates/documents/validation-report-template.md`

- [ ] **1.5** Create directories:
  ```bash
  mkdir -p docs/prd
  mkdir -p docs/architecture
  mkdir -p docs/plans
  mkdir -p docs/reports
  ```

**Replacement pattern:**

```
WAS:                            NOW:
ai-docs/prd/                    docs/prd/
ai-docs/architecture/           docs/architecture/
ai-docs/plans/                  docs/plans/
ai-docs/reports/                docs/reports/
ai-docs/rtm.md                  docs/rtm.md
```

---

## Problem #2: Missing metrics.md

### Problem Description

The implementation plan (`docs/history/2025-12-19-aidd-mvp-implementation-todo.md`)
references the file `roles/implementer/metrics.md` for metrics setup instructions.

**Planned in Phase 2:**

```
| 2.4.8 | [ ] | roles/implementer/metrics.md | Metrics (Level >= 3) |
```

**Actually exists (8 files instead of 9):**

```
roles/implementer/
├── infrastructure-setup.md   ✓
├── data-service.md           ✓
├── business-api.md           ✓
├── telegram-bot.md           ✓
├── background-worker.md      ✓
├── testing.md                ✓
├── logging.md                ✓
├── metrics.md                ✗ MISSING
└── nginx.md                  ✓
```

**Impact:**
- Implementer doesn't get Prometheus instructions
- Level 3+ projects have no metrics guide
- Documentation completeness broken

### Problem #2 Solution

**Task:** Create file `roles/implementer/metrics.md`

**File content:**

```markdown
# Function: Metrics Setup (Stage 4.8)

> **Purpose**: Prometheus metrics setup for monitoring.
> Applies to Level >= 3 projects.

---

## Goal

Add metrics collection for monitoring service performance and health.

---

## When to Apply

| Maturity Level | Metrics |
|----------------|---------|
| Level 1 (Prototype) | Not required |
| Level 2 (MVP) | Not required |
| Level 3 (Production) | **Required** |
| Level 4 (Scale) | **Required** |

---

## What Gets Created

### 1. Prometheus Metrics

File: `src/core/metrics.py`

- Request counters (request_count)
- Response time histograms (request_latency)
- Gauge for active connections
- Custom business metrics

### 2. /metrics Endpoint

File: `src/api/v1/metrics.py`

- Prometheus-compatible format
- Protected via internal network

### 3. Docker Configuration

File: `docker-compose.prod.yml`

- Prometheus service
- Grafana service
- Metrics network

---

## Standard Metrics

| Metric | Type | Description |
|--------|------|-------------|
| http_requests_total | Counter | Total request count |
| http_request_duration_seconds | Histogram | Processing time |
| http_requests_in_progress | Gauge | Active requests |
| db_connections_active | Gauge | DB connections |

---

## Code Template

### metrics.py

from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

---

## Sources

| Document | Description |
|----------|-------------|
| knowledge/quality/metrics/prometheus-setup.md | Prometheus setup |
| knowledge/quality/metrics/custom-metrics.md | Custom metrics |
| .ai-framework/docs/atomic/observability/ | Original documentation |
```

**Tasks:**

- [ ] **2.1** Create file `roles/implementer/metrics.md` with the content above
- [ ] **2.2** Add link in `.claude/agents/coder.md`
- [ ] **2.3** Create `knowledge/quality/metrics/prometheus-setup.md`
- [ ] **2.4** Create `knowledge/quality/metrics/custom-metrics.md`

---

## Problem #3: Incorrect PRD Template Links

### Problem Description

Several files reference a non-existent path `docs/prd/template.md`:

**Files with broken links:**

| File | Link |
|------|------|
| `.claude/agents/analyst.md` | `docs/prd/template.md` |
| `roles/analyst/prd-formation.md` | `docs/prd/template.md` |

**Actual template location:**

```
templates/documents/prd-template.md  ← Template is here
```

**Impact:**
- Analyst AI agent won't find the template
- PRD will be generated without structure
- Documentation quality decreases

### Problem #3 Solution

**Option A (recommended):** Update links in files

**Tasks:**

- [ ] **3.1** Update `.claude/agents/analyst.md`:
  ```
  WAS:  docs/prd/template.md
  NOW:  templates/documents/prd-template.md
  ```

- [ ] **3.2** Update `roles/analyst/prd-formation.md`:
  ```
  WAS:  docs/prd/template.md
  NOW:  templates/documents/prd-template.md
  ```

- [ ] **3.3** Check other files for broken links:
  ```bash
  grep -r "docs/prd/template" --include="*.md"
  ```

**Option B (alternative):** Create a symbolic link

```bash
mkdir -p docs/prd
ln -s ../templates/prd-template.md docs/prd/template.md
```

---

# IMPORTANT PROBLEMS

---

## Problem #4: No Working Project Example

### Problem Description

The framework contains 523 documentation and template files but no single
working example demonstrating the result.

**Current state:**

```
aidd-mvp-generator/
├── .claude/           # Agents and commands ✓
├── roles/             # Role instructions ✓
├── knowledge/         # Knowledge Base ✓
├── templates/         # Service templates ✓
├── docs/              # Documentation ✓
└── examples/          # ✗ DOES NOT EXIST
```

**Impact:**
- User doesn't see the end result
- Impossible to test the framework
- Hard to understand the actual work flow
- High entry barrier for new users

### Problem #4 Solution

**Task:** Create a complete "Restaurant Booking" example project

**Tasks:**

- [ ] **4.1** Create directory `examples/booking-restaurant/`
- [ ] **4.2** Write `README.md` with example description
- [ ] **4.3** Create a filled PRD document
- [ ] **4.4** Create an architecture document
- [ ] **4.5** Create an implementation plan
- [ ] **4.6** Implement `booking_data` service (Data API)
- [ ] **4.7** Implement `booking_api` service (Business API)
- [ ] **4.8** Configure docker-compose
- [ ] **4.9** Add tests with coverage >= 75%
- [ ] **4.10** Verify example functionality

---

## Problem #5: Quality Gates Not Automated

### Problem Description

In `settings.json` hooks are described for checking Quality Gates:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "check_gate PRD_READY"
      }
    ]
  }
}
```

However, the check scripts don't exist. Gates are only checked documentarily
via checklists in markdown files.

**Impact:**
- Can accidentally skip a stage
- Transitions between stages not controlled
- Quality Gates exist only on paper

### Problem #5 Solution

**Task:** Create an automatic gate checking system

**Tasks:**

- [ ] **5.1** Create directory `scripts/gates/`
- [ ] **5.2** Implement `base.py` — base Gate class
- [ ] **5.3** Implement `prd_ready.py` — PRD_READY
- [ ] **5.4** Implement `research_done.py` — RESEARCH_DONE
- [ ] **5.5** Implement `plan_approved.py` — PLAN_APPROVED
- [ ] **5.6** Implement `implement_ok.py` — IMPLEMENT_OK
- [ ] **5.7** Implement `review_ok.py` — REVIEW_OK
- [ ] **5.8** Implement `qa_passed.py` — QA_PASSED
- [ ] **5.9** Implement `all_gates_passed.py` — ALL_GATES_PASSED
- [ ] **5.10** Create `check_gate.py` CLI
- [ ] **5.11** Add tests for scripts
- [ ] **5.12** Update `settings.json` with real commands

---

## Problem #6: No Project Initialization Script

### Problem Description

User must manually create the directory structure before starting work.
This creates an entry barrier and error probability.

**Impact:**
- High entry barrier
- Probability of structure errors
- Time wasted on routine

### Problem #6 Solution

**Task:** Create a project initialization script

**Tasks:**

- [ ] **6.1** Create `scripts/init_project.py`
- [ ] **6.2** Add templates for copying (CLAUDE.md, .gitignore)
- [ ] **6.3** Add FEATURE mode support
- [ ] **6.4** Add tests
- [ ] **6.5** Update documentation (README.md)

---

# MINOR PROBLEMS

---

## Problem #7: RTM Path Ambiguous

### Problem Description

Requirements Traceability Matrix (RTM) is referenced with different paths.

**Impact:** Confusion about RTM storage location.

### Problem #7 Solution

**Standard:** `docs/rtm.md`

**Tasks:**

- [ ] **7.1** Update `templates/documents/README.md`
- [ ] **7.2** Check all RTM links

---

## Problem #8: No Template Versioning

### Problem Description

Templates in `templates/documents/` and `templates/services/` have no versions.

**Impact:**
- Hard to understand which version was used
- No changelog for templates

### Problem #8 Solution

**Tasks:**

- [ ] **8.1** Add version to each template
- [ ] **8.2** Create `templates/documents/CHANGELOG.md`
- [ ] **8.3** Add version to service templates

---

## Problem #9: Agent/Role Information Duplication

### Problem Description

Agent files (`.claude/agents/*.md`) contain information that is
duplicated in role files (`roles/**/*.md`).

**Impact:**
- When changing, both places need updating
- Risk of desynchronization

### Problem #9 Solution

**Approach:** Agents — entry point, roles — details.

**Tasks:**

- [ ] **9.1** Refactor agents
- [ ] **9.2** Apply template to all agents
- [ ] **9.3** Apply template to all agents

---

# EXECUTION ORDER

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXECUTION PRIORITY                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CRITICAL (first):                                                       │
│  ├── Problem #1: Path unification (~2 hours)                            │
│  ├── Problem #3: PRD template links (~30 min)                           │
│  └── Problem #2: Create metrics.md (~1 hour)                            │
│                                                                          │
│  IMPORTANT (after critical):                                             │
│  ├── Problem #6: Initialization script (~2 hours)                       │
│  ├── Problem #5: Gates automation (~4 hours)                            │
│  └── Problem #4: Example project (~6 hours)                             │
│                                                                          │
│  MINOR (when possible):                                                  │
│  ├── Problem #7: RTM path (~30 min)                                     │
│  ├── Problem #8: Versioning (~1 hour)                                   │
│  └── Problem #9: Deduplication (~2 hours)                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

Total time: ~19 hours
```

---

# EXECUTION CHECKLIST

## Critical

- [ ] **#1** Path unification (16 files)
- [ ] **#2** Create metrics.md
- [ ] **#3** Fix PRD links

## Important

- [ ] **#4** Create example project
- [ ] **#5** Quality Gates automation
- [ ] **#6** Initialization script

## Minor

- [ ] **#7** RTM path
- [ ] **#8** Versioning
- [ ] **#9** Deduplication

---

**Created**: 2025-12-19
**Author**: AI Agent
