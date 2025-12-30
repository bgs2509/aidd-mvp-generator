# Makefile — {project_name} MVP
#
# Команды для управления проектом.
#
# Использование:
#   make help      — показать справку
#   make dev       — запустить в dev режиме
#   make test      — запустить тесты
#   make deploy    — деплой на staging

.PHONY: help dev prod down logs test lint format clean build push check-logging ci

# === Цвета для вывода ===
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

# === Переменные ===
COMPOSE_DEV = docker compose -f docker-compose.yml -f docker-compose.dev.yml
COMPOSE_PROD = docker compose -f docker-compose.yml -f docker-compose.prod.yml
SERVICES = {context}_api {context}_data

# === Справка ===
help: ## Показать справку
	@echo ''
	@echo '${YELLOW}Доступные команды:${RESET}'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-15s${RESET} %s\n", $$1, $$2}'
	@echo ''

# === Development ===
dev: ## Запустить в dev режиме (с hot reload)
	@echo "${GREEN}Запуск в режиме разработки...${RESET}"
	$(COMPOSE_DEV) up -d
	@echo "${GREEN}Сервисы запущены!${RESET}"
	@echo "API: http://localhost:8000"
	@echo "Data API: http://localhost:8001"
	@echo "Docs: http://localhost:8000/docs"

dev-build: ## Пересобрать и запустить dev
	$(COMPOSE_DEV) up -d --build

dev-tools: ## Запустить dev с инструментами (pgAdmin, Redis Commander)
	$(COMPOSE_DEV) --profile tools up -d

# === Production ===
prod: ## Запустить в production режиме
	@echo "${GREEN}Запуск в production режиме...${RESET}"
	$(COMPOSE_PROD) up -d

prod-build: ## Пересобрать и запустить production
	$(COMPOSE_PROD) up -d --build

# === Управление контейнерами ===
down: ## Остановить все контейнеры
	docker compose down

down-v: ## Остановить и удалить volumes
	docker compose down -v

restart: ## Перезапустить все сервисы
	docker compose restart

logs: ## Показать логи всех сервисов
	docker compose logs -f

logs-api: ## Показать логи API
	docker compose logs -f {context}-api

logs-data: ## Показать логи Data API
	docker compose logs -f {context}-data

ps: ## Показать статус контейнеров
	docker compose ps

# === Тестирование ===
test: ## Запустить все тесты
	@echo "${GREEN}Запуск тестов...${RESET}"
	@for service in $(SERVICES); do \
		echo "${YELLOW}Тестирование $$service...${RESET}"; \
		cd services/$$service && pytest tests/ -v && cd ../..; \
	done

test-unit: ## Запустить unit тесты
	@for service in $(SERVICES); do \
		echo "${YELLOW}Unit тесты $$service...${RESET}"; \
		cd services/$$service && pytest tests/unit -v && cd ../..; \
	done

test-integration: ## Запустить integration тесты
	@for service in $(SERVICES); do \
		echo "${YELLOW}Integration тесты $$service...${RESET}"; \
		cd services/$$service && pytest tests/integration -v && cd ../..; \
	done

test-cov: ## Запустить тесты с coverage
	@for service in $(SERVICES); do \
		cd services/$$service && \
		pytest tests/ --cov=src --cov-report=html --cov-report=term-missing && \
		cd ../..; \
	done

# === Линтинг и форматирование ===
lint: ## Проверить код линтером
	@echo "${GREEN}Проверка кода...${RESET}"
	ruff check .

lint-fix: ## Исправить ошибки линтера
	ruff check . --fix

format: ## Отформатировать код
	@echo "${GREEN}Форматирование кода...${RESET}"
	ruff format .

format-check: ## Проверить форматирование
	ruff format . --check

type-check: ## Проверка типов (mypy)
	mypy . --ignore-missing-imports

# === Сборка ===
build: ## Собрать Docker образы
	@echo "${GREEN}Сборка образов...${RESET}"
	@for service in $(SERVICES); do \
		echo "${YELLOW}Сборка $$service...${RESET}"; \
		docker build -t $$service:latest services/$$service; \
	done

build-no-cache: ## Собрать без кэша
	@for service in $(SERVICES); do \
		docker build --no-cache -t $$service:latest services/$$service; \
	done

# === База данных ===
db-migrate: ## Применить миграции
	@echo "${GREEN}Применение миграций...${RESET}"
	docker compose exec {context}-data alembic upgrade head

