---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(mkdir :*), Bash(git :*), Bash(python3 :*)
argument-hint: "[project or feature idea description]"
description: Create PRD document from user's idea
---

> ⚠️ **ENFORCEMENT**: Before completing this command, AI MUST:
> 1. Find the "Gate Checklist" section at the end of this file
> 2. Create TodoWrite with ALL items (especially 🔴)
> 3. Complete ALL items and mark them completed
> 4. Command is complete ONLY when all 🔴 items are ✅
>
> Rules: `.aidd/CLAUDE.md` → "Executing /aidd-* commands"

# Command: /aidd-analyze

> Launches the Analyst to create a PRD document from an idea.
> **Pipeline State v2**: Parallel pipeline support.

---

## Syntax

```bash
/aidd-analyze "Project or feature idea description"
```

---

## Description

The `/aidd-analyze` command is the entry point into the AIDD-MVP pipeline. It transforms
a text description of an idea into a structured PRD (Product Requirements Document).

> **VERIFY BEFORE ACT**: Before creating files/directories, check their
> existence (see CLAUDE.md, "Critical Rules" section).

---

## Agent

**Analyst** (`.claude/agents/analyst.md`)

---

## Testing Questions

After gathering functional requirements, ask the user:

1. **Unit tests**: "Do you need unit tests (coverage ≥ {threshold} with mocks)?"
   - Yes → TRQ-005 = required
   - No → TRQ-005 = not required

2. **Integration tests**: "Do you need integration tests for critical pipelines (with testcontainers for DBs from PRD)?"
   - Yes → TRQ-006 = required, clarify which pipelines
   - No → TRQ-006 = not required

3. **E2E tests**: "Do you need E2E tests (end-to-end cross-service scenarios)?"
   - Yes → TRQ-007 = required, clarify scenarios
   - No → TRQ-007 = not required

**Smoke tests (TRQ-001..TRQ-004) — ALWAYS required, do not ask.**

---

## File Reading Order

> **Principle**: First TP context, then framework instructions.
> **Details**: [docs/initialization.md](../../docs/initialization.md)

### Phase 1: Target Project Context

| # | File | Condition | Purpose |
|---|------|-----------|---------|
| 1 | `./CLAUDE.md` | If exists | Project specifics |
| 2 | `./.pipeline-state.json` | If exists | Mode, stage, gates |
| 3 | `./ai-docs/docs/_analysis/` | If exists | Existing PRD (for FEATURE) |

### Phase 2: Preconditions and Auto-migration

> **Important**: Before executing the command, check `.pipeline-state.json` version
> and perform v1 → v2 migration if required.

```python
# Auto-migration (execute at command start)
def ensure_v2_state():
    """
    Check and migrate .pipeline-state.json to v2.

    Details: knowledge/pipeline/automigration.md
    """
    state_path = Path(".pipeline-state.json")

    if not state_path.exists():
        return None  # Will create new

    state = json.loads(state_path.read_text())

    if state.get("version") != "2.0":
        print("⚠️  Detected .pipeline-state.json v1.0")
        print("    Performing automatic migration...")

        # Call migration script
        result = subprocess.run(
            ["python3", ".aidd/scripts/migrate_pipeline_state.py"],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            print("    ✓ Migration complete")
            state = json.loads(state_path.read_text())
        else:
            print(f"    ❌ Migration error: {result.stderr}")
            return None

    return state
```

No other preconditions — `/aidd-analyze` is the first pipeline stage.

### Phase 3: Framework Instructions

| # | File | Purpose |
|---|------|---------|
| 4 | `.aidd/CLAUDE.md` | Framework rules |
| 5 | `.aidd/workflow.md` | Process and gates |
| 6 | `.aidd/.claude/commands/aidd-analyze.md` | This file |
| 7 | `.aidd/.claude/agents/analyst.md` | Role instructions |

### Phase 4: Templates

| # | File | Condition |
|---|------|-----------|
| 8 | `.aidd/templates/documents/prd-template.md` | If PRD does not exist |

---

## Bootstrap: Verification and Initialization

> **Important**: Before creating the PRD, the `/aidd-analyze` command automatically checks
> environment readiness (Bootstrap Pipeline). On errors — suggests `/aidd-init`.

### Bootstrap Check Algorithm

