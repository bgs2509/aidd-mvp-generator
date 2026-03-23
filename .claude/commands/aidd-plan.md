---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(git :*), Bash(python3 :*)
description: Create architectural plan for a new MVP project
---

> ⚠️ **ENFORCEMENT**: Before completing this command, AI MUST:
> 1. Find the "Gate Checklist" section at the end of this file
> 2. Create TodoWrite with ALL items (especially 🔴)
> 3. Complete ALL items and mark them completed
> 4. Command is complete ONLY when all 🔴 items are ✅
>
> Rules: `.aidd/CLAUDE.md` → "Executing /aidd-* commands"

# Command: /aidd-plan

> Launches the Planner for system design (CREATE mode).
> **Pipeline State v2**: Parallel pipeline support.

---

## Syntax

```bash
/aidd-plan
```

---

## Description

The `/aidd-plan` command creates a complete architectural plan for a new MVP project.
Used in CREATE mode for designing a system from scratch.

> **VERIFY BEFORE ACT**: Before creating files/directories, check their
> existence (see CLAUDE.md, "Critical Rules" section).

---

## Agent

**Planner** (`.claude/agents/planner.md`)

---

## File Reading Order

> **Principle**: First TP context, then framework instructions.
> **Details**: [docs/initialization.md](../../docs/initialization.md)

### Phase 1: Target Project Context

| # | File | Condition | Purpose |
|---|------|-----------|---------|
| 1 | `./CLAUDE.md` | If exists | Project specifics |
| 2 | `./.pipeline-state.json` | Required | Mode, stage, gates |
| 3 | `./ai-docs/docs/_analysis/*.md` | Required | Requirements from PRD |

### Phase 2: Auto-migration and Preconditions

> **Important**: Before executing the command, check `.pipeline-state.json` version
> and perform v1 → v2 migration if required (see `knowledge/pipeline/automigration.md`).

| Gate | Check (v2) |
|------|------------|
| `PRD_READY` | `active_pipelines[FID].gates.PRD_READY.passed == true` |
| `RESEARCH_DONE` | `active_pipelines[FID].gates.RESEARCH_DONE.passed == true` |

> **Note v2**: FID is determined by the current git branch.

### Phase 3: Framework Instructions

| # | File | Purpose |
|---|------|---------|
| 4 | `.aidd/CLAUDE.md` | Framework rules |
| 5 | `.aidd/workflow.md` | Process and gates |
| 6 | `.aidd/.claude/commands/plan.md` | This file |
| 7 | `.aidd/.claude/agents/planner.md` | Role instructions |

### Phase 4: Templates and Knowledge Base

| # | File | Condition |
|---|------|-----------|
| 8 | `.aidd/templates/documents/architecture-template.md` | For creating the plan |
| 9 | `.aidd/knowledge/architecture/ddd-hexagonal.md` | Architectural patterns |
| 10 | `.aidd/knowledge/architecture/http-only.md` | HTTP-only access |

---

## Modes

Only **CREATE** — for new projects.

For adding a feature to an existing project, use `/aidd-plan-feature`.

---

## Preconditions

| Gate | Requirement |
|------|-------------|
| `PRD_READY` | PRD document exists |
| `RESEARCH_DONE` | Research completed |

### Verification Algorithm (v2)

```python
def check_plan_preconditions() -> tuple[str, dict] | None:
    """
    Check preconditions for /plan.

    v2: Determine FID by git branch, check active_pipelines[fid].gates
    """
    # 1. Check and migrate state
    state = ensure_v2_state()  # see knowledge/pipeline/automigration.md
    if not state:
        print("❌ Pipeline not initialized → /aidd-analyze")
        return None

    # 2. Determine FID by current git branch
    fid, pipeline = get_current_feature_context(state)
    if not fid:
        print("❌ Could not determine feature context")
        return None

    gates = pipeline.get("gates", {})

    # 3. Check PRD_READY
    if not gates.get("PRD_READY", {}).get("passed"):
        print(f"❌ PRD_READY gate not passed for {fid}")
        print("   → First run /aidd-analyze")
        return None

    # 4. Check RESEARCH_DONE
    if not gates.get("RESEARCH_DONE", {}).get("passed"):
        print(f"❌ RESEARCH_DONE gate not passed for {fid}")
        print("   → First run /aidd-research")
        return None

    print(f"✓ Feature {fid}: {pipeline.get('title')}")
    return (fid, pipeline)
```

