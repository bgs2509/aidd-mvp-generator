# Artifact Naming System

**Note:** This document may contain outdated commands `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Current commands: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Purpose**: Specification of the naming and organization system for artifacts in long-term projects.
> **Problem**: In projects with hundreds of features, the `ai-docs/docs/` folder becomes chaotic without a clear system.

---

## TL;DR

```
File name format:
{YYYY-MM-DD}_{FID}_{slug}-{type}.md

Example:
2024-01-15_F001_user-auth-prd.md
```

| Component | Description | Example |
|-----------|-------------|---------|
| `YYYY-MM-DD` | Creation date | `2024-01-15` |
| `FID` | Feature ID (unique) | `F001`, `F042` |
| `slug` | Short name (kebab-case) | `user-auth` |
| `type` | Artifact type | `prd`, `plan`, `research` |

---

## 1. Problem

### Before: Chaos in a Long-Term Project

```
ai-docs/docs/
├── prd/
│   ├── booking-prd.md          # Which feature? When created?
│   ├── notifications-prd.md    # Related to booking?
│   ├── auth-prd.md             # Version 1 or iteration?
│   ├── auth-v2-prd.md          # Connection to auth-prd.md?
│   ├── payments-prd.md         #
│   └── ... (100+ files)        # Total chaos
├── architecture/
│   ├── booking-plan.md         # Same booking as in prd/?
│   └── ...
```

**Problems:**
- No connection between artifacts of one feature
- No chronology (what came first?)
- No versioning (iterations over a feature)
- Search requires opening every file

### After: Structured System

```
ai-docs/docs/
├── FEATURES.md                              # Registry of all features
├── prd/
│   ├── 2024-01-15_F001_user-auth-prd.md
│   ├── 2024-02-20_F002_table-booking-prd.md
│   ├── 2024-03-10_F003_email-notify-prd.md
│   └── 2024-06-01_F001_user-auth-v2-prd.md  # Iteration of F001!
├── architecture/
│   ├── 2024-01-16_F001_user-auth-plan.md
│   ├── 2024-02-21_F002_table-booking-plan.md
│   └── ...
```

**Advantages:**
- Sorting by date = chronology
- FID links all artifacts of a feature
- `grep F002` finds everything about booking
- FEATURES.md = project table of contents

---

## 2. File Naming Format

### 2.1 Name Structure

```
{YYYY-MM-DD}_{FID}_{slug}-{type}.md
     │        │      │      │
     │        │      │      └── Artifact type
     │        │      └── Short name (≤30 characters, kebab-case)
     │        └── Feature ID (F001, F002, ...)
     └── Creation date (ISO 8601)
```

### 2.2 Components

| Component | Format | Rules | Examples |
|-----------|--------|-------|---------|
| **Date** | `YYYY-MM-DD` | ISO 8601, creation date | `2024-01-15` |
| **FID** | `F{NNN}` | Unique, auto-increment | `F001`, `F042`, `F999` |
| **Slug** | `kebab-case` | ≤30 characters, only `a-z`, `0-9`, `-` | `user-auth`, `table-booking` |
| **Type** | `enum` | See types table | `prd`, `plan`, `research` |

### 2.3 Artifact Types

| Type | Full Name | Folder | Stage |
|------|-----------|--------|-------|
| `prd` | Product Requirements Document | `prd/` | 1 |
| `research` | Research Report | `research/` | 2 |
| `plan` | Architecture/Feature Plan | `architecture/` or `plans/` | 3 |
| `completion` | Completion Report | `reports/` | 5 |

### 2.4 Versioning (Iterations)

For iterations over a feature, the suffix `-v{N}` is added:

```
# Initial feature
2024-01-15_F001_user-auth-prd.md

# Iteration (MFA)
2024-06-01_F001_user-auth-v2-prd.md

# Next iteration
2024-09-15_F001_user-auth-v3-prd.md
```

**Versioning rules:**
- `v2`, `v3`, ... — major changes/additions to an existing feature
- New version = new file (not overwrite!)
- FID stays the same (it's the same feature)
- Date changes to the version creation date

---

## 3. Feature ID (FID)

### 3.1 Format

```
F{NNN}

