# workflow.md — AIDD-MVP Development Process

> **Purpose**: Description of the 6-stage MVP development process (stages 0-5).
> AI agent MUST follow this process and pass through quality gates.
>
> **Philosophy**: Artifacts = Memory. Do not rely on chat memory.

---

## Process Overview

AIDD-MVP Generator uses a 6-stage development pipeline (Stages 0-5)
with mandatory quality gates between stages. Transition to the next
stage is ONLY possible after passing the current stage's gates.

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

---

## Two Operating Modes

### CREATE — Creating a New MVP

Full 6-stage process (stages 0-5) for creating a project from scratch.

```bash
/aidd-analyze "Create a restaurant table booking service"
```

### FEATURE — Adding Functionality

Adapted process for adding a feature to an existing project.

```bash
/aidd-analyze "Add email notification system"
```

**FEATURE mode differences**:
- Stage 2 (Research) — analysis of existing code
- Stage 3 (Architecture) — `/aidd-plan-feature` instead of `/aidd-plan`
- Integration with existing components

---

## Bootstrap: Target Project Initialization

> **IMPORTANT**: Artifacts are created in the TARGET PROJECT, not in the generator!
> The framework must be connected as a Git Submodule in `.aidd/`
>
> **Full initialization algorithm**: [docs/initialization.md](docs/initialization.md)

### Initialization Principle