db-rollback: ## Откатить последнюю миграцию
	docker compose exec {context}-data alembic downgrade -1

db-revision: ## Создать новую миграцию
	@read -p "Название миграции: " name; \
	docker compose exec {context}-data alembic revision --autogenerate -m "$$name"

db-shell: ## Подключиться к PostgreSQL
	docker compose exec postgres psql -U $${POSTGRES_USER:-app} -d $${POSTGRES_DB:-{context}_db}

db-backup: ## Создать бэкап БД
	@mkdir -p backups
	docker compose exec postgres pg_dump -U $${POSTGRES_USER:-app} $${POSTGRES_DB:-{context}_db} > backups/backup-$$(date +%Y%m%d-%H%M%S).sql
	@echo "${GREEN}Бэкап создан в backups/${RESET}"

db-restore: ## Восстановить БД из бэкапа
	@read -p "Путь к бэкапу: " backup; \
	docker compose exec -T postgres psql -U $${POSTGRES_USER:-app} -d $${POSTGRES_DB:-{context}_db} < $$backup

# === Redis ===
redis-cli: ## Подключиться к Redis CLI
	docker compose exec redis redis-cli

redis-flush: ## Очистить Redis
	docker compose exec redis redis-cli FLUSHALL

# === Очистка ===
clean: ## Очистить временные файлы
	@echo "${GREEN}Очистка...${RESET}"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true

clean-docker: ## Очистить Docker ресурсы
	docker system prune -f
	docker volume prune -f

clean-all: clean clean-docker ## Полная очистка

# === Утилиты ===
shell-api: ## Shell в контейнере API
	docker compose exec {context}-api /bin/sh

shell-data: ## Shell в контейнере Data API
	docker compose exec {context}-data /bin/sh

env-check: ## Проверить переменные окружения
	@echo "${YELLOW}Проверка .env файла...${RESET}"
	@if [ -f .env ]; then \
		echo "${GREEN}.env найден${RESET}"; \
		grep -v '^#' .env | grep -v '^$$' | while read line; do \
			key=$$(echo $$line | cut -d= -f1); \
			if [ -z "$$(echo $$line | cut -d= -f2-)" ]; then \
				echo "${YELLOW}⚠ $$key не установлен${RESET}"; \
			fi; \
		done; \
	else \
		echo "${YELLOW}⚠ .env не найден, копирую из .env.example...${RESET}"; \
		cp .env.example .env; \
	fi

# === Проверка логирования ===
check-logging: ## Проверить Log-Driven Design
	@echo "${GREEN}Проверка Log-Driven Design...${RESET}"
	@echo "${YELLOW}1. Проверка RequestLoggingMiddleware...${RESET}"
	@if grep -rq "RequestLoggingMiddleware" services/*/src/main.py 2>/dev/null; then \
		echo "  ✓ RequestLoggingMiddleware найден"; \
	else \
		echo "  ✗ RequestLoggingMiddleware НЕ найден в main.py"; \
		exit 1; \
	fi
	@echo "${YELLOW}2. Проверка structlog...${RESET}"
	@if grep -rq "setup_logging\|structlog" services/*/src/core/logging.py 2>/dev/null; then \
		echo "  ✓ structlog настроен"; \
	else \
		echo "  ✗ structlog НЕ настроен"; \
		exit 1; \
	fi
	@echo "${YELLOW}3. Проверка tracing...${RESET}"
	@if grep -rq "request_id\|correlation_id" services/*/src/ 2>/dev/null; then \
		echo "  ✓ Tracing настроен"; \
	else \
		echo "  ⚠ Tracing не найден (проверьте вручную)"; \
	fi
	@echo "${YELLOW}4. Проверка секретов в логах...${RESET}"
	@if grep -rE "logger\.(info|debug|warning|error).*['\"].*password|secret|token|api_key" services/*/src/ 2>/dev/null; then \
		echo "  ✗ ВНИМАНИЕ: Возможно логирование секретов!"; \
		exit 1; \
	else \
		echo "  ✓ Секреты не логируются"; \
	fi
	@echo "${GREEN}Log-Driven Design: OK${RESET}"

# === CI/CD ===
ci: lint test check-logging ## Запустить CI локально (включая проверку логирования)
	@echo "${GREEN}CI проверки пройдены!${RESET}"

release: ## Создать релиз
	@read -p "Версия (например, 1.0.0): " version; \
	git tag -a "v$$version" -m "Release v$$version"; \
	git push origin "v$$version"
