# Функция: Stage 4.1 — Настройка инфраструктуры

> **Назначение**: Создание базовой инфраструктуры проекта.

---

## Цель

Подготовить инфраструктуру проекта: структуру директорий,
Docker конфигурацию, CI pipeline и вспомогательные файлы.

---

## Входные данные

| Артефакт | Путь | Описание |
|----------|------|----------|
| Implementation Plan | `ai-docs/docs/plans/{name}-plan.md` | План реализации |
| Архитектура | `ai-docs/docs/architecture/{name}-arch.md` | Архитектурное решение |
| Ворота | PLAN_APPROVED | Должны быть пройдены |

---

## Что создаётся

### 1. Структура директорий

```
{project}/
├── services/                    # Сервисы
│   ├── {context}_api/          # Business API
│   ├── {context}_data/         # Data API
│   ├── {context}_bot/          # Telegram Bot (если нужен)
│   └── {context}_worker/       # Background Worker (если нужен)
├── docs/                        # Документация
├── ai-docs/                     # AI документы
│   └── docs/
│       ├── prd/
│       ├── architecture/
│       └── plans/
├── .github/
│   └── workflows/
│       └── ci.yml
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
# Основная конфигурация Docker Compose
# Использовать шаблон: templates/infrastructure/docker-compose/

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

  # Redis (если нужен)
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
# Переопределения для разработки

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
# Переменные окружения (скопировать в .env)

# Общие
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

# Сервисы
DATA_API_URL=http://localhost:8001
BUSINESS_API_URL=http://localhost:8000

# Telegram Bot (если нужен)
BOT_TOKEN=your_bot_token_here
```

### 5. Makefile

```makefile
# Makefile
# Команды для разработки

.PHONY: help build up down logs test lint

# Переменные
COMPOSE = docker-compose
COMPOSE_DEV = $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml

help: ## Показать справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker
build: ## Собрать образы
	$(COMPOSE) build

up: ## Запустить сервисы
	$(COMPOSE_DEV) up -d

down: ## Остановить сервисы
	$(COMPOSE) down

logs: ## Показать логи
	$(COMPOSE) logs -f

restart: ## Перезапустить сервисы
	$(COMPOSE) restart

# Разработка
dev: ## Запустить в режиме разработки
	$(COMPOSE_DEV) up

shell-api: ## Shell в Business API
	$(COMPOSE) exec {context}-api bash

shell-data: ## Shell в Data API
	$(COMPOSE) exec {context}-data bash

# Тестирование
test: ## Запустить все тесты
	$(COMPOSE) exec {context}-api pytest
	$(COMPOSE) exec {context}-data pytest

test-api: ## Тесты Business API
	$(COMPOSE) exec {context}-api pytest -v

test-data: ## Тесты Data API
	$(COMPOSE) exec {context}-data pytest -v

coverage: ## Отчёт о покрытии
	$(COMPOSE) exec {context}-api pytest --cov=src --cov-report=html

# Качество кода
lint: ## Проверка линтером
	$(COMPOSE) exec {context}-api ruff check src tests
	$(COMPOSE) exec {context}-data ruff check src tests

format: ## Форматирование кода
	$(COMPOSE) exec {context}-api ruff format src tests
	$(COMPOSE) exec {context}-data ruff format src tests

# База данных
db-migrate: ## Применить миграции
	$(COMPOSE) exec {context}-data alembic upgrade head

db-rollback: ## Откатить миграцию
	$(COMPOSE) exec {context}-data alembic downgrade -1

db-shell: ## Shell PostgreSQL
	$(COMPOSE) exec {context}-postgres psql -U postgres -d {context}

# Очистка
clean: ## Очистить всё
	$(COMPOSE) down -v --rmi local
	docker system prune -f
```

### 6. CI Pipeline (.github/workflows/ci.yml)

```yaml
# .github/workflows/ci.yml
# CI pipeline для проверки кода

name: CI

on:
  push:
    branches: [main, master, develop]
  pull_request:
    branches: [main, master, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    strategy:
      matrix:
        service: [{context}_api, {context}_data]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        working-directory: services/${{ matrix.service }}
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linter
        working-directory: services/${{ matrix.service }}
        run: |
          ruff check src tests

      - name: Run tests
        working-directory: services/${{ matrix.service }}
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
        run: |
          pytest -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: services/${{ matrix.service }}/coverage.xml
          flags: ${{ matrix.service }}

  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install ruff
        run: pip install ruff

      - name: Run ruff
        run: ruff check .
```

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

## Порядок выполнения

```
1. Создать корневую директорию проекта
2. Создать структуру директорий services/
3. Создать docker-compose.yml из шаблона
4. Создать docker-compose.dev.yml
5. Создать .env.example
6. Создать Makefile
7. Создать .github/workflows/ci.yml
8. Создать .gitignore
9. Инициализировать git репозиторий
```

---

## Шаблоны для использования

| Файл | Шаблон |
|------|--------|
| docker-compose.yml | `templates/infrastructure/docker-compose/docker-compose.yml` |
| docker-compose.dev.yml | `templates/infrastructure/docker-compose/docker-compose.dev.yml` |
| .env.example | `templates/infrastructure/docker-compose/.env.example` |
| ci.yml | `templates/infrastructure/github-actions/.github/workflows/ci.yml` |

---

## Качественные ворота

### INFRA_READY

- [ ] Структура директорий создана
- [ ] docker-compose.yml создан и валиден
- [ ] .env.example содержит все переменные
- [ ] Makefile содержит основные команды
- [ ] CI pipeline настроен
- [ ] .gitignore настроен
- [ ] `docker-compose config` выполняется без ошибок

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/infrastructure/docker-compose.md` | Docker Compose |
| `knowledge/infrastructure/ci-cd.md` | CI/CD паттерны |
| `templates/infrastructure/` | Шаблоны |
