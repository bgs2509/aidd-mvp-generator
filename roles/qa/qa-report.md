# Function: QA Report Creation

> **Purpose**: Creating the final testing report.

---

## Goal

Create a structured testing results report,
ready for handoff to the validation stage.

---

## Report Structure

```markdown
# QA Report: {Project Name}

**Version**: 1.0
**Date**: {YYYY-MM-DD}
**QA**: AI Agent (QA)
**Status**: PASSED / FAILED / PASSED_WITH_ISSUES

---

## 1. Testing Overview

### 1.1 Scope

| Parameter | Value |
|-----------|-------|
| Services tested | {list} |
| Test scenarios | {N} |
| Tests executed | {N} |
| Testing period | {date} |

### 1.2 Environment

| Parameter | Value |
|-----------|-------|
| Python | 3.11.x |
| pytest | 7.x.x |
| Docker | 24.x |
| CI | {tool or "none"} |

---

## 2. Test Results

### 2.1 Summary

| Test Type | Total | Passed | Failed | Skipped | % Passed |
|-----------|-------|--------|--------|---------|----------|
| Unit | {N} | {N} | {N} | {N} | {N}% |
| Integration | {N} | {N} | {N} | {N} | {N}% |
| **Total** | **{N}** | **{N}** | **{N}** | **{N}** | **{N}%** |

### 2.2 Results by Service

#### {context}_api

| Metric | Value |
|--------|-------|
| Unit tests | {N}/{N} passed |
| Integration tests | {N}/{N} passed |
| Code coverage | {N}% |
| Execution time | {N}s |

#### {context}_data

| Metric | Value |
|--------|-------|
| Unit tests | {N}/{N} passed |
| Integration tests | {N}/{N} passed |
| Code coverage | {N}% |
| Execution time | {N}s |

---

## 3. Code Coverage

### 3.1 Coverage Summary

| Service | Statements | Missing | Coverage | Status |
|---------|------------|---------|----------|--------|
| {context}_api | {N} | {N} | {N}% | ✓/✗ |
| {context}_data | {N} | {N} | {N}% | ✓/✗ |
| **Overall** | **{N}** | **{N}** | **{N}%** | **✓/✗** |

### 3.2 Modules with Low Coverage

| Module | Coverage | Reason | Action |
|--------|----------|--------|--------|
| {module} | {N}% | {reason} | {action} |

---

## 4. Requirements Coverage

### 4.1 Summary

| Priority | Total | Covered | % | Status |
|----------|-------|---------|---|--------|
| Must | {N} | {N} | {N}% | ✓/✗ |
| Should | {N} | {N} | {N}% | ✓/✗ |
| Could | {N} | {N} | {N}% | — |

### 4.2 RTM Status

| Req ID | Description | Tests | Result |
|--------|-------------|-------|--------|
| FR-001 | {description} | TS-001, TS-002 | ✓ PASSED |
| FR-002 | {description} | TS-003 | ✓ PASSED |
| NF-001 | {description} | TS-010 | ✓ PASSED |

---

## 5. Defects Found

### 5.1 Critical (Blocker)

| # | Description | Test | Service | Status |
|---|-------------|------|---------|--------|
| — | No critical defects | — | — | — |

### 5.2 Major

| # | Description | Test | Service | Status |
|---|-------------|------|---------|--------|
| 1 | {description} | {test} | {service} | Open/Fixed |

### 5.3 Minor

| # | Description | Test | Service | Status |
|---|-------------|------|---------|--------|
| 1 | {description} | {test} | {service} | Open/Fixed |

---

## 6. Automated Checks

### 6.1 CI Pipeline

| Step | Status | Time | Comment |
|------|--------|------|---------|
| Build | ✓ PASSED | 45s | — |
| Unit Tests | ✓ PASSED | 30s | — |
| Integration Tests | ✓ PASSED | 60s | — |
| Coverage Check | ✓ PASSED | 5s | 84% ≥ 75% |
| Lint | ✓ PASSED | 10s | — |

### 6.2 Code Quality

| Check | Result | Errors |
|-------|--------|--------|
| ruff check | PASSED | 0 |
| ruff format | PASSED | 0 |
| mypy | PASSED | 0 |

---

## 7. Quality Metrics

### 7.1 Metrics Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Code Coverage | {N}% | ≥75% | ✓/✗ |
| Test Pass Rate | {N}% | 100% | ✓/✗ |
| Must Coverage | {N}% | 100% | ✓/✗ |
| Critical Defects | {N} | 0 | ✓/✗ |

### 7.2 Trends (if applicable)

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Coverage | {N}% | {N}% | +{N}% |
| Test Count | {N} | {N} | +{N} |

---

## 8. Recommendations

### 8.1 Required Actions

1. {Action 1 — if there are failed tests}
2. {Action 2 — if coverage is below threshold}

### 8.2 Recommended Improvements

1. {Improvement 1}
2. {Improvement 2}

---

## 9. Conclusion

### Overall Status: {PASSED / FAILED / PASSED_WITH_ISSUES}

### Summary

{Brief summary of testing results}

### Quality Gates

- [ ] All tests pass (100% pass rate)
- [ ] Code coverage ≥75%
- [ ] Must requirements covered at 100%
- [ ] No critical defects
- [ ] CI pipeline passes

---

## 10. Appendices

### A. Full Test List

{Link to file or expanded list}

### B. HTML Coverage Report

{Path to htmlcov/}

### C. CI Logs

{Link to CI run}
```

---

## Report Formation Rules

### 1. QA Status

```
PASSED:
- 100% of tests pass
- Coverage ≥75%
- All Must requirements covered
- No critical defects

PASSED_WITH_ISSUES:
- All tests pass
- Coverage ≥75%
- There are minor defects
- Documented issues

FAILED:
- There are failing tests
- Coverage <75%
- There are critical defects
- Must requirements not covered
```

### 2. Defect Classification

```
Blocker:
- Application doesn't start
- Critical functionality doesn't work
- Data loss

Major:
- Important function works incorrectly
- Business logic errors
- Performance issues

Minor:
- Cosmetic issues
- UX inconveniences
- Edge cases
```

---

## Save Path

```
ai-docs/docs/_validation/qa-report.md

Or with date:
ai-docs/docs/_validation/{YYYY-MM-DD}-qa-report.md
```

---

## Quality Gates: QA_PASSED

### Passing Criteria

- [ ] QA status: PASSED or PASSED_WITH_ISSUES
- [ ] 100% of tests pass
- [ ] Coverage ≥75%
- [ ] 100% of Must requirements covered
- [ ] No critical defects
- [ ] CI pipeline passes
- [ ] RTM updated

---

## Sources

| Document | Description |
|----------|-------------|
| `roles/qa/test-scenarios.md` | Test scenarios |
| `roles/qa/test-execution.md` | Test execution |
| `roles/qa/coverage-verification.md` | Coverage verification |
| `docs/reports/qa-template.md` | Report template |