```python
def auto_bootstrap() -> bool:
    """
    Automatic check and initialization before /aidd-analyze.

    Returns:
        True if BOOTSTRAP_READY, False if /aidd-init is needed
    """
    # 1. Check if BOOTSTRAP_READY already passed
    if Path(".pipeline-state.json").exists():
        state = read_json(".pipeline-state.json")
        # v2: BOOTSTRAP_READY in global_gates
        # v1: BOOTSTRAP_READY in gates (for backward compatibility)
        global_gates = state.get("global_gates", {})
        legacy_gates = state.get("gates", {})
        bootstrap_gate = global_gates.get("BOOTSTRAP_READY") or legacy_gates.get("BOOTSTRAP_READY")
        if bootstrap_gate and bootstrap_gate.get("passed"):
            return True  # Already initialized

    # 2. Run environment checks
    checks = {
        "git": run("git rev-parse --git-dir").ok,
        "framework": Path(".aidd/CLAUDE.md").exists(),
        "python": check_python_version() >= (3, 11),
        "docker": run("docker --version").ok,
    }

    # 3. If all checks pass — auto-initialize
    if all(checks.values()):
        # Create structure
        create_directory_structure()
        # Create .pipeline-state.json
        create_pipeline_state()
        # Create CLAUDE.md
        create_project_claude_md()
        return True

    # 4. If errors — report and suggest /aidd-init
    failed = [k for k, v in checks.items() if not v]
    print(f"❌ Checks failed: {failed}")
    print("→ Run /aidd-init for diagnostics and fixing")
    return False
```

### Actions on First Run

> **VERIFY BEFORE ACT**: Before creating directories and files, check their existence.

```bash
# 1. Determine mode
if [ -d "services" ] || [ -f "docker-compose.yml" ]; then
    MODE="FEATURE"
else
    MODE="CREATE"
fi

# 2. VERIFY: Check existing artifact structure
if [ -d "ai-docs/docs" ]; then
    existing_count=$(ls -d ai-docs/docs/*/ 2>/dev/null | wc -l)
    echo "✓ Structure ai-docs/docs/ already exists ($existing_count directories)"
fi

# 3. ACT: Create only missing directories
for dir in prd architecture plans reports research; do
    if [ ! -d "ai-docs/docs/$dir" ]; then
        mkdir -p "ai-docs/docs/$dir"
        echo "✓ Created directory: ai-docs/docs/$dir"
    fi
done

# 4. Initialize pipeline state (if doesn't exist)
if [ ! -f ".pipeline-state.json" ]; then
    echo '{"project_name":"","mode":"'$MODE'","current_stage":1,"gates":{"BOOTSTRAP_READY":{"passed":true}}}' > .pipeline-state.json
    echo "✓ Created .pipeline-state.json"
else
    echo "✓ .pipeline-state.json already exists"
fi

# 5. Create CLAUDE.md if doesn't exist
if [ ! -f "CLAUDE.md" ]; then
    echo "# Project\n\nSee .aidd/CLAUDE.md" > CLAUDE.md
    echo "✓ Created CLAUDE.md"
else
    echo "✓ CLAUDE.md already exists"
fi
```

### Preconditions

| Gate | Check |
|------|-------|
| `BOOTSTRAP_READY` | Auto-check on `/aidd-analyze` launch |

If `BOOTSTRAP_READY` not passed:
```
❌ Environment not ready. Errors:
- framework: Framework .aidd/ not found
- docker: Docker not installed

→ Run /aidd-init for detailed diagnostics
```

---

## Modes

| Mode | Condition | Behavior |
|------|-----------|----------|
| **CREATE** | No `services/` or `docker-compose.yml` | Creates full PRD for new MVP |
| **FEATURE** | Existing code present | Creates FEATURE_PRD for new function |

---

## Preconditions

None — this is the first pipeline stage.

---

## Output Artifacts (in target project)

| Artifact | Path (v2) | Path (v3) |
|----------|-----------|-----------|
| PRD document | `ai-docs/docs/_analysis/{YYYY-MM-DD}_{FID}_{slug}-prd.md` | `ai-docs/docs/_analysis/{YYYY-MM-DD}_{FID}_{slug}.md` |
| Feature registry | `ai-docs/docs/FEATURES.md` | `ai-docs/docs/FEATURES.md` |
| State | `.pipeline-state.json` | `.pipeline-state.json` |

> **Note (v2.4+)**:
> - **v2** (default): Old structure `prd/`, name with duplication `{name}-prd.md`
> - **v3** (after migration): New structure `_analysis/`, name without duplication `{name}.md`
> - Mode determined from `.pipeline-state.json → naming_version`
> - Migration: `python .aidd/scripts/migrate-naming-v3.py`

---

## Feature ID (FID) Generation

> **Specification**: [docs/artifact-naming.md](../../docs/artifact-naming.md)

### FID Assignment Algorithm (v2: active_pipelines)

