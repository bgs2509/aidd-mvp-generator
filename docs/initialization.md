# AI Agent Initialization Algorithm

**Note:** This document may contain outdated commands `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Current commands: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Purpose**: Single source of truth for the file reading order when launching any command.
>
> **Principle**: First understand WHERE we are (TP context), then HOW to act (framework).

---

## Overview

When launching any slash command (`/aidd-analyze`, `/aidd-research`, `/aidd-plan`, etc.) the AI agent
MUST follow the 4-phase initialization algorithm.

```
┌─────────────────────────────────────────────────────────────────────┐
│              AI AGENT INITIALIZATION ALGORITHM                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PHASE 1: Target Project (TP) context                               │
│  ────────────────────────────────────                               │
│  1. ./CLAUDE.md              ← TP Entry Point                       │
│  2. ./.pipeline-state.json   ← Pipeline state                       │
│  3. ./ai-docs/docs/          ← Existing artifacts                   │
│                                                                     │
│  PHASE 2: Precondition check                                        │
│  ────────────────────────────                                       │
│  4. Check required gates                                            │
│  5. If not passed → notify user                                     │
│                                                                     │
│  PHASE 3: Framework instructions                                    │
│  ────────────────────────────                                       │
│  6. .aidd/CLAUDE.md          ← Framework rules                      │
│  7. .aidd/workflow.md        ← Process and gates                    │
│  8. .aidd/.claude/commands/  ← Command instructions                 │
│  9. .aidd/.claude/agents/    ← Role instructions                    │
│                                                                     │
│  PHASE 4: Templates and Knowledge Base (as needed)                  │
│  ─────────────────────────────────────────────────                  │
│  10. .aidd/templates/documents/  ← If artifact doesn't exist        │
│  11. .aidd/knowledge/        ← By command topic                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Source Determination Criteria

When choosing where to read a file from — TP or Framework — use these criteria:

### Criteria Table

| Criterion | TP (`./`) | Framework (`.aidd/`) |
|-----------|-----------|---------------------|
| **Content** | THIS project's data | Universal instructions |
| **Mutability** | Changed by AI and user | NOT changed (read-only) |
| **Uniqueness** | Unique to the project | Same for all projects |
| **Source** | Created during development | Template/rule/pattern |
| **Question** | "WHAT are we doing?" | "HOW are we doing it?" |

### Selection Algorithm

```
IF the file answers the question:
├── "What are THIS project's requirements?" → TP
├── "What is THIS project's architecture?" → TP
├── "What code is ALREADY WRITTEN?" → TP
├── "What stage are WE at now?" → TP
│
├── "HOW to write code correctly?" → Framework
├── "HOW to structure a project?" → Framework
├── "WHICH template to use?" → Framework
└── "WHICH patterns to apply?" → Framework
```

### Examples

| Need to know | Source | File |
|--------------|--------|------|
| Requirements for feature X | TP | `./ai-docs/docs/_analysis/X-prd.md` |
| How to write FastAPI | Framework | `.aidd/knowledge/services/fastapi.md` |
| What services already exist | TP | `./services/` |
| Template for a new service | Framework | `.aidd/templates/services/` |
| Are gates passed | TP | `./.pipeline-state.json` |
| What gates to check | Framework | `.aidd/workflow.md` |

### Simple Rule

> **TP** = Project state and artifacts (unique, mutable)
> **Framework** = Instructions and templates (universal, read-only)

---

## Phase 1: Target Project Context

AI reads TP files **FIRST** to understand:
- What project this is
- What development stage it's at
- What artifacts already exist
- What mode is active (CREATE or FEATURE)

### 1.1 Reading ./CLAUDE.md

```python
if exists("./CLAUDE.md"):
    read("./CLAUDE.md")
    # Understand: project name, specific rules, context
```

### 1.2 Reading ./.pipeline-state.json

```python
if exists("./.pipeline-state.json"):
    state = read_json("./.pipeline-state.json")

    mode = state.get("mode")                         # CREATE or FEATURE
    active_pipelines = state.get("active_pipelines", {})  # Active features
    global_gates = state.get("global_gates", {})     # Global gates
    features_registry = state.get("features_registry", {})  # Completed features

    # For current feature (by git branch):
    # fid = get_current_feature_context()
    # feature_gates = active_pipelines.get(fid, {}).get("gates", {})
else:
    # New project — initialization needed
    mode = None
```

### 1.3 Checking Existing Artifacts