Where NNN — sequential number with leading zeros (001-999)
```

**Examples:** `F001`, `F042`, `F123`, `F999`

### 3.2 Assignment Rules

1. **Auto-increment**: Each new feature gets the next number
2. **Uniqueness**: FID is never reused
3. **Immutability**: FID is assigned once and never changes
4. **Scope**: FID is unique within a single project

### 3.3 Storage

FID is stored in `.pipeline-state.json`:

```json
{
  "features_registry": {
    "F001": {
      "name": "user-auth",
      "title": "User authentication",
      "created": "2024-01-15",
      "status": "DEPLOYED",
      "services": ["auth_api", "auth_data"]
    },
    "F002": {
      "name": "table-booking",
      "title": "Table booking",
      "created": "2024-02-20",
      "status": "DEPLOYED",
      "services": ["booking_api", "booking_data"]
    }
  },
  "next_feature_id": 3
}
```

### 3.4 FID Generation

```python
def generate_feature_id(state: dict) -> str:
    """Generate the next FID."""
    next_id = state.get("next_feature_id", 1)
    fid = f"F{next_id:03d}"
    state["next_feature_id"] = next_id + 1
    return fid
```

---

## 4. Feature Registry (FEATURES.md)

### 4.1 Location

```
ai-docs/docs/FEATURES.md
```

### 4.2 Format

```markdown
# Project Feature Registry

> Automatically updated when features are created/completed.
> Last update: 2024-12-23

---

## Statistics

| Metric | Value |
|--------|-------|
| Total features | 42 |
| Deployed | 38 |
| In Progress | 3 |
| Archived | 1 |

---

## Active Features

| FID | Name | Status | Date | Services | Artifacts |
|-----|------|--------|------|----------|-----------|
| F042 | Email notifications | IN_PROGRESS | 2024-12-20 | notify_worker |  |
| F041 | Payment system | QA_PASSED | 2024-12-15 | payments_api | [PRD](...), [Plan](...) |

---

## Completed Features

| FID | Name | Deployed | Services | Artifacts |
|-----|------|----------|----------|-----------|
| F001 | Authentication | 2024-01-20 | auth_api, auth_data | [PRD](...), [Plan](...), [v2](...) |
| F002 | Table booking | 2024-02-25 | booking_api, booking_data | [PRD](...), [Plan](...) |
| ... | ... | ... | ... | ... |

---

## Archived Features

| FID | Name | Archive Reason | Date |
|-----|------|----------------|------|
| F010 | Integration with X | Cancelled by customer | 2024-05-01 |
```

### 4.3 Automatic Updates

FEATURES.md is automatically updated by commands:
- `/aidd-analyze` — adds a new feature (IN_PROGRESS)
- `/aidd-validate` — updates status to DEPLOYED
- On manual archiving — moves to "Archived"

---

## 5. YAML Frontmatter

### 5.1 Purpose

Each artifact contains YAML frontmatter with metadata for:
- Machine readability (AI agents)
- Artifact linking
- Quick search

### 5.2 Required Fields

```yaml
---
feature_id: F002
feature_name: table-booking
title: Restaurant table booking
created: 2024-02-20
author: AI (Analyst)
type: prd
status: PRD_READY
version: 1
---
```

### 5.3 Optional Fields

```yaml
---
# ... required fields ...

# Relations
related_features:
  - F001  # Depends on authentication
  - F003  # Email notifications
previous_version: null  # or path to previous version
supersedes: null        # which document it replaces

# Context
services:
  - booking_api
  - booking_data
requirements_count: 12
mode: CREATE  # or FEATURE

# History
updated: 2024-02-21
approved_by: user
approved_at: 2024-02-21
---
```

### 5.4 Examples by Artifact Type

**PRD:**
```yaml
---
feature_id: F002
feature_name: table-booking
title: Table booking system
created: 2024-02-20
author: AI (Analyst)
type: prd
status: PRD_READY
version: 1
mode: CREATE
requirements_count: 15
---
```

**Architecture Plan:**
```yaml
---
feature_id: F002
feature_name: table-booking
title: Booking system architecture
created: 2024-02-21
author: AI (Architect)
type: plan
status: PLAN_APPROVED
version: 1
prd_ref: prd/2024-02-20_F002_table-booking-prd.md
research_ref: research/2024-02-20_F002_table-booking-research.md
services:
  - booking_api
  - booking_data