```python
def create_feature(state: dict, idea: str) -> dict:
    """
    Creates a new feature with unique FID in active_pipelines.

    Args:
        state: Contents of .pipeline-state.json (v2)
        idea: Idea description from user

    Returns:
        dict: New feature data

    Changes v2:
        - Feature created in active_pipelines[fid] instead of current_feature
        - Gates isolated in active_pipelines[fid].gates
        - Git branch feature/{fid}-{slug} is created
    """
    # 1. Generate FID
    next_id = state.get("next_feature_id", 1)
    fid = f"F{next_id:03d}"

    # 2. Create slug from name
    # "Restaurant table booking system" → "table-booking"
    slug = generate_slug(idea)  # kebab-case, ≤30 chars

    # 3. Get current date
    date = datetime.now().strftime("%Y-%m-%d")

    # 4. Determine naming_version and artifact structure
    naming_version = state.get("naming_version", "v2")

    if naming_version == "v3":
        folder = "_analysis"
        filename = f"{date}_{fid}_{slug}.md"  # Without duplication
    else:
        folder = "prd"
        filename = f"{date}_{fid}_{slug}-prd.md"  # With duplication

    artifact_path = f"{folder}/{filename}"

    # 5. Form branch name
    branch = f"feature/{fid}-{slug}"

    # 6. Create git branch for feature
    subprocess.run(["git", "checkout", "-b", branch], check=True)
    print(f"✓ Created branch: {branch}")

    # 7. Create feature entry in active_pipelines (v2)
    state["active_pipelines"] = state.get("active_pipelines", {})
    state["active_pipelines"][fid] = {
        "branch": branch,
        "name": slug,
        "title": extract_title(idea),
        "stage": "IDEA",
        "created": date,
        "gates": {
            "PRD_READY": {"passed": False, "passed_at": None, "artifact": None},
            "RESEARCH_DONE": {"passed": False, "passed_at": None},
            "PLAN_APPROVED": {"passed": False, "passed_at": None, "artifact": None, "approved_by": None},
            "IMPLEMENT_OK": {"passed": False, "passed_at": None},
            "REVIEW_OK": {"passed": False, "passed_at": None, "artifact": None},
            "QA_PASSED": {"passed": False, "passed_at": None, "artifact": None, "coverage": None},
            "ALL_GATES_PASSED": {"passed": False, "passed_at": None, "artifact": None},
            "DEPLOYED": {"passed": False, "passed_at": None}
        },
        "artifacts": {}
    }

    # 8. Add to feature registry
    state["features_registry"] = state.get("features_registry", {})
    state["features_registry"][fid] = {
        "name": slug,
        "title": extract_title(idea),
        "created": date,
        "status": "IN_PROGRESS",
        "services": []
    }

    # 9. Increment counter
    state["next_feature_id"] = next_id + 1

    # 10. Update updated_at
    state["updated_at"] = datetime.now().isoformat()

    return state["active_pipelines"][fid]
```

### Getting Current Feature Context

```python
def get_current_feature_context(state: dict) -> tuple[str, dict] | None:
    """
    Determine current feature by git branch.

    Returns:
        (fid, pipeline) or None if not on a feature branch

    Algorithm:
        1. Get current git branch
        2. Find FID in active_pipelines by branch
        3. If branch not found but only one active feature — use it
    """
    # Get current branch
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    )
    current_branch = result.stdout.strip()

    active_pipelines = state.get("active_pipelines", {})

    # Search by branch
    for fid, pipeline in active_pipelines.items():
        if pipeline.get("branch") == current_branch:
            return (fid, pipeline)

    # If only one active feature — use it
    if len(active_pipelines) == 1:
        fid = list(active_pipelines.keys())[0]
        return (fid, active_pipelines[fid])

    # Not in feature context
    return None
```

### File Name Format

**v2 (default, with duplication)**:
```
{YYYY-MM-DD}_{FID}_{slug}-prd.md

Examples:
- 2024-12-23_F001_table-booking-prd.md
- 2024-12-23_F002_email-notify-prd.md
```

**v3 (after migration, without duplication)**:
```
{YYYY-MM-DD}_{FID}_{slug}.md

Examples:
- 2024-12-23_F001_table-booking.md
- 2024-12-23_F002_email-notify.md
```

### Updating FEATURES.md

After creating the PRD, update the feature registry:

**v2 (default)**:
```markdown
# In ai-docs/docs/FEATURES.md add a row:

| F001 | Table Booking | IN_PROGRESS | 2024-12-23 | — | `prd/2024-12-23_F001_table-booking-prd.md` |
```

