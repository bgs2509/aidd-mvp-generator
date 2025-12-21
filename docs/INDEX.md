# Индекс файлов AIDD-MVP Generator

> **Назначение**: Навигация по файлам ФРЕЙМВОРКА (генератора).
> Для структуры целевого проекта см. [target-project-structure.md](target-project-structure.md)

---

## Точки входа

| Файл | Назначение | Когда читать |
|------|-----------|--------------|
| [CLAUDE.md](../CLAUDE.md) | Главная точка входа | Первым |
| [conventions.md](../conventions.md) | Соглашения о коде | При написании кода |
| [workflow.md](../workflow.md) | 8-этапный процесс | При работе с пайплайном |

---

## Роли агентов

| Файл | Роль | Этапы | Ворота |
|------|------|-------|--------|
| [.claude/agents/analyst.md](../.claude/agents/analyst.md) | Аналитик | 1 | PRD_READY |
| [.claude/agents/researcher.md](../.claude/agents/researcher.md) | Исследователь | 2 | RESEARCH_DONE |
| [.claude/agents/architect.md](../.claude/agents/architect.md) | Архитектор | 3 | PLAN_APPROVED |
| [.claude/agents/implementer.md](../.claude/agents/implementer.md) | Реализатор | 4 | IMPLEMENT_OK |
| [.claude/agents/reviewer.md](../.claude/agents/reviewer.md) | Ревьюер | 5 | REVIEW_OK |
| [.claude/agents/qa.md](../.claude/agents/qa.md) | QA | 6 | QA_PASSED |
| [.claude/agents/validator.md](../.claude/agents/validator.md) | Валидатор | 7-8 | ALL_GATES_PASSED |

---

## Slash-команды

| Команда | Файл | Описание |
|---------|------|----------|
| `/idea` | [.claude/commands/idea.md](../.claude/commands/idea.md) | Создание PRD |
| `/research` | [.claude/commands/research.md](../.claude/commands/research.md) | Исследование |
| `/plan` | [.claude/commands/plan.md](../.claude/commands/plan.md) | Архитектура (CREATE) |
| `/feature-plan` | [.claude/commands/feature-plan.md](../.claude/commands/feature-plan.md) | План фичи (FEATURE) |
| `/generate` | [.claude/commands/generate.md](../.claude/commands/generate.md) | Генерация кода |
| `/review` | [.claude/commands/review.md](../.claude/commands/review.md) | Код-ревью |
| `/test` | [.claude/commands/test.md](../.claude/commands/test.md) | Тестирование |
| `/validate` | [.claude/commands/validate.md](../.claude/commands/validate.md) | Валидация |
| `/deploy` | [.claude/commands/deploy.md](../.claude/commands/deploy.md) | Деплой |

---

## База знаний

### Архитектура
| Файл | Тема |
|------|------|
| [knowledge/architecture/ddd-hexagonal.md](../knowledge/architecture/ddd-hexagonal.md) | DDD/Hexagonal архитектура |
| [knowledge/architecture/http-only.md](../knowledge/architecture/http-only.md) | HTTP-only принцип |
| [knowledge/architecture/project-structure.md](../knowledge/architecture/project-structure.md) | Структура проекта |
| [knowledge/architecture/maturity-levels.md](../knowledge/architecture/maturity-levels.md) | Уровни зрелости |

### Сервисы
| Файл | Тема |
|------|------|
| [knowledge/services/fastapi.md](../knowledge/services/fastapi.md) | FastAPI сервисы |
| [knowledge/services/aiogram.md](../knowledge/services/aiogram.md) | Telegram боты |
| [knowledge/services/workers.md](../knowledge/services/workers.md) | Background workers |

### Интеграции
| Файл | Тема |
|------|------|
| [knowledge/integrations/http-clients.md](../knowledge/integrations/http-clients.md) | HTTP клиенты |
| [knowledge/integrations/redis.md](../knowledge/integrations/redis.md) | Redis интеграция |

### Инфраструктура
| Файл | Тема |
|------|------|
| [knowledge/infrastructure/docker.md](../knowledge/infrastructure/docker.md) | Docker контейнеры |
| [knowledge/infrastructure/nginx.md](../knowledge/infrastructure/nginx.md) | Nginx gateway |
| [knowledge/infrastructure/github-actions.md](../knowledge/infrastructure/github-actions.md) | CI/CD |

### Качество
| Файл | Тема |
|------|------|
| [knowledge/quality/testing.md](../knowledge/quality/testing.md) | Тестирование |
| [knowledge/quality/logging.md](../knowledge/quality/logging.md) | Логирование |

---

## Шаблоны документов

