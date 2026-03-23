# Function: Test Execution

> **Purpose**: Running tests and collecting results.

---

## Goal

Execute all test scenarios and collect results
for generating the QA report.

---

## Testing Tools

### pytest

```bash
# Main tool for Python tests

# Run all tests
pytest

# With verbose output
pytest -v

# Specific file
pytest tests/unit/test_service.py

# Specific test
pytest tests/unit/test_service.py::test_create_entity

# With coverage
pytest --cov=src --cov-report=html

# Parallel execution
pytest -n auto
```

### Makefile Commands

```bash
# All tests for all services
make test

# Tests for a specific service
make test-api
make test-data

# With coverage
make coverage

# Unit tests
make test-unit

# Integration tests
make test-integration
```

---

## Execution Process

### Step 1: Environment Preparation

```bash
# Start all services
make up

# Check status
docker-compose ps

# Ensure all are healthy
curl http://localhost:8000/api/v1/health
curl http://localhost:8001/api/v1/health
```

### Step 2: Run Unit Tests

```bash
# Run unit tests for each service

# Business API
docker-compose exec {context}-api pytest tests/unit -v

# Data API
docker-compose exec {context}-data pytest tests/unit -v

# Bot (if exists)
docker-compose exec {context}-bot pytest tests/unit -v

# Worker (if exists)
docker-compose exec {context}-worker pytest tests/unit -v
```

### Step 3: Run Integration Tests

```bash
# Integration tests require running services

# Business API
docker-compose exec {context}-api pytest tests/integration -v

# Data API
docker-compose exec {context}-data pytest tests/integration -v
```

### Step 4: Check Coverage

```bash
# Run with coverage measurement
docker-compose exec {context}-api pytest --cov=src --cov-report=term --cov-report=html

# Check minimum coverage (75%)
docker-compose exec {context}-api pytest --cov=src --cov-fail-under=75
```

### Step 5: Run Linters

```bash
# Ruff (linting)
docker-compose exec {context}-api ruff check src tests

# Ruff (formatting)
docker-compose exec {context}-api ruff format --check src tests

# Mypy (types)
docker-compose exec {context}-api mypy src
```

---

## Collecting Results

### pytest Output Format

```
==================== test session starts ====================
platform linux -- Python 3.11.x, pytest-7.x.x
plugins: asyncio-0.x.x, cov-4.x.x
collected 50 items

tests/unit/test_service.py::test_create_entity PASSED    [  2%]
tests/unit/test_service.py::test_get_entity PASSED       [  4%]
tests/unit/test_service.py::test_update_entity PASSED    [  6%]
...
tests/integration/test_api.py::test_full_flow PASSED     [100%]

==================== 50 passed in 5.23s ====================
```

### Coverage Report Format

```
---------- coverage: platform linux, python 3.11.x ----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/{context}_api/__init__.py               0      0   100%
src/{context}_api/main.py                  25      2    92%
src/{context}_api/api/v1/routes.py         45      3    93%
src/{context}_api/application/services/    80      8    90%
...
-----------------------------------------------------------
TOTAL                                     500     50    90%
```

---

## Error Handling

### Failing Test

```
FAILED tests/unit/test_service.py::test_create_entity

E   AssertionError: assert 'Expected' == 'Actual'
E     - Actual
E     + Expected

tests/unit/test_service.py:42: AssertionError
```

### Actions on Failure

```
1. Record the failed test in the report
2. Determine the cause:
   - Bug in code → create a fix task
   - Bug in test → fix the test
   - Requirements changed → update the test
3. Continue executing remaining tests
```

---

## Results Table

```markdown
## Test Execution Results

### Unit Tests

| Service | Total | Passed | Failed | Skipped | Time |
|---------|-------|--------|--------|---------|------|
| {context}_api | 30 | 30 | 0 | 0 | 2.1s |
| {context}_data | 25 | 25 | 0 | 0 | 1.8s |
| {context}_bot | 15 | 14 | 1 | 0 | 1.2s |
| **Total** | **70** | **69** | **1** | **0** | **5.1s** |

### Integration Tests

| Service | Total | Passed | Failed | Skipped | Time |
|---------|-------|--------|--------|---------|------|
| {context}_api | 15 | 15 | 0 | 0 | 8.5s |
| {context}_data | 10 | 10 | 0 | 0 | 6.2s |
| **Total** | **25** | **25** | **0** | **0** | **14.7s** |

### Code Coverage

| Service | Statements | Missing | Coverage |
|---------|------------|---------|----------|
| {context}_api | 500 | 50 | 90% |
| {context}_data | 300 | 25 | 92% |
| {context}_bot | 200 | 30 | 85% |
| **Total** | **1000** | **105** | **89%** |

### Linters

| Tool | Status | Errors |
|------|--------|--------|
| ruff check | PASSED | 0 |
| ruff format | PASSED | 0 |
| mypy | PASSED | 0 |
```

---

## CI Automation

### CI (command examples)

```bash
# Unit tests
pytest tests/unit -v --junitxml=junit-unit.xml

# Integration tests
pytest tests/integration -v --junitxml=junit-integration.xml

# Coverage
pytest --cov=src --cov-fail-under=75 --cov-report=xml
```

---

## Success Criteria

### Minimum Requirements (Level 2)

```
✓ All unit tests pass
✓ All integration tests pass
✓ Coverage ≥75%
✓ Linters pass without errors
```

### Acceptable Deviations

```
- Skipped tests are acceptable with justification
- Flaky tests must be marked and documented
```

---

## Sources

| Document | Description |
|----------|-------------|
| `knowledge/quality/testing/pytest-setup.md` | pytest setup |
| `roles/implementer/testing.md` | Test creation |
