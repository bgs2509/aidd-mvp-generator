# Function: Coverage Verification

> **Purpose**: Verifying code and requirements test coverage.

---

## Goal

Verify that code and requirements coverage
meets Level 2 (MVP) standards.

---

## Coverage Types

### 1. Code Coverage

```
Metric: Percentage of code lines executed during tests.

Level 2 requirement: ≥75%

Tools:
- pytest-cov
- coverage.py
```

### 2. Requirements Coverage

```
Metric: Percentage of requirements covered by tests.

Requirement: 100% for Must, ≥80% for Should

Tool:
- RTM (Requirements Traceability Matrix)
```

---

## Verification Process

### Step 1: Measuring Code Coverage

```bash
# Run tests with coverage measurement
pytest --cov=src --cov-report=term --cov-report=html --cov-report=xml

# Check minimum threshold
pytest --cov=src --cov-fail-under=75
```

### Step 2: Analyzing the Coverage Report

```
---------- coverage: platform linux, python 3.11.x ----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/booking_api/__init__.py                 0      0   100%
src/booking_api/main.py                    25      2    92%
src/booking_api/api/v1/routes.py           45      3    93%
src/booking_api/application/services/      80      8    90%
src/booking_api/infrastructure/http/       40     10    75%
-----------------------------------------------------------
TOTAL                                     190     23    88%
```

### Step 3: Identifying Uncovered Code

```bash
# View uncovered lines
coverage report --show-missing

# HTML report with highlighting
coverage html
# Open htmlcov/index.html
```

### Step 4: Updating RTM

```markdown
## Requirements Traceability Matrix

| Req ID | Description | Implementation | Test | Status |
|--------|-------------|----------------|------|--------|
| FR-001 | Restaurant creation | api/v1/routes.py:45 | test_create_restaurant | ✓ |
| FR-002 | Restaurant list | api/v1/routes.py:60 | test_list_restaurants | ✓ |
| FR-003 | Restaurant search | api/v1/routes.py:75 | test_search_restaurant | ✓ |
| NF-001 | Response time <500ms | — | test_response_time | ✓ |
| NF-003 | Coverage ≥75% | — | CI check | ✓ |
```

---

## Results Analysis

### Code Coverage

```markdown
### Code Coverage Analysis

| Service | Coverage | Status | Comment |
|---------|----------|--------|---------|
| {context}_api | 88% | ✓ PASSED | Above threshold |
| {context}_data | 92% | ✓ PASSED | Above threshold |
| {context}_bot | 72% | ✗ FAILED | Below threshold (75%) |
| **Overall** | **84%** | **✓ PASSED** | — |

### Uncovered Areas

| File | Lines | Reason | Action |
|------|-------|--------|--------|
| http_client.py | 45-52 | Error handling | Add tests |
| handlers.py | 80-95 | Edge cases | Add tests |
```

### Requirements Coverage

```markdown
### Requirements Coverage Analysis

| Priority | Total | Covered | Percentage | Status |
|----------|-------|---------|------------|--------|
| Must | 10 | 10 | 100% | ✓ PASSED |
| Should | 5 | 4 | 80% | ✓ PASSED |
| Could | 3 | 2 | 67% | — (not required) |
| **Total** | **18** | **16** | **89%** | — |

### Uncovered Requirements

| Req ID | Description | Reason | Action |
|--------|-------------|--------|--------|
| UI-003 | Button animation | Hard to test | Manual testing |
| FR-008 | Report export | Not implemented | Deferred |
```

---

## Passing Criteria

### Code Coverage

```
Level 2 (MVP):
✓ Overall coverage ≥75%
✓ Critical modules ≥80%
✓ No files with 0% coverage

Exceptions:
- __init__.py
- Configuration files
- Abstract classes
```

### Requirements Coverage

```
✓ 100% of Must requirements covered by tests
✓ ≥80% of Should requirements covered
✓ Could — when possible
✓ RTM is up to date
```

---

## Improving Coverage

### Prioritization

```
1. Critical paths (create, delete)
2. Business logic
3. Error handling
4. Edge cases
```

### Typical Areas for Improvement

```python
# 1. Error handling
try:
    result = await api_client.get_entity(id)
except DataApiError:  # ← Add test
    raise NotFoundError()

# 2. Edge cases
if items and len(items) > 0:  # ← Add test for empty list
    process(items)

# 3. Negative scenarios
if not is_valid(data):  # ← Add test with invalid data
    raise ValidationError()
```

### Example Tests for Improving Coverage

```python
# test_error_handling.py

@pytest.mark.asyncio
async def test_get_entity_data_api_error():
    """Test for Data API error handling."""
    mock_client = AsyncMock()
    mock_client.get_entity.side_effect = DataApiError("Connection failed")

    service = EntityService(mock_client)

    with pytest.raises(NotFoundError):
        await service.get_entity(uuid4())


@pytest.mark.asyncio
async def test_empty_list():
    """Test for empty list handling."""
    mock_client = AsyncMock()
    mock_client.list_entities.return_value = {"items": [], "total": 0}

    service = EntityService(mock_client)
    result = await service.list_entities()

    assert result.items == []
    assert result.total == 0
```

---

## Verification Result

```markdown
## Coverage Verification

### Status: PASSED / FAILED

### Code Coverage

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Overall coverage | 84% | 75% | ✓ |
| Critical modules | 90% | 80% | ✓ |
| Files with 0% | 0 | 0 | ✓ |

### Requirements Coverage

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Must requirements | 100% | 100% | ✓ |
| Should requirements | 80% | 80% | ✓ |
| Overall coverage | 89% | — | — |

### Recommendations

1. {Coverage improvement recommendation}
2. {Areas for additional tests}
```

---

## Sources

| Document | Description |
|----------|-------------|
| `docs/rtm-template.md` | RTM Template |
| `workflow.md` | Level 2 requirements |