```
┌─────────────────────────────────────────────────────────────────────┐
│  First understand WHERE we are (TP context),                         │
│  then HOW to act (framework instructions)                           │
├─────────────────────────────────────────────────────────────────────┤
│  PHASE 1: ./CLAUDE.md → ./.pipeline-state.json → ./ai-docs/docs/    │
│  PHASE 2: Precondition check (gates)                                 │
│  PHASE 3: .aidd/CLAUDE.md → .aidd/workflow.md → command → role       │
│  PHASE 4: Templates (if artifact does not exist)                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Prerequisites

Before running `/aidd-analyze`, the framework must be connected:

```bash
# If the framework is not yet connected
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd
git submodule update --init --recursive
```

### Automatic Initialization with `/aidd-analyze`

On the first run of `/aidd-analyze`, the AI agent performs:

> **VERIFY BEFORE ACT**: Before creating, we verify directory existence.

```bash
# 1. VERIFY: Check existing artifact structure
if [ -d "ai-docs/docs" ]; then
    existing_count=$(ls -d ai-docs/docs/*/ 2>/dev/null | wc -l)
    echo "✓ ai-docs/docs/ structure already exists ($existing_count directories)"
fi

# 2. ACT: Create only missing directories
mkdir -p "ai-docs/docs/_analysis"
mkdir -p "ai-docs/docs/_research"
mkdir -p "ai-docs/docs/_plans/mvp"
mkdir -p "ai-docs/docs/_plans/features"
mkdir -p "ai-docs/docs/_validation"

# 2. Initialize pipeline state (v2 format)
cat > .pipeline-state.json << 'EOF'
{
  "version": "2.0",
  "project_name": "",
  "mode": "CREATE",
  "global_gates": {
    "BOOTSTRAP_READY": { "passed": true, "passed_at": null }
  },
  "active_pipelines": {},
  "features_registry": {},
  "next_feature_id": 1
}
EOF
```

### Mode Detection

| Indicator | Mode |
|-----------|------|
| `services/` or `docker-compose.yml` exists | **FEATURE** |
| Empty directory or no project indicators | **CREATE** |

#### Mode Detection Algorithm (P-006)

```python
def detect_mode() -> str:
    """
    Exact mode detection algorithm.

    Returns:
        'CREATE' or 'FEATURE'
    """
    # 1. Check .pipeline-state.json (priority)
    if Path(".pipeline-state.json").exists():
        state = read_json(".pipeline-state.json")
        return state.get("mode", "CREATE")

    # 2. Existing project indicators
    project_markers = [
        "services/",           # Generated services
        "docker-compose.yml",  # Infrastructure
        "docker-compose.yaml",
        "ai-docs/docs/",       # AIDD Artifacts
        "Makefile",            # Build
    ]

    for marker in project_markers:
        if Path(marker).exists():
            return "FEATURE"

    # 3. Additional check — presence of Python code
    python_files = list(Path(".").glob("**/*.py"))
    if len(python_files) > 5:  # More than 5 files — likely a project
        return "FEATURE"

    return "CREATE"
```

**Important**: The mode can be explicitly overridden:
```bash
/aidd-analyze --mode=FEATURE "Add a feature"
```

---

## Process Stages

### Stage 0: Bootstrap (Initialization)

| Parameter | Value |
|-----------|-------|
| **Command** | `/aidd-init` (manual) or auto with `/aidd-analyze` |
| **Agent** | — (system) |
| **Input** | Empty directory with git and .aidd/ |
| **Output** | TP structure, `.pipeline-state.json`, `CLAUDE.md` |
| **Gate** | `BOOTSTRAP_READY` |

**BOOTSTRAP_READY gate passing criteria**:
- [ ] Git repository initialized
- [ ] Framework `.aidd/` connected (submodule)
- [ ] Python version >= 3.11
- [ ] Docker installed
- [ ] `ai-docs/docs/` structure created
- [ ] `.pipeline-state.json` initialized

**Environment checks**:
```bash
# 1. Git repository
git rev-parse --git-dir

# 2. Framework connected
test -f .aidd/CLAUDE.md

# 3. Python version
python3 --version  # >= 3.11

# 4. Docker
docker --version
```

**Initialization actions**:

> **VERIFY BEFORE ACT**: Before creating, we verify existence.

```bash
# 1. VERIFY + ACT: Create only missing directories
mkdir -p "ai-docs/docs/_analysis"
mkdir -p "ai-docs/docs/_research"
mkdir -p "ai-docs/docs/_plans/mvp"
mkdir -p "ai-docs/docs/_plans/features"
mkdir -p "ai-docs/docs/_validation"

# 2. Initialize state (if not exists, v2 format)
[ -f ".pipeline-state.json" ] || echo '{"version":"2.0","project_name":"","mode":"CREATE","global_gates":{"BOOTSTRAP_READY":{"passed":true}},"active_pipelines":{},"next_feature_id":1}' > .pipeline-state.json

# 3. Create CLAUDE.md (if not exists)
[ -f "CLAUDE.md" ] || echo "# Project\n\nSee .aidd/CLAUDE.md" > CLAUDE.md
```

**Note**: Stage 0 is executed automatically on the first `/aidd-analyze` if checks
were not passed earlier. Explicit `/aidd-init` is recommended for diagnostics.

---

### Stage 1: Idea → PRD

| Parameter | Value |
|-----------|-------|
| **Command** | `/aidd-analyze "description"` |
| **Agent** | Analyst |
| **Input** | Idea description from user |
| **Output** | `ai-docs/docs/_analysis/{name}.md` |
| **Gate** | `PRD_READY` |

**PRD_READY gate passing criteria**:
- [ ] All PRD sections filled in
- [ ] Requirements have IDs (FR-*, NF-*, UI-*, INT-*)
- [ ] Acceptance criteria defined
- [ ] No blocking open questions

**Artifacts** (in the target project):
```
{project-name}/
└── ai-docs/docs/_analysis/
    └── booking-restaurant.md
```

---

### Stage 2: Research

| Parameter | Value |
|-----------|-------|
| **Command** | `/aidd-research` |
| **Agent** | Researcher |
| **Input** | PRD, existing code (for FEATURE) |
| **Output** | `ai-docs/docs/_research/{name}.md` |
| **Gate** | `RESEARCH_DONE` |

**RESEARCH_DONE gate passing criteria**:
- [ ] Existing code analyzed (for FEATURE)
- [ ] Architectural patterns identified and described in the report
- [ ] Technical constraints defined
- [ ] Integration recommendations formulated
- [ ] Research report saved to `ai-docs/docs/_research/{name}.md`

**CREATE mode**: Requirements analysis, technology selection, hypothesis capture.
**FEATURE mode**: Code analysis, extension point identification, findings capture.

**Artifacts** (in the target project):
```
{project-name}/
└── ai-docs/docs/_research/
    └── booking-restaurant.md
```

---

### Stage 3: Architecture

| Parameter | Value |
|-----------|-------|
| **Command** | `/aidd-plan` (CREATE) or `/aidd-plan-feature` (FEATURE) |
| **Agent** | Planner |
| **Input** | PRD, Research Report |
| **Output** | `ai-docs/docs/_plans/mvp/{name}.md` |
| **Gate** | `PLAN_APPROVED` |

**PLAN_APPROVED gate passing criteria**:
- [ ] System components described
- [ ] API contracts defined
- [ ] NFR (non-functional requirements) accounted for
- [ ] **Plan approved by user**

**Important**: This stage REQUIRES explicit user confirmation!

**Artifacts** (in the target project):
```
{project-name}/
└── ai-docs/docs/
    └── _plans/
        ├── mvp/
        │   └── booking-restaurant.md
        └── features/
            └── notification-feature.md  # for FEATURE
```

---

### Stage 4: Implementation

| Parameter | Value |
|-----------|-------|
| **Command** | `/aidd-code` |
| **Agent** | Coder |
| **Input** | Approved plan |
| **Output** | Service code, tests, infrastructure |
| **Gate** | `IMPLEMENT_OK` |

**IMPLEMENT_OK gate passing criteria**:
- [ ] Code written according to plan
- [ ] All unit tests pass
- [ ] Structure follows DDD/Hexagonal
- [ ] HTTP-only: business services do NOT access DB directly (only through Data API)
- [ ] Type hints and docstrings present

**Implementation sub-stages**:

| # | Sub-stage | Output |
|---|-----------|--------|
| 4.1 | Infrastructure | docker-compose, Makefile, CI/CD |
| 4.2 | Data Service | API for DB operations |
| 4.3 | Business API | REST API on FastAPI |
| 4.4 | Background Worker | Background tasks (if needed) |
| 4.5 | Telegram Bot | Bot (if needed) |
| 4.6 | Tests | Unit + Integration tests |

---

### Stage 5: Quality & Deploy

**Command**: `/aidd-validate`
**Role**: Validator (`.claude/agents/validator.md`)
**Precondition**: `IMPLEMENT_OK` ✓
**Artifact**: `ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}.md`

#### Description

The Quality & Deploy stage performs a complete quality check and deployment cycle in 4 sequential steps:

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1: Code Review                                          │
│  ├─ Architecture (DDD, HTTP-only)                             │
│  ├─ Quality Cascade (QC-1...QC-17)                           │
│  ├─ Log-Driven Design                                        │
│  └─ Security checklist                                       │
│  → Gate: REVIEW_OK ✓                                          │
├──────────────────────────────────────────────────────────────┤
│  Step 2: Testing                                              │
│  ├─ Run pytest with coverage                                  │
│  ├─ Verify coverage ≥75%                                      │
│  └─ Requirements FR-* verification                            │
│  → Gate: QA_PASSED ✓                                          │
├──────────────────────────────────────────────────────────────┤
│  Step 3: Validation                                           │
│  ├─ Check all gates (PRD_READY...QA_PASSED)                  │
│  ├─ Artifact verification                                     │
│  └─ Final security check                                      │
│  → Gate: ALL_GATES_PASSED ✓                                   │
├──────────────────────────────────────────────────────────────┤
│  Step 4: Deploy & Completion Report                           │
│  ├─ docker-compose build                                     │
│  ├─ docker-compose up                                        │
│  ├─ Health-check                                             │
│  ├─ Basic scenarios                                           │
│  ├─ CREATE COMPLETION REPORT (mandatory!)                     │
│  └─ Move to features_registry                                 │
│  → Gate: DEPLOYED ✓                                           │
└──────────────────────────────────────────────────────────────┘
```

