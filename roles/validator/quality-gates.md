# Function: Quality Gates Verification

> **Purpose**: Verifying that all Quality Gates have been passed.

---

## Goal

Verify that all pipeline Quality Gates
have been successfully passed before release.

---

## AIDD-MVP Quality Gates

### Full List of Gates

| # | Gate | Stage | Description |
|---|------|-------|-------------|
| 1 | PRD_READY | Analysis | PRD document is ready |
| 2 | RESEARCH_DONE | Research | Code analysis completed |
| 3 | PLAN_APPROVED | Architecture | Plan approved |
| 4 | IMPLEMENT_OK | Implementation | Code written |
| 5 | REVIEW_OK | Review | Code passed review |
| 6 | QA_PASSED | Testing | Tests passed |
| 7 | ALL_GATES_PASSED | Validation | Everything verified |
| 8 | DEPLOYED | Deploy | Deployed |

---

## Criteria for Each Gate

### 1. PRD_READY

```markdown
Criteria:
- [ ] All PRD sections filled in
- [ ] Requirements have unique IDs
- [ ] Priorities set (Must/Should/Could)
- [ ] Acceptance criteria defined for Must
- [ ] No blocking open questions

Artifact: ai-docs/docs/_analysis/{name}-prd.md
```

### 2. RESEARCH_DONE

```markdown
Criteria:
- [ ] Code structure analyzed
- [ ] Patterns identified
- [ ] Constraints identified
- [ ] Pipeline refined

Artifact: ai-docs/docs/research/{name}-research.md
```

### 3. PLAN_APPROVED

```markdown
Criteria:
- [ ] Architecture designed
- [ ] Components defined
- [ ] API contracts described
- [ ] Implementation Plan created
- [ ] Requirements traceability exists

Artifacts:
- ai-docs/docs/_plans/mvp/{name}-arch.md
- ai-docs/docs/_plans/features/{name}-plan.md
```

### 4. IMPLEMENT_OK

```markdown
Criteria:
- [ ] All services created per plan
- [ ] Code matches architecture
- [ ] Docker compose works
- [ ] Health checks pass
- [ ] Basic tests written

Artifact: services/
```

### 5. REVIEW_OK

```markdown
Criteria:
- [ ] Architectural principles followed
- [ ] Conventions followed
- [ ] No critical issues
- [ ] Automated checks pass

Artifact: ai-docs/docs/_validation/review-report.md
```

### 6. QA_PASSED

```markdown
Criteria:
- [ ] 100% of tests pass
- [ ] Coverage ≥75%
- [ ] 100% of Must requirements covered by tests
- [ ] No critical defects
- [ ] CI pipeline passes (if configured)

Artifact: ai-docs/docs/_validation/qa-report.md
```

### 7. ALL_GATES_PASSED

```markdown
Criteria:
- [ ] All previous gates passed
- [ ] RTM is up to date and complete
- [ ] All artifacts are in place
- [ ] No open blocking questions

Artifact: ai-docs/docs/_validation/validation-report.md
```

### 8. DEPLOYED

```markdown
Criteria:
- [ ] Application deployed
- [ ] Smoke tests passed
- [ ] Monitoring configured (Level 3+)

Artifact: Deployment URL / CI/CD logs
```

---

## Verification Process

### Step 1: Checking Artifacts

```bash
# Check for all artifacts

# PRD
ls ai-docs/docs/_analysis/

# Architecture
ls ai-docs/docs/_plans/mvp/

# Plan
ls ai-docs/docs/_plans/features/

# Reports
ls ai-docs/docs/_validation/

# RTM
cat ai-docs/docs/rtm.md
```

### Step 2: Checking Statuses

```markdown
## Gate Status

| Gate | Artifact | Status | Date |
|------|----------|--------|------|
| PRD_READY | prd.md | ✓ | 2024-01-10 |
| RESEARCH_DONE | research.md | ✓ | 2024-01-10 |
| PLAN_APPROVED | plan.md | ✓ | 2024-01-11 |
| IMPLEMENT_OK | services/ | ✓ | 2024-01-13 |
| REVIEW_OK | review-report.md | ✓ | 2024-01-14 |
| QA_PASSED | qa-report.md | ✓ | 2024-01-15 |
```

### Step 3: Validating Each Gate

```python
# Validation pseudocode

def validate_prd_ready():
    prd = read("ai-docs/docs/_analysis/*.md")
    assert prd.has_all_sections()
    assert prd.requirements_have_ids()
    assert prd.no_blocking_questions()
    return True

def validate_implement_ok():
    services = glob("services/*/")
    for service in services:
        assert docker_compose_works(service)
        assert health_check_passes(service)
    return True

def validate_qa_passed():
    qa_report = read("ai-docs/docs/_validation/qa-report.md")
    assert qa_report.status in ["PASSED", "PASSED_WITH_ISSUES"]
    assert qa_report.coverage >= 75
    assert qa_report.all_tests_pass()
    return True

def validate_all_gates():
    gates = [
        validate_prd_ready,
        validate_plan_approved,
        validate_implement_ok,
        validate_review_ok,
        validate_qa_passed,
    ]
    return all(gate() for gate in gates)
```

---

## Verification Result

```markdown
## Quality Gates Verification

### Overall Status: ALL_GATES_PASSED / BLOCKED

### Detailed Status

| Gate | Status | Artifact | Comment |
|------|--------|----------|---------|
| PRD_READY | ✓ PASSED | prd.md | — |
| RESEARCH_DONE | ✓ PASSED | research.md | — |
| PLAN_APPROVED | ✓ PASSED | plan.md | — |
| IMPLEMENT_OK | ✓ PASSED | services/ | — |
| REVIEW_OK | ✓ PASSED | review-report.md | — |
| QA_PASSED | ✓ PASSED | qa-report.md | — |

### Blocking Issues

| # | Gate | Issue | Action |
|---|------|-------|--------|
| — | — | No blocking issues | — |
```

---

## Passing Criteria

```
ALL_GATES_PASSED:
- All 6 gates (PRD → QA) passed
- All artifacts exist and are up to date
- No blocking issues

BLOCKED:
- At least one gate not passed
- A required artifact is missing
- There are blocking issues
```

---

## Sources

| Document | Description |
|----------|-------------|
| `workflow.md` | Gates description |
| `.claude/settings.json` | Hooks for verification |
