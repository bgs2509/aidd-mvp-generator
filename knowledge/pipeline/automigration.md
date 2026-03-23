# Pipeline State Automigration

> **For AI agents**: This document contains instructions for automatic `.pipeline-state.json` migration.

---

## When to Execute

**WHEN RUNNING ANY SLASH COMMAND** (except `/aidd-init`):

1. Read `.pipeline-state.json`
2. Check the `version` field
3. If `version != "2.0"` -- perform migration

---

## Check Algorithm

```python
import json
from pathlib import Path

def check_and_migrate() -> dict | None:
    """
    Check state version and migrate if needed.

    Returns:
        State in v2 format or None if file not found
    """
    state_path = Path(".pipeline-state.json")

    if not state_path.exists():
        return None

    state = json.loads(state_path.read_text())

    if state.get("version") != "2.0":
        print("⚠️  Detected .pipeline-state.json v1.0")
        print("    Performing automatic migration...")

        # Call migration script
        import subprocess
        result = subprocess.run(
            ["python", ".aidd/scripts/migrate_pipeline_state.py"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("    ✓ Migration completed")
            # Re-read updated file
            state = json.loads(state_path.read_text())
        else:
            print("    ❌ Migration error:")
            print(result.stderr)
            return None

    return state
```

---

## For AI Agent (Text Instructions)

### Step 1: Version Check

```bash
# Read file and check version
cat .pipeline-state.json | grep '"version"'
```

Expected result: `"version": "2.0"`

### Step 2: Migration (if version != 2.0)

```bash
# Show migration plan
python .aidd/scripts/migrate_pipeline_state.py --dry-run

# Perform migration
python .aidd/scripts/migrate_pipeline_state.py
```

### Step 3: Continue Command Execution

After successful migration, continue executing the requested command.

---

## What the Migration Does

1. **Creates a backup**: `.pipeline-state.json.v1.backup`

2. **Moves global gates**:
   ```
   gates.BOOTSTRAP_READY -> global_gates.BOOTSTRAP_READY
   ```

3. **Creates active_pipelines** (if there is active work):
   - Moves `current_feature` to `active_pipelines[FID]`
   - Moves local gates to `active_pipelines[FID].gates`
   - Determines branch by current git branch

4. **Preserves features_registry** without changes

5. **Sets version**: `"2.0"`

---

## Migration Output Example

```
Detected version: 1.0
Migration to v2.0 required

============================================================
MIGRATION PLAN
============================================================

Structural changes:
  • gates -> global_gates (only BOOTSTRAP_READY)
  • Local gates -> active_pipelines[FID].gates
  • current_feature -> active_pipelines
  • Added: parallel_mode, version 2.0

Active pipelines after migration:
  F001: OAuth authorization
       Branch: feature/F001-oauth
       Stage: IMPLEMENT
       Gates: PRD_READY, RESEARCH_DONE, PLAN_APPROVED

next_feature_id: 2

✓ Backup created: .pipeline-state.json.v1.backup
✓ Saved: .pipeline-state.json

============================================================
MIGRATION COMPLETED
============================================================
```

---

## Error Handling

### File Not Found

```
File .pipeline-state.json not found
```

**Action**: Continue command execution (the command will create the file itself if needed).

### Invalid JSON

```
JSON reading error: ...
```

**Action**: Notify the user about the error, suggest checking the file manually.

### Already v2.0

```
✓ File is already in v2.0 format, no migration needed
```

**Action**: Continue command execution.