```python
existing_artifacts = {
    "prd": glob("./ai-docs/docs/_analysis/*-prd.md"),
    "plan": glob("./ai-docs/docs/_plans/mvp/*-plan.md"),
    "feature_plans": glob("./ai-docs/docs/_plans/features/*-plan.md"),
    "services": exists("./services/"),
    "reports": glob("./ai-docs/docs/_validation/*.md"),
}
```

### 1.4 Reading Completion Reports (for FEATURE mode)

> **Critically important**: Completion Report is the only document containing
> the full context of a deployed feature: ADR, scope changes, known limitations.

```python
# PHASE 1.4: Reading Completion Reports
if context.mode == "FEATURE" or len(state.get("features_registry", {})) > 0:
    for fid, feature in state.get("features_registry", {}).items():
        completion_path = feature.get("artifacts", {}).get("completion")
        if completion_path and exists(f"./ai-docs/docs/{completion_path}"):
            context.completion_reports[fid] = read(f"./ai-docs/docs/{completion_path}")
            # AI now knows EVERYTHING about deployed features in 1 file per feature
```

**When to read Completion Reports**:

| Situation | Action |
|-----------|--------|
| FEATURE mode (adding a feature) | Read ALL completion reports |
| CREATE mode, has deployed features | Read for context understanding |
| New session with the same project | Read for context restoration |
| Integration with a deployed feature | Read depends_on, enables |

**What AI learns from Completion Report**:

- **Executive Summary** — what was done
- **ADR** — why architectural decisions were made
- **Scope Changes** — what was deferred, what changed
- **Known Limitations** — limitations and workarounds
- **Services** — what services and endpoints are available
- **Dependencies** — what can be used (enables)

---

## Phase 2: Precondition Check

Each command has preconditions — gates that must be passed.

### Precondition Matrix

| Command | Required Gates | If not passed |
|---------|---------------|---------------|
| `/aidd-analyze` | — | — (first stage) |
| `/aidd-research` | `PRD_READY` | "First run /aidd-analyze" |
| `/aidd-plan` | `PRD_READY`, `RESEARCH_DONE` | "First run /aidd-research" |
| `/aidd-plan-feature` | `PRD_READY`, `RESEARCH_DONE` | "First run /aidd-research" |
| `/aidd-code` | `PLAN_APPROVED` | "First approve the plan" |
| `/aidd-validate` | `IMPLEMENT_OK` | "First run /aidd-code" |

### Check Algorithm

```python
def check_preconditions(command: str) -> bool:
    """
    Check preconditions before executing a command.

    Returns:
        True if all gates passed, False otherwise
    """
    preconditions = {
        "/aidd-analyze": [],
        "/aidd-research": ["PRD_READY"],
        "/aidd-plan": ["PRD_READY", "RESEARCH_DONE"],
        "/aidd-plan-feature": ["PRD_READY", "RESEARCH_DONE"],
        "/aidd-code": ["PLAN_APPROVED"],
        "/aidd-validate": ["IMPLEMENT_OK"],
    }

    state = read_json("./.pipeline-state.json")
    if not state:
        return command == "/aidd-analyze"  # Only /aidd-analyze can work without state

    for gate in preconditions.get(command, []):
        if not state.get("gates", {}).get(gate, {}).get("passed"):
            print(f"Gate {gate} not passed")
            print(f"→ {recovery_hint(gate)}")
            return False

    return True
```

---

## Phase 3: Framework Instructions

**AFTER** understanding the TP context, AI reads framework instructions.

### 3.1 Base Documents (always)

```python
read(".aidd/CLAUDE.md")      # General framework rules
read(".aidd/workflow.md")    # Process and Quality Gates
```

### 3.2 Command and Role Instructions (on demand)

```python
command_file = f".aidd/.claude/commands/{command}.md"
read(command_file)

# Determine role from command
role = COMMAND_TO_ROLE[command]
role_file = f".aidd/.claude/agents/{role}.md"
read(role_file)
```

### Command-to-Role Mapping

| Command | Role |
|---------|------|
| `/aidd-analyze` | analyst |
| `/aidd-research` | researcher |
| `/aidd-plan` | architect |
| `/aidd-plan-feature` | architect |
| `/aidd-code` | implementer |
| `/aidd-validate` | validator |

---

## Phase 4: Templates and Knowledge Base

Templates and knowledge base are read **ONLY IF NEEDED**.

### 4.1 Document Templates

```python
# Read template ONLY if artifact doesn't exist
if command == "/aidd-analyze" and not existing_artifacts["prd"]:
    read(".aidd/templates/documents/prd-template.md")

if command == "/aidd-plan" and not existing_artifacts["plan"]:
    read(".aidd/templates/documents/architecture-template.md")
```

