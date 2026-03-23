# Git Integration for Parallel Pipelines

**Note:** This document may contain outdated command references `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Current commands: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Version**: Pipeline State v2
> **Related files**:
> - `scripts/git_helpers.py` -- command line utilities
> - `knowledge/pipeline/state-v2.md` -- v2 specification
> - `knowledge/pipeline/automigration.md` -- automigration

---

## Concept

Each feature is developed in a separate git branch. This ensures:

- **Isolation**: Changes in one feature do not affect others
- **Parallelism**: Multiple features can be developed simultaneously
- **Traceability**: Change history is tied to a specific feature
- **Safety**: Merge through Pull Request with review

### Parallel Development Rules

```
┌─────────────────────────────────────────────────────────────────┐
│  ✅ You CAN start a new feature even if the previous one         │
│     is not completed                                             │
├─────────────────────────────────────────────────────────────────┤
│  • Features are isolated in separate git branches                │
│  • Gates are isolated in active_pipelines[FID].gates             │
│  • No limit on the number of active features                     │
│                                                                 │
│  ⚠️  RECOMMENDED to track conflicts:                             │
│  • Use: python3 scripts/git_helpers.py conflicts F042 F043       │
│  • Avoid changing the same files in different features           │
│  • On conflicts -- complete one feature before merging another   │
└─────────────────────────────────────────────────────────────────┘
```

**Legitimate scenario examples**:
- F042 (OAuth) development stalled -> start F043 (Payments)
- F042 in review stage -> develop F043 in parallel
- Multiple independent features in different modules

---

## Branch Naming

### Format

```
feature/{FID}-{slug}
```

### Examples

| FID | Slug | Branch |
|-----|------|-------|
| F001 | table-booking | `feature/F001-table-booking` |
| F042 | oauth-auth | `feature/F042-oauth-auth` |
| F043 | payments | `feature/F043-payments` |

### Slug Rules

- Latin letters, digits, and hyphens only
- No spaces or special characters
- Maximum 30 characters
- kebab-case (words separated by hyphens)

---

## Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PARALLEL WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  main                                                                   │
│    │                                                                    │
│    ├──┬── feature/F042-oauth ─────────────────────────▶ merge           │
│    │  │     ├── /aidd-analyze      <- Creates branch automatically      │
│    │  │     ├── /aidd-research                                          │
│    │  │     ├── /aidd-plan                                              │
│    │  │     ├── /aidd-code                                              │
│    │  │     └── /aidd-validate ─────────────▶ DEPLOYED                  │
│    │  │                                                                 │
│    │  └── feature/F043-payments ──────────────────────▶ merge           │
│    │        ├── /aidd-analyze      (in parallel with F042!)             │
│    │        ├── /aidd-research                                          │
│    │        ├── ...                                                     │
│    │        └── /aidd-validate ─────────────▶ DEPLOYED                  │
│    │                                                                    │
│    ▼                                                                    │
│  main (with both features)                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Auto-creating Branches

### When running `/aidd-analyze`

The `/aidd-analyze` command automatically creates a branch:

```python
# From aidd-idea.md, function create_feature():

# 5. Create git branch for the feature
branch = f"feature/{fid}-{slug}"
subprocess.run(["git", "checkout", "-b", branch], check=True)
print(f"✓ Branch created: {branch}")
```

### Result

```bash
$ /aidd-analyze "Add OAuth authorization"

✓ Branch created: feature/F042-oauth-auth
✓ Feature F042 added to active_pipelines
✓ PRD created: ai-docs/docs/_analysis/2025-12-25_F042_oauth-auth-prd.md
```

---

## Feature Context Detection

### Algorithm

```python
def get_current_feature_context(state: dict) -> tuple[str, dict] | None:
    """
    1. Get current git branch
    2. Find FID in active_pipelines by branch
    3. If not found -- extract FID from branch name
    4. If one active feature -- use it
    5. Otherwise -- return None (explicit specification required)
    """
```

### Examples

```bash
# Branch feature/F042-oauth -> automatically F042
$ git checkout feature/F042-oauth
$ /aidd-code
# -> Generates code for F042

# Branch main, one active feature -> it is used
$ git checkout main
$ /aidd-research
# -> ⚠️ Using the only active feature: F042

# Branch main, multiple features -> error
$ git checkout main
$ /aidd-code
# -> ❌ Multiple active features. Switch to a feature branch:
#   git checkout feature/F042-oauth
#   git checkout feature/F043-payments
```

---

## Git Helpers

### Script `scripts/git_helpers.py`

```bash
# Show current context
python3 scripts/git_helpers.py context

# Create branch
python3 scripts/git_helpers.py branch F042 oauth-auth

# Check conflicts between features
python3 scripts/git_helpers.py conflicts F042 F043

# Complete feature and prepare for merge
python3 scripts/git_helpers.py merge F042
```

### Command `context`

```
$ python3 scripts/git_helpers.py context

✓ Current feature: F042
  Title: OAuth authorization
  Branch: feature/F042-oauth-auth
  Stage: IMPLEMENT
  Gates passed: PRD_READY, RESEARCH_DONE, PLAN_APPROVED