approved_by: user
approved_at: 2024-02-21
---
```

**Feature Plan (FEATURE mode):**
```yaml
---
feature_id: F042
feature_name: email-notify
title: Adding email notifications
created: 2024-12-20
author: AI (Architect)
type: feature-plan
status: PLAN_APPROVED
version: 1
mode: FEATURE
prd_ref: prd/2024-12-20_F042_email-notify-prd.md
affected_services:
  - booking_api      # Modification
  - notify_worker    # Creation
related_features:
  - F002  # Booking
---
```

---

## 6. Folder Structure

### 6.1 Full Structure

```
ai-docs/docs/
│
├── FEATURES.md                    # Main feature registry
│
├── prd/                           # PRD documents
│   ├── 2024-01-15_F001_user-auth-prd.md
│   ├── 2024-02-20_F002_table-booking-prd.md
│   ├── 2024-06-01_F001_user-auth-v2-prd.md
│   └── ...
│
├── research/                      # Research reports
│   ├── 2024-01-15_F001_user-auth-research.md
│   ├── 2024-02-20_F002_table-booking-research.md
│   └── ...
│
├── architecture/                  # Architecture plans (CREATE mode)
│   ├── 2024-01-16_F001_user-auth-plan.md
│   ├── 2024-02-21_F002_table-booking-plan.md
│   └── ...
│
├── plans/                         # Feature plans (FEATURE mode)
│   ├── 2024-06-02_F001_user-auth-v2-plan.md
│   ├── 2024-12-20_F042_email-notify-plan.md
│   └── ...
│
├── reports/                       # Completion Reports
│   ├── 2024-01-20_F001_user-auth-completion.md
│   └── ...
│
└── archive/                       # Obsolete/cancelled features
    └── F010_integration-x/
        ├── 2024-04-01_F010_integration-x-prd.md
        └── ARCHIVED.md            # Archive reason
```

### 6.2 Organization Rules

| Rule | Description |
|------|-------------|
| By type | Artifacts in folders by type (prd/, architecture/, ...) |
| Chronology | Files sorted by date (ISO format) |
| Linking via FID | All artifacts of a feature share the same FID |
| Archiving | Cancelled features are moved to archive/ |

---

## 7. .pipeline-state.json Extension

### 7.1 New Structure

```json
{
  "version": "2.0",
  "project_name": "booking-service",
  "mode": "CREATE",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-12-23T15:30:00Z",

  "global_gates": {
    "BOOTSTRAP_READY": {"passed": true, "passed_at": "2024-01-15T10:00:00Z"}
  },

  "active_pipelines": {
    "F042": {
      "branch": "feature/F042-email-notify",
      "name": "email-notify",
      "title": "Email notifications",
      "created": "2024-12-20",
      "stage": "QA",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-20T10:05:00Z"},
        "RESEARCH_DONE": {"passed": true, "passed_at": "2024-12-20T10:10:00Z"},
        "PLAN_APPROVED": {"passed": true, "passed_at": "2024-12-20T10:20:00Z"},
        "IMPLEMENT_OK": {"passed": true, "passed_at": "2024-12-21T14:00:00Z"},
        "REVIEW_OK": {"passed": true, "passed_at": "2024-12-22T10:00:00Z"},
        "QA_PASSED": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2024-12-20_F042_email-notify-prd.md",
        "research": "research/2024-12-20_F042_email-notify-research.md",
        "plan": "plans/2024-12-20_F042_email-notify-plan.md"
      }
    }
  },

  "features_registry": {
    "F001": {
      "name": "user-auth",
      "title": "User authentication",
      "created": "2024-01-15",
      "status": "DEPLOYED",
      "deployed_at": "2024-01-20",
      "services": ["auth_api", "auth_data"],
      "versions": [
        {"version": 1, "date": "2024-01-15"},
        {"version": 2, "date": "2024-06-01", "note": "MFA"}
      ]
    },
    "F002": {
      "name": "table-booking",
      "title": "Table booking",
      "created": "2024-02-20",
      "status": "DEPLOYED",
      "deployed_at": "2024-02-25",
      "services": ["booking_api", "booking_data"]
    }
  },

  "next_feature_id": 43
}
```

### 7.2 Feature Statuses

| Status | Description | After stage |
|--------|-------------|-------------|
| `IN_PROGRESS` | Feature in development | 1 (PRD_READY) |
| `PLAN_APPROVED` | Plan approved | 3 |
| `IMPLEMENTED` | Code written | 4 |
| `REVIEW_OK` | Code reviewed | 5 |
| `QA_PASSED` | Tests passed | 6 |
| `VALIDATED` | All gates passed | 7 |
| `DEPLOYED` | In production | 8 |
| `ARCHIVED` | Cancelled/obsolete | — |

---

## 8. Artifact Search

### 8.1 By FID

```bash
# Find all artifacts for feature F002
grep -r "F002" ai-docs/docs/
find ai-docs/docs -name "*F002*"

