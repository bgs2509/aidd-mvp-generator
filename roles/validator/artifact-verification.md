# Function: Artifact Verification

> **Purpose**: Verifying the presence and completeness of all artifacts.

---

## Goal

Verify that all artifacts created during pipeline stages
exist, are up to date, and meet requirements.

---

## Artifact List

### Documentation (ai-docs/)

| Artifact | Path | Stage | Required |
|----------|------|-------|----------|
| PRD | `ai-docs/docs/_analysis/{name}-prd.md` | Analysis | Yes |
| Research Report | `ai-docs/docs/research/{name}-research.md` | Research | Yes |
| Architecture | `ai-docs/docs/_plans/mvp/{name}-arch.md` | Architecture | Yes |
| Implementation Plan | `ai-docs/docs/_plans/features/{name}-plan.md` | Architecture | Yes |
| Review Report | `ai-docs/docs/_validation/review-report.md` | Review | Yes |
| QA Report | `ai-docs/docs/_validation/qa-report.md` | QA | Yes |
| RTM | `ai-docs/docs/rtm.md` | All stages | Yes |

### Code (services/)

| Artifact | Path | Description |
|----------|------|-------------|
| Business API | `services/{context}_api/` | REST API service |
| Data API | `services/{context}_data/` | Data service |
| Telegram Bot | `services/{context}_bot/` | Bot (optional) |
| Background Worker | `services/{context}_worker/` | Worker (optional) |

### Infrastructure

| Artifact | Path | Description |
|----------|------|-------------|
| Docker Compose | `docker-compose.yml` | Main configuration |
| Docker Compose Dev | `docker-compose.dev.yml` | Dev overrides |
| Environment | `.env.example` | Environment variables example |
| Makefile | `Makefile` | Commands |
| CI configuration (optional) | — | CI/CD (if used) |

### Tests

| Artifact | Path | Description |
|----------|------|-------------|
| Unit Tests | `services/*/tests/unit/` | Unit tests |
| Integration Tests | `services/*/tests/integration/` | Integration tests |
| conftest.py | `services/*/tests/conftest.py` | Fixtures |
| Coverage Report | `htmlcov/` | HTML report |

---

## Verification Process

### Step 1: Documentation Check

```bash
# Check for document presence

# PRD
if [ -f "ai-docs/docs/_analysis/*-prd.md" ]; then
    echo "✓ PRD exists"
else
    echo "✗ PRD missing"
fi

# Research Report
if ls ai-docs/docs/research/*-research.md >/dev/null 2>&1; then
    echo "✓ Research Report exists"
else
    echo "✗ Research Report missing"
fi

# Architecture
if [ -f "ai-docs/docs/_plans/mvp/*-arch.md" ]; then
    echo "✓ Architecture exists"
else
    echo "✗ Architecture missing"
fi

# Plan
if [ -f "ai-docs/docs/_plans/features/*-plan.md" ]; then
    echo "✓ Plan exists"
else
    echo "✗ Plan missing"
fi

# Reports
ls ai-docs/docs/_validation/

# RTM
if [ -f "ai-docs/docs/rtm.md" ]; then
    echo "✓ RTM exists"
else
    echo "✗ RTM missing"
fi
```

### Step 2: Code Check

```bash
# Check service structure

for service in services/*/; do
    echo "Checking $service..."

    # Main files
    [ -f "$service/Dockerfile" ] && echo "  ✓ Dockerfile" || echo "  ✗ Dockerfile"
    [ -f "$service/requirements.txt" ] && echo "  ✓ requirements.txt" || echo "  ✗ requirements.txt"
    [ -d "$service/src/" ] && echo "  ✓ src/" || echo "  ✗ src/"
    [ -d "$service/tests/" ] && echo "  ✓ tests/" || echo "  ✗ tests/"
done
```

### Step 3: Infrastructure Check

```bash
# Check infrastructure files

[ -f "docker-compose.yml" ] && echo "✓ docker-compose.yml" || echo "✗ docker-compose.yml"
[ -f "docker-compose.dev.yml" ] && echo "✓ docker-compose.dev.yml" || echo "✗ docker-compose.dev.yml"
[ -f ".env.example" ] && echo "✓ .env.example" || echo "✗ .env.example"
[ -f "Makefile" ] && echo "✓ Makefile" || echo "✗ Makefile"
```

