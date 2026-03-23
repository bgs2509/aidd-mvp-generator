# Pipeline State v2: Parallel Pipelines

**Note:** This document may contain outdated command references `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Current commands: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Version**: 2.0
> **Date**: 2025-12-25

---

## Overview

Pipeline State v2 supports **parallel development of multiple features** through isolation of each feature's state in a separate pipeline.

---

## `.pipeline-state.json` v2 Structure

```json
{
  "$schema": "pipeline-state-schema",
  "version": "2.0",
  "project_name": "my-project",
  "mode": "FEATURE",
  "parallel_mode": true,

  "global_gates": {
    "BOOTSTRAP_READY": { "passed": true, ... }
  },

  "active_pipelines": {
    "F042": {
      "branch": "feature/F042-oauth",
      "name": "oauth-auth",
      "title": "OAuth authorization",
      "stage": "IMPLEMENT",
      "created": "2025-12-25",
      "gates": { ... },
      "artifacts": { ... }
    },
    "F043": { ... }
  },

  "features_registry": {
    "F001": { "status": "DEPLOYED", ... }
  },

  "next_feature_id": 44,
  "services": []
}
```

---

## Key Changes v1 -> v2

| Aspect | v1 | v2 |
|--------|----|----|
| Active features | 1 (`current_feature`) | N (`active_pipelines`) |
| Gates | Shared (`gates`) | Isolated (`active_pipelines[FID].gates`) |
| Global gates | Mixed with local | Separate (`global_gates`) |
| Feature context | Implicit | By git branch |

---

## Automigration

### When running any slash command

The AI agent MUST check the `.pipeline-state.json` version:

```python
# Check pseudocode
state = read_json(".pipeline-state.json")

if state.get("version") != "2.0":
    # Perform migration
    run("python .aidd/scripts/migrate_pipeline_state.py")
    # Or notify user
    print("⚠️ Migration required. Run:")
    print("   python .aidd/scripts/migrate_pipeline_state.py")
```

### Migration Command

```bash
# Show migration plan
python .aidd/scripts/migrate_pipeline_state.py --dry-run

# Perform migration
python .aidd/scripts/migrate_pipeline_state.py
```

---

## Feature Context Detection

### Algorithm

1. **Check current git branch**
   ```bash
   git rev-parse --abbrev-ref HEAD
   # -> feature/F042-oauth
   ```

2. **Find FID in active_pipelines by branch**
   ```python
   for fid, pipeline in state["active_pipelines"].items():
       if pipeline["branch"] == current_branch:
           return fid  # -> "F042"
   ```

3. **If only one active feature** -- use it

4. **If multiple features and branch doesn't match** -- ask the user

### Example for AI Agent

```markdown
When executing a command:

1. Read .pipeline-state.json
2. Check version (must be "2.0")
3. Get current git branch: `git rev-parse --abbrev-ref HEAD`
4. Find FID by branch in active_pipelines
5. Use active_pipelines[FID].gates for gate checks
6. Update active_pipelines[FID] when passing stages
```

---

## Working with Gates

### Global Gates

Checked once per project:
- `BOOTSTRAP_READY` -- environment is set up

### Local Gates (per feature)

```
PRD_READY -> RESEARCH_DONE -> PLAN_APPROVED -> IMPLEMENT_OK ->
-> REVIEW_OK -> QA_PASSED -> ALL_GATES_PASSED -> DEPLOYED
```

### Gate Checking

```python
def check_gate(fid: str, gate: str) -> bool:
    state = read_json(".pipeline-state.json")

    # Global gates
    if gate == "BOOTSTRAP_READY":
        return state["global_gates"]["BOOTSTRAP_READY"]["passed"]

    # Local gates
    pipeline = state["active_pipelines"].get(fid)
    if not pipeline:
        return False

    return pipeline["gates"].get(gate, {}).get("passed", False)
```

### Gate Updating

```python
def pass_gate(fid: str, gate: str, artifact: str = None) -> None:
    state = read_json(".pipeline-state.json")

    state["active_pipelines"][fid]["gates"][gate] = {
        "passed": True,
        "passed_at": datetime.now().isoformat(),
        "artifact": artifact
    }

    write_json(".pipeline-state.json", state)