#### Two Operating Modes

| Mode | When to use | Gates |
|------|-------------|-------|
| **Full** (recommended) | Production-ready MVP | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` |
| **Quick** | Documentation, stalled feature | `DOCUMENTED` (static analysis only) |

**Quick mode**:
- Runs only mypy, ruff, bandit (without tests)
- Creates DRAFT Completion Report with note "⚠️ DRAFT — QA not performed"
- Feature stays in `active_pipelines` (NOT moved to `features_registry`)
- Allows switching to another feature without completing the current one

#### Instruction Libraries

The Validator uses two auxiliary libraries:

| Library | File | Contents |
|---------|------|----------|
| **Code Review** | `.claude/agents/code-review-library.md` | Quality Cascade (17 checks), Log-Driven Design, Security |
| **Testing** | `.claude/agents/testing-library.md` | Test scenarios, Coverage, Requirements verification |

#### Completion Report

The sole artifact of the Quality & Deploy stage. Contains:

- Executive Summary
- Code Review Summary (results of 17 checks)
- Testing Summary (coverage, requirements)
- Requirements Traceability (FR-* compliance)
- ADR (architectural decisions)
- Scope Changes (plan vs actual)
- Known Limitations
- Quality metrics

**Path**: `ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}.md`

#### Commands

```bash
# Full mode (recommended)
/aidd-validate

