---
allowed-tools: Read(*), Glob(*), Grep(*), Bash(git :*), Bash(python3 :*)
description: Analyze codebase and technologies
---

> ⚠️ **ENFORCEMENT**: Before completing this command, AI MUST:
> 1. Find the "Gate Checklist" section at the end of this file
> 2. Create TodoWrite with ALL items (especially 🔴)
> 3. Complete ALL items and mark them completed
> 4. Command is complete ONLY when all 🔴 items are ✅
>
> Rules: `.aidd/CLAUDE.md` → "Executing /aidd-* commands"

# Command: /aidd-research

> Launches the Researcher to analyze the codebase and technologies.
> **Pipeline State v2**: Parallel pipeline support.

---

## Syntax

```bash
/aidd-research
```

---

## Description

The `/aidd-research` command performs analysis of existing code (for FEATURE)
or analysis of requirements and technologies (for CREATE).

> **VERIFY BEFORE ACT**: Before creating files/directories, check their
> existence (see CLAUDE.md, "Critical Rules" section).

---

## Agent

**Researcher** (`.claude/agents/researcher.md`)

---

## File Reading Order

> **Principle**: First TP context, then framework instructions.
> **Details**: [docs/initialization.md](../../docs/initialization.md)

### Phase 1: Target Project Context

| # | File | Condition | Purpose |
|---|------|-----------|---------|
| 1 | `./CLAUDE.md` | If exists | Project specifics |
| 2 | `./.pipeline-state.json` | Required | Mode, stage, gates |
| 3 | `./ai-docs/docs/_analysis/*.md` | Required | PRD for analysis |
| 4 | `./services/` | For FEATURE | Existing code |

### Phase 2: Auto-migration and Preconditions

> **Important**: Before executing the command, check `.pipeline-state.json` version
> and perform v1 → v2 migration if required (see `knowledge/pipeline/automigration.md`).

| Gate | Check (v2) |
|------|------------|
| `PRD_READY` | `active_pipelines[FID].gates.PRD_READY.passed == true` |

> **Note v2**: FID is determined by the current git branch.

### Phase 3: Framework Instructions

| # | File | Purpose |
|---|------|---------|
| 5 | `.aidd/CLAUDE.md` | Framework rules |
| 6 | `.aidd/workflow.md` | Process and gates |
| 7 | `.aidd/.claude/commands/research.md` | This file |
| 8 | `.aidd/.claude/agents/researcher.md` | Role instructions |

### Phase 4: Knowledge Base

| # | File | Condition |
|---|------|-----------|
| 9 | `.aidd/knowledge/architecture/*.md` | As needed |

---

## Modes

| Mode | Behavior |
|------|----------|
| **CREATE** | Requirements analysis from PRD, technology selection |
| **FEATURE** | Existing code analysis, pattern identification |

---

## Test Analysis (FEATURE)

If the project already contains code, it is mandatory to:
- Analyze existing tests (smoke/unit/integration/e2e)
- Fill in section "3.6 Existing Test Analysis" in the Research Report
- Map found tests to PRD section 6.5 requirements (TRQ-001..TRQ-007)

---

## Preconditions

| Gate | Requirement |
|------|-------------|
| `PRD_READY` | PRD document must exist |

### Verification Algorithm (v2)

```python
def check_research_preconditions() -> tuple[str, dict] | None:
    """
    Check preconditions for /research.

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

    # 3. Check PRD_READY
    if not pipeline["gates"].get("PRD_READY", {}).get("passed"):
        print(f"❌ PRD_READY gate not passed for {fid}")
        print("   → First run /aidd-analyze")
        return None

    print(f"✓ Feature {fid}: {pipeline.get('title')}")
    return (fid, pipeline)
```

---

## Output Artifacts

| Artifact | Path (v2) | Path (v3) |
|----------|-----------|-----------|
| Research Report | `ai-docs/docs/research/{YYYY-MM-DD}_{FID}_{slug}-research.md` | `ai-docs/docs/_research/{YYYY-MM-DD}_{FID}_{slug}.md` |

> **Note (v2.4+)**:
> - **v2** (default): Old structure `research/`, name with duplication `{name}-research.md`
> - **v3** (after migration): New structure `_research/`, name without duplication `{name}.md`
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
    folder = "_research"
    filename = f"{date}_{fid}_{slug}.md"  # Without duplication
else:
    folder = "research"
    filename = f"{date}_{fid}_{slug}-research.md"  # With duplication

artifact_path = f"{folder}/{filename}"
# v2: research/2024-12-23_F001_table-booking-research.md
# v3: _research/2024-12-23_F001_table-booking.md
```

### Updating .pipeline-state.json

After creating the report, update `active_pipelines[FID].artifacts` (v2):

**Example for v2 (default)**:
```json
{
  "naming_version": "v2",
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Table Booking",
      "stage": "RESEARCH",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md"
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
        "research": "_research/2024-12-23_F001_table-booking.md"
      }
    }
  }
}
```

---

## Quality Gates

### RESEARCH_DONE

| Criterion | Description |
|-----------|-------------|
| Code analysis | Existing code studied (for FEATURE) |
| Test analysis | Existing tests analyzed (for FEATURE) |
| Patterns | Architectural patterns identified |
| Constraints | Technical constraints defined |
| Recommendations | Recommendations formulated |
| File saved | Report saved in correct folder:<br>v2: `research/{YYYY-MM-DD}_{FID}_{slug}-research.md`<br>v3: `_research/{YYYY-MM-DD}_{FID}_{slug}.md` |

---

## Usage Examples

```bash
# After /aidd-analyze
/aidd-research
```

---

## RESEARCH_DONE Gate Checklist

> ⚠️ AI MUST create TodoWrite with these items.

- [ ] 🔴 Research report created in correct folder:
  - v2: `ai-docs/docs/research/{name}-research.md`
  - v3: `ai-docs/docs/_research/{name}.md`
- [ ] 🔴 Existing code analyzed
- [ ] 🔴 Existing tests analyzed (FEATURE)
- [ ] 🔴 Dependencies identified
- [ ] 🔴 `.pipeline-state.json` updated (gate: RESEARCH_DONE, artifact path matches naming_version)
- [ ] 🟡 Risks identified
- [ ] 🟡 Technical constraints described

---

## Next Step

After passing the `RESEARCH_DONE` gate:

```bash
/aidd-plan          # for CREATE
/aidd-plan-feature  # for FEATURE
```