**v3 (after migration)**:
```markdown
# In ai-docs/docs/FEATURES.md add a row:

| F001 | Table Booking | IN_PROGRESS | 2024-12-23 | — | `_analysis/2024-12-23_F001_table-booking.md` |
```

### Updating .pipeline-state.json (v2)

**Example for v2 (default)**:
```json
{
  "version": "2.0",
  "naming_version": "v2",
  "global_gates": {
    "BOOTSTRAP_READY": { "passed": true, "passed_at": "2024-12-23T09:00:00Z" }
  },
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Restaurant Table Booking System",
      "stage": "IDEA",
      "created": "2024-12-23",
      "gates": {
        "PRD_READY": {
          "passed": true,
          "passed_at": "2024-12-23T10:30:00Z",
          "artifact": "prd/2024-12-23_F001_table-booking-prd.md"
        },
        "RESEARCH_DONE": { "passed": false, "passed_at": null },
        "PLAN_APPROVED": { "passed": false, "passed_at": null, "artifact": null }
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md"
      }
    }
  },
  "features_registry": {
    "F001": {
      "name": "table-booking",
      "title": "Restaurant Table Booking System",
      "created": "2024-12-23",
      "status": "IN_PROGRESS",
      "services": []
    }
  },
  "next_feature_id": 2
}
```

**Example for v3 (after migration)**:
```json
{
  "version": "2.0",
  "naming_version": "v3",
  "gate_aliases": {
    "PRD_READY": "ANALYSIS_READY"
  },
  "active_pipelines": {
    "F001": {
      "gates": {
        "PRD_READY": {
          "passed": true,
          "artifact": "_analysis/2024-12-23_F001_table-booking.md"
        }
      },
      "artifacts": {
        "prd": "_analysis/2024-12-23_F001_table-booking.md"
      }
    }
  }
}
```

> **Note v2**: Gates are now isolated in `active_pipelines[FID].gates`,
> not in the shared `gates`. This allows running multiple features in parallel.

---

## Quality Gates

### PRD_READY

| Criterion | Description |
|-----------|-------------|
| All sections | PRD fully completed |
| Requirement IDs | Each requirement has a unique ID |
| Priorities | Must/Should/Could for all requirements |
| Acceptance criteria | Defined for all FRs |
| Testing | Section 6.5 filled, TRQ-001..004 required |
| Open questions | No blocking questions |
| State | `active_pipelines[FID].gates.PRD_READY` = true |

### Gate Update (v2)

```python
def pass_prd_ready_gate(state: dict, fid: str, artifact_path: str):
    """
    Mark PRD_READY as passed for the specified feature.

    Args:
        artifact_path: Path to PRD (must respect naming_version)
                      v2: "prd/{name}-prd.md"
                      v3: "_analysis/{name}.md"

    v2: Gates updated in active_pipelines[fid].gates
    """
    now = datetime.now().isoformat()

    state["active_pipelines"][fid]["gates"]["PRD_READY"] = {
        "passed": True,
        "passed_at": now,
        "artifact": artifact_path
    }

    state["active_pipelines"][fid]["stage"] = "RESEARCH"
    state["active_pipelines"][fid]["artifacts"]["prd"] = artifact_path

    state["updated_at"] = now
```

---

## Usage Examples

### Creating a New MVP

```bash
/aidd-analyze "Create a restaurant table booking service.
Users can search restaurants by cuisine and location,
view available tables and book for the desired time.
Restaurants receive booking notifications in Telegram."
```

### Adding a Feature

```bash
/aidd-analyze "Add email notification system for booking confirmation
and reminder 2 hours before the visit."
```

### Brief Description

```bash
/aidd-analyze "Personal finance tracking service with expense categorization"
```

---

## PRD_READY Gate Checklist

> ⚠️ AI MUST create TodoWrite with these items.

- [ ] 🔴 PRD document created in correct folder:
  - v2: `ai-docs/docs/_analysis/{name}-prd.md`
  - v3: `ai-docs/docs/_analysis/{name}.md`
- [ ] 🔴 Section 6.5 "Testing Requirements" filled
- [ ] 🔴 TRQ-001..TRQ-004 (smoke) marked as required
- [ ] 🔴 All FR-* requirements defined
- [ ] 🔴 NFR-* requirements defined
- [ ] 🔴 `.pipeline-state.json` updated (gate: PRD_READY, artifact path matches naming_version)
- [ ] 🟡 Clarifying questions asked to user
- [ ] 🟡 User answered questions about unit/integration/e2e
- [ ] 🟡 Scope boundaries defined (in/out of scope)

---

## Next Step

After passing the `PRD_READY` gate:

```bash
/aidd-research
```
