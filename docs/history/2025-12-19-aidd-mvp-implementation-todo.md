# TODO: Реализация AIDD-MVP Generator Framework

**Дата создания**: 2025-12-19
**Источник**: docs/history/2025-12-19-aidd-mvp-framework-plan.md
**Статус**: К реализации

---

## ОБЗОР

Этот документ содержит полный чек-лист задач для создания фреймворка AIDD-MVP Generator.
Общее количество файлов для создания: **~177 файлов**
Оценка времени: **~33 часа**

---

## ЛЕГЕНДА СТАТУСОВ

- [ ] — Не начато
- [~] — В процессе
- [x] — Завершено
- [!] — Заблокировано
- [?] — Требует уточнения

---

# ФАЗА 0: ОСНОВА ФРЕЙМВОРКА

## 0.1 Корневые файлы конфигурации

| # | Статус | Файл | Описание | Источник | Зависит от |
|---|--------|------|----------|----------|------------|
| 0.1.1 | [ ] | `CLAUDE.md` | Главная точка входа для AI-агентов | Раздел 4.1, .ai-framework/CLAUDE.md | — |
| 0.1.2 | [ ] | `conventions.md` | Соглашения о коде (snake_case, docstrings, типы) | Раздел 4.1 | — |
| 0.1.3 | [ ] | `workflow.md` | Описание 8-этапного процесса AIDD-MVP | Раздел 3.1 | — |
| 0.1.4 | [ ] | `README.md` | Документация фреймворка | — | 0.1.1-0.1.3 |

### Детали задачи 0.1.1: CLAUDE.md

**Содержимое должно включать:**
```
- Описание фреймворка AIDD-MVP Generator
- Ссылки на ключевые файлы:
  - conventions.md
  - workflow.md
  - .claude/agents/
  - .claude/commands/
- Правила верификации перед действием (из .ai-framework/CLAUDE.md)
- Архитектурные принципы (HTTP-only, DDD, Hexagonal)
- Порядок чтения документации для AI
- Ссылка на knowledge/ для деталей
```

### Детали задачи 0.1.2: conventions.md

**Содержимое должно включать:**
```
- Именование: snake_case для Python, kebab-case для файлов
- Docstrings: Google стиль, на русском языке
- Type hints: обязательны для всех функций
- Импорты: absolute imports, группировка (stdlib, third-party, local)
- Структура сервиса: DDD слои (api, application, domain, infrastructure)
- Тестирование: pytest, coverage ≥75%
- Логирование: structlog, JSON формат
- Обработка ошибок: кастомные исключения
```

### Детали задачи 0.1.3: workflow.md

**Содержимое должно включать:**
```
- Два режима: CREATE (новый MVP) и FEATURE (добавление фичи)
- 8 этапов пайплайна с воротами (таблица из раздела 3.1)
- Описание каждого этапа
- Артефакты каждого этапа
- Критерии прохождения ворот
```

---

# ФАЗА 1: ИНТЕГРАЦИЯ CLAUDE CODE (.claude/)

## 1.1 Настройки и хуки

| # | Статус | Файл | Описание | Источник | Зависит от |
|---|--------|------|----------|----------|------------|
| 1.1.1 | [ ] | `.claude/settings.json` | Хуки для проверки качественных ворот | Раздел 1.5 (Строгий AIDD) | — |

### Детали задачи 1.1.1: settings.json

**Содержимое должно включать:**
```json
{
  "hooks": {
    "pre_edit": ["check_prd_ready", "check_plan_approved"],
    "pre_commit": ["check_tests_pass", "check_coverage"]
  },
  "permissions": {
    "allow_edit": ["*.py", "*.md", "*.yml", "*.json"],
    "deny_edit": [".env", "*.secret"]
  }
}
```

---

## 1.2 Агенты (7 файлов)

| # | Статус | Файл | Роль | Источник | Зависит от |
|---|--------|------|------|----------|------------|
| 1.2.1 | [ ] | `.claude/agents/analyst.md` | Аналитик | Раздел 3.4, таблица 3.3.1 | 0.1.1 |
| 1.2.2 | [ ] | `.claude/agents/researcher.md` | Исследователь | Раздел 3.4, таблица 3.3.2 | 0.1.1 |
| 1.2.3 | [ ] | `.claude/agents/architect.md` | Архитектор | Раздел 3.4, таблица 3.3.3 | 0.1.1 |
| 1.2.4 | [ ] | `.claude/agents/implementer.md` | Реализатор | Раздел 3.4, таблица 3.3.4 | 0.1.1 |
| 1.2.5 | [ ] | `.claude/agents/reviewer.md` | Ревьюер | Раздел 3.4, таблица 3.3.5 | 0.1.1 |
| 1.2.6 | [ ] | `.claude/agents/qa.md` | QA | Раздел 3.4, таблица 3.3.6 | 0.1.1 |
| 1.2.7 | [ ] | `.claude/agents/validator.md` | Валидатор | Раздел 3.4, таблица 3.3.7 | 0.1.1 |

