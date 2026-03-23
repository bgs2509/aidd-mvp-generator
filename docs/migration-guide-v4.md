# Migration Guide: v3.x → v4.0

> **Date**: 2026-01-29
> **Version**: v4.0 (Immediate Deprecation)

---

## Executive Summary

In v4.0, the AIDD-MVP Generator framework has fully transitioned to a unified naming system based on 5 key words:

**analyst, researcher, planner, coder, validator**

All legacy commands and agents have been removed.

---

## What Changed

### Removed Commands

| Legacy (REMOVED) | New (REQUIRED) | Description |
|-------------------|----------------|-------------|
| `/aidd-idea` | `/aidd-analyze` | Idea analysis → PRD |
| `/aidd-feature-plan` | `/aidd-plan-feature` | Feature planning |
| `/aidd-generate` | `/aidd-code` | Code generation |
| `/aidd-finalize` | `/aidd-validate` | Quality & Deploy |

### Removed Agents

| Legacy (REMOVED) | New (REQUIRED) |
|-------------------|----------------|
| `planner.md` | `planner.md` |
| `coder.md` | `coder.md` |

### Artifact Changes

**v3 is now default**:

| v2 (deprecated) | v3 (default) |
|-----------------|--------------|
| `prd/{name}-prd.md` | `_analysis/{name}.md` |
| `architecture/{name}-plan.md` | `_plans/mvp/{name}.md` |
| `plans/{name}-plan.md` | `_plans/features/{name}.md` |
| `reports/{name}-completion.md` | `_validation/{name}.md` |
| `research/{name}-research.md` | `_research/{name}.md` |

---

## For Existing Projects

### Option 1: Continue with v2 (deprecated)

If you want to keep the current artifact structure (prd/, architecture/, etc.):

```bash
# REQUIRED: Update to new commands
# Old commands NO LONGER work!

/aidd-idea        → /aidd-analyze       Command not found
/aidd-generate    → /aidd-code          Command not found
/aidd-finalize    → /aidd-validate      Command not found
/aidd-feature-plan → /aidd-plan-feature Command not found
```

**What to do**:
1. Update all scripts and documentation to new commands
2. Ensure `.pipeline-state.json` contains `"naming_version": "v2"`
3. Continue working with new commands

**Limitations**:
- v2 structure is **deprecated** (not recommended for new projects)
- Legacy commands are **removed** (cannot be called)
- v2 support will be removed in future versions

### Option 2: Migrate to v3 (recommended)

To transition to the new artifact structure (_analysis/, _plans/, etc.):

```bash
# Navigate to project root
cd your-project/

# Run migration script
python3 .aidd/scripts/migrate-naming-v3.py
```

**What the script does**:
1. Renames artifact folders:
   - `prd/` → `_analysis/`
   - `architecture/` → `_plans/mvp/`
   - `plans/` → `_plans/features/`
   - `reports/` → `_validation/`
   - `research/` → `_research/`

2. Removes duplication in file names:
   - `{name}-prd.md` → `{name}.md`
   - `{name}-plan.md` → `{name}.md`
   - `{name}-completion.md` → `{name}.md`

3. Updates `.pipeline-state.json`:
   - `"naming_version": "v2"` → `"v3"`
   - Updates artifact paths in `active_pipelines` and `features_registry`

4. (Optional) Updates links in markdown documents

**Example**:

```bash
# Before migration
ai-docs/docs/
├── prd/
│   └── 2026-01-15_F001_booking-prd.md
├── architecture/
│   └── 2026-01-15_F001_booking-plan.md
└── reports/
    └── 2026-01-20_F001_booking-completion.md

# After migration
ai-docs/docs/
├── _analysis/
│   └── 2026-01-15_F001_booking.md
├── _plans/
│   └── mvp/
│       └── 2026-01-15_F001_booking.md
└── _validation/
    └── 2026-01-20_F001_booking.md
```

---

## For CI/CD Scripts

If you have automation scripts, update the commands:

```bash
# Old script (DOES NOT work)
#!/bin/bash
/aidd-idea "New feature"
/aidd-research
/aidd-plan
/aidd-generate
/aidd-finalize

# New script (works)
#!/bin/bash
/aidd-analyze "New feature"
/aidd-research
/aidd-plan
/aidd-code
/aidd-validate
```

---

## For New Projects

New projects are automatically created with v3:

```bash
# Create new project
mkdir my-new-mvp && cd my-new-mvp
git init
git submodule add <framework-repo> .aidd

# Launch Claude Code
claude

# Initialize project
/aidd-init
# → naming_version = "v3" (default)

# Start development (new commands only!)
/aidd-analyze "Your MVP idea"
/aidd-research
/aidd-plan
/aidd-code
/aidd-validate
```

---

## Breaking Changes in Detail

### 1. Legacy Commands Removed

**Attempt to call**:
```bash
/aidd-idea "test"
# → Error: Command not found
```

**Solution**: Use `/aidd-analyze`

### 2. Legacy Agents Removed

**Files removed**:
- `.claude/agents/planner.md`
- `.claude/agents/coder.md`

**Replaced by**:
- `.claude/agents/planner.md`
- `.claude/agents/coder.md`

### 3. Default naming_version Changed

**Was** (v3.x):
```json
{
  "naming_version": "v2"  // default
}
```

**Now** (v4.0):
```json
{
  "naming_version": "v3"  // default
}
```

**What this means**:
- New projects are created with v3
- Existing projects with v2 continue to work (deprecated)

---

## FAQ

### Q: My old commands don't work. What to do?

**A**: Update to new commands (see the table at the beginning of the document). Legacy commands were removed in v4.0.

### Q: Can I continue using the v2 structure?

**A**: Yes, but:
1. You need to use **only new commands** (`/aidd-analyze`, `/aidd-code`, etc.)
2. v2 structure is **deprecated** and will be removed in future versions
3. Migrating to v3 is recommended

### Q: How to migrate to v3?

**A**: Run `python3 .aidd/scripts/migrate-naming-v3.py` in the project root.

### Q: What if migration breaks my project?

**A**: The migration script creates a backup. If something went wrong:
```bash
# Roll back to previous commit
git log --oneline | head -5
git reset --hard <commit-before-migration>
```

### Q: Do I need to update documentation in my project?

**A**: Yes, if you use legacy commands in README or other documents:
- Replace `/aidd-idea` → `/aidd-analyze`
- Replace `/aidd-generate` → `/aidd-code`
- Replace `/aidd-finalize` → `/aidd-validate`
- Replace `/aidd-feature-plan` → `/aidd-plan-feature`

### Q: What to do with CI/CD pipelines?

**A**: Update scripts to new commands (see "For CI/CD Scripts" section).

---

## Support

If you encounter migration issues:

1. **Check CHANGELOG.md** — all v4.0 changes are described there
2. **Read this guide** — most issues are resolved here
3. **Create an issue** (if public repository)
4. **Roll back to v3.x** — if v4.0 critically broke your project

---

## Timeline

- **2026-01-19**: Phase 2 completed — Migration Mode active
- **2026-01-29**: v4.0 released — Immediate Deprecation (legacy removed)

---

**Document version**: 1.0
**Updated**: 2026-01-29
**Applies to**: v4.0+