# Quick mode (explicit)
/aidd-validate --mode=quick
```

#### Detailed Instructions

See `.claude/commands/aidd-validate.md` → sections for each step.

---

## Commands and Gates Table

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


## Artifacts by Stage (in the Target Project)

> **IMPORTANT**: All artifacts are created in the TARGET PROJECT, not in the generator!

```
{project-name}/                      ← Target Project
│
├── .pipeline-state.json             # Pipeline state
│
└── ai-docs/docs/
    ├── _analysis/
    │   └── {name}.md                # Stage 1: PRD document
    │
    ├── _research/
    │   └── {name}.md                # Stage 2: Research Report
    │
    ├── _plans/
    │   ├── mvp/
    │   │   └── {name}.md            # Stage 3: Architecture plan (CREATE)
    │   └── features/
    │       └── {name}.md            # Stage 3: Feature plan (FEATURE)
    │
    └── _validation/
        └── {date}_{FID}_{slug}.md   # Stage 5: Single Completion Report
```

---

## Full Pass-through Example (CREATE mode)

```bash
# 1. Describe the idea
/aidd-analyze "Create a restaurant table booking service.
Users can search for restaurants, view available tables,
book for a specific time. Restaurants receive notifications
about new bookings via Telegram."

# Agent: Analyst creates PRD
# Gate: PRD_READY ✓

# 2. Research
/aidd-research

# Agent: Researcher analyzes requirements
# Gate: RESEARCH_DONE ✓

# 3. Architecture
/aidd-plan

# Agent: Planner creates plan
# User approves the plan
# Gate: PLAN_APPROVED ✓

# 4. Implementation
/aidd-code

# Agent: Coder generates code
# Created: infrastructure, data-api, business-api, bot
# Gate: IMPLEMENT_OK ✓

# 5. Quality & Deploy
/aidd-validate

# Agent: Validator performs 4 steps
# ✓ Step 1/4: Code Review → REVIEW_OK
# ✓ Step 2/4: Testing (Coverage 82%) → QA_PASSED
# ✓ Step 3/4: Validation → ALL_GATES_PASSED
# ✓ Step 4/4: Deploy + Completion Report → DEPLOYED
# ✓ Completion Report: ai-docs/docs/_validation/2025-12-23_F001_table-booking.md

# Done! MVP launched in ~10 minutes
```

---

## Pipeline State (.pipeline-state.json)

> **Philosophy**: Artifacts = Memory. Pipeline state is the single source of truth.

### File Format (v2 — parallel pipelines)

The `.pipeline-state.json` file is created in the root of the TARGET PROJECT on the first `/aidd-analyze`.

```json
{
  "version": "2.0",
  "project_name": "booking-service",
  "mode": "FEATURE",

  "global_gates": {
    "BOOTSTRAP_READY": {"passed": true, "passed_at": "2025-12-25T10:00:00Z"}
  },

  "active_pipelines": {
    "F042": {
      "branch": "feature/F042-oauth-auth",
      "name": "oauth-auth",
      "title": "OAuth authorization",
      "stage": "IMPLEMENT",
      "created": "2025-12-25",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "..."},
        "RESEARCH_DONE": {"passed": true, "passed_at": "..."},
        "PLAN_APPROVED": {"passed": true, "passed_at": "...", "approved_by": "user"}
      },
      "artifacts": {
        "prd": "_analysis/2025-12-25_F042_oauth-auth.md",
        "research": "_research/2025-12-25_F042_oauth-auth.md",
        "plan": "_plans/features/2025-12-25_F042_oauth-auth.md"
      }
    }
  },

  "next_feature_id": 43,

  "features_registry": {
    "F001": {"status": "DEPLOYED", "deployed": "2025-12-20"}
  }
}
```

**Key v2 changes**:
- `active_pipelines` — dictionary of active features (instead of `current_feature`)
- `global_gates` — project-level gates (BOOTSTRAP_READY)
- Gates are isolated in `active_pipelines[FID].gates`
- `features_registry` — registry of completed features

**Template**: [templates/documents/pipeline-state-template.json](templates/documents/pipeline-state-template.json)
**v2 Specification**: [knowledge/pipeline/state-v2.md](knowledge/pipeline/state-v2.md)

### State Update

Each command MUST update `.pipeline-state.json`:
1. On start — check preconditions
2. On success — mark gates as passed
3. On artifact creation — record the path

---

## Artifact Discovery Algorithm

Commands use the following algorithm to find input artifacts:

```python
def find_artifact(artifact_type: str) -> Path | None:
    """
    Algorithm for finding an artifact in the target project.

    Args:
        artifact_type: 'prd', 'plan', 'feature_plan', 'review_report', etc.

    Returns:
        Path to artifact or None
    """
    # 1. Check .pipeline-state.json
    state = read_json(".pipeline-state.json")
    if state and state.get("artifacts", {}).get(artifact_type):
        return Path(state["artifacts"][artifact_type])

    # 2. Glob by standard patterns
    patterns = {
        "prd": "ai-docs/docs/_analysis/*.md",
        "research": "ai-docs/docs/_research/*.md",
        "plan": "ai-docs/docs/_plans/mvp/*.md",
        "feature_plan": "ai-docs/docs/_plans/features/*.md",
        "review_report": "ai-docs/docs/_validation/review-*.md",
        "qa_report": "ai-docs/docs/_validation/qa-*.md",
        "rtm": "ai-docs/docs/rtm.md"
    }

    files = glob(patterns.get(artifact_type, ""))
    if files:
        # Return the most recent
        return max(files, key=lambda f: f.stat().st_mtime)

    return None
