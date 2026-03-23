# Function: Stage 4.1 — Infrastructure Setup

> **Purpose**: Creating the base project infrastructure.

---

## Goal

Prepare the project infrastructure: directory structure,
Docker configuration and auxiliary files. CI/CD is configured manually as needed.

---

## Input Data

| Artifact | Path | Description |
|----------|------|-------------|
| Implementation Plan | `ai-docs/docs/_plans/features/{name}-plan.md` | Implementation plan |
| Architecture | `ai-docs/docs/_plans/mvp/{name}-arch.md` | Architectural solution |
| Gates | PLAN_APPROVED | Must be passed |

---

## What Gets Created

### 1. Directory Structure

```
{project}/
├── services/                    # Services
│   ├── {context}_api/          # Business API
│   ├── {context}_data/         # Data API
│   ├── {context}_bot/          # Telegram Bot (if needed)
│   └── {context}_worker/       # Background Worker (if needed)
├── docs/                        # Documentation
├── ai-docs/                     # AI documents
│   └── docs/
│       ├── prd/
│       ├── architecture/
│       └── plans/
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── Makefile
├── README.md
└── .gitignore
```

### 2. docker-compose.yml

```yaml
# docker-compose.yml
# Main Docker Compose configuration
# Use template: templates/infrastructure/docker-compose/

version: "3.8"

services:
  # Business API
  {context}-api:
    build:
      context: ./services/{context}_api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATA_API_URL=http://{context}-data:8001
    depends_on:
      - {context}-data
    networks:
      - {context}-network

  # Data API
  {context}-data:
    build:
      context: ./services/{context}_data
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@{context}-postgres:5432/{context}
    depends_on:
      - {context}-postgres
    networks:
      - {context}-network

  # PostgreSQL
  {context}-postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB={context}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - {context}-network

  # Redis (if needed)
  {context}-redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - {context}-network

networks:
  {context}-network:
    driver: bridge

volumes:
  postgres_data:
```

### 3. docker-compose.dev.yml

```yaml
# docker-compose.dev.yml
# Overrides for development

version: "3.8"

services:
  {context}-api:
    build:
      target: development
    volumes:
      - ./services/{context}_api/src:/app/src
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG

  {context}-data:
    build:
      target: development
    volumes:
      - ./services/{context}_data/src:/app/src
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
```

### 4. .env.example

```bash
# .env.example
# Environment variables (copy to .env)

# General
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB={context}
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/{context}

# Redis
REDIS_URL=redis://localhost:6379/0

# Services
DATA_API_URL=http://localhost:8001
BUSINESS_API_URL=http://localhost:8000

# Telegram Bot (if needed)
BOT_TOKEN=your_bot_token_here
```

### 5. Makefile

```makefile
# Makefile
# Development commands

.PHONY: help build up down logs test lint

# Variables
COMPOSE = docker-compose
COMPOSE_DEV = $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker
build: ## Build images
	$(COMPOSE) build

up: ## Start services
	$(COMPOSE_DEV) up -d

down: ## Stop services
	$(COMPOSE) down

logs: ## Show logs
	$(COMPOSE) logs -f

restart: ## Restart services
	$(COMPOSE) restart

# Development
dev: ## Start in development mode
	$(COMPOSE_DEV) up

shell-api: ## Shell into Business API
	$(COMPOSE) exec {context}-api bash

shell-data: ## Shell into Data API
	$(COMPOSE) exec {context}-data bash

# Testing
test: ## Run all tests
	$(COMPOSE) exec {context}-api pytest
	$(COMPOSE) exec {context}-data pytest

test-api: ## Business API tests
	$(COMPOSE) exec {context}-api pytest -v

test-data: ## Data API tests
	$(COMPOSE) exec {context}-data pytest -v

coverage: ## Coverage report
	$(COMPOSE) exec {context}-api pytest --cov=src --cov-report=html

# Code quality
lint: ## Lint check
	$(COMPOSE) exec {context}-api ruff check src tests
	$(COMPOSE) exec {context}-data ruff check src tests

format: ## Format code
	$(COMPOSE) exec {context}-api ruff format src tests
	$(COMPOSE) exec {context}-data ruff format src tests

# Database
db-migrate: ## Apply migrations
	$(COMPOSE) exec {context}-data alembic upgrade head

db-rollback: ## Rollback migration
	$(COMPOSE) exec {context}-data alembic downgrade -1

db-shell: ## PostgreSQL shell
	$(COMPOSE) exec {context}-postgres psql -U postgres -d {context}

# Cleanup
clean: ## Clean everything
	$(COMPOSE) down -v --rmi local
	docker system prune -f
```

### 6. CI/CD (optional)

CI/CD templates are not created automatically. Configure CI/CD for your tool as needed. Recommendations: `knowledge/infrastructure/ci-cd.md`.

### 7. .gitignore

```gitignore
# .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
coverage.xml
*.cover

# Environment
.env
.env.local
*.local

# Docker
.docker/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Secrets
*.pem
*.key
credentials.json
```

---

## Execution Order

```
1. Create the root project directory
2. Create the services/ directory structure
3. Create docker-compose.yml from template
4. Create docker-compose.dev.yml
5. Create .env.example
6. Create Makefile
7. Create .gitignore
8. Initialize the git repository
```

1. Create the root project directory
2. Create the services/ directory structure
3. Create docker-compose.yml from template
4. Create docker-compose.dev.yml
5. Create .env.example
6. Create Makefile
8. Create .gitignore
9. Initialize the git repository
```

---

## Templates to Use

| File | Template |
|------|----------|
| docker-compose.yml | `templates/infrastructure/docker-compose/docker-compose.yml` |
| docker-compose.dev.yml | `templates/infrastructure/docker-compose/docker-compose.dev.yml` |
| .env.example | `templates/infrastructure/docker-compose/.env.example` |

---

## Quality Gates

### INFRA_READY

- [ ] Directory structure created
- [ ] docker-compose.yml created and valid
- [ ] .env.example contains all variables
- [ ] Makefile contains essential commands
- [ ] CI pipeline configured (optional)
- [ ] .gitignore configured
- [ ] `docker-compose config` executes without errors

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/infrastructure/docker-compose.md` | Docker Compose |
| `knowledge/infrastructure/ci-cd.md` | CI/CD patterns |
| `templates/infrastructure/` | Templates |