### Шаблон для каждого агента:

```markdown
# Роль: {Название}

## Описание
{Основная задача роли}

## Входные данные
- {Что читает агент}

## Выходные данные
- {Что создаёт агент}

## Инструкции
1. {Шаг 1}
2. {Шаг 2}
...

## Качественные ворота
- {Название ворот}: {Критерии прохождения}

## Ссылки на документацию
- roles/{role}/*.md — детальные инструкции по функциям
- knowledge/{topic}/ — база знаний
```

### Детали задачи 1.2.1: analyst.md

**Содержимое должно включать:**
```
Роль: Аналитик
Основная задача: Преобразование идеи пользователя в структурированный PRD

Входные данные:
- Описание идеи от пользователя
- CLAUDE.md — контекст проекта
- conventions.md — соглашения

Выходные данные:
- ai-docs/docs/prd/{name}-prd.md

Инструкции:
1. Инициализация (roles/analyst/initialization.md)
2. Верификация промпта (roles/analyst/prompt-validation.md)
3. Сбор требований (roles/analyst/requirements-gathering.md)
4. Формирование PRD (roles/analyst/prd-formation.md)

Ворота: PRD_READY
Критерии:
- Все секции PRD заполнены
- Требования имеют ID (FR-*, NF-*, UI-*)
- Определены критерии приёмки
- Нет блокирующих вопросов
```

---

## 1.3 Команды (9 файлов)

| # | Статус | Файл | Команда | Агент | Источник | Зависит от |
|---|--------|------|---------|-------|----------|------------|
| 1.3.1 | [ ] | `.claude/commands/idea.md` | /idea | Аналитик | Раздел 3.1, 3.9 | 1.2.1 |
| 1.3.2 | [ ] | `.claude/commands/research.md` | /research | Исследователь | Раздел 3.1, 3.9 | 1.2.2 |
| 1.3.3 | [ ] | `.claude/commands/plan.md` | /plan | Архитектор | Раздел 3.1, 3.9 | 1.2.3 |
| 1.3.4 | [ ] | `.claude/commands/feature-plan.md` | /feature-plan | Архитектор | Раздел 3.1, 3.9 | 1.2.3 |
| 1.3.5 | [ ] | `.claude/commands/generate.md` | /generate | Реализатор | Раздел 3.1, 3.9 | 1.2.4 |
| 1.3.6 | [ ] | `.claude/commands/review.md` | /review | Ревьюер | Раздел 3.1, 3.9 | 1.2.5 |
| 1.3.7 | [ ] | `.claude/commands/test.md` | /test | QA | Раздел 3.1, 3.9 | 1.2.6 |
| 1.3.8 | [ ] | `.claude/commands/validate.md` | /validate | Валидатор | Раздел 3.1, 3.9 | 1.2.7 |
| 1.3.9 | [ ] | `.claude/commands/deploy.md` | /deploy | Валидатор | Раздел 3.1, 3.9 | 1.2.7 |

### Шаблон для каждой команды:

```markdown
# Команда: /{name}

## Синтаксис
`/{name} [аргументы]`

## Описание
{Что делает команда}

## Агент
{Какой агент выполняет}

## Режимы
- CREATE: {Поведение при создании нового MVP}
- FEATURE: {Поведение при добавлении фичи}

## Предусловия
- {Какие ворота должны быть пройдены}

## Выходные артефакты
- {Путь к создаваемым файлам}

## Качественные ворота
- {Ворота после выполнения}

## Примеры использования
/{name} "Описание"
```

### Детали задачи 1.3.1: idea.md

**Содержимое должно включать:**
```
Команда: /idea

Синтаксис:
/idea "Описание идеи проекта или фичи"

Описание:
Запускает Аналитика для создания PRD документа

Агент: Аналитик (.claude/agents/analyst.md)

Режимы:
- CREATE: Создаёт полный PRD для нового MVP проекта
- FEATURE: Создаёт FEATURE_PRD для новой функциональности

Предусловия:
- Нет (это первый этап пайплайна)

Выходные артефакты:
- ai-docs/docs/prd/{name}-prd.md
- ai-docs/docs/rtm.md (начальная секция)

Качественные ворота:
- PRD_READY

Примеры:
/idea "Создать сервис бронирования столиков в ресторанах"
/idea "Добавить систему уведомлений по email"
```

---

