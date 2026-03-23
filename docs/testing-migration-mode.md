# Testing Migration Mode (v2.4)

**Note:** This document may contain outdated commands `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Current commands: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Goal**: Test the migration mode operation and ensure both command variants (v2 and v3) work correctly.

---

## Test 1: New Project with v2 (default)

### Step 1: Create Project

```bash
mkdir test-v2-project
cd test-v2-project
git init
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd
```

### Step 2: Initialization

```bash
claude
/aidd-init
```

**Expected result**:
- `.pipeline-state.json` created with `naming_version: "v2"`
- Folders created: `ai-docs/docs/_analysis/`, `ai-docs/docs/research/`, `ai-docs/docs/_plans/mvp/`, `ai-docs/docs/_validation/`

### Step 3: Execute commands (old names)

```bash
/aidd-analyze "Test project for booking"
/aidd-research
/aidd-plan
```

**Expected result**:
- `ai-docs/docs/_analysis/{date}_{FID}_{slug}-prd.md` created
- `ai-docs/docs/research/{date}_{FID}_{slug}-research.md` created
- `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}-plan.md` created
- File names contain duplication (`-prd`, `-research`, `-plan`)

### Step 4: Execute commands (new names)

```bash
# Create a new feature
git checkout -b feature/F002-test
/aidd-analyze "Add notifications"
/aidd-research
/aidd-plan-feature
```

**Expected result**:
- New commands work
- Artifacts created in the same folders (v2)
- `prd/{date}_F002_{slug}-prd.md` created
- `plans/{date}_F002_{slug}-plan.md` created

### Test 1 Checklist

- [ ] `.pipeline-state.json` contains `naming_version: "v2"`
- [ ] v2 folders created (`prd/`, `research/`, `architecture/`, `plans/`, `reports/`)
- [ ] Old commands work (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`)
- [ ] New commands work (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`)
- [ ] Artifacts in correct folders (v2)
- [ ] File names with duplication (`-prd.md`, `-plan.md`)

---

## Test 2: New Project with v3

### Step 1: Create Project

```bash
mkdir test-v3-project
cd test-v3-project
git init
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd
```

### Step 2: Initialization with v3

```bash
claude
/aidd-init
```

**Action**: During initialization, manually edit `.pipeline-state.json`:

```json
{
  "naming_version": "v3",
  ...
}
```

Or use the script (if flag support is added):
```bash
/aidd-init --naming-version=v3
```

**Expected result**:
- `.pipeline-state.json` created with `naming_version: "v3"`
- Folders created: `ai-docs/docs/_analysis/`, `ai-docs/docs/_research/`, `ai-docs/docs/_plans/mvp/`, `ai-docs/docs/_plans/features/`, `ai-docs/docs/_validation/`

### Step 3: Execute commands (new names)

```bash
/aidd-analyze "Test project for booking"
/aidd-research
/aidd-plan
```

**Expected result**:
- `ai-docs/docs/_analysis/{date}_{FID}_{slug}.md` created
- `ai-docs/docs/_research/{date}_{FID}_{slug}.md` created
- `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}.md` created
- File names WITHOUT duplication (no `-prd`, `-research`, `-plan`)

### Step 4: Execute commands (old names)

```bash
# Create a new feature
git checkout -b feature/F002-test
/aidd-analyze "Add notifications"
/aidd-research
/aidd-plan-feature
```

**Expected result**:
- Old commands work
- Artifacts created in new folders (v3)
- `_analysis/{date}_F002_{slug}.md` created
- `_plans/features/{date}_F002_{slug}.md` created

### Test 2 Checklist

- [ ] `.pipeline-state.json` contains `naming_version: "v3"`
- [ ] v3 folders created (`_analysis/`, `_research/`, `_plans/mvp/`, `_plans/features/`, `_validation/`)
- [ ] New commands work (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`)
- [ ] Old commands work (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`)
- [ ] Artifacts in correct folders (v3)
- [ ] File names without duplication (`.md` instead of `-prd.md`)

---

## Test 3: Migration v2 → v3

### Precondition

**Test 1** completed and a v2 project created.

### Step 1: Pre-migration check

```bash
cd test-v2-project

# Check structure
ls -la ai-docs/docs/
# Should be: prd/, research/, architecture/, plans/, reports/

# Check naming_version
cat .pipeline-state.json | grep naming_version
# Should be: "naming_version": "v2"

# Check file names
ls ai-docs/docs/_analysis/
# Should be files with duplication: *-prd.md
```

### Step 2: Run migration

```bash
python3 .aidd/scripts/migrate-naming-v3.py
```

**Expected output**:
```
Migration v2 → v3 started...

Step 1: Renaming folders...
  Renamed prd/ → _analysis/
  Renamed research/ → _research/
  Renamed architecture/ → _plans/mvp/
  Renamed plans/ → _plans/features/
  Renamed reports/ → _validation/

Step 2: Renaming files (removing duplication)...
  Renamed 5 files in _analysis/
  Renamed 3 files in _research/
  Renamed 2 files in _plans/mvp/
  Renamed 1 file in _plans/features/

Step 3: Updating .pipeline-state.json...
  Set naming_version: "v3"
  Updated artifact paths in active_pipelines
  Updated artifact paths in features_registry

Step 4: Updating references in documents...
  Updated 12 references

Migration complete!
```

### Step 3: Post-migration check

```bash
# Check structure
ls -la ai-docs/docs/
# Should be: _analysis/, _research/, _plans/, _validation/

# Check naming_version
cat .pipeline-state.json | grep naming_version
# Should be: "naming_version": "v3"

# Check file names
ls ai-docs/docs/_analysis/
# Should be files without duplication: *.md (not *-prd.md)

# Check .pipeline-state.json content
cat .pipeline-state.json | jq '.active_pipelines[].artifacts'
# Paths should be updated to v3 (_analysis/, _plans/, etc.)
```

### Step 4: Verify commands work after migration

```bash
# Create a new feature
git checkout -b feature/F003-test-after-migration
/aidd-analyze "Test after migration"
/aidd-research
```

**Expected result**:
- Commands work
- Artifacts created in new folders (v3)
- `_analysis/{date}_F003_{slug}.md` created
- `_research/{date}_F003_{slug}.md` created

### Test 3 Checklist

- [ ] Migration script executed without errors
- [ ] Folders renamed: `prd/` → `_analysis/`, `architecture/` → `_plans/mvp/`, etc.
- [ ] Files renamed: `{name}-prd.md` → `{name}.md`
- [ ] `.pipeline-state.json` updated: `naming_version: "v3"`
- [ ] Artifact paths in `.pipeline-state.json` updated
- [ ] Commands work after migration
- [ ] New artifacts created in v3 folders

---

## Test 4: Backward Compatibility (mixed usage)

### Goal

Ensure that old and new commands can be used interchangeably.

### Scenario

```bash
cd test-v2-project  # or test-v3-project

# Use old command
/aidd-analyze "Feature 1"

# Use new command
/aidd-research

# Use old command
/aidd-plan-feature

# Use new command
/aidd-code

# Use old command
/aidd-validate
```

**Expected result**:
- All commands work
- Artifacts created correctly
- Gates pass correctly
- No errors or warnings

### Test 4 Checklist

- [ ] Old commands work in any order
- [ ] New commands work in any order
- [ ] Mixed usage works
- [ ] No conflicts between commands
- [ ] Artifacts are correct

---

## Test 5: Edge Cases

### Test 5.1: Missing naming_version

**Scenario**: Remove `naming_version` from `.pipeline-state.json`

```bash
# Edit .pipeline-state.json, remove naming_version field
/aidd-analyze "Test without naming_version"
```

**Expected result**:
- Command uses v2 by default (fallback)
- Artifacts created in `prd/` (v2)
- No errors

### Test 5.2: Invalid naming_version value

**Scenario**: Set `naming_version: "v99"`

```bash
# Edit .pipeline-state.json
{
  "naming_version": "v99",
  ...
}

/aidd-analyze "Test with invalid version"
```

**Expected result**:
- Command uses v2 by default (fallback)
- Or shows an error with instructions
- System doesn't crash

### Test 5 Checklist

- [ ] Missing `naming_version` handled (fallback to v2)
- [ ] Invalid value handled
- [ ] No critical errors
- [ ] System continues working

---

## Final Checklist

### Functionality

- [ ] Test 1: v2 project works
- [ ] Test 2: v3 project works
- [ ] Test 3: Migration v2 → v3 works
- [ ] Test 4: Backward compatibility works
- [ ] Test 5: Edge cases handled

### Commands

- [ ] All old commands work (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`)
- [ ] All new commands work (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`)
- [ ] Mixed usage works

### Artifacts

- [ ] v2 artifacts created in correct folders (`prd/`, `architecture/`, etc.)
- [ ] v3 artifacts created in correct folders (`_analysis/`, `_plans/`, etc.)
- [ ] v2 file names with duplication (`-prd.md`, `-plan.md`)
- [ ] v3 file names without duplication (`.md`)

### Migration

- [ ] Migration script works without errors
- [ ] Folders renamed correctly
- [ ] Files renamed correctly
- [ ] `.pipeline-state.json` updated correctly
- [ ] Commands work after migration

---

## Testing Report

After passing all tests, fill in the report:

```markdown
# Migration Mode Testing Report

**Date**: YYYY-MM-DD
**Tester**: [Name]
**Framework version**: v2.4.0

## Results

- [ ] Test 1: v2 project - PASSED / FAILED
- [ ] Test 2: v3 project - PASSED / FAILED
- [ ] Test 3: Migration - PASSED / FAILED
- [ ] Test 4: Backward compat - PASSED / FAILED
- [ ] Test 5: Edge cases - PASSED / FAILED

## Issues Found

1. [Issue description]
   - Severity: HIGH / MEDIUM / LOW
   - Reproduction steps: ...
   - Expected behavior: ...
   - Actual behavior: ...

## Recommendations

[Your recommendations]

## Conclusion

Migration mode is ready for production
Improvements required
```

---

**Document version**: 1.0
**Created**: 2026-01-19
