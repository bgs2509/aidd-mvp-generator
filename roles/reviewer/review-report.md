# Function: Review Report Creation

> **Purpose**: Creating the final code review report.

---

## Goal

Create a structured code review report,
ready for handoff to the testing stage.

---

## Report Structure

```markdown
# Code Review Report: {Project Name}

**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Reviewer**: AI Agent (Reviewer)
**Status**: PASSED / FAILED / PASSED_WITH_NOTES

---

## 1. Overview

### 1.1 Review Scope

| Service | Files | Lines of Code |
|---------|-------|---------------|
| {context}_api | {N} | {N} |
| {context}_data | {N} | {N} |
| {context}_bot | {N} | {N} |

### 1.2 Evaluation Criteria

- Architectural principles
- Convention compliance
- Code quality
- Test coverage

---

## 2. Architecture

### 2.1 HTTP-only Data Access

**Status**: ✓ PASSED / ✗ FAILED

{Check description and results}

### 2.2 DDD Structure

**Status**: ✓ PASSED / ✗ FAILED

{Check description and results}

### 2.3 Service Separation

**Status**: ✓ PASSED / ✗ FAILED

{Check description and results}

---

## 3. Conventions

### 3.1 Naming

**Status**: ✓ PASSED / ✗ FAILED

{Check description and results}

### 3.2 Type Hints

**Status**: ✓ PASSED / ✗ FAILED

{Check description and results}

### 3.3 Docstrings

**Status**: ✓ PASSED / ✗ FAILED

{Check description and results}

---

## 4. Code Quality

### 4.1 DRY (Don't Repeat Yourself)

**Status**: ✓ PASSED / ✗ FAILED

{Check description and results}

### 4.2 KISS (Keep It Simple)

**Status**: ✓ PASSED / ✗ FAILED

{Check description and results}

### 4.3 YAGNI (You Aren't Gonna Need It)

**Status**: ✓ PASSED / ✗ FAILED

{Check description and results}

---

## 5. Automated Checks

| Tool | Command | Result | Errors |
|------|---------|--------|--------|
| Ruff Lint | `ruff check` | PASSED/FAILED | {N} |
| Ruff Format | `ruff format --check` | PASSED/FAILED | {N} |
| Mypy | `mypy` | PASSED/FAILED | {N} |

---

## 6. Issues Found

### 6.1 Critical (Blocker)

| # | File | Line | Issue | Recommendation |
|---|------|------|-------|----------------|
| — | — | — | No critical issues | — |

### 6.2 Major

| # | File | Line | Issue | Recommendation |
|---|------|------|-------|----------------|
| 1 | {file} | {line} | {issue} | {recommendation} |

### 6.3 Minor

| # | File | Line | Issue | Recommendation |
|---|------|------|-------|----------------|
| 1 | {file} | {line} | {issue} | {recommendation} |

---

## 7. Recommendations

### 7.1 Required Changes

1. {Change 1}
2. {Change 2}

### 7.2 Optional Improvements

1. {Improvement 1}
2. {Improvement 2}

---

## 8. Requirements Traceability

| Req ID | Implemented | File | Comment |
|--------|-------------|------|---------|
| FR-001 | ✓ | api/v1/routes.py | — |
| FR-002 | ✓ | api/v1/routes.py | — |

---

## 9. Conclusion

### Overall Status: {PASSED / FAILED / PASSED_WITH_NOTES}

### Summary

{Brief summary of review results}

### Quality Gates

- [ ] Architectural principles are followed
- [ ] Conventions are followed
- [ ] No critical issues
- [ ] No major issues (or they are documented)
- [ ] Automated checks pass

---

## 10. Next Steps

1. {Fix found issues}
2. {Re-review (if FAILED)}
3. {Proceed to testing (if PASSED)}
```

---

## Report Formation Rules

### 1. Review Status

```
PASSED:
- No critical issues
- No major issues
- All automated checks pass

PASSED_WITH_NOTES:
- No critical issues
- There are major or minor issues
- They don't block the transition to testing

FAILED:
- There are critical issues
- Fixing and re-review required
```

### 2. Issue Classification

```
Blocker (Critical):
- HTTP-only violation
- Direct DB access from business service
- Event loop issues
- Security vulnerabilities

Major:
- DDD structure violation
- Missing type hints
- Bare except
- Code duplication

Minor:
- Naming violations
- Missing docstrings
- Formatting
- Stylistic issues
```

### 3. Recommendations

```
Required:
- Critical and major issues
- Must be fixed before proceeding to the next stage

Optional:
- Minor issues
- Quality improvements
- Don't block progress
```

---

## Save Path

```
ai-docs/docs/_validation/review-report.md

Or with date:
ai-docs/docs/_validation/{YYYY-MM-DD}-review-report.md
```

---

## Quality Gates: REVIEW_OK

### Passing Criteria

- [ ] Review status: PASSED or PASSED_WITH_NOTES
- [ ] No critical issues (Blocker)
- [ ] Major issues are documented
- [ ] Automated checks pass
- [ ] RTM updated (Review column)

---

## Sources

| Document | Description |
|----------|-------------|
| `roles/reviewer/architecture-compliance.md` | Architecture check |
| `roles/reviewer/convention-compliance.md` | Convention check |
| `docs/reports/review-template.md` | Report template |
