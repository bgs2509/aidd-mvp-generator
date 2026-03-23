---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(git :*), Bash(python3 :*)
description: Create implementation plan for a new feature in an existing project
---

> ⚠️ **ENFORCEMENT**: Before completing this command, AI MUST:
> 1. Find the "Gate Checklist" section at the end of this file
> 2. Create TodoWrite with ALL items (especially 🔴)
> 3. Complete ALL items and mark them completed
> 4. Command is complete ONLY when all 🔴 items are ✅
>
> Rules: `.aidd/CLAUDE.md` → "Executing /aidd-* commands"

# Command: /aidd-plan-feature

> Launches the Planner for feature planning (FEATURE mode).
> **Pipeline State v2**: Parallel pipeline support.

---

## Syntax

```bash
/aidd-plan-feature
```

---

## Description

The `/aidd-plan-feature` command creates an implementation plan for a new feature
in an existing project. Takes into account the current architecture and patterns.

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
| 3 | `./ai-docs/docs/_analysis/*.md` | Required | Feature requirements |
| 4 | `./ai-docs/docs/_plans/mvp/*.md` | Required | Existing architecture |
| 5 | `./services/` | Required | Existing code |

### Phase 2: Auto-migration and Preconditions

> **Important**: Before executing the command, check `.pipeline-state.json` version
> and perform v1 → v2 migration if required (see `knowledge/pipeline/automigration.md`).

| Gate | Check (v2) |
|------|------------|
| `mode` | `.pipeline-state.json → mode == "FEATURE"` |
| `PRD_READY` | `active_pipelines[FID].gates.PRD_READY.passed == true` |
| `RESEARCH_DONE` | `active_pipelines[FID].gates.RESEARCH_DONE.passed == true` |

> **Note v2**: FID is determined by the current git branch.

### Phase 3: Framework Instructions

| # | File | Purpose |
|---|------|---------|
| 6 | `.aidd/CLAUDE.md` | Framework rules |
| 7 | `.aidd/workflow.md` | Process and gates |
| 8 | `.aidd/.claude/commands/feature-plan.md` | This file |
| 9 | `.aidd/.claude/agents/planner.md` | Role instructions |

### Phase 4: Knowledge Base

| # | File | Condition |
|---|------|-----------|
| 10 | `.aidd/knowledge/architecture/*.md` | As needed |

---

## Modes

Only **FEATURE** — for existing projects.

For a new project, use `/aidd-plan`.

---

## Preconditions

| Gate | Requirement |
|------|-------------|
| `PRD_READY` | FEATURE_PRD document exists |
| `RESEARCH_DONE` | Code analyzed |

### Verification Algorithm (v2)

```python
def check_feature_plan_preconditions() -> tuple[str, dict] | None:
    """
    Check preconditions for /feature-plan.

    v2: Determine FID by git branch, check active_pipelines[fid].gates
    """
    # 1. Check and migrate state
    state = ensure_v2_state()  # see knowledge/pipeline/automigration.md
    if not state:
        print("❌ Pipeline not initialized → /aidd-analyze")
        return None

    # 2. Check mode
    if state.get("mode") != "FEATURE":
        print("⚠️  CREATE mode — use /aidd-plan instead of /aidd-plan-feature")
        return None

    # 3. Determine FID by current git branch
    fid, pipeline = get_current_feature_context(state)
    if not fid:
        print("❌ Could not determine feature context")
        return None

    gates = pipeline.get("gates", {})

    # 4. Check PRD_READY
    if not gates.get("PRD_READY", {}).get("passed"):
        print(f"❌ PRD_READY gate not passed for {fid}")
        print("   → First run /aidd-analyze")
        return None

    # 5. Check RESEARCH_DONE
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
| Feature Plan | `ai-docs/docs/_plans/features/{YYYY-MM-DD}_{FID}_{slug}-plan.md` | `ai-docs/docs/_plans/features/{YYYY-MM-DD}_{FID}_{slug}.md` |

> **Note (v2.4+)**:
> - **v2** (default): Old structure `plans/`, name with duplication `{name}-plan.md`
> - **v3** (after migration): New structure `_plans/features/`, name without duplication `{name}.md`
> - Mode determined from `.pipeline-state.json → naming_version`

### Artifact Naming

FID and slug are taken from `active_pipelines[FID]` in `.pipeline-state.json` (v2):

```python
# Get data from state (v2)
fid, pipeline = get_current_feature_context(state)
if not fid:
    print("❌ Could not determine feature context")
    return None