# ФАЗА 2: ИНСТРУКЦИИ РОЛЕЙ (roles/)

## 2.1 Аналитик (4 файла)

| # | Статус | Файл | Функция | Источник .ai-framework | Зависит от |
|---|--------|------|---------|----------------------|------------|
| 2.1.1 | [ ] | `roles/analyst/initialization.md` | Инициализация (Stage 0) | AGENTS.md, agent-context-summary.md | 1.2.1 |
| 2.1.2 | [ ] | `roles/analyst/prompt-validation.md` | Верификация промпта | prompt-validation-guide.md, maturity-levels.md | 2.1.1 |
| 2.1.3 | [ ] | `roles/analyst/requirements-gathering.md` | Сбор требований | prompt-templates.md, requirements-intake-template.md | 2.1.2 |
| 2.1.4 | [ ] | `roles/analyst/prd-formation.md` | Формирование PRD | analyst-workflow.md, aidd-roles-reference.md | 2.1.3 |

### Детали задачи 2.1.1: initialization.md

**Содержимое должно включать:**
```
# Функция: Инициализация (Stage 0)

## Цель
Загрузка контекста фреймворка и подготовка к работе

## Порядок чтения документов
1. CLAUDE.md — основные правила
2. conventions.md — соглашения о коде
3. workflow.md — процесс разработки
4. knowledge/architecture/ — архитектурные принципы

## Критические правила
- Не начинать работу без понимания контекста
- Проверить режим работы (CREATE/FEATURE)
- Определить уровень зрелости (всегда Level 2 — MVP)

## Источники
- .ai-framework/AGENTS.md § AI Agent Reading Order
- .ai-framework/docs/reference/agent-context-summary.md
```

---

## 2.2 Исследователь (4 файла)

| # | Статус | Файл | Функция | Источник .ai-framework | Зависит от |
|---|--------|------|---------|----------------------|------------|
| 2.2.1 | [ ] | `roles/researcher/codebase-analysis.md` | Анализ кодовой базы | project-structure.md, ARCHITECTURE.md | 1.2.2 |
| 2.2.2 | [ ] | `roles/researcher/pattern-identification.md` | Выявление паттернов | ddd-hexagonal-principles.md, service-separation-principles.md | 2.2.1 |
| 2.2.3 | [ ] | `roles/researcher/constraint-identification.md` | Выявление ограничений | tech_stack.md, event-loop-management.md | 2.2.2 |
| 2.2.4 | [ ] | `roles/researcher/pipeline-refinement.md` | Уточнение пайплайна | aidd-roles-reference.md, conditional-stage-rules.md | 2.2.3 |

---

## 2.3 Архитектор (5 файлов)

| # | Статус | Файл | Функция | Источник .ai-framework | Зависит от |
|---|--------|------|---------|----------------------|------------|
| 2.3.1 | [ ] | `roles/architect/architecture-design.md` | Проектирование архитектуры | ARCHITECTURE.md, improved-hybrid-overview.md | 1.2.3 |
| 2.3.2 | [ ] | `roles/architect/maturity-level-selection.md` | Выбор по уровню зрелости | maturity-levels.md, conditional-stage-rules.md | 2.3.1 |
| 2.3.3 | [ ] | `roles/architect/service-naming.md` | Именование сервисов | naming/README.md, service-naming-checklist.md | 2.3.2 |
| 2.3.4 | [ ] | `roles/architect/implementation-plan.md` | Создание Implementation Plan | implementation-plan-template.md, requirements-traceability-guide.md | 2.3.3 |
| 2.3.5 | [ ] | `roles/architect/api-contracts.md` | Определение контрактов API | routing-patterns.md, schema-validation.md | 2.3.4 |

---

## 2.4 Реализатор (8 файлов)

| # | Статус | Файл | Функция | Источник .ai-framework | Зависит от |
|---|--------|------|---------|----------------------|------------|
| 2.4.1 | [ ] | `roles/implementer/infrastructure-setup.md` | Stage 4.1: Инфраструктура | project-structure.md, docker-compose-setup.md | 1.2.4 |
| 2.4.2 | [ ] | `roles/implementer/data-service.md` | Stage 4.2: Data Service | postgres-service-setup.md, repository-patterns.md | 2.4.1 |
| 2.4.3 | [ ] | `roles/implementer/business-api.md` | Stage 4.3: Business API | application-factory.md, routing-patterns.md | 2.4.2 |
| 2.4.4 | [ ] | `roles/implementer/background-worker.md` | Stage 4.4: Background Worker | basic-setup.md, task-management.md | 2.4.3 |
| 2.4.5 | [ ] | `roles/implementer/telegram-bot.md` | Stage 4.5: Telegram Bot | basic-setup.md, handler-patterns.md | 2.4.3 |
| 2.4.6 | [ ] | `roles/implementer/testing.md` | Stage 4.6: Тестирование | pytest-setup.md, fixture-patterns.md | 2.4.1-2.4.5 |
| 2.4.7 | [ ] | `roles/implementer/logging.md` | Логирование (Level ≥ 2) | structured-logging.md, log-correlation.md | 2.4.1 |
| 2.4.8 | [ ] | `roles/implementer/nginx.md` | Nginx (Level ≥ 3) | nginx-setup.md, ssl-configuration.md | 2.4.1 |

