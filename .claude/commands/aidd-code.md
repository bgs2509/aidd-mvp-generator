---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**), Write(**), Bash(make :*), Bash(docker :*), Bash(pytest :*), Bash(git :*), Bash(python3 :*)
description: Generate code based on approved plan
---

> ⚠️ **ENFORCEMENT**: Before completing this command, AI MUST:
> 1. Find the "Gate Checklist" section at the end of this file
> 2. Create TodoWrite with ALL items (especially 🔴)
> 3. Complete ALL items and mark them completed
> 4. Command is complete ONLY when all 🔴 items are ✅
>
> Rules: `.aidd/CLAUDE.md` → "Executing /aidd-* commands"

# Command: /aidd-code

> Launches the Coder for code generation.
> **Pipeline State v2**: Parallel pipeline support.

---

## Syntax

```bash
/aidd-code
```

---

## Description

The `/aidd-code` command creates code based on the approved plan:
- Infrastructure (Docker, CI/CD)
- Data Services
- Business Services
- Tests

> **VERIFY BEFORE ACT**: Before creating files/directories, check their
> existence (see CLAUDE.md, "Critical Rules" section).

---

## Agent

**Coder** (`.claude/agents/coder.md`)

---

## File Reading Order

> **Principle**: First TP context, then framework instructions.
> **Details**: [docs/initialization.md](../../docs/initialization.md)

### Phase 1: Target Project Context

| # | File | Condition | Purpose |
|---|------|-----------|---------|
| 1 | `./CLAUDE.md` | If exists | Project specifics |
| 2 | `./.pipeline-state.json` | Required | Mode, stage, gates |
| 3 | `./ai-docs/docs/_analysis/*.md` | Required | Requirements |
| 4 | `./ai-docs/docs/_plans/mvp/*.md` | For CREATE | Architectural plan |
| 5 | `./ai-docs/docs/_plans/features/*.md` | For FEATURE | Feature plan |
| 6 | `./services/` | For FEATURE | Existing code |

### Phase 2: Auto-migration and Preconditions

> **Important**: Before executing the command, check `.pipeline-state.json` version
> and perform v1 → v2 migration if required (see `knowledge/pipeline/automigration.md`).

| Gate | Check (v2) |
|------|------------|
| `PLAN_APPROVED` | `active_pipelines[FID].gates.PLAN_APPROVED.passed == true` |
| `approved_by` | `active_pipelines[FID].gates.PLAN_APPROVED.approved_by != null` |

> **Note v2**: FID is determined by the current git branch (see algorithm below).

### Phase 3: Framework Instructions

| # | File | Purpose |
|---|------|---------|
| 7 | `.aidd/CLAUDE.md` | Framework rules |
| 8 | `.aidd/workflow.md` | Process and gates |
| 9 | `.aidd/conventions.md` | Code conventions |
| 10 | `.aidd/.claude/commands/generate.md` | This file |
| 11 | `.aidd/.claude/agents/coder.md` | Role instructions |

### Phase 4: Templates

| # | File | Condition |
|---|------|-----------|
| 12 | `.aidd/templates/services/*.md` | Service templates |
| 13 | `.aidd/templates/infrastructure/*.md` | Infrastructure |

---

## Modes

| Mode | Behavior |
|------|----------|
| **CREATE** | Creates complete project structure |
| **FEATURE** | Adds code to existing project |

---

## Preconditions

| Gate | Requirement |
|------|-------------|
| `PLAN_APPROVED` | Plan approved by user |

### Verification Algorithm (v2)

```python
def check_generate_preconditions() -> tuple[str, dict] | None:
    """
    Check preconditions for /generate.

    Returns:
        (fid, pipeline) or None on error

    Algorithm v2:
        1. Check .pipeline-state.json and migrate if needed
        2. Determine FID by git branch
        3. Check active_pipelines[fid].gates.PLAN_APPROVED
    """
    # 1. Check existence and version
    state_path = Path(".pipeline-state.json")
    if not state_path.exists():
        print("❌ Pipeline not initialized")
        print("   → First run /aidd-analyze")
        return None

    state = json.loads(state_path.read_text())

    # 2. Auto-migration v1 → v2
    if state.get("version") != "2.0":
        print("⚠️  v1 detected, performing migration...")
        subprocess.run(["python3", ".aidd/scripts/migrate_pipeline_state.py"])
        state = json.loads(state_path.read_text())

    # 3. Determine FID by current git branch
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    )
    current_branch = result.stdout.strip()

    active_pipelines = state.get("active_pipelines", {})
    fid, pipeline = None, None

    # Search by branch
    for f, p in active_pipelines.items():
        if p.get("branch") == current_branch:
            fid, pipeline = f, p
            break

    # If single feature — use it
    if not fid and len(active_pipelines) == 1:
        fid = list(active_pipelines.keys())[0]
        pipeline = active_pipelines[fid]

    if not fid:
        print("❌ Could not determine feature context")
        print(f"   Current branch: {current_branch}")
        print("   → Switch to feature branch: git checkout feature/F00X-...")
        return None

    # 4. Check PLAN_APPROVED
    gates = pipeline.get("gates", {})
    plan_gate = gates.get("PLAN_APPROVED", {})

    if not plan_gate.get("passed"):
        print(f"❌ PLAN_APPROVED gate not passed for {fid}")
        print("   → First run /aidd-plan or /aidd-plan-feature")
        return None

    if not plan_gate.get("approved_by"):
        print(f"⚠️  Plan {fid} requires explicit user approval")
        return None

    print(f"✓ Feature {fid}: {pipeline.get('title')}")
    print(f"  Branch: {pipeline.get('branch')}")
    return (fid, pipeline)
```