```

### Search Patterns

| Artifact | Pattern |
|----------|---------|
| PRD | `ai-docs/docs/_analysis/*.md` |
| Research Report | `ai-docs/docs/_research/*.md` |
| Architecture Plan | `ai-docs/docs/_plans/mvp/*.md` |
| Feature Plan | `ai-docs/docs/_plans/features/*.md` |
| Review Report | `ai-docs/docs/_validation/review-*.md` |
| QA Report | `ai-docs/docs/_validation/qa-*.md` |
| RTM | `ai-docs/docs/rtm.md` |

---

## Precondition Check (Gate Check)

Each command MUST check preconditions before execution:

```python
def check_preconditions(command: str) -> bool:
    """Check preconditions before executing the command."""

    preconditions = {
        "/aidd-init": [],  # No preconditions — first stage
        "/aidd-analyze": ["BOOTSTRAP_READY"],  # Auto-bootstrap if not passed
        "/aidd-research": ["PRD_READY"],
        "/aidd-plan": ["PRD_READY", "RESEARCH_DONE"],
        "/aidd-plan-feature": ["PRD_READY", "RESEARCH_DONE"],
        "/aidd-code": ["PLAN_APPROVED"],
        "/aidd-validate": ["IMPLEMENT_OK"],  # Full mode - requires implementation
        # Quick mode (/aidd-validate --quick) - no preconditions
    }

    state = read_json(".pipeline-state.json")
    if not state:
        return command == "/aidd-analyze"

    for gate in preconditions.get(command, []):
        if not state.get("gates", {}).get(gate, {}).get("passed"):
            print(f"❌ Gate {gate} not passed")
            return False

    return True
```

### Precondition Matrix

| Command | Required Gates | If Not Passed |
|---------|---------------|---------------|
| `/aidd-init` | — | — |
| `/aidd-analyze` | BOOTSTRAP_READY | Auto-run bootstrap or "/aidd-init" |
| `/aidd-research` | PRD_READY | "First execute /aidd-analyze" |
| `/aidd-plan` | PRD_READY, RESEARCH_DONE | "First execute /aidd-research" |
| `/aidd-plan-feature` | PRD_READY, RESEARCH_DONE | "First execute /aidd-research" |
| `/aidd-code` | PLAN_APPROVED | "First approve the plan" |
| `/aidd-validate` (Full) | IMPLEMENT_OK | "First execute /aidd-code" |
| `/aidd-validate` (Quick) | — | Creates DRAFT report without preconditions |

---

## Gate Passing Rules

### Gate Check Algorithm (P-009)

Each gate is checked using a unified algorithm:

```python
def check_gate(gate: str) -> GateResult:
    """
    Gate check algorithm.

    Args:
        gate: Gate name

    Returns:
        GateResult: {passed: bool, reason: str, checklist: list}
    """
    checklist_map = {
        "BOOTSTRAP_READY": [
            ("git_repo", "git rev-parse --git-dir"),
            ("framework_exists", ".aidd/CLAUDE.md"),
            ("python_version", "python3 --version >= 3.11"),
            ("docker_installed", "docker --version"),
            ("structure_created", "ai-docs/docs/ exists"),
            ("state_initialized", ".pipeline-state.json exists"),
        ],
        "PRD_READY": [
            ("artifact_exists", "ai-docs/docs/_analysis/*.md"),
            ("sections_complete", ["Overview", "FR-*", "NF-*"]),
            ("ids_present", "All requirements have IDs"),
            ("no_blockers", "No Open questions without resolution"),
        ],
        "RESEARCH_DONE": [
            ("artifact_exists", "ai-docs/docs/_research/*.md"),
            ("analysis_complete", "Code analyzed"),
            ("patterns_identified", "Patterns identified"),
            ("constraints_defined", "Constraints defined"),
        ],
        "PLAN_APPROVED": [
            ("artifact_exists", "ai-docs/docs/_plans/mvp/*.md"),
            ("components_defined", "Components defined"),
            ("api_contracts", "API contracts described"),
            ("user_approved", "User confirmed"),  # Requires interaction
        ],
        "IMPLEMENT_OK": [
            ("code_exists", "services/*/"),
            ("tests_pass", "pytest exit code 0"),
            ("types_present", "Type hints in code"),
            ("structure_ok", "DDD structure followed"),
        ],
        "REVIEW_OK": [
            ("artifact_exists", "ai-docs/docs/_validation/review-*.md"),
            ("no_blockers", "No Blocker findings"),
            ("no_critical", "No Critical findings"),
        ],
        "QA_PASSED": [
            ("artifact_exists", "ai-docs/docs/_validation/qa-*.md"),
            ("tests_pass", "All tests pass"),
            ("coverage_ok", "Coverage >= 75%"),
            ("no_critical_bugs", "No Critical/Blocker bugs"),
        ],
        "ALL_GATES_PASSED": [
            ("all_previous", "All previous gates passed"),
            ("artifacts_exist", "All artifacts exist"),
            ("rtm_complete", "RTM is up to date"),
        ],
        "DEPLOYED": [
            ("containers_up", "docker-compose ps: all running"),
            ("health_ok", "Health endpoints respond 200"),
            ("logs_clean", "No errors in logs"),
        ],
    }

    checklist = checklist_map.get(gate, [])
    results = []

    for check_name, check_value in checklist:
        passed = run_check(check_name, check_value)
        results.append((check_name, passed, check_value))

    all_passed = all(r[1] for r in results)
    return GateResult(
        passed=all_passed,
        reason="OK" if all_passed else f"Failed: {[r[0] for r in results if not r[1]]}",
        checklist=results
    )