### Детали задачи 2.4.1: infrastructure-setup.md

**Содержимое должно включать:**
```
# Функция: Stage 4.1 — Настройка инфраструктуры

## Цель
Создание базовой инфраструктуры проекта

## Что создаётся
1. Структура директорий проекта
2. docker-compose.yml
3. docker-compose.dev.yml
4. docker-compose.prod.yml
5. .env.example
6. Makefile
7. .github/workflows/ci.yml
8. .github/workflows/cd.yml

## Шаблоны для использования
- templates/infrastructure/docker-compose/
- templates/infrastructure/github-actions/

## Источники
- .ai-framework/docs/reference/project-structure.md
- .ai-framework/docs/atomic/infrastructure/containerization/docker-compose-setup.md
- .ai-framework/docs/atomic/infrastructure/containerization/dockerfile-patterns.md
```

---

## 2.5 Ревьюер (3 файла)

| # | Статус | Файл | Функция | Источник .ai-framework | Зависит от |
|---|--------|------|---------|----------------------|------------|
| 2.5.1 | [ ] | `roles/reviewer/architecture-compliance.md` | Проверка архитектуры | ARCHITECTURE.md, dry-kiss-yagni-principles.md | 1.2.5 |
| 2.5.2 | [ ] | `roles/reviewer/convention-compliance.md` | Проверка конвенций | naming/README.md, linting-standards.md | 2.5.1 |
| 2.5.3 | [ ] | `roles/reviewer/review-report.md` | Создание Review Report | aidd-roles-reference.md, code-review-checklist.md | 2.5.2 |

---

## 2.6 QA (4 файла)

| # | Статус | Файл | Функция | Источник .ai-framework | Зависит от |
|---|--------|------|---------|----------------------|------------|
| 2.6.1 | [ ] | `roles/qa/test-scenarios.md` | Создание тестовых сценариев | e2e-test-setup.md, user-journey-testing.md | 1.2.6 |
| 2.6.2 | [ ] | `roles/qa/test-execution.md` | Выполнение тестов | agent-toolbox.md, development-commands.md | 2.6.1 |
| 2.6.3 | [ ] | `roles/qa/coverage-verification.md` | Верификация coverage | maturity-levels.md, requirements-traceability-guide.md | 2.6.2 |
| 2.6.4 | [ ] | `roles/qa/qa-report.md` | Создание QA Report | qa-report-template.md, aidd-roles-reference.md | 2.6.3 |

---

## 2.7 Валидатор (3 файла)

| # | Статус | Файл | Функция | Источник .ai-framework | Зависит от |
|---|--------|------|---------|----------------------|------------|
| 2.7.1 | [ ] | `roles/validator/quality-gates.md` | Проверка quality gates | agent-verification-checklist.md, aidd-roles-reference.md | 1.2.7 |
| 2.7.2 | [ ] | `roles/validator/artifact-verification.md` | Проверка артефактов | deliverables-catalog.md, requirements-traceability-guide.md | 2.7.1 |
| 2.7.3 | [ ] | `roles/validator/validation-report.md` | Создание Validation Report | aidd-roles-reference.md | 2.7.2 |

---

# ФАЗА 3: БАЗА ЗНАНИЙ (knowledge/)

## 3.1 Архитектура

| # | Статус | Файл | Описание | Источник .ai-framework |
|---|--------|------|----------|----------------------|
| 3.1.1 | [ ] | `knowledge/architecture/improved-hybrid.md` | Гибридная архитектура | docs/atomic/architecture/improved-hybrid-overview.md |
| 3.1.2 | [ ] | `knowledge/architecture/ddd-hexagonal.md` | DDD и Hexagonal принципы | docs/atomic/architecture/ddd-hexagonal-principles.md |
| 3.1.3 | [ ] | `knowledge/architecture/data-access.md` | HTTP-only доступ к данным | docs/atomic/architecture/data-access-architecture.md |
| 3.1.4 | [ ] | `knowledge/architecture/service-separation.md` | Разделение сервисов | docs/atomic/architecture/service-separation-principles.md |
| 3.1.5 | [ ] | `knowledge/architecture/event-loop.md` | Управление event loop | docs/atomic/architecture/event-loop-management.md |
| 3.1.6 | [ ] | `knowledge/architecture/naming/README.md` | Соглашения об именовании | docs/atomic/architecture/naming/README.md |
| 3.1.7 | [ ] | `knowledge/architecture/naming/services.md` | Именование сервисов | docs/atomic/architecture/naming/naming-services.md |
| 3.1.8 | [ ] | `knowledge/architecture/naming/python.md` | Именование в Python | docs/atomic/architecture/naming/naming-python.md |
| 3.1.9 | [ ] | `knowledge/architecture/quality-standards.md` | Стандарты качества | docs/atomic/architecture/quality-standards.md |
| 3.1.10 | [ ] | `knowledge/architecture/project-structure.md` | Структура проекта | docs/atomic/architecture/project-structure-patterns.md |