---

## Output Artifacts (in target project)

| Artifact | Path |
|----------|------|
| Services | `services/{name}_api/`, `services/{name}_data/` |
| Infrastructure | `docker-compose.yml`, `Makefile` |
| CI/CD | (optional, manual) |
| Tests | `services/*/tests/` |
| State | `.pipeline-state.json` (updated) |

> **Note (v2.4+)**:
> - Code generation does not depend on naming_version — services are always in `services/`
> - The command **reads** artifacts from previous stages (PRD, Research, Plan) respecting naming_version
> - Mode determined from `.pipeline-state.json → naming_version`

### Updating .pipeline-state.json (v2)

After code generation, update `active_pipelines[fid]`:

```python
def update_after_generate(state: dict, fid: str, services: list[str]):
    """
    Update state after successful code generation.

    v2: Update active_pipelines[fid], not current_feature
    """
    now = datetime.now().isoformat()

    pipeline = state["active_pipelines"][fid]

    # Update IMPLEMENT_OK gate
    pipeline["gates"]["IMPLEMENT_OK"] = {
        "passed": True,
        "passed_at": now
    }

    # Update stage
    pipeline["stage"] = "REVIEW"

    # Add services
    pipeline["services"] = services

    state["updated_at"] = now
```

```json
{
  "version": "2.0",
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "stage": "REVIEW",
      "gates": {
        "PRD_READY": { "passed": true, "passed_at": "..." },
        "RESEARCH_DONE": { "passed": true, "passed_at": "..." },
        "PLAN_APPROVED": { "passed": true, "passed_at": "...", "approved_by": "user" },
        "IMPLEMENT_OK": { "passed": true, "passed_at": "2024-12-23T12:00:00Z" }
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md",
        "plan": "architecture/2024-12-23_F001_table-booking-plan.md"
      },
      "services": ["booking_api", "booking_data"]
    }
  }
}
```

> **Note**: Services and infrastructure files do not follow
> the FID naming pattern, since they are code, not documents.

---

## Quality Gates

### IMPLEMENT_OK

| Criterion | Description |
|-----------|-------------|
| Code | Written according to plan |
| Structure | DDD/Hexagonal followed |
| Types | Type hints everywhere |
| Documentation | Docstrings in Russian |
| Tests | Smoke tests pass, others per TRQ requirements |

---

## Generation Order

```
1. Infrastructure (docker-compose, Makefile, CI/CD)
2. Data Service (models, repositories, API)
3. Business API (services, API, HTTP clients)
4. Background Worker (if needed)
5. Telegram Bot (if needed)
6. Tests
```

---

## Usage Examples

```bash
# After plan approval
/generate
```

---

## IMPLEMENT_OK Gate Checklist

> ⚠️ AI MUST create TodoWrite with these items.

- [ ] 🔴 All code generated according to plan
- [ ] 🔴 All services created in `services/`
- [ ] 🔴 Smoke tests implemented (TRQ-001..TRQ-004)
- [ ] 🔴 Smoke tests pass
- [ ] 🟡 Unit tests implemented (TRQ-005, if required)
- [ ] 🟡 Integration tests implemented (TRQ-006, if required)
- [ ] ⚪ E2E tests implemented (TRQ-007, if required)
- [ ] 🔴 Type hints added (100%)
- [ ] 🔴 `.pipeline-state.json` updated (gate: IMPLEMENT_OK)
- [ ] 🟡 Quality Cascade (17 checks) passed
- [ ] 🟡 `docker-compose.yml` updated

---

## Next Step

After passing the `IMPLEMENT_OK` gate:

```bash
/review
```
