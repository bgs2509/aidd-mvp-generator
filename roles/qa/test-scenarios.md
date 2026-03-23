# Function: Test Scenario Creation

> **Purpose**: Creating test scenarios based on requirements.

---

## Goal

Create test scenarios that cover all functional
and non-functional requirements from the PRD.

---

## Input Data

| Artifact | Path | Description |
|----------|------|-------------|
| PRD | `ai-docs/docs/_analysis/{name}-prd.md` | Requirements |
| RTM | `ai-docs/docs/rtm.md` | Traceability matrix |
| Code | `services/` | Implemented services |
| Gate | REVIEW_OK | Must be passed |

---

## Types of Test Scenarios

### 1. Functional Tests (FR)

```
Cover functional requirements:
- CRUD operations
- Business logic
- Data validation
- Error handling
```

### 2. UI/UX Tests (UI) — for bots

```
Cover UI requirements:
- Bot commands
- Keyboards
- Messages
- Navigation
```

### 3. Non-Functional Tests (NF)

```
Cover NFR:
- Performance (response time)
- Availability
- Security
- Test coverage
```

---

## Test Scenario Template

```markdown
## TS-{NNN}: {Scenario Name}

**Requirement**: {FR-XXX / UI-XXX / NF-XXX}
**Priority**: High / Medium / Low
**Type**: Unit / Integration / E2E

### Preconditions
- {Precondition 1}
- {Precondition 2}

### Steps

| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | {Action} | {Result} |
| 2 | {Action} | {Result} |

### Test Data
```json
{
  "input": {...},
  "expected_output": {...}
}
```

### Success Criteria
{How to determine the test passed}
```

---

## Scenario Examples

### Functional Test

```markdown
## TS-001: Create Restaurant

**Requirement**: FR-001 (Restaurant creation)
**Priority**: High
**Type**: Integration

### Preconditions
- Business API is running
- Data API is running
- Database is available

### Steps

| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | POST /api/v1/restaurants with valid data | HTTP 201 Created |
| 2 | Verify response body | Contains id, name, address |
| 3 | GET /api/v1/restaurants/{id} | HTTP 200, data matches |

### Test Data
```json
{
  "input": {
    "name": "Test Restaurant",
    "address": "123 Main St",
    "capacity": 50
  },
  "expected_output": {
    "id": "uuid",
    "name": "Test Restaurant",
    "address": "123 Main St",
    "capacity": 50,
    "created_at": "datetime"
  }
}
```

### Success Criteria
Restaurant is created and can be retrieved by ID
```

### Negative Test

```markdown
## TS-002: Create Restaurant with Invalid Data

**Requirement**: FR-001 (Restaurant creation)
**Priority**: High
**Type**: Integration

### Preconditions
- Business API is running

### Steps

| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | POST /api/v1/restaurants without name | HTTP 422 Validation Error |
| 2 | Verify error body | Contains "name" field |

### Test Data
```json
{
  "input": {
    "address": "123 Main St"
  },
  "expected_output": {
    "error": {
      "code": "VALIDATION_ERROR",
      "details": [{"field": "name", "message": "Field required"}]
    }
  }
}
```

### Success Criteria
Validation error is returned with problem description
```

### Performance Test

```markdown
## TS-010: API Response Time

**Requirement**: NF-001 (Response time <500ms)
**Priority**: High
**Type**: Performance

### Preconditions
- All services are running
- Database contains 1000 records

### Steps

| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | GET /api/v1/restaurants (100 requests) | Average time <500ms |
| 2 | POST /api/v1/restaurants (50 requests) | Average time <500ms |

### Metrics
- p50: <200ms
- p95: <500ms
- p99: <1000ms

### Success Criteria
95% of requests complete in less than 500ms
```

---

## Coverage Matrix

```markdown
## Requirements-to-Tests Coverage Matrix

| Req ID | Description | Test Scenarios | Status |
|--------|-------------|----------------|--------|
| FR-001 | Restaurant creation | TS-001, TS-002 | Covered |
| FR-002 | Restaurant list | TS-003 | Covered |
| FR-003 | Restaurant search | TS-004, TS-005 | Covered |
| NF-001 | Response time | TS-010 | Covered |
| NF-003 | Coverage ≥75% | TS-020 | Covered |

### Statistics

- Total requirements: {N}
- Covered by tests: {N}
- Coverage: {N}%
```

---

## Scenario Creation Process

### Step 1: PRD Analysis

```
1. Read all FR, UI, NF requirements
2. For each requirement determine:
   - Positive scenarios (happy path)
   - Negative scenarios (error cases)
   - Edge cases
```

### Step 2: Determining Priorities

```
High:
- Must requirements
- Critical business logic
- Security

Medium:
- Should requirements
- Secondary functionality

Low:
- Could requirements
- UI/UX details
```

### Step 3: Determining Test Type

```
Unit:
- Individual functions
- Business logic in isolation
- Mocks for dependencies

Integration:
- API endpoints
- Service interactions
- Database

E2E (for Level 3+):
- Full user flow
- All services together
```

---

## Result

```markdown
# Test Scenarios: {Project Name}

**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Author**: AI Agent (QA)

---

## Overview

| Metric | Value |
|--------|-------|
| Total requirements | {N} |
| Test scenarios | {N} |
| Requirements coverage | {N}% |

---

## Scenarios by Category

### Functional (FR)
- TS-001: ...
- TS-002: ...

### UI/UX (UI)
- TS-050: ...

### Non-Functional (NF)
- TS-100: ...

---

## Coverage Matrix

{Coverage table}
```

---

## Save Path

```
ai-docs/docs/test-scenarios.md
```

---

## Sources

| Document | Description |
|----------|-------------|
| `templates/documents/prd-template.md` | PRD Template |
| `templates/documents/rtm-template.md` | RTM Template |