---

## 3.2 Сервисы

| # | Статус | Файл | Описание | Источник .ai-framework |
|---|--------|------|----------|----------------------|
| 3.2.1 | [ ] | `knowledge/services/fastapi/application-factory.md` | Фабрика приложений | docs/atomic/services/fastapi/application-factory.md |
| 3.2.2 | [ ] | `knowledge/services/fastapi/routing-patterns.md` | Паттерны маршрутизации | docs/atomic/services/fastapi/routing-patterns.md |
| 3.2.3 | [ ] | `knowledge/services/fastapi/dependency-injection.md` | Внедрение зависимостей | docs/atomic/services/fastapi/dependency-injection.md |
| 3.2.4 | [ ] | `knowledge/services/fastapi/schema-validation.md` | Валидация схем | docs/atomic/services/fastapi/schema-validation.md |
| 3.2.5 | [ ] | `knowledge/services/fastapi/error-handling.md` | Обработка ошибок | docs/atomic/services/fastapi/error-handling.md |
| 3.2.6 | [ ] | `knowledge/services/aiogram/basic-setup.md` | Базовая настройка бота | docs/atomic/services/aiogram/basic-setup.md |
| 3.2.7 | [ ] | `knowledge/services/aiogram/handler-patterns.md` | Паттерны обработчиков | docs/atomic/services/aiogram/handler-patterns.md |
| 3.2.8 | [ ] | `knowledge/services/aiogram/middleware-setup.md` | Настройка middleware | docs/atomic/services/aiogram/middleware-setup.md |
| 3.2.9 | [ ] | `knowledge/services/aiogram/state-management.md` | Управление состоянием | docs/atomic/services/aiogram/state-management.md |
| 3.2.10 | [ ] | `knowledge/services/asyncio-workers/basic-setup.md` | Базовая настройка воркера | docs/atomic/services/asyncio-workers/basic-setup.md |
| 3.2.11 | [ ] | `knowledge/services/asyncio-workers/task-management.md` | Управление задачами | docs/atomic/services/asyncio-workers/task-management.md |
| 3.2.12 | [ ] | `knowledge/services/asyncio-workers/signal-handling.md` | Обработка сигналов | docs/atomic/services/asyncio-workers/signal-handling.md |
| 3.2.13 | [ ] | `knowledge/services/data-services/postgres-setup.md` | Настройка PostgreSQL | docs/atomic/services/data-services/postgres-service-setup.md |
| 3.2.14 | [ ] | `knowledge/services/data-services/repository-patterns.md` | Паттерны репозиториев | docs/atomic/services/data-services/repository-patterns.md |

---

## 3.3 Интеграции

| # | Статус | Файл | Описание | Источник .ai-framework |
|---|--------|------|----------|----------------------|
| 3.3.1 | [ ] | `knowledge/integrations/http/business-to-data.md` | HTTP вызовы между сервисами | docs/atomic/integrations/http-communication/business-to-data-calls.md |
| 3.3.2 | [ ] | `knowledge/integrations/http/client-patterns.md` | Паттерны HTTP клиентов | docs/atomic/integrations/http-communication/http-client-patterns.md |
| 3.3.3 | [ ] | `knowledge/integrations/http/error-handling.md` | Обработка ошибок HTTP | docs/atomic/integrations/http-communication/error-handling-strategies.md |
| 3.3.4 | [ ] | `knowledge/integrations/redis/caching.md` | Стратегии кэширования | docs/atomic/integrations/redis/caching-strategies.md |
| 3.3.5 | [ ] | `knowledge/integrations/redis/connection.md` | Управление соединениями | docs/atomic/integrations/redis/connection-management.md |

---

## 3.4 Инфраструктура