### 4.2 Knowledge Base

```python
# Read as needed for the specific command
knowledge_map = {
    "/plan": [
        ".aidd/knowledge/architecture/ddd-hexagonal.md",
        ".aidd/knowledge/architecture/http-only.md",
    ],
    "/generate": [
        ".aidd/knowledge/services/fastapi.md",
        ".aidd/knowledge/infrastructure/docker.md",
    ],
    "/review": [
        ".aidd/knowledge/quality/testing.md",
    ],
}

for knowledge_file in knowledge_map.get(command, []):
    read(knowledge_file)
```

---

## Full Algorithm (pseudocode)

```python
def initialize_context(command: str) -> Context:
    """
    Full AI agent initialization algorithm.

    Principle: First WHERE we are, then HOW to act.

    Args:
        command: Slash command (/aidd-analyze, /aidd-research, etc.)

    Returns:
        Context: Full context for command execution
    """
    context = Context()

    # ═══════════════════════════════════════════════════════════════
    # PHASE 1: Target Project context
    # ═══════════════════════════════════════════════════════════════

    # 1.1 TP Entry Point
    if exists("./CLAUDE.md"):
        context.project_info = read("./CLAUDE.md")

    # 1.2 Pipeline state (v2 format)
    if exists("./.pipeline-state.json"):
        context.state = read_json("./.pipeline-state.json")
        context.mode = context.state.get("mode")
        context.active_pipelines = context.state.get("active_pipelines", {})
        context.global_gates = context.state.get("global_gates", {})
    else:
        context.mode = None  # Initialization required

    # 1.3 Existing artifacts
    context.existing_artifacts = {
        "prd": glob("./ai-docs/docs/_analysis/*-prd.md"),
        "plan": glob("./ai-docs/docs/_plans/mvp/*-plan.md"),
        "feature_plans": glob("./ai-docs/docs/_plans/features/*-plan.md"),
        "services": exists("./services/"),
        "reports": glob("./ai-docs/docs/_validation/*.md"),
    }

    # 1.4 Completion Reports (memory of deployed features)
    context.completion_reports = {}
    features_registry = context.state.get("features_registry", {}) if context.state else {}
    for fid, feature in features_registry.items():
        completion_path = feature.get("artifacts", {}).get("completion")
        if completion_path and exists(f"./ai-docs/docs/{completion_path}"):
            context.completion_reports[fid] = read(f"./ai-docs/docs/{completion_path}")
            # AI now knows: ADR, scope changes, known limitations

    # ═══════════════════════════════════════════════════════════════
    # PHASE 2: Precondition check
    # ═══════════════════════════════════════════════════════════════

    if not check_preconditions(command):
        raise GateNotPassedError(f"Preconditions for {command} not met")

    # ═══════════════════════════════════════════════════════════════
    # PHASE 3: Framework instructions
    # ═══════════════════════════════════════════════════════════════

    # Base documents
    context.framework_rules = read(".aidd/CLAUDE.md")
    context.workflow = read(".aidd/workflow.md")

    # Command instructions
    context.command_instructions = read(f".aidd/.claude/commands/{command}.md")

    # Role instructions
    role = COMMAND_TO_ROLE[command]
    context.role_instructions = read(f".aidd/.claude/agents/{role}.md")

    # ═══════════════════════════════════════════════════════════════
    # PHASE 4: Templates and Knowledge Base (as needed)
    # ═══════════════════════════════════════════════════════════════

    # Templates — only if artifact doesn't exist
    template_needed = should_load_template(command, context.existing_artifacts)
    if template_needed:
        context.template = read(template_needed)

    # Knowledge Base — by command topic
    for knowledge_file in KNOWLEDGE_MAP.get(command, []):
        context.knowledge.append(read(knowledge_file))

    return context
```

---

## Operating Mode Detection

```python
def detect_mode(state: dict, existing_artifacts: dict) -> str:
    """
    Detect operating mode: CREATE or FEATURE.

    Returns:
        'CREATE' — new project from scratch
        'FEATURE' — adding functionality to an existing project
    """
    # 1. Priority: explicit specification in state
    if state and state.get("mode"):
        return state["mode"]

    # 2. Existing project indicators
    project_markers = [
        existing_artifacts.get("services"),     # services/
        exists("./docker-compose.yml"),         # Infrastructure
        exists("./docker-compose.yaml"),
        bool(existing_artifacts.get("plan")),   # Architecture plan
    ]

    if any(project_markers):
        return "FEATURE"

    # 3. Additional: many Python files
    python_files = list(glob("./**/*.py"))
    if len(python_files) > 5:
        return "FEATURE"

    return "CREATE"
```

