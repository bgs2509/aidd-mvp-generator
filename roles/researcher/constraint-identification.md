# Function: Constraint Identification

> **Purpose**: Identifying technical and architectural constraints.

---

## Goal

Identify constraints that must be considered during design
and implementation of new functionality.

**Artifact**: each constraint is recorded in the
`Constraints` section of the report `ai-docs/docs/research/{name}-research.md`
with a description of the impact on subsequent stages.

---

## Types of Constraints

### Technical Constraints

| Category | What to check |
|----------|---------------|
| Python version | `python --version`, pyproject.toml |
| Dependencies | requirements.txt, compatibility |
| Async/Sync | Code style (async everywhere?) |
| Event Loop | Event loop ownership |

### Architectural Constraints

| Category | What to check |
|----------|---------------|
| HTTP-only | Can direct DB access be added? (No!) |
| Services | How many services? How do they communicate? |
| API versions | Are there v1, v2? Is a new version needed? |

### Infrastructure Constraints

| Category | What to check |
|----------|---------------|
| Docker | Is Docker used? |
| Ports | Which ports are occupied? |
| DB | PostgreSQL? MongoDB? Both? |
| Redis | Is it used? For what? |

---

## Identification Process

### 1. Python and Dependencies

```bash
# Python version
Read: pyproject.toml (python_requires)
Read: Dockerfile (FROM python:X.X)

# Dependencies
Read: requirements.txt
Read: requirements-dev.txt
```

**Questions**:
- Is the new feature compatible with current dependencies?
- Are new libraries needed?
- Are there version conflicts?

### 2. Async vs Sync

```bash
Grep: "async def"
Grep: "await "
Grep: "asyncio"
```

**Rule**: If the project is async — new code must also be async.

### 3. Event Loop

```bash
Grep: "asyncio.run"
Grep: "get_event_loop"
Grep: "FastAPI"
Grep: "Dispatcher"
```

**Rule**: Each service owns ONE event loop.

### 4. Data Access

```bash
# Check HTTP-only
Grep: "from sqlalchemy" (in business layer — BAD)
Grep: "httpx" (in business layer — GOOD)
Grep: "DataApiClient"
```

**Rule**: Business services DO NOT access the DB directly.

### 5. Infrastructure

```bash
Read: docker-compose.yml
Read: docker-compose.dev.yml
```

**Questions**:
- Which services are running?
- Which ports are occupied?
- Which volumes are used?

---

## Analysis Result

```markdown
## Technical Constraints

| Constraint | Value | Impact on Feature |
|------------|-------|-------------------|
| Python | 3.11+ | Can use new syntax |
| Async | Yes | All new code is async |
| FastAPI | 0.100+ | Use Annotated DI |

## Architectural Constraints

| Constraint | Description |
|------------|-------------|
| HTTP-only | New feature must use HTTP client |
| DDD | Follow layered structure |

## Infrastructure Constraints

| Resource | Status |
|----------|--------|
| Port 8000 | Occupied (business-api) |
| Port 8001 | Occupied (data-api) |
| Port 8002 | Available |

## Recommendations

1. {Integration recommendation}
2. {Potential risk}
```

---

## Sources

| Document | Description |
|----------|-------------|
| `.ai-framework/docs/reference/tech_stack.md` | Technology stack |
| `.ai-framework/docs/atomic/architecture/event-loop-management.md` | Event Loop |
