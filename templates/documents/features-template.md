# Project Feature Registry

> Automatically updated when features are created/completed.
> Last update: {YYYY-MM-DD}

---

## Statistics

| Metric | Value |
|--------|-------|
| Total features | 0 |
| Deployed | 0 |
| In Progress | 0 |
| Archived | 0 |

---

## Active Features

| FID | Name | Status | Date | Services | Artifacts |
|-----|------|--------|------|----------|-----------|
| — | — | — | — | — | — |

---

## Completed Features

| FID | Name | Deployed | Services | Artifacts |
|-----|------|----------|----------|-----------|
| — | — | — | — | — |

---

## Archived Features

| FID | Name | Archive Reason | Date |
|-----|------|----------------|------|
| — | — | — | — |

---

## Status Legend

| Status | Description | Pipeline Stage |
|--------|-------------|----------------|
| `IN_PROGRESS` | Feature in development | 1-4 |
| `PLAN_APPROVED` | Plan approved | 3 |
| `IMPLEMENTED` | Code written | 4 |
| `REVIEW_OK` | Code reviewed | 5 |
| `QA_PASSED` | Tests passed | 6 |
| `VALIDATED` | All gates passed | 7 |
| `DEPLOYED` | In production | 8 |
| `ARCHIVED` | Cancelled/obsolete | — |

---

## How to Find Artifacts

### By FID
```bash
# Find all artifacts for feature F002
find ai-docs/docs -name "*F002*"
grep -r "feature_id: F002" ai-docs/docs/
```

### By Date
```bash
# Artifacts from December 2024
ls ai-docs/docs/*/2024-12-*
```

### By Type
```bash
# All PRDs
ls ai-docs/docs/_analysis/

# All plans
ls ai-docs/docs/_plans/mvp/ ai-docs/docs/_plans/features/
```

---

**Naming format**: `{YYYY-MM-DD}_{FID}_{slug}-{type}.md`
**Specification**: See `.aidd/docs/artifact-naming.md`