```

### 1. Blocking Gates

AI agent **CANNOT** proceed to the next stage if gates are not passed.

```
❌ PRD_READY not passed → /aidd-plan is blocked
❌ PLAN_APPROVED not passed → /aidd-code is blocked
```

### 2. Rollback and Recovery on Failure (P-004)

If gates are not passed, the AI agent follows a recovery algorithm:

```python
def handle_gate_failure(gate: str, reason: str) -> Action:
    """
    Algorithm for handling failed gates.

    Args:
        gate: Gate name (PRD_READY, PLAN_APPROVED, etc.)
        reason: Failure reason

    Returns:
        Action: Recommended action
    """
    recovery_actions = {
        "PRD_READY": {
            "incomplete_sections": "Complete missing PRD sections",
            "missing_criteria": "Add acceptance criteria to requirements",
            "open_questions": "Clarify questions with user",
        },
        "PLAN_APPROVED": {
            "not_approved": "Request confirmation from user",
            "missing_components": "Complete the architecture plan",
        },
        "IMPLEMENT_OK": {
            "tests_failed": "Fix code and rerun tests",
            "missing_types": "Add type hints",
            "structure_error": "Fix DDD structure",
        },
        "REVIEW_OK": {
            "critical_issues": "Fix critical findings",
            "convention_violations": "Align code with conventions.md",
        },
        "QA_PASSED": {
            "low_coverage": "Add tests to increase coverage",
            "tests_failed": "Fix failing tests",
            "bugs_found": "Fix discovered bugs",
        },
        "ALL_GATES_PASSED": {
            "gates_missing": "Return to the failed stage",
        },
        "DEPLOYED": {
            "build_failed": "Fix Dockerfile/docker-compose",
            "health_failed": "Check service configuration",
        },
    }

    return recovery_actions.get(gate, {}).get(reason, "Contact the user")
