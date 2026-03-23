# Function: Architecture Compliance Check

> **Purpose**: Verifying code compliance with architectural principles.

---

## Goal

Verify that the implemented code complies with
the architectural principles of the AIDD-MVP Framework.

---

## Input Data

| Artifact | Path | Description |
|----------|------|-------------|
| Code | `services/` | Implemented services |
| Architecture | `ai-docs/docs/_plans/mvp/` | Architectural decision |
| Gate | IMPLEMENT_OK | Must be passed |

---

## Verified Principles

### 1. HTTP-only Data Access

```
RULE: Business services DO NOT access the DB directly.

Check:
- Business API uses HTTP client for Data API
- No SQLAlchemy imports in business services
- No direct DB connections
```

**Verification commands:**

```bash
# Search for SQLAlchemy imports in business services
Grep: "from sqlalchemy" in services/{context}_api/
Grep: "import sqlalchemy" in services/{context}_api/

# Should be EMPTY. If found — VIOLATION.

# Search for HTTP clients
Grep: "httpx" in services/{context}_api/
Grep: "DataApiClient" in services/{context}_api/

# Should be found. If not — VIOLATION.
```

### 2. DDD Structure

```
RULE: Code is organized by DDD layers.

Check:
- api/ — only routes and HTTP handling
- application/ — application services
- domain/ — business logic
- infrastructure/ — adapters
```

**Verification commands:**

```bash
# Check structure
ls services/{context}_api/src/{context}_api/
# Should have: api/, application/, domain/, infrastructure/

# Check dependencies
# api/ SHOULD NOT import from infrastructure/ directly
Grep: "from.*infrastructure" in services/{context}_api/src/{context}_api/api/

# domain/ SHOULD NOT import from api/ or infrastructure/
Grep: "from.*api" in services/{context}_api/src/{context}_api/domain/
Grep: "from.*infrastructure" in services/{context}_api/src/{context}_api/domain/
```

### 3. One Event Loop per Service

```
RULE: Each service owns one event loop.

Check:
- No asyncio.run() inside async functions
- No creation of new event loops
- No asyncio.get_event_loop().run_until_complete()
```

**Verification commands:**

```bash
# Search for problematic patterns
Grep: "asyncio.run(" in services/
Grep: "get_event_loop().run" in services/
Grep: "new_event_loop()" in services/

# Allowed only in main.py at the top level
```

### 4. Service Separation

```
RULE: Services are isolated and communicate via HTTP.

Check:
- Each service is a separate directory
- No shared imports between services
- Interaction only through HTTP clients
```

**Verification commands:**

```bash
# Check isolation
# Service A should not import from service B
Grep: "from {context}_data" in services/{context}_api/
Grep: "from {context}_api" in services/{context}_data/

# Should be EMPTY
```

---

## Verification Checklist

### Architectural Principles

- [ ] **HTTP-only**: Business API uses only HTTP clients
- [ ] **No SQLAlchemy in business**: SQLAlchemy imports only in data services
- [ ] **DDD structure**: All layers present and properly organized
- [ ] **Separation**: Services do not import from each other directly
- [ ] **Event Loop**: One event loop per service

### Code Quality

- [ ] **DRY**: No code duplication
- [ ] **KISS**: Solutions are simple and clear
- [ ] **YAGNI**: No excessive functionality

---

## Verification Result

```markdown
## Architecture Check

### Status: PASSED / FAILED

### Verified Principles

| Principle | Status | Comment |
|-----------|--------|---------|
| HTTP-only | ✓/✗ | {Comment} |
| DDD structure | ✓/✗ | {Comment} |
| One Event Loop | ✓/✗ | {Comment} |
| Service separation | ✓/✗ | {Comment} |

### Violations Found

| # | File | Line | Violation | Recommendation |
|---|------|------|-----------|----------------|
| 1 | {file} | {line} | {description} | {how to fix} |

### Recommendations

1. {Recommendation 1}
2. {Recommendation 2}
```

---

## Passing Criteria

```
PASSED: All principles are followed, no critical violations.

FAILED: At least one violation:
- HTTP-only violated
- DDD structure violated
- Event Loop issues
- Services not isolated
```

---

## Sources

| Document | Description |
|----------|-------------|
| `knowledge/architecture/improved-hybrid.md` | Hybrid architecture |
| `knowledge/architecture/ddd-hexagonal.md` | DDD principles |
| `knowledge/architecture/data-access.md` | HTTP-only access |
| `knowledge/quality/dry-kiss-yagni.md` | Quality principles |