```

### Gate Aliases (v2.4+)

Starting with v2.4, the framework supports **gate aliases** for unified naming conventions:

```json
{
  "gate_aliases": {
    "PRD_READY": "ANALYSIS_READY",
    "RESEARCH_DONE": "RESEARCH_READY",
    "IMPLEMENT_OK": "CODE_READY",
    "REVIEW_OK": "REVIEW_READY",
    "QA_PASSED": "TESTING_READY",
    "ALL_GATES_PASSED": "VALIDATION_READY"
  }
}
```

**How it works:**
- Old names (`PRD_READY`, `IMPLEMENT_OK`) remain primary in the gate structure
- New names (`ANALYSIS_READY`, `CODE_READY`) are aliases that can be used in code
- The AI agent can check gates by either name: `check_gate(fid, "PRD_READY")` or `check_gate(fid, "ANALYSIS_READY")`

**Extended gate checking example:**

```python
def check_gate_with_alias(fid: str, gate: str) -> bool:
    state = read_json(".pipeline-state.json")

    # Resolve alias -> primary name
    gate_aliases = state.get("gate_aliases", {})
    reverse_aliases = {v: k for k, v in gate_aliases.items()}

    # If gate is an alias, get primary name
    primary_gate = reverse_aliases.get(gate, gate)

    # Global gates
    if primary_gate == "BOOTSTRAP_READY":
        return state["global_gates"]["BOOTSTRAP_READY"]["passed"]

    # Local gates
    pipeline = state["active_pipelines"].get(fid)
    if not pipeline:
        return False

    return pipeline["gates"].get(primary_gate, {}).get("passed", False)
```

**Status:** Phase 1 (backward compatible) -- both variants work simultaneously.

---

## Feature Lifecycle

### 1. Creation (`/aidd-analyze`)

```python
def create_feature(title: str) -> str:
    state = read_json(".pipeline-state.json")

    fid = f"F{state['next_feature_id']:03d}"
    state['next_feature_id'] += 1

    slug = slugify(title)[:30]
    branch = f"feature/{fid}-{slug}"

    # Create git branch
    run(f"git checkout -b {branch}")

    state["active_pipelines"][fid] = {
        "branch": branch,
        "name": slug,
        "title": title,
        "stage": "IDEA",
        "created": today(),
        "gates": create_empty_gates(),
        "artifacts": {}
    }

    write_json(".pipeline-state.json", state)
    return fid
```

### 2. Progress Through Stages

At each successful stage:
1. Update `active_pipelines[FID].stage`
2. Mark gates as passed
3. Record artifact path

### 3. Completion (`/aidd-validate`)

```python
def complete_feature(fid: str) -> None:
    state = read_json(".pipeline-state.json")

    pipeline = state["active_pipelines"].pop(fid)
    slug = pipeline["name"]
    today_str = today()

    # Add completion report to artifacts
    completion_path = f"reports/{today_str}_{fid}_{slug}-completion.md"
    pipeline["artifacts"]["completion"] = completion_path

    state["features_registry"][fid] = {
        "name": pipeline["name"],
        "title": pipeline["title"],
        "status": "DEPLOYED",
        "created": pipeline["created"],
        "deployed": today_str,
        "artifacts": pipeline["artifacts"],  # Includes completion
        "services": pipeline.get("services", [])
    }

    write_json(".pipeline-state.json", state)
```

### features_registry Structure

```json
{
  "features_registry": {
    "F001": {
      "name": "table-booking",
      "title": "Table booking",
      "status": "DEPLOYED",
      "created": "2024-12-23",
      "deployed": "2024-12-24",
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md",
        "plan": "architecture/2024-12-23_F001_table-booking-plan.md",
        "completion": "reports/2024-12-24_F001_table-booking-completion.md"
      },
      "services": ["booking_api", "booking_data"]
    }
  }
}
```

> **Completion Report**: The final document containing a summary of everything done,
> ADR (architecture decisions), scope changes, and known limitations.
> AI MUST read this document when working with deployed features.

---

## AI Agent Checklist

When executing any command:

- [ ] Check `.pipeline-state.json` existence
- [ ] Check version (migrate if v1)
- [ ] Determine feature context by git branch
- [ ] Check preconditions (gates) for the command
- [ ] Execute the command
- [ ] Update gates and artifacts in `active_pipelines[FID]`
- [ ] Update `updated_at`

---

## Compatibility

### parallel_mode

- `false` (v1 default) -- sequential mode, one active feature
- `true` (v2 recommended) -- parallel mode, multiple active features

```
┌─────────────────────────────────────────────────────────────────┐
│  ✅ ALLOWED: Starting a new feature without completing           │
│     the previous one                                             │
├─────────────────────────────────────────────────────────────────┤
│  • parallel_mode: true (default in v2)                           │
│  • No limit on active_pipelines count                            │
│  • Each feature in its own git branch feature/{FID}-{slug}       │
│  • Gates are isolated in active_pipelines[FID].gates             │
│                                                                 │
│  ⚠️  Developer responsibility:                                   │
│  • Track conflicts between features                              │
│  • Avoid changing the same files in different features           │
│  • Use git_helpers.py conflicts for checking                     │
└─────────────────────────────────────────────────────────────────┘
```

With `parallel_mode: false`:
- Only one active pipeline allowed
- Warning when attempting to create a second one
- Used for projects with strict sequencing

### Backward compatibility (v1) fields

These fields are preserved for compatibility but NOT used:
- `current_feature` -- replaced by `active_pipelines`
- `current_stage` -- replaced by `active_pipelines[FID].stage`
- `gates` (root) -- replaced by `global_gates` + `active_pipelines[FID].gates`
- `artifacts` (root) -- replaced by `active_pipelines[FID].artifacts`