---

## Reading Order Table for All Commands

| Command | Phase 1 (TP) | Phase 2 | Phase 3 (Framework) | Phase 4 |
|---------|-------------|---------|--------------------|---------
| `/aidd-analyze` | CLAUDE.md, state, ai-docs | — | CLAUDE, workflow, idea.md, analyst.md | prd-template (if no PRD) |
| `/aidd-research` | CLAUDE.md, state, PRD | PRD_READY | CLAUDE, workflow, research.md, researcher.md | knowledge/architecture |
| `/aidd-plan` | CLAUDE.md, state, PRD | PRD_READY, RESEARCH_DONE | CLAUDE, workflow, plan.md, planner.md | architecture-template, knowledge/architecture |
| `/aidd-plan-feature` | CLAUDE.md, state, PRD, existing architecture | PRD_READY, RESEARCH_DONE | CLAUDE, workflow, feature-plan.md, planner.md | — |
| `/aidd-code` | CLAUDE.md, state, plan | PLAN_APPROVED | CLAUDE, workflow, generate.md, coder.md | templates/services, knowledge/services |
| `/aidd-validate` | CLAUDE.md, state, code, all artifacts | IMPLEMENT_OK | CLAUDE, workflow, finalize.md, validator.md, code-review-library.md, testing-library.md | conventions.md, knowledge/quality, knowledge/infrastructure |

---

## Example: Initialization for /aidd-analyze

```python
# User runs: /aidd-analyze "Create a booking service"

# PHASE 1: TP Context
if exists("./CLAUDE.md"):
    read("./CLAUDE.md")  # → Understand project specifics

if exists("./.pipeline-state.json"):
    state = read_json("./.pipeline-state.json")  # → mode, gates
else:
    state = None  # → New project

artifacts = glob("./ai-docs/docs/_analysis/*-prd.md")  # → []

# PHASE 2: Preconditions
# /aidd-analyze requires no preconditions — skip

# PHASE 3: Framework
read(".aidd/CLAUDE.md")
read(".aidd/workflow.md")
read(".aidd/.claude/commands/aidd-analyze.md")
read(".aidd/.claude/agents/analyst.md")

# PHASE 4: Templates
if not artifacts:  # PRD doesn't exist
    read(".aidd/templates/documents/prd-template.md")

# Mode detection
mode = detect_mode(state, {"prd": artifacts, "services": False})
# → mode = "CREATE"

# Bootstrap (only for /aidd-analyze when mode == None)
mkdir("./ai-docs/docs/{prd,architecture,plans,reports,research}")
write("./.pipeline-state.json", {"mode": "CREATE", ...})

# Execution: create PRD
create_prd("./ai-docs/docs/_analysis/booking-prd.md")
```

---

## Example: Initialization for /aidd-code (mid-pipeline)

```python
# User runs: /generate

# PHASE 1: TP Context
read("./CLAUDE.md")  # → "Booking Service"
state = read_json("./.pipeline-state.json")
# → mode: "CREATE", stage: 4, gates: {PRD_READY: ✓, RESEARCH_DONE: ✓, PLAN_APPROVED: ✓}

plan = read(state["artifacts"]["plan"])  # → Architecture plan

# PHASE 2: Preconditions
assert state["gates"]["PLAN_APPROVED"]["passed"]  # ✓

# PHASE 3: Framework
read(".aidd/CLAUDE.md")
read(".aidd/workflow.md")
read(".aidd/.claude/commands/aidd-code.md")
read(".aidd/.claude/agents/coder.md")
read(".aidd/conventions.md")

# PHASE 4: Templates and knowledge
read(".aidd/templates/services/fastapi_business_api/")
read(".aidd/templates/services/postgres_data_api/")
read(".aidd/templates/infrastructure/docker/")
read(".aidd/knowledge/services/fastapi.md")

# Execution: code generation
generate_services(plan)
```

---

## Related Documents

| Document | Description |
|----------|-------------|
| [CLAUDE.md](../CLAUDE.md) | Framework main Entry Point |
| [workflow.md](../workflow.md) | Pipeline and gates |
| [NAVIGATION.md](NAVIGATION.md) | Navigation matrix by stages |
| [target-project-structure.md](target-project-structure.md) | Target Project structure |

---

**Version**: 2.0
**Created**: 2025-12-21
**Purpose**: Single source of truth for the AI agent initialization algorithm