| # | Статус | Файл | Описание | Источник .ai-framework |
|---|--------|------|----------|----------------------|
| 3.4.1 | [ ] | `knowledge/infrastructure/docker-compose.md` | Настройка Docker Compose | docs/atomic/infrastructure/containerization/docker-compose-setup.md |
| 3.4.2 | [ ] | `knowledge/infrastructure/dockerfile.md` | Паттерны Dockerfile | docs/atomic/infrastructure/containerization/dockerfile-patterns.md |
| 3.4.3 | [ ] | `knowledge/infrastructure/nginx.md` | Настройка Nginx | docs/atomic/infrastructure/api-gateway/nginx-setup.md |
| 3.4.4 | [ ] | `knowledge/infrastructure/ssl.md` | Конфигурация SSL | docs/atomic/infrastructure/api-gateway/ssl-configuration.md |
| 3.4.5 | [ ] | `knowledge/infrastructure/ci-cd.md` | Паттерны CI/CD | docs/atomic/infrastructure/deployment/ci-cd-patterns.md |

---

## 3.5 Качество

| # | Статус | Файл | Описание | Источник .ai-framework |
|---|--------|------|----------|----------------------|
| 3.5.1 | [ ] | `knowledge/quality/dry-kiss-yagni.md` | Принципы DRY/KISS/YAGNI | docs/guides/dry-kiss-yagni-principles.md |
| 3.5.2 | [ ] | `knowledge/quality/testing/pytest-setup.md` | Настройка pytest | docs/atomic/testing/unit-testing/pytest-setup.md |
| 3.5.3 | [ ] | `knowledge/quality/testing/fixture-patterns.md` | Паттерны фикстур | docs/atomic/testing/unit-testing/fixture-patterns.md |
| 3.5.4 | [ ] | `knowledge/quality/testing/mocking.md` | Стратегии мокирования | docs/atomic/testing/unit-testing/mocking-strategies.md |
| 3.5.5 | [ ] | `knowledge/quality/testing/fastapi-testing.md` | Тестирование FastAPI | docs/atomic/testing/service-testing/fastapi-testing-patterns.md |
| 3.5.6 | [ ] | `knowledge/quality/testing/testcontainers.md` | Использование Testcontainers | docs/atomic/testing/integration-testing/testcontainers-setup.md |
| 3.5.7 | [ ] | `knowledge/quality/logging/structured.md` | Структурированное логирование | docs/atomic/observability/logging/structured-logging.md |
| 3.5.8 | [ ] | `knowledge/quality/logging/correlation.md` | Корреляция логов | docs/atomic/observability/logging/log-correlation.md |
| 3.5.9 | [ ] | `knowledge/quality/production-requirements.md` | Требования к продакшену для MVP | Раздел 4.3 плана |

---

# ФАЗА 4: ШАБЛОНЫ СЕРВИСОВ (templates/services/)

## 4.1 Адаптация существующих шаблонов

| # | Статус | Директория | Описание | Источник .ai-framework |
|---|--------|------------|----------|----------------------|
| 4.1.1 | [ ] | `templates/services/fastapi_business_api/` | Business API шаблон | templates/services/template_business_api/ |
| 4.1.2 | [ ] | `templates/services/aiogram_bot/` | Telegram Bot шаблон | templates/services/template_business_bot/ |
| 4.1.3 | [ ] | `templates/services/asyncio_worker/` | Background Worker шаблон | templates/services/template_business_worker/ |
| 4.1.4 | [ ] | `templates/services/postgres_data_api/` | PostgreSQL Data API шаблон | templates/services/template_data_postgres_api/ |
| 4.1.5 | [ ] | `templates/services/mongo_data_api/` | MongoDB Data API шаблон | templates/services/template_data_mongo_api/ |

### Детали задачи 4.1.1: fastapi_business_api/

**Файлы для адаптации:**
```
templates/services/fastapi_business_api/
├── Dockerfile
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   └── health.py
│   │   └── dependencies.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/
│   │   └── dtos/
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── http/
│   │   └── messaging/
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── base.py
│   └── core/
│       ├── __init__.py
│       ├── config.py
│       └── logging.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    └── integration/
```

**Изменения при адаптации:**
1. Все docstrings на русском языке
2. Добавить комментарии на русском
3. Переменные и названия — snake_case
4. Добавить шаблоны для замены {context}, {domain}

---

# ФАЗА 5: ОБЩИЕ КОМПОНЕНТЫ (templates/shared/)

## 5.1 Утилиты

| # | Статус | Файл | Описание |
|---|--------|------|----------|
| 5.1.1 | [ ] | `templates/shared/utils/logger.py` | Структурированное логирование (structlog) |
| 5.1.2 | [ ] | `templates/shared/utils/validators.py` | Общие валидаторы |
| 5.1.3 | [ ] | `templates/shared/utils/exceptions.py` | Кастомные исключения |
| 5.1.4 | [ ] | `templates/shared/utils/pagination.py` | Пагинация |
| 5.1.5 | [ ] | `templates/shared/utils/request_id.py` | Генерация request_id |