# Or by filename
ls ai-docs/docs/**/\*F002\*
```

### 8.2 By Date

```bash
# Artifacts for December 2024
ls ai-docs/docs/*/2024-12-*

# Last 10 artifacts
ls -t ai-docs/docs/**/*.md | head -10
```

### 8.3 By Type

```bash
# All PRDs
ls ai-docs/docs/_analysis/

# All plans
ls ai-docs/docs/_plans/mvp/ ai-docs/docs/_plans/features/
```

### 8.4 Via Frontmatter (for AI)

```python
def find_artifacts_by_feature(docs_dir: Path, fid: str) -> list[Path]:
    """Find all feature artifacts via frontmatter."""
    import yaml

    artifacts = []
    for md_file in docs_dir.rglob("*.md"):
        content = md_file.read_text()
        if content.startswith("---"):
            # Extract frontmatter
            _, fm, _ = content.split("---", 2)
            meta = yaml.safe_load(fm)
            if meta.get("feature_id") == fid:
                artifacts.append(md_file)
    return artifacts
```

---

## 9. Migrating Existing Artifacts

### 9.1 Strategy

1. **Analysis**: Read existing files
2. **Grouping**: Group by features (heuristic)
3. **FID Assignment**: Assign unique IDs
4. **Renaming**: Add date and FID
5. **Frontmatter**: Add YAML metadata
6. **FEATURES.md**: Generate registry

### 9.2 Migration Script

See file `scripts/migrate_artifacts.py` (created separately).

### 9.3 Migration Example

**Before:**
```
ai-docs/docs/_analysis/booking-prd.md
```

**After:**
```
ai-docs/docs/_analysis/2024-02-20_F002_table-booking-prd.md
```

**Added frontmatter:**
```yaml
---
feature_id: F002
feature_name: table-booking
title: Table booking system
created: 2024-02-20  # From git log
author: AI (Analyst)
type: prd
status: DEPLOYED
version: 1
migrated_from: booking-prd.md
migrated_at: 2024-12-23
---
```

---

## 10. Integration with Commands

### 10.1 /aidd-analyze

```python
# When creating a PRD:
1. Generate FID (or take existing for FEATURE mode)
2. Create slug from name
3. Form file name: {date}_{FID}_{slug}-prd.md
4. Add frontmatter
5. Update .pipeline-state.json (active_pipelines[FID])
6. Update FEATURES.md
```

### 10.2 /aidd-plan and /aidd-plan-feature

```python
# When creating a plan:
1. Take FID from active_pipelines (current git branch)
2. Form name: {date}_{FID}_{slug}-plan.md
3. Add frontmatter with links to PRD and research
4. Save path in active_pipelines[FID].artifacts.plan
```

### 10.3 /aidd-validate

```python
# On successful deploy (step 4: Deploy):
1. Move feature from active_pipelines to features_registry
2. Add deployed_at and DEPLOYED status
3. Create Completion Report
4. Update FEATURES.md (move to "Completed")
5. Remove record from active_pipelines
```

---

## 11. Quality Gates

### Checklist for a New Artifact

- [ ] File name follows format `{date}_{FID}_{slug}-{type}.md`
- [ ] YAML frontmatter contains all required fields
- [ ] FID is unique and registered in .pipeline-state.json
- [ ] FEATURES.md updated
- [ ] Artifact in the correct folder

---

## See Also

- [target-project-structure.md](target-project-structure.md) — Target Project structure
- [workflow.md](../workflow.md) — 9-stage pipeline
- [NAVIGATION.md](NAVIGATION.md) — Navigation matrix

---

**Version**: 1.0
**Created**: 2024-12-23