| Шаблон | Путь в генераторе | Создаёт в целевом проекте |
|--------|-------------------|---------------------------|
| PRD | [docs/templates/prd-template.md](templates/prd-template.md) | `ai-docs/docs/prd/{name}-prd.md` |
| Архитектура | [docs/templates/architecture-template.md](templates/architecture-template.md) | `ai-docs/docs/architecture/{name}-plan.md` |

---

## Шаблоны сервисов

| Тип сервиса | Путь шаблона | Порт |
|-------------|-------------|------|
| Business API | [templates/services/fastapi_business_api/](../templates/services/fastapi_business_api/) | 8000-8099 |
| Data API (PostgreSQL) | [templates/services/postgres_data_api/](../templates/services/postgres_data_api/) | 8001 |
| Data API (MongoDB) | [templates/services/mongo_data_api/](../templates/services/mongo_data_api/) | 8002 |
| Telegram Bot | [templates/services/aiogram_bot/](../templates/services/aiogram_bot/) | — |
| Background Worker | [templates/services/asyncio_worker/](../templates/services/asyncio_worker/) | — |

---

## Инфраструктурные шаблоны

| Компонент | Путь |
|-----------|------|
| Docker | [templates/infrastructure/docker/](../templates/infrastructure/docker/) |
| Nginx | [templates/infrastructure/nginx/](../templates/infrastructure/nginx/) |
| GitHub Actions | [templates/infrastructure/github-actions/](../templates/infrastructure/github-actions/) |

---

## Детальные инструкции (roles/)

### Аналитик
| Файл | Функция |
|------|---------|
| [roles/analyst/initialization.md](../roles/analyst/initialization.md) | Инициализация |
| [roles/analyst/prompt-validation.md](../roles/analyst/prompt-validation.md) | Валидация промпта |
| [roles/analyst/requirements-gathering.md](../roles/analyst/requirements-gathering.md) | Сбор требований |
| [roles/analyst/prd-formation.md](../roles/analyst/prd-formation.md) | Формирование PRD |

### Исследователь
| Файл | Функция |
|------|---------|
| [roles/researcher/codebase-analysis.md](../roles/researcher/codebase-analysis.md) | Анализ кода |
| [roles/researcher/pattern-identification.md](../roles/researcher/pattern-identification.md) | Выявление паттернов |
| [roles/researcher/constraint-identification.md](../roles/researcher/constraint-identification.md) | Ограничения |

### Архитектор
| Файл | Функция |
|------|---------|
| [roles/architect/architecture-design.md](../roles/architect/architecture-design.md) | Проектирование |
| [roles/architect/maturity-level-selection.md](../roles/architect/maturity-level-selection.md) | Выбор уровня |
| [roles/architect/service-naming.md](../roles/architect/service-naming.md) | Именование |
| [roles/architect/api-contracts.md](../roles/architect/api-contracts.md) | API контракты |

### Реализатор
| Файл | Функция |
|------|---------|
| [roles/implementer/infrastructure-setup.md](../roles/implementer/infrastructure-setup.md) | Инфраструктура |
| [roles/implementer/data-service.md](../roles/implementer/data-service.md) | Data Service |
| [roles/implementer/business-api.md](../roles/implementer/business-api.md) | Business API |
| [roles/implementer/testing.md](../roles/implementer/testing.md) | Тестирование |

### Ревьюер
| Файл | Функция |
|------|---------|
| [roles/reviewer/architecture-compliance.md](../roles/reviewer/architecture-compliance.md) | Архитектура |
| [roles/reviewer/convention-compliance.md](../roles/reviewer/convention-compliance.md) | Соглашения |

### QA
| Файл | Функция |
|------|---------|
| [roles/qa/test-execution.md](../roles/qa/test-execution.md) | Запуск тестов |
| [roles/qa/coverage-verification.md](../roles/qa/coverage-verification.md) | Покрытие |

### Валидатор
| Файл | Функция |
|------|---------|
| [roles/validator/quality-gates.md](../roles/validator/quality-gates.md) | Проверка ворот |
| [roles/validator/artifact-verification.md](../roles/validator/artifact-verification.md) | Верификация |

---

## Быстрый поиск

| Ищу | Смотреть |
|----|----------|
| Как начать проект | [CLAUDE.md](../CLAUDE.md) → Быстрый старт |
| Какие файлы создавать | [target-project-structure.md](target-project-structure.md) |
| Правила кода | [conventions.md](../conventions.md) |
| Этапы процесса | [workflow.md](../workflow.md) |
| Инструкции роли | `.claude/agents/{role}.md` |
| Шаблон документа | `docs/templates/*.md` |
| Шаблон сервиса | `templates/services/*/` |

---

## См. также

- [NAVIGATION.md](NAVIGATION.md) — Навигационная матрица по этапам
- [target-project-structure.md](target-project-structure.md) — Структура целевого проекта

---

**Версия**: 1.0
**Создан**: 2025-12-21