### Step 4: Content Validation

```python
# Content validation pseudocode

def validate_prd(path):
    """Validate PRD structure."""
    content = read(path)

    required_sections = [
        "## 1. Overview",
        "## 2. Functional Requirements",
        "## 3. User Stories",
        "## 4. Pipelines",
        "## 5. UI/UX Requirements",
        "## 6. Non-Functional Requirements",
        "## 7. Technical Constraints",
        "## 8. Assumptions and Risks",
        "## 9. Open Questions",
        "## 10. Glossary",
        "## 11. Change History",
    ]

    for section in required_sections:
        if section not in content:
            return False, f"Missing section: {section}"

    # Check requirement IDs
    if not re.search(r"FR-\d{3}", content):
        return False, "No FR IDs found"

    return True, "Valid"


def validate_rtm(path):
    """Validate RTM."""
    content = read(path)

    # Must contain all FRs from PRD
    prd = read("ai-docs/docs/_analysis/*.md")
    fr_ids = extract_fr_ids(prd)

    for fr_id in fr_ids:
        if fr_id not in content:
            return False, f"Missing {fr_id} in RTM"

    return True, "Valid"
```

---

## Artifact Checklist

### Documentation

- [ ] PRD exists and contains all sections
- [ ] Architecture document exists
- [ ] Implementation Plan exists
- [ ] Review Report exists
- [ ] QA Report exists
- [ ] RTM exists and is up to date

### Code

- [ ] Business API service created
- [ ] Data API service created
- [ ] Telegram Bot created (if required)
- [ ] Background Worker created (if required)
- [ ] All services have Dockerfile
- [ ] All services have tests/

### Infrastructure

- [ ] docker-compose.yml exists and is valid
- [ ] docker-compose.dev.yml exists
- [ ] .env.example contains all variables
- [ ] Makefile contains main commands
- [ ] CI pipeline configured

### Tests

- [ ] Unit tests exist for all services
- [ ] Integration tests exist
- [ ] Coverage report generated
- [ ] Coverage ≥75%

---

## Verification Result

```markdown
## Artifact Verification

### Overall Status: COMPLETE / INCOMPLETE

### Documentation

| Artifact | Status | Path | Comment |
|----------|--------|------|---------|
| PRD | ✓ | ai-docs/docs/_analysis/booking-prd.md | — |
| Architecture | ✓ | ai-docs/docs/_plans/mvp/booking-arch.md | — |
| Plan | ✓ | ai-docs/docs/_plans/features/booking-plan.md | — |
| Review Report | ✓ | ai-docs/docs/_validation/review-report.md | — |
| QA Report | ✓ | ai-docs/docs/_validation/qa-report.md | — |
| RTM | ✓ | ai-docs/docs/rtm.md | Up to date |

### Code

| Service | Status | Dockerfile | Tests | Comment |
|---------|--------|------------|-------|---------|
| booking_api | ✓ | ✓ | ✓ | — |
| booking_data | ✓ | ✓ | ✓ | — |
| booking_bot | ✓ | ✓ | ✓ | — |

### Infrastructure

| Artifact | Status | Comment |
|----------|--------|---------|
| docker-compose.yml | ✓ | Valid |
| docker-compose.dev.yml | ✓ | — |
| .env.example | ✓ | 15 variables |
| Makefile | ✓ | 20 commands |
| CI Pipeline | ✓ | — |

### Missing Artifacts

| # | Artifact | Reason | Action |
|---|----------|--------|--------|
| — | None missing | — | — |
```

---

## Passing Criteria

```
COMPLETE:
- All required artifacts exist
- Documents contain required sections
- Code matches structure
- Tests are present

INCOMPLETE:
- At least one required artifact is missing
- Document lacks required sections
- Service has no tests
```

---

## Sources

| Document | Description |
|----------|-------------|
| `workflow.md` | Artifacts by stage description |
| `knowledge/architecture/project-structure.md` | Project structure |