---

## Output Artifacts (in target project)

| Artifact | Path (v2) | Path (v3) |
|----------|-----------|-----------|
| Architectural Plan (MVP) | `ai-docs/docs/_plans/mvp/{YYYY-MM-DD}_{FID}_{slug}-plan.md` | `ai-docs/docs/_plans/mvp/{YYYY-MM-DD}_{FID}_{slug}.md` |

> **Note (v2.4+)**:
> - **v2** (default): Old structure `architecture/`, name with duplication `{name}-plan.md`
> - **v3** (after migration): New structure `_plans/mvp/`, name without duplication `{name}.md`
> - Mode determined from `.pipeline-state.json → naming_version`

### Artifact Naming

FID and slug are taken from `active_pipelines[FID]` in `.pipeline-state.json` (v2):

```python
# Get data from state (v2)
fid, pipeline = get_current_feature_context(state)
if not fid:
    print("❌ Could not determine feature context")
    return None

slug = pipeline["name"]  # table-booking
date = datetime.now().strftime("%Y-%m-%d")  # 2024-12-23

# Determine naming_version and artifact structure
naming_version = state.get("naming_version", "v2")

if naming_version == "v3":
    folder = "_plans/mvp"
    filename = f"{date}_{fid}_{slug}.md"  # Without duplication
else:
    folder = "architecture"
    filename = f"{date}_{fid}_{slug}-plan.md"  # With duplication

artifact_path = f"{folder}/{filename}"
# v2: architecture/2024-12-23_F001_table-booking-plan.md
# v3: _plans/mvp/2024-12-23_F001_table-booking.md
```

### Updating .pipeline-state.json

After creating the plan, update `active_pipelines[FID].artifacts` (v2):

**Example for v2 (default)**:
```json
{
  "naming_version": "v2",
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Table Booking",
      "stage": "PLAN",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": true, "passed_at": "2024-12-23T11:00:00Z"},
        "PLAN_APPROVED": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md",
        "plan": "architecture/2024-12-23_F001_table-booking-plan.md"
      }
    }
  }
}
```

**Example for v3 (after migration)**:
```json
{
  "naming_version": "v3",
  "active_pipelines": {
    "F001": {
      "artifacts": {
        "prd": "_analysis/2024-12-23_F001_table-booking.md",
        "research": "_research/2024-12-23_F001_table-booking.md",
        "plan": "_plans/mvp/2024-12-23_F001_table-booking.md"
      }
    }
  }
}
```

---

## Quality Gates

### PLAN_APPROVED

| Criterion | Description |
|-----------|-------------|
| Components | All system components defined |
| API contracts | Endpoints and schemas described |
| NFR | Non-functional requirements addressed |
| Test plan | Testing section filled (smoke/unit/integration/e2e) |
| **Approval** | Plan approved by user |

**IMPORTANT**: Explicit user confirmation required!

---

## Usage Examples

```bash
# After /aidd-research
/aidd-plan
```

---

## PLAN_APPROVED Gate Checklist

> ⚠️ AI MUST create TodoWrite with these items.

- [ ] 🔴 Architecture Plan created in correct folder:
  - v2: `ai-docs/docs/_plans/mvp/{name}-plan.md`
  - v3: `ai-docs/docs/_plans/mvp/{name}.md`
- [ ] 🔴 All services defined with types
- [ ] 🔴 API contracts described
- [ ] 🔴 Test plan filled (smoke/unit/integration/e2e)
- [ ] 🔴 **User approved the plan** ← CRITICALLY IMPORTANT
- [ ] 🔴 `.pipeline-state.json` updated (gate: PLAN_APPROVED, artifact path matches naming_version)
- [ ] 🟡 ADRs documented

---

## Next Step

After passing the `PLAN_APPROVED` gate:

```bash
/aidd-code
```