---

## 5.2 Схемы

| # | Статус | Файл | Описание |
|---|--------|------|----------|
| 5.2.1 | [ ] | `templates/shared/schemas/base.py` | Базовые Pydantic схемы |
| 5.2.2 | [ ] | `templates/shared/schemas/pagination.py` | Схемы пагинации |
| 5.2.3 | [ ] | `templates/shared/schemas/errors.py` | Схемы ошибок |

---

## 5.3 HTTP клиенты

| # | Статус | Файл | Описание |
|---|--------|------|----------|
| 5.3.1 | [ ] | `templates/shared/http_clients/base_client.py` | Базовый HTTP клиент (httpx) |
| 5.3.2 | [ ] | `templates/shared/http_clients/data_api_client.py` | Клиент для Data API |

---

## 5.4 Тестирование

| # | Статус | Файл | Описание |
|---|--------|------|----------|
| 5.4.1 | [ ] | `templates/shared/testing/base_fixtures.py` | Базовые pytest фикстуры |
| 5.4.2 | [ ] | `templates/shared/testing/factory_base.py` | Базовые фабрики для тестов |

---

# ФАЗА 6: ИНФРАСТРУКТУРА (templates/infrastructure/)

## 6.1 Docker Compose

| # | Статус | Файл | Описание | Источник .ai-framework |
|---|--------|------|----------|----------------------|
| 6.1.1 | [ ] | `templates/infrastructure/docker-compose/docker-compose.yml` | Базовый docker-compose | templates/infrastructure/docker-compose.yml |
| 6.1.2 | [ ] | `templates/infrastructure/docker-compose/docker-compose.dev.yml` | Dev overrides | templates/infrastructure/docker-compose.dev.yml |
| 6.1.3 | [ ] | `templates/infrastructure/docker-compose/docker-compose.prod.yml` | Production config | templates/infrastructure/docker-compose.prod.yml |
| 6.1.4 | [ ] | `templates/infrastructure/docker-compose/.env.example` | Шаблон переменных окружения | templates/infrastructure/.env.example |
| 6.1.5 | [ ] | `templates/infrastructure/Makefile` | Команды проекта (build, run, test) | Раздел 3.3.4 плана |

---

## 6.2 Nginx

| # | Статус | Файл | Описание | Источник .ai-framework |
|---|--------|------|----------|----------------------|
| 6.2.1 | [ ] | `templates/infrastructure/nginx/nginx.conf` | Конфигурация Nginx | templates/nginx/nginx.conf |
| 6.2.2 | [ ] | `templates/infrastructure/nginx/Dockerfile` | Dockerfile для Nginx | templates/nginx/Dockerfile |
| 6.2.3 | [ ] | `templates/infrastructure/nginx/conf.d/upstream.conf` | Upstream конфигурация | Раздел 3.3.4 плана |
| 6.2.4 | [ ] | `templates/infrastructure/nginx/conf.d/api-gateway.conf` | API Gateway конфигурация | Раздел 3.3.4 плана |

---

## 6.3 GitHub Actions

| # | Статус | Файл | Описание | Источник .ai-framework |
|---|--------|------|----------|----------------------|
| 6.3.1 | [ ] | `templates/infrastructure/github-actions/.github/workflows/ci.yml` | CI pipeline | templates/ci-cd/.github/workflows/ci.yml |
| 6.3.2 | [ ] | `templates/infrastructure/github-actions/.github/workflows/cd.yml` | CD pipeline | templates/ci-cd/.github/workflows/cd.yml |

---

# ФАЗА 7: ШАБЛОНЫ ДОКУМЕНТОВ (docs/)

## 7.1 Шаблоны для генерации

| # | Статус | Файл | Описание |
|---|--------|------|----------|
| 7.1.1 | [ ] | `docs/prd/template.md` | Шаблон PRD документа |
| 7.1.2 | [ ] | `docs/architecture/template.md` | Шаблон архитектурного плана |
| 7.1.3 | [ ] | `docs/plans/template.md` | Шаблон плана фичи |
| 7.1.4 | [ ] | `docs/reports/review-template.md` | Шаблон отчёта ревью |
| 7.1.5 | [ ] | `docs/reports/qa-template.md` | Шаблон QA отчёта |
| 7.1.6 | [ ] | `docs/reports/validation-template.md` | Шаблон отчёта валидации |
| 7.1.7 | [ ] | `docs/rtm-template.md` | Шаблон матрицы трассировки требований |
| 7.1.8 | [ ] | `docs/tasklists/template.md` | Шаблон чек-листа задач |