```

**Recovery example**:
```
/aidd-validate
→ ❌ Step 2/4: Testing failed (Coverage 68%, required ≥75%)
→ Automatic action: Add tests
[AI adds tests]
/aidd-validate
→ ✓ Step 2/4: Testing passed (Coverage 76%)
→ ✓ Step 3/4: Validation → ALL_GATES_PASSED
→ ✓ Step 4/4: Deploy → DEPLOYED
```

**Recovery principles**:
1. **Do not skip stages** — return to the problematic stage
2. **Fix, don't bypass** — eliminate the cause, not the symptom
3. **Notify the user** — if automatic recovery is not possible

### 3. Explicit User Confirmation

Some gates require explicit confirmation:

| Gate | Requires Confirmation |
|------|----------------------|
| `PRD_READY` | No (automatic check) |
| `PLAN_APPROVED` | **YES** (user must approve the plan) |
| `REVIEW_OK` | No (automatic check) |
| `QA_PASSED` | No (automatic check) |
| `DEPLOYED` | No (automatic check) |

---

## Reviewer and QA Role Separation (P-005)

Two roles perform different functions in the pipeline:

| Aspect | Reviewer (Stage 5) | QA (Stage 6) |
|--------|-------------------|---------------|
| **Focus** | Code quality | Functionality |
| **What is checked** | Architecture, conventions, DRY/KISS/YAGNI | Tests, coverage, PRD compliance |
| **Methods** | Static code analysis | Test execution |
| **Artifact** | `review-report.md` | `qa-report.md` |
| **Gate** | `REVIEW_OK` | `QA_PASSED` |

### Reviewer answers:
- Does the code match the architecture plan?
- Are conventions.md standards followed?
- Is there code duplication (DRY)?
- Is the code overly complex (KISS)?
- Is there unnecessary functionality (YAGNI)?

### QA answers:
- Do all tests pass?
- Is code coverage sufficient (≥75%)?
- Are all PRD requirements implemented and working?
- Are there bugs?

**Important**: Review precedes QA. First we check code quality, then its functionality.

---

## FEATURE Mode: Full Description (P-025)

FEATURE mode is designed for adding functionality to an existing project.

### Differences from CREATE

| Aspect | CREATE | FEATURE |
|--------|--------|---------|
| Goal | New MVP from scratch | Adding a feature |
| Stage 2 | Requirements analysis | Code analysis |
| Stage 3 | `/aidd-plan` — full architecture | `/aidd-plan-feature` — integration plan |
| Artifacts | New `ai-docs/` | Integration into existing |
| Tests | Created from scratch | Extending existing |

### Full FEATURE Process

```
Stage 1: /aidd-analyze "Add email notifications"
├── Analyst creates FEATURE_PRD
├── Focus on integration with existing functionality
└── Artifact: ai-docs/docs/_analysis/notifications.md

Stage 2: /aidd-research
├── Researcher analyzes EXISTING code
├── Identifies extension points
├── Determines dependencies
└── Integration recommendations

Stage 3: /aidd-plan-feature (NOT /aidd-plan!)
├── Planner creates INTEGRATION plan
├── Accounts for existing components
├── Minimizes changes to existing code
└── Artifact: ai-docs/docs/_plans/features/notifications.md

Stage 4: /aidd-code
├── Coder creates new code
├── Integrates with existing services
├── Extends, does not break
└── New tests + update existing

Stages 5-8: Same as CREATE
```

### FEATURE Pipeline Example

```bash
# 1. Launch in existing project directory
cd booking-service/

# 2. Describe the feature
/aidd-analyze "Add email notification system.
When booking, send confirmation to email.
When cancelling — send cancellation notification."

# 3. Research existing code
/aidd-research
# Agent analyzes:
# - Service structure
# - Points where notifications are needed
# - Existing integrations

# 4. Feature plan (NOT /aidd-plan!)
/aidd-plan-feature
# Agent creates integration plan:
# - NotificationService in booking_api
# - Integration with BookingService
# - New HTTP client for email

# 4-5. Generation and finalization
/aidd-code
/aidd-validate
```

### FEATURE Mode Markers

AI detects FEATURE mode when the following are present:

```
{project}/
├── services/           ← Existing services
├── docker-compose.yml  ← Infrastructure
├── ai-docs/docs/       ← Previous artifacts
└── Makefile            ← Build
```

---

## Parallel Pipelines (Pipeline State v2)

The framework supports simultaneous development of multiple features in separate git branches.

### Concept

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PARALLEL WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  main                                                                   │
│    │                                                                    │
│    ├──┬── feature/F042-oauth ─────────────────────────▶ merge           │
│    │  │     ├── /aidd-analyze      ← Creates branch automatically         │
│    │  │     ├── /aidd-research                                          │
│    │  │     ├── /aidd-plan                                              │
│    │  │     ├── /aidd-code                                          │
│    │  │     └── /aidd-validate ───────────▶ DEPLOYED                   │
│    │  │                                                                 │
│    │  └── feature/F043-payments ──────────────────────▶ merge           │
│    │        ├── /aidd-analyze      (in parallel with F042!)               │
│    │        └── ...                                                     │
│    ▼                                                                    │
│  main (with both features)                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Branch Naming

```
feature/{FID}-{slug}

