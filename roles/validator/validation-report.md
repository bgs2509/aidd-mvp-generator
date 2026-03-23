# Function: Validation Report Creation

> **Purpose**: Creating the final validation report.

---

## Goal

Create a structured validation results report,
confirming the project's readiness for deployment.

---

## Report Structure

```markdown
# Validation Report: {Project Name}

**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Validator**: AI Agent (Validator)
**Status**: ALL_GATES_PASSED / BLOCKED

---

## 1. Overview

### 1.1 Project Information

| Parameter | Value |
|-----------|-------|
| Name | {name} |
| Mode | CREATE / FEATURE |
| Maturity Level | Level 2 (MVP) |
| Development period | {start date} — {end date} |

### 1.2 Team (AI Agents)

| Role | Status | Artifacts |
|------|--------|-----------|
| Analyst | ✓ | PRD |
| Researcher | ✓/— | Research Report |
| Planner | ✓ | Architecture, Plan |
| Coder | ✓ | Services |
| Reviewer | ✓ | Review Report |
| QA | ✓ | QA Report |

---

## 2. Quality Gates

### 2.1 Gate Status

| # | Gate | Status | Date | Artifact |
|---|------|--------|------|----------|
| 1 | PRD_READY | ✓ PASSED | {date} | prd.md |
| 2 | RESEARCH_DONE | ✓ PASSED / — | {date} | research.md |
| 3 | PLAN_APPROVED | ✓ PASSED | {date} | plan.md |
| 4 | IMPLEMENT_OK | ✓ PASSED | {date} | services/ |
| 5 | REVIEW_OK | ✓ PASSED | {date} | review-report.md |
| 6 | QA_PASSED | ✓ PASSED | {date} | qa-report.md |

### 2.2 Gate Details

#### PRD_READY

| Criterion | Status |
|-----------|--------|
| All sections filled in | ✓ |
| Requirements have IDs | ✓ |
| Priorities set | ✓ |
| Acceptance criteria defined | ✓ |
| No blocking questions | ✓ |

#### PLAN_APPROVED

| Criterion | Status |
|-----------|--------|
| Architecture designed | ✓ |
| Components defined | ✓ |
| API contracts described | ✓ |
| Implementation Plan created | ✓ |

#### IMPLEMENT_OK

| Criterion | Status |
|-----------|--------|
| All services created | ✓ |
| Docker works | ✓ |
| Health checks pass | ✓ |

#### REVIEW_OK

| Criterion | Status |
|-----------|--------|
| Architecture followed | ✓ |
| Conventions followed | ✓ |
| No critical issues | ✓ |

#### QA_PASSED

| Criterion | Status |
|-----------|--------|
| 100% of tests pass | ✓ |
| Coverage ≥75% | ✓ ({N}%) |
| Must requirements covered | ✓ |
| No critical defects | ✓ |

---

## 3. Artifacts

### 3.1 Documentation

| Artifact | Status | Path |
|----------|--------|------|
| PRD | ✓ | ai-docs/docs/_analysis/{name}-prd.md |
| Architecture | ✓ | ai-docs/docs/_plans/mvp/{name}-arch.md |
| Implementation Plan | ✓ | ai-docs/docs/_plans/features/{name}-plan.md |
| Review Report | ✓ | ai-docs/docs/_validation/review-report.md |
| QA Report | ✓ | ai-docs/docs/_validation/qa-report.md |
| RTM | ✓ | ai-docs/docs/rtm.md |

### 3.2 Code

| Service | Status | Dockerfile | Tests | Coverage |
|---------|--------|------------|-------|----------|
| {context}_api | ✓ | ✓ | ✓ | {N}% |
| {context}_data | ✓ | ✓ | ✓ | {N}% |
| {context}_bot | ✓ | ✓ | ✓ | {N}% |

### 3.3 Infrastructure

| Artifact | Status |
|----------|--------|
| docker-compose.yml | ✓ |
| docker-compose.dev.yml | ✓ |
| .env.example | ✓ |
| Makefile | ✓ |
| CI Pipeline (if any) | {Status} |

---

## 4. Requirements Traceability

### 4.1 Summary

| Priority | Total | Implemented | Tested | % |
|----------|-------|-------------|--------|---|
| Must | {N} | {N} | {N} | 100% |
| Should | {N} | {N} | {N} | {N}% |
| Could | {N} | {N} | {N} | {N}% |

### 4.2 RTM Excerpt

| Req ID | Description | Implementation | Test | Review | QA |
|--------|-------------|----------------|------|--------|-----|
| FR-001 | {desc} | ✓ | ✓ | ✓ | ✓ |
| FR-002 | {desc} | ✓ | ✓ | ✓ | ✓ |
| NF-001 | {desc} | ✓ | ✓ | ✓ | ✓ |

---

## 5. Quality Metrics

### 5.1 Code

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Code Coverage | {N}% | ≥75% | ✓ |
| Lines of Code | {N} | — | — |
| Test Count | {N} | — | — |
| Test Pass Rate | 100% | 100% | ✓ |

### 5.2 Quality

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Critical Defects | 0 | 0 | ✓ |
| Major Defects | {N} | — | — |
| Minor Defects | {N} | — | — |

### 5.3 CI/CD

| Metric | Value |
|--------|-------|
| Build Time | {N}s |
| Test Time | {N}s |
| Total Pipeline | {N}s |

---

## 6. Open Questions

### 6.1 Blocking

| # | Question | Status |
|---|----------|--------|
| — | No blocking questions | — |

### 6.2 Non-blocking

| # | Question | Recommendation |
|---|----------|----------------|
| 1 | {Question} | {Recommendation} |

---

## 7. Recommendations

### 7.1 For Deployment

1. {Deployment recommendation}
2. {Production configuration}

### 7.2 For Development

1. {Improvement recommendation}
2. {Potential optimizations}

---

## 8. Conclusion

### Overall Status: ALL_GATES_PASSED

### Summary

{Brief summary of validation results}

### Deployment Readiness

- [x] All quality gates passed
- [x] All artifacts in place
- [x] 100% of Must requirements implemented and tested
- [x] No blocking issues
- [x] CI pipeline passes

### Decision

**APPROVED FOR DEPLOYMENT**

---

## 9. Signatures

| Role | Agent | Date |
|------|-------|------|
| Validator | AI Agent | {date} |

---

## Appendices

### A. Full RTM

{Link to ai-docs/docs/rtm.md}

### B. Stage Reports

- Review Report: ai-docs/docs/_validation/review-report.md
- QA Report: ai-docs/docs/_validation/qa-report.md

### C. CI/CD Logs

{Link to last successful CI run}
```

---

## Report Formation Rules

### 1. Validation Status

```
ALL_GATES_PASSED:
- All 6 Quality Gates passed
- All artifacts in place
- No blocking issues

BLOCKED:
- At least one gate not passed
- A required artifact is missing
- There are blocking issues
```

### 2. Information Gathering

```
1. Read all reports from previous stages
2. Check for all artifacts
3. Verify RTM
4. Aggregate metrics
5. Form conclusion
```

---

## Save Path

```
ai-docs/docs/_validation/validation-report.md

Or with date:
ai-docs/docs/_validation/{YYYY-MM-DD}-validation-report.md
```

---

## Quality Gates: ALL_GATES_PASSED

### Passing Criteria

- [ ] All quality gates passed
- [ ] All artifacts exist and are up to date
- [ ] RTM is complete and up to date
- [ ] No blocking issues
- [ ] CI pipeline passes

### Result

After passing:
- Project is ready for deployment
- Can proceed to DEPLOYED stage

---

## Sources

| Document | Description |
|----------|-------------|
| `roles/validator/quality-gates.md` | Gate verification |
| `roles/validator/artifact-verification.md` | Artifact verification |
| `docs/reports/validation-template.md` | Report template |