### Детали задачи 7.1.1: template.md (PRD)

**Содержимое шаблона:**
```markdown
# PRD: {Название проекта/фичи}

**Версия**: 1.0
**Дата**: {YYYY-MM-DD}
**Автор**: AI Agent (Аналитик)
**Статус**: Draft | Review | Approved

---

## 1. Обзор

### 1.1 Проблема
{Описание проблемы, которую решает проект/фича}

### 1.2 Решение
{Краткое описание предлагаемого решения}

### 1.3 Целевая аудитория
{Кто будет использовать}

---

## 2. Функциональные требования

| ID | Название | Описание | Приоритет | Критерий приёмки |
|----|----------|----------|-----------|------------------|
| FR-001 | {Название} | {Описание} | Must/Should/Could | {Как проверить} |

---

## 3. UI/UX требования

| ID | Название | Описание | Приоритет |
|----|----------|----------|-----------|
| UI-001 | {Название} | {Описание} | Must/Should/Could |

---

## 4. Нефункциональные требования

| ID | Название | Описание | Метрика |
|----|----------|----------|---------|
| NF-001 | Производительность | {Описание} | {Измеримая метрика} |

---

## 5. Ограничения и допущения

### 5.1 Ограничения
- {Ограничение 1}

### 5.2 Допущения
- {Допущение 1}

---

## 6. Открытые вопросы

| # | Вопрос | Статус | Решение |
|---|--------|--------|---------|
| 1 | {Вопрос} | Open/Resolved | {Решение} |

---

## 7. Матрица трассировки требований

| Req ID | Описание | Статус | Файл реализации | Тест |
|--------|----------|--------|-----------------|------|
| FR-001 | {Описание} | Pending | — | — |

---

## Качественные ворота

- [ ] **PRD_READY**: Все секции заполнены, нет блокирующих вопросов
```

---

# СВОДКА

## Общее количество файлов

| Фаза | Категория | Количество файлов |
|------|-----------|-------------------|
| 0 | Корневые файлы | 4 |
| 1 | .claude/ (settings, agents, commands) | 17 |
| 2 | roles/ | 31 |
| 3 | knowledge/ | 43 |
| 4 | templates/services/ | 5 директорий (~50 файлов) |
| 5 | templates/shared/ | 12 |
| 6 | templates/infrastructure/ | 11 |
| 7 | docs/ шаблоны | 8 |
| **ИТОГО** | | **~176 файлов** |

---

## Порядок выполнения

```
Фаза 0 (Основа) ──────────────────────────────────────────►
                │
                ▼
Фаза 1 (.claude/) ────────────────────────────────────────►
                │
                ▼
Фаза 2 (roles/) ──────────────────────────────────────────►
                │
                ▼
Фаза 3 (knowledge/) ──────────────────────────────────────►
                │
                ▼
Фаза 4 (templates/services/) ─────────────────────────────►
                │
                ▼
Фаза 5 (templates/shared/) ───────────────────────────────►
                │
                ▼
Фаза 6 (templates/infrastructure/) ───────────────────────►
                │
                ▼
Фаза 7 (docs/) ───────────────────────────────────────────►
```

---

## Критический путь

Минимально необходимые файлы для работающего прототипа:

1. `CLAUDE.md` — без него AI не поймёт контекст
2. `.claude/agents/analyst.md` — нужен для /idea
3. `.claude/commands/idea.md` — первая команда пайплайна
4. `docs/prd/template.md` — шаблон для генерации PRD

**С этими 4 файлами можно запустить первый этап пайплайна.**

---

## Зависимости между фазами

```
Фаза 0 ←── Фаза 1 (агенты читают CLAUDE.md)
Фаза 1 ←── Фаза 2 (roles/ детализируют агентов)
Фаза 1 ←── Фаза 3 (knowledge/ используется агентами)
Фаза 2 ←── Фаза 4 (templates используются Реализатором)
Фаза 4 ←── Фаза 5 (shared/ используется в templates/services/)
Фаза 4 ←── Фаза 6 (infrastructure/ используется в templates/services/)
Фаза 1 ←── Фаза 7 (docs/ шаблоны используются агентами)
```

---

## Оценка времени

| Фаза | Файлов | Время (часы) |
|------|--------|--------------|
| 0 | 4 | 2 |
| 1 | 17 | 5 |
| 2 | 31 | 8 |
| 3 | 43 | 7 |
| 4 | ~50 | 4 (адаптация) |
| 5 | 12 | 3 |
| 6 | 11 | 2 |
| 7 | 8 | 2 |
| **ИТОГО** | **~176** | **~33 часа** |
