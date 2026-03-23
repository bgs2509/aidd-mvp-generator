# Naming v3: Implementation Guide for Commands

> **Status**: Phase 2.3 Complete (Migration mode active)
> **Date**: 2026-01-19
> **Completed**: 2026-01-19

## Overview

Each command must support both modes:
- **v2** (old structure): `prd/`, `architecture/`, `plans/`, `reports/`
- **v3** (new structure): `_analysis/`, `_research/`, `_plans/mvp/`, `_plans/features/`, `_validation/`

## Algorithm for Commands

### 1. Read naming_version from .pipeline-state.json

```python
def get_artifact_folder(state: dict, artifact_type: str) -> str:
    """
    Determine the artifact folder path based on naming_version.

    Args:
        state: Contents of .pipeline-state.json
        artifact_type: Artifact type ("prd", "plan", "validation", etc.)

    Returns:
        Folder path (relative to ai-docs/docs/)
    """
    naming_version = state.get("naming_version", "v2")

    # Mapping for v2 → v3
    folder_map = {
        "v2": {
            "prd": "prd",
            "research": "research",
            "plan_mvp": "architecture",
            "plan_feature": "plans",
            "validation": "reports",
        },
        "v3": {
            "prd": "_analysis",
            "research": "_research",
            "plan_mvp": "_plans/mvp",
            "plan_feature": "_plans/features",
            "validation": "_validation",
        },
    }

    return folder_map[naming_version].get(artifact_type, artifact_type)
```

### 2. Use in Commands

```python
# Example for /aidd-analyze (creates PRD)
state = json.loads(Path(".pipeline-state.json").read_text())
folder = get_artifact_folder(state, "prd")
# folder = "prd" (v2) or "_analysis" (v3)

artifact_path = f"ai-docs/docs/{folder}/{date}_{FID}_{slug}-prd.md"  # v2
# OR
artifact_path = f"ai-docs/docs/{folder}/{date}_{FID}_{slug}.md"  # v3 (no duplication)
```

## Commands to Update

| # | Command | Artifact (v2) | Artifact (v3) | Status | Commit |
|---|---------|--------------|--------------|--------|--------|
| 1 | `/aidd-analyze` | `prd/{name}-prd.md` | `_analysis/{name}.md` | DONE | ea568ca |
| 2 | `/aidd-research` | `research/{name}-research.md` | `_research/{name}.md` | DONE | c0ec969 |
| 3 | `/aidd-plan` | `architecture/{name}-plan.md` | `_plans/mvp/{name}.md` | DONE | f9c810e |
| 4 | `/aidd-plan-feature` | `plans/{name}-plan.md` | `_plans/features/{name}.md` | DONE | 6e84bbc |
| 5 | `/aidd-code` | `services/` | `services/` | No changes | — |
| 6 | `/aidd-validate` | `reports/{name}-completion.md` | `_validation/{name}.md` | DONE | e56630d |

## Template for Updating a Command

### Step 1: Find the artifact creation section

Look for lines like:
```python
artifact_path = f"ai-docs/docs/_analysis/{date}_{FID}_{slug}-prd.md"
```

### Step 2: Replace with dynamic selection

```python
# 1. Read .pipeline-state.json
state = json.loads(Path(".pipeline-state.json").read_text())

# 2. Determine naming_version
naming_version = state.get("naming_version", "v2")

# 3. Select folder
if naming_version == "v3":
    folder = "_analysis"
    filename = f"{date}_{FID}_{slug}.md"  # No duplication
else:
    folder = "prd"
    filename = f"{date}_{FID}_{slug}-prd.md"  # With duplication

artifact_path = f"ai-docs/docs/{folder}/{filename}"
```

### Step 3: Update comments

```markdown
## Output Artifacts (in Target Project)

| Mode | Artifact | Path |
|------|----------|------|
| v2 | PRD | `prd/{YYYY-MM-DD}_{FID}_{slug}-prd.md` |
| v3 | Analysis | `_analysis/{YYYY-MM-DD}_{FID}_{slug}.md` |

> **Note**: Mode is determined from `.pipeline-state.json → naming_version`
```

## Testing

### Test v2 (backward compatible)

```bash
# 1. Create project with v2
/aidd-init
# → .pipeline-state.json: naming_version = "v2"

# 2. Create PRD
/aidd-analyze "test idea"
# → ai-docs/docs/_analysis/2026-01-19_F001_test-idea-prd.md
```

### Test v3 (after migration)

```bash
# 1. Migrate project
python .aidd/scripts/migrate-naming-v3.py

# 2. Check naming_version
cat .pipeline-state.json | grep naming_version
# → "naming_version": "v3"

# 3. Create new feature
/aidd-analyze "new feature"
# → ai-docs/docs/_analysis/2026-01-19_F002_new-feature.md
```

## Checklist for Each Command

- [ ] Read `.pipeline-state.json`
- [ ] Get `naming_version`
- [ ] Determine artifact folder via `get_artifact_folder()`
- [ ] Determine file name (with/without duplication)
- [ ] Create artifact in the correct folder
- [ ] Update `artifacts` in pipeline state
- [ ] Update command documentation

## Update Priority

1. **Critical** (create artifacts): `/aidd-analyze`, `/aidd-plan`, `/aidd-validate`
2. **Important**: `/aidd-research`, `/aidd-plan-feature`
3. **Low**: `/aidd-code` (unchanged)

## See Also

- [Migration plan](../../../.claude/plans/idempotent-drifting-wirth.md)
- [Migration script](../scripts/migrate-naming-v3.py)
- [Pipeline State v2](../knowledge/pipeline/state-v2.md)
