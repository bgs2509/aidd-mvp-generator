# Function: Maturity Level Selection

> **Purpose**: Determining components based on the project's Maturity Level.

---

## Goal

Select the correct set of components and practices
depending on the project's Maturity Level.

---

## Maturity Levels

### Level 1: PoC (Proof of Concept)

```
Goal: Quick idea validation
Time: 1-2 days

Components:
├── Single service (monolith)
├── SQLite or JSON files
└── Minimal UI

INCLUDED:
- Basic functionality
- Simplest storage
- Console or simple web interface

EXCLUDED:
- Docker
- Tests
- Logging
- CI/CD
```

### Level 2: MVP (Minimum Viable Product) ⭐ PRIMARY

```
Goal: First product for users
Time: 1-2 weeks

Components:
├── Business API (FastAPI)
├── Data API (PostgreSQL/MongoDB)
├── Telegram Bot (optional)
├── Background Worker (optional)
├── Redis (optional)
└── Docker Compose

INCLUDED:
✓ DDD/Hexagonal architecture
✓ HTTP-only data access
✓ Docker containerization
✓ Tests (coverage ≥75%)
✓ Structured logging
✓ CI pipeline (any tool)
✓ Basic documentation

EXCLUDED:
✗ Prometheus/Grafana
✗ Nginx (direct API access)
✗ SSL certificates
✗ CD pipeline
✗ Rate limiting
✗ Distributed tracing
```

### Level 3: Production

```
Goal: Production readiness
Time: 3-4 weeks

Components (added to Level 2):
├── Nginx reverse proxy
├── SSL/TLS
├── Prometheus + Grafana
├── CD pipeline
└── Rate limiting

ADDED to Level 2:
+ Nginx as API Gateway
+ SSL certificates
+ Metrics (Prometheus)
+ Monitoring (Grafana)
+ CD pipeline
+ Rate limiting
+ Health checks
```

### Level 4: Enterprise

```
Goal: Scalability and fault tolerance
Time: 2+ months

Components (added to Level 3):
├── Kubernetes
├── Service Mesh (Istio)
├── Distributed Tracing (Jaeger)
├── Centralized Logging (ELK)
└── Multi-region deployment

ADDED to Level 3:
+ Kubernetes orchestration
+ Horizontal scaling
+ Service mesh
+ Distributed tracing
+ Centralized logs
+ Multi-region
```

---

## AIDD-MVP Framework = Level 2

```
IMPORTANT: This framework ALWAYS operates at Level 2 (MVP).

Why:
1. MVP — optimal balance of quality and speed
2. Sufficient for first users
3. Can easily be extended to Level 3
4. Not excessive like Level 3-4
```

---

## Component Matrix by Levels

| Component | L1 | L2 | L3 | L4 |
|-----------|----|----|----|----|
| FastAPI | ✓ | ✓ | ✓ | ✓ |
| PostgreSQL | — | ✓ | ✓ | ✓ |
| MongoDB | — | ○ | ○ | ○ |
| Redis | — | ○ | ✓ | ✓ |
| Docker | — | ✓ | ✓ | ✓ |
| Docker Compose | — | ✓ | ✓ | — |
| Kubernetes | — | — | — | ✓ |
| Nginx | — | — | ✓ | ✓ |
| SSL | — | — | ✓ | ✓ |
| Prometheus | — | — | ✓ | ✓ |
| Grafana | — | — | ✓ | ✓ |
| CI (any tool) | — | ✓ | ✓ | ✓ |
| CD | — | — | ✓ | ✓ |
| Unit tests | — | ✓ | ✓ | ✓ |
| Integration tests | — | ✓ | ✓ | ✓ |
| E2E tests | — | — | ✓ | ✓ |

**Legend**: ✓ = required, ○ = optional, — = not needed

---

## Conditional Rules for Level 2

### When to Add Components

```python
# Decision-making pseudocode

if "REST API" in FR or "endpoint" in FR:
    add_component("Business API")

if "store" in FR or "data" in FR:
    add_component("Data API PostgreSQL")

if "documents" in FR or "logs" in FR:
    add_component("Data API MongoDB")

if "Telegram" in FR or "bot" in FR:
    add_component("Telegram Bot")

if "background task" in FR or "scheduled" in FR:
    add_component("Background Worker")

if "cache" in FR or "sessions" in FR:
    add_component("Redis")
```

### Standard Level 2 Set

```
Minimal MVP:
├── Business API (FastAPI) — port 8000
├── Data API (PostgreSQL) — port 8001
├── PostgreSQL — port 5432
└── Docker Compose

Extended MVP (if needed):
├── + Telegram Bot
├── + Background Worker
├── + Redis — port 6379
└── + MongoDB — port 27017
```

---

## Selection Result

```markdown
## Maturity Level

**Selected level**: Level 2 (MVP)

## Justification

AIDD-MVP Framework always operates at Level 2, which provides:
- Quality architecture (DDD/Hexagonal)
- Testing (≥75% coverage)
- Containerization (Docker)
- CI pipeline

## Components for This Project

| Component | Included | Justification |
|-----------|----------|---------------|
| Business API | Yes | FR-001, FR-002 require REST API |
| Data API PG | Yes | Main data storage |
| Telegram Bot | Yes/No | {Justification} |
| Redis | Yes/No | {Justification} |

## Excluded Components (Level 3+)

- Nginx — not needed for MVP
- Prometheus/Grafana — not needed for MVP
- SSL — configured at deployment
```

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/architecture/quality-standards.md` | Quality standards |
| `workflow.md` | Level 2 description |