Examples:
- feature/F001-table-booking
- feature/F042-oauth-auth
- feature/F043-payments
```

### Feature Context Detection

AI automatically determines the current feature by git branch:

```python
def get_current_feature_context(state: dict) -> tuple[str, dict] | None:
    """
    1. Get current git branch
    2. Find FID in active_pipelines by branch
    3. If one active feature — use it
    4. Otherwise — return None (explicit specification required)
    """
```

### Gate Isolation

Each feature has its own gates in `active_pipelines[FID].gates`:

```
┌─────────────────────────────────────────────────────────────────┐
│  GATES: Global vs Local                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GLOBAL (once per project):                                      │
│  └── BOOTSTRAP_READY                                            │
│                                                                 │
│  LOCAL (separate for each feature):                              │
│  ├── PRD_READY                                                  │
│  ├── RESEARCH_DONE                                              │
│  ├── PLAN_APPROVED                                              │
│  ├── IMPLEMENT_OK                                               │
│  ├── REVIEW_OK                                                  │
│  ├── QA_PASSED                                                  │
│  ├── ALL_GATES_PASSED                                           │
│  └── DEPLOYED                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Feature Completion

After `/aidd-validate`, the feature is moved from `active_pipelines` to `features_registry`:

```python
def complete_feature_deploy(state: dict, fid: str):
    """
    1. Mark DEPLOYED in gates
    2. Create Completion Report (final document)
    3. Add completion path to artifacts
    4. Move to features_registry
    5. Remove from active_pipelines
    """
```

> **Completion Report** — a single document that AI MUST read when working
> with deployed features. Contains: ADR, scope changes, known limitations, metrics.
> **Path**: `_validation/{date}_{FID}_{slug}.md`

### Git Helpers

```bash
# Show current context
python3 scripts/git_helpers.py context

# Check conflicts between features
python3 scripts/git_helpers.py conflicts F042 F043

# Complete feature and prepare for merge
python3 scripts/git_helpers.py merge F042
```

**Documentation**: [knowledge/pipeline/git-integration.md](knowledge/pipeline/git-integration.md)

---

## Artifact Versioning (P-028)

During iterative development, artifacts may have versions.

### Version Naming

```
ai-docs/docs/_analysis/
├── booking.md               ← Current version
├── booking-v1.md            ← Archive v1
└── booking-v2.md            ← Archive v2

ai-docs/docs/_plans/mvp/
├── booking.md               ← Current version
└── booking-v1.md            ← Archive v1
```

### When to Create a Version

| Situation | Action |
|-----------|--------|
| Requirements change | New PRD version |
| Architecture redesign | New plan version |
| Significant changes | Archive old version |

### Versioning Algorithm

```python
def version_artifact(artifact_path: Path) -> Path:
    """
    Create an artifact version before significant changes.

    Args:
        artifact_path: Path to current artifact

    Returns:
        Path to archived version
    """
    # 1. Determine current version
    versions = glob(f"{artifact_path.stem}-v*.md")
    next_version = len(versions) + 1

    # 2. Create archive copy
    archive_name = f"{artifact_path.stem}-v{next_version}.md"
    archive_path = artifact_path.parent / archive_name

    # 3. Copy current to archive
    shutil.copy(artifact_path, archive_path)

    # 4. Add header to archive
    content = archive_path.read_text()
    header = f"<!-- Archive version v{next_version}. See {artifact_path.name} -->\n\n"
    archive_path.write_text(header + content)

    return archive_path
```

### Updating .pipeline-state.json

```json
{
  "artifacts": {
    "prd": "ai-docs/docs/_analysis/booking.md",
    "prd_history": [
      "ai-docs/docs/_analysis/booking-v1.md",
      "ai-docs/docs/_analysis/booking-v2.md"
    ]
  }
}
```

---

## Related Documents

| Document | Description |
|----------|-------------|
| [CLAUDE.md](CLAUDE.md) | Main Entry Point |
| [conventions.md](conventions.md) | Code Conventions |
| [.claude/agents/](.claude/agents/) | AI Role Definitions |
| [.claude/commands/](.claude/commands/) | Command Definitions |

---

**Document version**: 1.2
**Created**: 2025-12-19
**Updated**: 2025-12-25
**Purpose**: AIDD-MVP Generator Development Process