```

### Command `conflicts`

```
$ python3 scripts/git_helpers.py conflicts F042 F043

┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ WARNING: Potential conflicts detected                        │
├─────────────────────────────────────────────────────────────────┤
│  Features F042 and F043 edit the same files:                     │
│  • services/auth_api/domain/models.py                           │
│  • docker-compose.yml                                           │
│                                                                 │
│  Recommendations:                                                │
│  1. Complete and merge one feature before continuing the other  │
│  2. Separate changes into different modules                     │
│  3. Coordinate merge with the team                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Merge Strategy

### Completing a Feature

After passing all gates and `/aidd-validate`:

```bash
# 1. Complete the feature (moves to features_registry)
python3 scripts/git_helpers.py merge F042

# 2. Switch to main
git checkout main

# 3. Perform merge
git merge feature/F042-oauth-auth

# 4. Resolve conflicts in .pipeline-state.json (if any)
# AI automatically merges states

# 5. Push
git push origin main
```

### Merging `.pipeline-state.json`

Branch merge conflicts in `.pipeline-state.json` are resolved automatically:

```python
def merge_pipeline_states(main_state, feature_state, fid):
    """
    1. Move completed feature to features_registry
    2. Remove from active_pipelines
    3. Take maximum of next_feature_id
    4. Update timestamp
    """
```

### Merge Example

**main/.pipeline-state.json:**
```json
{
  "active_pipelines": {
    "F043": { "stage": "RESEARCH" }
  },
  "next_feature_id": 44,
  "features_registry": {}
}
```

**feature/F042-oauth/.pipeline-state.json:**
```json
{
  "active_pipelines": {
    "F042": { "stage": "DEPLOYED", "gates": { "DEPLOYED": { "passed": true } } }
  },
  "next_feature_id": 43,
  "features_registry": {}
}
```

**After merge:**
```json
{
  "active_pipelines": {
    "F043": { "stage": "RESEARCH" }
  },
  "next_feature_id": 44,
  "features_registry": {
    "F042": {
      "status": "DEPLOYED",
      "deployed": "2025-12-25"
    }
  }
}
```

---

## Conflict Detection

### Automatic Check

AI automatically checks for conflicts when:
- Running `/aidd-code` (if there are other active features)
- Running `/aidd-validate` (before completion)

### Manual Check

```bash
# Get list of changed files in branch
git diff --name-only main...feature/F042-oauth

# Compare with another feature
python3 scripts/git_helpers.py conflicts F042 F043
```

### Recommendations for Conflicts

```
┌─────────────────────────────────────────────────────────────────┐
│  Features F042 and F043 edit the same files -> Actions:          │
├─────────────────────────────────────────────────────────────────┤
│  1. Assess conflict severity                                     │
│  2. If conflicts are critical:                                   │
│     -> Complete and merge one feature before continuing another  │
│  3. If conflicts are minor:                                      │
│     -> Continue development, resolve conflicts at merge          │
│  4. Alternative:                                                 │
│     -> Extract shared code into a separate module               │
└─────────────────────────────────────────────────────────────────┘
```

**Resolution strategies**:
1. **Prioritize features**: Complete the more critical feature first
2. **Separate changes**: Extract shared code into a separate module
3. **Coordination**: In team work, agree on merge order
4. **Frequent sync**: Regularly synchronize feature branch with main
5. **Continue work**: If conflicts are minor, continue both features

---

## Integration with Commands

### Context Check in Every Command

All `/aidd-*` commands check the feature context:

```python
def check_preconditions():
    state = ensure_v2_state()

    # Determine FID by current git branch
    fid, pipeline = get_current_feature_context(state)
    if not fid:
        print("❌ Could not determine feature context")
        print("   -> Switch to a feature branch: git checkout feature/FXXX-...")
        return None

    print(f"✓ Feature {fid}: {pipeline.get('title')}")
    return (fid, pipeline)
```

### Gates Are Isolated Per Feature

```python
# v2: Each feature has its own gates
gates = state["active_pipelines"][fid]["gates"]

if not gates.get("PLAN_APPROVED", {}).get("passed"):
    print(f"❌ PLAN_APPROVED not passed for {fid}")
```

---

## Troubleshooting

### Branch Not Detected

```
❌ Could not determine feature context
```

**Solution**: Switch to the feature branch:
```bash
git checkout feature/F042-oauth-auth
```

### Multiple Active Features

```
❌ Multiple active features. Specify context.
```

**Solution**: Either switch to the branch or use explicit specification:
```bash
git checkout feature/F042-oauth-auth
# or
/aidd-code --feature=F042  # if supported
```

### Branch Already Exists

```
❌ Branch feature/F042-oauth-auth already exists
```

**Solution**: Use the existing branch:
```bash
git checkout feature/F042-oauth-auth
```

---

## See Also

- `knowledge/pipeline/state-v2.md` -- Pipeline State v2 Specification
- `knowledge/pipeline/automigration.md` -- Automigration v1 -> v2
- `contributors/2025-12-25-aidd-enhancement-parallel-pipelines.md` -- Design document
