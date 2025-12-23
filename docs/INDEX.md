# Индекс файлов AIDD-MVP Generator

> **Назначение**: Навигация по файлам ФРЕЙМВОРКА (генератора).
> Для структуры целевого проекта см. [target-project-structure.md](target-project-structure.md)

---

## Точки входа

| Файл | Назначение | Когда читать |
|------|-----------|--------------|
| [CLAUDE.md](../CLAUDE.md) | Главная точка входа | Первым |
| [initialization.md](initialization.md) | Алгоритм инициализации (4 фазы) | При запуске команды |
| [conventions.md](../conventions.md) | Соглашения о коде | При написании кода |
| [workflow.md](../workflow.md) | Пайплайн (этапы 0-8) | При работе с пайплайном |
| [artifact-naming.md](artifact-naming.md) | Система именования артефактов (FID) | При создании артефактов |

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
| `/aidd-init` | [.claude/commands/aidd-init.md](../.claude/commands/aidd-init.md) | Bootstrap (инициализация ЦП) |
| `/aidd-idea` | [.claude/commands/aidd-idea.md](../.claude/commands/aidd-idea.md) | Создание PRD |
| `/aidd-research` | [.claude/commands/aidd-research.md](../.claude/commands/aidd-research.md) | Исследование |
| `/aidd-plan` | [.claude/commands/aidd-plan.md](../.claude/commands/aidd-plan.md) | Архитектура (CREATE) |
| `/aidd-feature-plan` | [.claude/commands/aidd-feature-plan.md](../.claude/commands/aidd-feature-plan.md) | План фичи (FEATURE) |
| `/aidd-generate` | [.claude/commands/aidd-generate.md](../.claude/commands/aidd-generate.md) | Генерация кода |
| `/aidd-review` | [.claude/commands/aidd-review.md](../.claude/commands/aidd-review.md) | Код-ревью |
| `/aidd-test` | [.claude/commands/aidd-test.md](../.claude/commands/aidd-test.md) | Тестирование |
| `/aidd-validate` | [.claude/commands/aidd-validate.md](../.claude/commands/aidd-validate.md) | Валидация |
| `/aidd-deploy` | [.claude/commands/aidd-deploy.md](../.claude/commands/aidd-deploy.md) | Деплой |

