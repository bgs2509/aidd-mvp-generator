# Function: Pattern Identification

> **Purpose**: Identifying architectural and code patterns.

---

## Goal

Identify patterns in use to ensure consistency
when adding new code.

**Artifact**: discovered patterns are recorded in the report section
`ai-docs/docs/research/{name}-research.md`, so architects understand
which principles are already established in the project.

---

## Architectural Patterns

### DDD (Domain-Driven Design)

```bash
# DDD indicators
Grep: "domain/"
Grep: "application/"
Grep: "infrastructure/"
Grep: "Entity"
Grep: "ValueObject"
Grep: "AggregateRoot"
```

**DDD Checklist**:
- [ ] Domain layer is defined
- [ ] Entities and value objects exist
- [ ] Application services are separated from domain
- [ ] Infrastructure contains adapters

### Hexagonal Architecture

```bash
# Hexagonal indicators
Grep: "ports/"
Grep: "adapters/"
Grep: "Port"
Grep: "Adapter"
```

**Hexagonal Checklist**:
- [ ] Ports (interfaces) are defined
- [ ] Inbound adapters exist (API, CLI)
- [ ] Outbound adapters exist (DB, HTTP)
- [ ] Domain does not depend on infrastructure

### HTTP-only Data Access

```bash
# HTTP-only indicators
Grep: "httpx"
Grep: "DataApiClient"
Grep: "async def.*get.*http"
```

**HTTP-only Checklist**:
- [ ] Business services use HTTP clients
- [ ] No direct SQLAlchemy imports in business layer
- [ ] Data API is a separate service

---

## Code Patterns

### Repository Pattern

```bash
Grep: "class.*Repository"
Grep: "def get_by_id"
Grep: "def create"
Grep: "def update"
Grep: "def delete"
```

### Service Pattern

```bash
Grep: "class.*Service"
Grep: "def __init__.*repository"
Grep: "def __init__.*client"
```

### Factory Pattern

```bash
Grep: "def create_app"
Grep: "def get_.*factory"
Grep: "Factory"
```

### Dependency Injection

```bash
Grep: "Depends("
Grep: "@inject"
Grep: "def get_.*service"
```

---

## Naming Patterns

### Files

```bash
# Check style
ls -la src/**/*.py

# snake_case? kebab-case?
```

### Classes

```bash
Grep: "^class "
# PascalCase?
```

### Functions

```bash
Grep: "^def "
Grep: "async def "
# snake_case?
```

---

## Analysis Result

```markdown
## Architectural Patterns

| Pattern | Used | Comment |
|---------|------|---------|
| DDD | Yes/No | |
| Hexagonal | Yes/No | |
| HTTP-only | Yes/No | |

## Code Patterns

| Pattern | Used | Example |
|---------|------|---------|
| Repository | Yes | UserRepository |
| Service | Yes | OrderService |
| Factory | Yes | create_app() |
| DI | Yes | Depends() |

## Naming Style

| Element | Style |
|---------|-------|
| Files | snake_case |
| Classes | PascalCase |
| Functions | snake_case |
```

---

## Sources

| Document | Description |
|----------|-------------|
| `.ai-framework/docs/atomic/architecture/ddd-hexagonal-principles.md` | DDD and Hexagonal |
| `.ai-framework/docs/atomic/architecture/service-separation-principles.md` | Service separation |
