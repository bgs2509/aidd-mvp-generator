# Function: Codebase Analysis

> **Purpose**: Studying existing code for FEATURE mode.

---

## Goal

Understand the structure and patterns of the existing project for correct
integration of new functionality.

**Artifact**: all findings are recorded in `ai-docs/docs/research/{name}-research.md`
in the "Structure", "Services", "API", "Data" sections, so the path to decisions
is transparent for subsequent roles.

---

## When Applied

```
if MODE == FEATURE:
    → Perform full code analysis
else:  # MODE == CREATE
    → Skip (no existing code)
```

---

## Analysis Steps

### 1. Project Structure

```bash
# Determine structure
Glob: **/*.py
Glob: **/*.md
Glob: **/Dockerfile

# Understand organization
ls -la src/ services/
```

**What to look for**:
- DDD structure (api/application/domain/infrastructure)
- Monolith or microservices
- Separation by services

### 2. Services and Components

```bash
# Find services
Grep: "class.*Service"
Grep: "class.*Repository"
Grep: "class.*Client"
```

**What to determine**:
- What services exist
- How business logic is organized
- What external clients are used

### 3. API Endpoints

```bash
# Find routes
Grep: "@router"
Grep: "@app.get"
Grep: "@app.post"
```

**What to determine**:
- Existing endpoints
- API versioning (v1, v2)
- Routing patterns

### 4. Data Models

```bash
# Find models
Grep: "class.*BaseModel"
Grep: "class.*Base"
Grep: "Column("
```

**What to determine**:
- Data structure
- Relationships between models
- Types used

### 5. Dependencies

```bash
# Check dependencies
Read: requirements.txt
Read: pyproject.toml
```

**What to determine**:
- Libraries used
- Versions
- Compatibility

---

## Analysis Result

```markdown
## Project Structure

Type: {DDD/Hexagonal | Monolith | Microservices}
Services: {Service list}

## Components

| Component | Type | File |
|-----------|------|------|
| UserService | Application Service | user_service.py |
| OrderRepository | Repository | order_repository.py |

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/users | List of users |

## Data Models

| Model | Fields |
|-------|--------|
| User | id, name, email |

## Dependencies

| Library | Version |
|---------|---------|
| FastAPI | 0.100+ |
| SQLAlchemy | 2.0+ |
```

---

## Sources

| Document | Description |
|----------|-------------|
| `.ai-framework/docs/reference/project-structure.md` | Project structure |
| `.ai-framework/ARCHITECTURE.md` | Architecture |