> Обзор пайплайна: [CLAUDE.md](../CLAUDE.md#9-этапный-пайплайн)

---

## База знаний

> Индекс knowledge base: [knowledge/README.md](../knowledge/README.md)

### Архитектура
| Файл | Тема |
|------|------|
| [knowledge/architecture/ddd-hexagonal.md](../knowledge/architecture/ddd-hexagonal.md) | DDD/Hexagonal архитектура |
| [knowledge/architecture/project-structure.md](../knowledge/architecture/project-structure.md) | Структура проекта |
| [knowledge/architecture/service-separation.md](../knowledge/architecture/service-separation.md) | Разделение сервисов |
| [knowledge/architecture/data-access.md](../knowledge/architecture/data-access.md) | Доступ к данным |

### Сервисы
| Папка | Тема |
|-------|------|
| [knowledge/services/fastapi/](../knowledge/services/fastapi/) | FastAPI сервисы (5 файлов) |
| [knowledge/services/aiogram/](../knowledge/services/aiogram/) | Telegram боты (4 файла) |
| [knowledge/services/asyncio-workers/](../knowledge/services/asyncio-workers/) | Background workers (3 файла) |
| [knowledge/services/data-services/](../knowledge/services/data-services/) | Data Services (2 файла) |

### Интеграции
| Папка | Тема |
|-------|------|
| [knowledge/integrations/http/](../knowledge/integrations/http/) | HTTP клиенты (3 файла) |
| [knowledge/integrations/redis/](../knowledge/integrations/redis/) | Redis интеграция (2 файла) |

### Инфраструктура
| Файл | Тема |
|------|------|
| [knowledge/infrastructure/docker-compose.md](../knowledge/infrastructure/docker-compose.md) | Docker Compose |
| [knowledge/infrastructure/dockerfile.md](../knowledge/infrastructure/dockerfile.md) | Dockerfile |
| [knowledge/infrastructure/nginx.md](../knowledge/infrastructure/nginx.md) | Nginx gateway |
| [knowledge/infrastructure/ci-cd.md](../knowledge/infrastructure/ci-cd.md) | CI/CD |

### Качество
| Путь | Тема |
|------|------|
| [knowledge/quality/testing/](../knowledge/quality/testing/) | Тестирование (5 файлов) |
| [knowledge/quality/logging/](../knowledge/quality/logging/) | Логирование (2 файла) |
| [knowledge/quality/dry-kiss-yagni.md](../knowledge/quality/dry-kiss-yagni.md) | Принципы DRY/KISS/YAGNI |
| [knowledge/quality/production-requirements.md](../knowledge/quality/production-requirements.md) | Production требования |

---

## Шаблоны документов

| Шаблон | Путь в генераторе | Создаёт в целевом проекте |
|--------|-------------------|---------------------------|
| PRD | [templates/documents/prd-template.md](../templates/documents/prd-template.md) | `ai-docs/docs/prd/{name}-prd.md` |
| Research Report | [templates/documents/research-report-template.md](../templates/documents/research-report-template.md) | `ai-docs/docs/research/{name}-research.md` |
| Архитектура | [templates/documents/architecture-template.md](../templates/documents/architecture-template.md) | `ai-docs/docs/architecture/{name}-plan.md` |
| План фичи (FEATURE) | [templates/documents/feature-plan-template.md](../templates/documents/feature-plan-template.md) | `ai-docs/docs/plans/{feature}-plan.md` |
| План реализации | [templates/documents/implementation-plan-template.md](../templates/documents/implementation-plan-template.md) | `ai-docs/docs/architecture/{name}-impl.md` |
| Отчёт ревью | [templates/documents/review-report-template.md](../templates/documents/review-report-template.md) | `ai-docs/docs/reports/review-report.md` |
| Отчёт QA | [templates/documents/qa-report-template.md](../templates/documents/qa-report-template.md) | `ai-docs/docs/reports/qa-report.md` |
| Отчёт валидации | [templates/documents/validation-report-template.md](../templates/documents/validation-report-template.md) | `ai-docs/docs/reports/validation-report.md` |
| RTM | [templates/documents/rtm-template.md](../templates/documents/rtm-template.md) | `ai-docs/docs/rtm.md` |
| Состояние пайплайна | [templates/documents/pipeline-state-template.json](../templates/documents/pipeline-state-template.json) | `.pipeline-state.json` |

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

## Шаблоны проекта (корневые файлы ЦП)

> Файлы, создаваемые в корне целевого проекта при `/aidd-init`.

| Шаблон | Путь в генераторе | Создаёт в ЦП | Назначение |
|--------|-------------------|--------------|------------|
| CLAUDE.md | [templates/project/CLAUDE.md.template](../templates/project/CLAUDE.md.template) | `./CLAUDE.md` | Точка входа для AI |
| README.md | [templates/project/README.md.template](../templates/project/README.md.template) | `./README.md` | Документация проекта |
| .gitignore | [templates/project/.gitignore.template](../templates/project/.gitignore.template) | `./.gitignore` | Игнорируемые файлы |
| .env.example | [templates/project/.env.example.template](../templates/project/.env.example.template) | `./.env.example` | Пример переменных окружения |
| settings.local | [templates/project/.claude/settings.local.json.example](../templates/project/.claude/settings.local.json.example) | `./.claude/settings.local.json.example` | Локальные настройки Claude Code |

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
| Алгоритм инициализации | [initialization.md](initialization.md) |
| Какие файлы создавать | [target-project-structure.md](target-project-structure.md) |
| Правила кода | [conventions.md](../conventions.md) |
| Этапы процесса | [workflow.md](../workflow.md) |
| Порядок чтения файлов | [initialization.md](initialization.md) → "Таблица порядка чтения" |
| Критерии ЦП vs Фреймворк | [initialization.md](initialization.md) → "Критерии определения источника" |
| Инструкции роли | `.claude/agents/{role}.md` |
| Шаблон документа | `templates/documents/*.md` |
| Шаблон сервиса | `templates/services/*/` |
| Шаблон файлов ЦП | `templates/project/*.template` |

---

## Аудит документации

| Шаблон | Назначение |
|--------|-----------|
| [audit/templates/comprehensive-audit.md](audit/templates/comprehensive-audit.md) | Комплексный аудит (12 smoke tests, 16 objectives) |

---

## См. также

- [initialization.md](initialization.md) — Алгоритм инициализации (4 фазы)
- [NAVIGATION.md](NAVIGATION.md) — Навигационная матрица по этапам
- [PIPELINE-TREE.md](PIPELINE-TREE.md) — Дерево всех пайплайнов
- [target-project-structure.md](target-project-structure.md) — Структура целевого проекта

---

**Версия**: 2.0
**Обновлён**: 2025-12-21