slug = pipeline["name"]  # email-notify
date = datetime.now().strftime("%Y-%m-%d")  # 2024-12-23

# Determine naming_version and artifact structure
naming_version = state.get("naming_version", "v2")

if naming_version == "v3":
    folder = "_plans/features"
    filename = f"{date}_{fid}_{slug}.md"  # Without duplication
else:
    folder = "plans"
    filename = f"{date}_{fid}_{slug}-plan.md"  # With duplication

artifact_path = f"{folder}/{filename}"
# v2: plans/2024-12-23_F042_email-notify-plan.md
# v3: _plans/features/2024-12-23_F042_email-notify.md
```

### Updating .pipeline-state.json

After creating the plan, update `active_pipelines[FID].artifacts` (v2):

**Example for v2 (default)**:
```json
{
  "naming_version": "v2",
  "active_pipelines": {
    "F042": {
      "branch": "feature/F042-email-notify",
      "name": "email-notify",
      "title": "Email Notifications",
      "stage": "PLAN",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": true, "passed_at": "2024-12-23T11:00:00Z"},
        "PLAN_APPROVED": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F042_email-notify-prd.md",
        "research": "research/2024-12-23_F042_email-notify-research.md",
        "plan": "plans/2024-12-23_F042_email-notify-plan.md"
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
    "F042": {
      "artifacts": {
        "prd": "_analysis/2024-12-23_F042_email-notify.md",
        "research": "_research/2024-12-23_F042_email-notify.md",
        "plan": "_plans/features/2024-12-23_F042_email-notify.md"
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
| Integration | Integration points defined |
| Changes | Required changes described |
| Risks | Potential risks addressed |
| Test plan | Testing section filled (smoke/unit/integration/e2e) |
| **Approval** | Plan approved by user |

**IMPORTANT**: Explicit user confirmation required!

---

## Usage Examples

```bash
# After /aidd-research (for a feature)
/feature-plan
```

---

## Differences from /aidd-plan

| Aspect | /aidd-plan (CREATE) | /aidd-plan-feature (FEATURE) |
|--------|----------------|-------------------------|
| Goal | Full system architecture | Feature integration plan |
| Artifact (v2) | `architecture/{name}-plan.md` | `plans/{feature}-plan.md` |
| Artifact (v3) | `_plans/mvp/{name}.md` | `_plans/features/{name}.md` |
| Focus | Components from scratch | Extension points |
| Changes | Creating new | Minimizing changes |

---

## Feature Plan Template

The feature plan must contain:

```markdown
# Feature Plan: {Name}

## 1. Overview
- Brief description
- Relation to existing functionality

## 2. Existing Code Analysis
- Affected services
- Integration points
- Existing dependencies

## 3. Change Plan

### 3.1 New Components
| Component | Location | Description |

### 3.2 Modifications to Existing Code
| File | Change | Reason |

### 3.3 New Dependencies
| Dependency | Version | Purpose |

## 4. API Contracts (if any)

## 5. Impact on Existing Tests

## 6. Integration Plan
| # | Step | Dependencies |

## 7. Risks and Mitigation
| Risk | Probability | Mitigation |
```

---

## Integration Considerations

When creating a feature plan, consider:

### 1. Minimizing Changes
```
✓ Add new module
✗ Rewrite existing module

✓ Extend interface
✗ Change signatures of existing methods

✓ Add new endpoint
✗ Change URLs of existing endpoints
```

### 2. Backward Compatibility
- Existing APIs must work without changes
- New fields must be optional
- DB migrations must be reversible

### 3. Testing
- Existing tests must not break
- New tests are isolated from old ones
- Integration tests cover connection points

---

## PLAN_APPROVED Gate Checklist

> ⚠️ AI MUST create TodoWrite with these items.

- [ ] 🔴 Feature Plan created in correct folder:
  - v2: `ai-docs/docs/_plans/features/{feature}-plan.md`
  - v3: `ai-docs/docs/_plans/features/{feature}.md`
- [ ] 🔴 Integration with existing code described
- [ ] 🔴 Test plan filled (smoke/unit/integration/e2e)
- [ ] 🔴 **User approved the plan** ← CRITICALLY IMPORTANT
- [ ] 🔴 `.pipeline-state.json` updated (gate: PLAN_APPROVED, artifact path matches naming_version)
- [ ] 🟡 Breaking changes identified
- [ ] 🟡 DB migrations described (if applicable)

---

## Next Step

After passing the `PLAN_APPROVED` gate:

```bash
/aidd-code
```
