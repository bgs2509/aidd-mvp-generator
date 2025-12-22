# План: Фреймворк AIDD-MVP Generator

**Создан**: 2025-12-19
**Статус**: В разработке

---

## Обзор

Создание фреймворка для быстрой генерации MVP проектов, объединяющего:
- **Методологию AIDD** (роли, качественные gates, артефакты) из статьи на Хабре
- **Архитектуру из .ai-framework** (шаблоны, паттерны, инфраструктура)

**Качество**: Готово к продакшену сразу (без промежуточных стадий)
- Полный процесс AIDD с качественными воротами
- Продакшн-качество кода с первого запуска
- Полный стек: Nginx, SSL, тесты, CI/CD, логирование

> **⚠️ Ограничение scope**: Этот фреймворк создаёт ТОЛЬКО **Level 2 (MVP)** версии.
> Уровни PoC, Production и Enterprise из `.ai-framework/docs/reference/maturity-levels.md`
> не поддерживаются. Все генерируемые проекты включают:
> - Docker-compose + dev overrides
> - Структурированное логирование
> - Покрытие тестами ≥75%
> - ~10 мин на генерацию

---

# ЧАСТЬ 1: ИСХОДНЫЕ ДАННЫЕ ИЗ СТАТЬИ AIDD

**Источник**: https://habr.com/ru/articles/974924/
**Название**: AI-Driven Development (AIDD): Полное руководство

## 1.1 Концепция AIDD

AIDD превращает LLM из "одного большого мозга" в "команду ролей" для управляемой разработки.
Вместо "вайб-кодинга" предлагается структурированный процесс с качественными воротами.

**Ключевая идея**: Артефакты хранятся в репозитории как "структурированная память", не полагаясь на "память чата".

## 1.2 Роли AIDD

Статья определяет **8 ролей** AI-агентов: Аналитик, Исследователь, Планировщик, Реализатор, Ревьюер, QA, **Техпис**, Валидатор.

> 👥 **MVP-адаптация (7 ролей)** — см. [раздел 3.3](#33-таблицы-соответствия-функций-ролей).
> Техпис исключён — документация генерируется автоматически.

## 1.3 Структура репозитория (из статьи)

```
project/
├── conventions.md          # Соглашения проекта (код, стиль, именование)
├── CLAUDE.md              # Инструкции для Claude Code
├── workflow.md            # Описание процесса разработки
│
├── .claude/               # Конфигурация Claude Code
│   ├── agents/            # Определения ролей AI-агентов
│   │   ├── analyst.md
│   │   ├── researcher.md
│   │   ├── planner.md
│   │   ├── implementer.md
│   │   ├── reviewer.md
│   │   ├── qa.md
│   │   ├── tech-writer.md
│   │   └── validator.md
│   │
│   ├── commands/          # Slash-команды
│   │   ├── idea.md        # /idea → PRD
│   │   ├── researcher.md  # /researcher → анализ кода
│   │   ├── plan.md        # /plan → архитектура
│   │   ├── tasks.md       # /tasks → декомпозиция
│   │   ├── implement.md   # /implement → код
│   │   ├── review.md      # /review → ревью
│   │   ├── qa.md          # /qa → тестирование
│   │   ├── docs-update.md # /docs-update → документация
│   │   └── validate.md    # /validate → проверка ворот
│   │
│   └── hooks/             # Pre/Post обработчики
│       └── settings.json  # Блокировка нарушений
│
├── docs/                  # Артефакты разработки
│   ├── prd/              # Документы требований продукта
│   ├── plan/             # Планы архитектуры
│   ├── tasklist/         # Чек-листы задач
│   └── research/         # Технические исследования
│
└── reports/
    └── qa/               # QA отчёты
```

## 1.4 Качественные ворота (из статьи)

| Этап | ID ворот | Критерии прохождения |
|------|----------|----------------------|
| Проект | `AGREEMENTS_ON` | conventions.md, workflow.md, базовые агенты присутствуют |
| PRD | `PRD_READY` | Все секции заполнены, метрики определены, нет блокирующих вопросов |
| Архитектура | `PLAN_APPROVED` | Компоненты описаны, контракты определены, NFR учтены |
| Задачи | `TASKLIST_READY` | Мелкие задачи с критериями приёмки |
| Реализация | `IMPLEMENT_STEP_OK` | Код написан + тесты проходят |
| Ревью | `REVIEW_OK` | CI зелёный, нет блокирующих комментариев |
| QA | `RELEASE_READY` | Нет критических багов |
| Документация | `DOCS_UPDATED` | Архитектура и runbook актуальны |

## 1.5 Три уровня внедрения AIDD

### Минимальный AIDD
- `CLAUDE.md` + `conventions.md`
- Шаблоны PRD и чек-листа задач
- Базовый workflow без автоматизации

### Полный AIDD
- Полный набор агентов в `.claude/agents/`
- Slash-команды для каждого этапа
- Валидатор и оркестратор

### Строгий AIDD
- Хуки в `.claude/settings.json` блокируют нарушения ворот
- Headless CI интеграция
- Автоматические пре-релизные проверки

## 1.6 Пример рабочего процесса по тикету (T-104)

```
1. /idea T-104      → создание PRD аналитиком
2. /researcher T-104 → анализ кодовой базы
3. /plan T-104      → проектирование архитектуры
4. /tasks T-104     → декомпозиция задач
5. /implement T-104 → реализация малыми шагами (с подтверждением)
6. /review T-104    → код-ревью с проверкой соответствия
7. /qa T-104        → финальное QA тестирование
8. /docs-update T-104 → обновление документации
9. /validate T-104  → проверка всех ворот
```

## 1.7 Ключевые принципы из статьи

1. **Артефакты = память**: Не полагаться на память чата, всё в файлах
2. **Независимые задачи**: Каждая задача должна иметь проверяемые критерии приёмки
3. **Ранняя валидация**: Валидатор помогает выявлять "галлюцинации" рано
4. **Хуки для контроля**: Предотвращение обхода этапов, блокировка Edit/Write без пройденных ворот
5. **Управляемый процесс**: "Не вайб-кодинг, а управляемый процесс, интегрированный в SDLC"

---

# ЧАСТЬ 2: ИСХОДНЫЕ ДАННЫЕ ИЗ .ai-framework

**Источник**: /home/bgs/Henry_Bud_GitHub/aidd-mvp-generator/.ai-framework/
**Название**: AI Generator для асинхронных микросервисов

## 2.1 Архитектура: Улучшенный гибридный подход

```
┌─────────────────────────────────────────────────────────────┐
│                    СЛОЙ ПРЕДСТАВЛЕНИЯ                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Бизнес API   │  │ Бизнес Бот   │  │    Воркер    │      │
│  │   (FastAPI)  │  │   (Aiogram)  │  │   (AsyncIO)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│               ТОЛЬКО HTTP (без прямого доступа к БД)         │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                     ┌───────┴───────┐
                     │               │
         ┌───────────▼─────┐  ┌──────▼───────────┐
         │  Сервис данных  │  │  Сервис данных   │
         │  PostgreSQL API │  │   MongoDB API    │
         │   (Порт: 8001)  │  │   (Порт: 8002)   │
         └─────────────────┘  └──────────────────┘
                 │                      │
         ┌───────▼─────────┐    ┌──────▼──────────┐
         │   PostgreSQL    │    │    MongoDB      │
         │    База данных  │    │    База данных  │
         └─────────────────┘    └─────────────────┘
```

## 2.2 Ключевые принципы архитектуры

| Принцип | Описание |
|---------|----------|
| **Только HTTP доступ к данным** | Бизнес-сервисы НИКОГДА не обращаются к БД напрямую |
| **Единый Event Loop** | Каждый сервис владеет своим event loop (без sharing) |
| **Async-First** | Все I/O операции используют async/await |
| **Типобезопасность** | Полные type hints, mypy strict режим |
| **DDD и Hexagonal** | Domain-Driven Design с портами/адаптерами |
| **Разделение сервисов** | FastAPI, Aiogram, Workers в отдельных процессах |

## 2.3 Типы сервисов

### Бизнес API (FastAPI)
- REST API эндпоинты
- Порт 8000-8099
- Вызывает Data Services через HTTP
- БЕЗ доступа к базе данных

### Бизнес Бот (Aiogram)
- Telegram Bot API
- Event-driven обработчики
- Вызывает Data Services через HTTP
- БЕЗ доступа к базе данных

### Бизнес Воркер (AsyncIO)
- Фоновая обработка задач
- Асинхронная обработка
- Вызывает Data Services через HTTP
- БЕЗ доступа к базе данных

### Data API PostgreSQL
- CRUD операции
- Порт 8001
- Прямой доступ к PostgreSQL
- SQLAlchemy + Alembic

### Data API MongoDB
- Операции с документами
- Порт 8002
- Прямой доступ к MongoDB
- Motor async драйвер

## 2.4 Структура сервиса (DDD/Hexagonal)

```
service/
├── src/
│   ├── api/              # API слой (FastAPI роуты)
│   │   ├── v1/
│   │   │   ├── health.py
│   │   │   └── {domain}_router.py
│   │   └── dependencies.py
│   │
│   ├── application/      # Слой приложения (Use cases)
│   │   ├── services/
│   │   └── dtos/
│   │
│   ├── domain/           # Доменный слой (Чистая бизнес-логика)
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   │
│   ├── infrastructure/   # Инфраструктурный слой (Внешние зависимости)
│   │   ├── http/         # HTTP клиенты к data services
│   │   ├── database/     # Только для Data APIs
│   │   └── messaging/    # Redis и т.д.
│   │
│   ├── schemas/          # Pydantic схемы
│   │   └── base.py
│   │
│   ├── core/             # Основные утилиты
│   │   ├── config.py
│   │   └── logging.py
│   │
│   └── main.py           # Точка входа приложения
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── Dockerfile
├── requirements.txt
└── README.md
```

## 2.5 Шаблоны в .ai-framework/templates/

### services/
```
template_business_api/          # Шаблон FastAPI
├── src/
│   ├── api/v1/health.py
│   ├── schemas/base.py
│   └── main.py
├── tests/
├── Dockerfile
└── requirements.txt

template_business_bot/          # Шаблон Aiogram
├── src/
│   ├── bot/
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   ├── middlewares/
│   │   └── states/
│   └── main.py
├── tests/
├── Dockerfile
└── requirements.txt

template_business_worker/       # Шаблон AsyncIO Worker
├── src/
│   ├── worker/
│   │   ├── handlers/
│   │   └── task_processor.py
│   └── main.py
├── tests/
├── Dockerfile
└── requirements.txt

template_data_postgres_api/     # PostgreSQL Data API
├── src/
│   ├── api/v1/health.py
│   ├── models/base.py
│   ├── repositories/base_repository.py
│   ├── schemas/base.py
│   └── main.py
├── alembic/
├── tests/
├── Dockerfile
└── requirements.txt

template_data_mongo_api/        # MongoDB Data API
├── src/
│   ├── api/v1/health.py
│   ├── models/base.py
│   ├── repositories/base_repository.py
│   ├── schemas/base.py
│   └── main.py
├── tests/
├── Dockerfile
└── requirements.txt
```

### infrastructure/
```
docker-compose.yml          # Разработка
docker-compose.dev.yml      # Dev переопределения
docker-compose.prod.yml     # Продакшн
.env.example                # Шаблон переменных окружения
```

### nginx/
```
nginx.conf                  # Конфиг API Gateway
Dockerfile                  # Образ Nginx
```

### ci-cd/
```
.github/workflows/
├── ci.yml                  # Непрерывная интеграция
└── cd.yml                  # Непрерывное развёртывание
```

## 2.6 Технологический стек .ai-framework

| Категория | Технологии |
|-----------|------------|
| **Ядро** | Python 3.12+, FastAPI 0.115+, Aiogram 3.13+, AsyncIO |
| **Данные** | PostgreSQL 16+, MongoDB 7+, Redis 7+, SQLAlchemy 2.0+ |
| **Инфраструктура** | Docker 24+, Nginx 1.27+, Docker Compose 2.20+ |
| **Наблюдаемость** | Prometheus, Grafana, Jaeger, ELK Stack, Sentry |
| **Качество** | pytest 8.3+, mypy 1.11+, Ruff 0.6+, Testcontainers |
| **CI/CD** | GitHub Actions |

## 2.7 7-этапный AI рабочий процесс

| Этап | Название | Действия |
|------|----------|----------|
| **0** | Инициализация AI | Загрузка контекста фреймворка |
| **1** | Валидация промпта | Проверка полноты пользовательского промпта |
| **2** | Приём требований | Формализация требований |
| **3** | Маппинг архитектуры | Планирование реализации |
| **4** | Генерация кода | Поэтапная генерация кода |
| **5** | Проверка качества | Проверка качества (тесты, линтинг) |
| **6** | QA отчёт и передача | Финальный отчёт и передача |

## 2.8 Соглашения об именовании

**Сервисы**: `{контекст}_{домен}_{тип}`
- `finance_lending_api` - Бизнес API для P2P кредитования
- `healthcare_telemedicine_bot` - Telegram бот для телемедицины
- `construction_house_worker` - Фоновый воркер для строительства

**Шаблоны**: `template_{домен}_{тип}`
- `template_business_api`
- `template_business_bot`
- `template_data_postgres_api`

---

# ЧАСТЬ 3: ПАЙПЛАЙНЫ И СТРУКТУРА MVP ПРОЕКТА

## 3.1 Единый пайплайн AIDD-MVP Generator

**Два режима работы:**
- **CREATE** — создание нового MVP проекта. Запуск: `/idea <описание проекта>`
- **FEATURE** — добавление фичи в существующий MVP. Запуск: `/feature <описание фичи>`

| № | Команда | Агент | CREATE | FEATURE | Ворота |
|---|---------|-------|--------|---------|--------|
| 1 | `/idea` | Аналитик | PRD.md (требования к проекту) | FEATURE_PRD.md (требования к фиче) | PRD_READY |
| 2 | `/research` | Исследователь | Пропуск (нет кодобазы) | RESEARCH.md (анализ кодобазы) | RESEARCH_SKIPPED / RESEARCH_DONE |
| 3 | `/plan` или `/feature-plan` | Архитектор | PLAN.md (полная архитектура) | FEATURE_PLAN.md (дельта к архитектуре) | PLAN_APPROVED |
| 4 | `/generate` | Реализатор | Код + Тесты (с нуля) | Код + Тесты (изменения) | IMPLEMENT_OK |
| 5 | `/review` | Ревьюер | REVIEW.md | REVIEW.md | REVIEW_OK |
| 6 | `/test` | QA | QA_REPORT.md | QA_REPORT.md | QA_PASSED |
| 7 | `/validate` | Валидатор | Статус ворот | Статус ворот | ALL_GATES_PASSED |
| 8 | `/deploy` | Валидатор | Развёрнутый проект | Развёрнутый проект | DEPLOYED |

---

## 3.2 Артефакты пайплайна

> 📋 **Пайплайн (команды, агенты, ворота)** см. таблицу в [разделе 3.1](#31-единый-пайплайн-aidd-mvp-generator)

**Пути артефактов:**
- PRD: `ai-docs/docs/prd/{name}-prd.md`
- Research: `ai-docs/docs/research/{name}-research.md`
- Plan: `ai-docs/docs/architecture/{name}-plan.md` (CREATE) или `ai-docs/docs/plans/{name}-plan.md` (FEATURE)
- Review: `ai-docs/docs/reports/{name}-review.md`
- QA: `ai-docs/docs/reports/{name}-qa.md`

---

## 3.3 Таблицы соответствий файлов ролей

> Каждая таблица связывает функции роли с файлами в `roles/` и документацией `.ai-framework/`.

### 3.3.1 Аналитик (Analyst)

| Функция | Файл роли | Файлы .ai-framework и разделы |
|---------|-----------|-------------------------------|
| **Инициализация (Stage 0)** | `roles/analyst/initialization.md` | `.ai-framework/AGENTS.md` — § AI Agent Reading Order, § Stage 0: Initialization |
| | | `.ai-framework/docs/reference/agent-context-summary.md` — Весь файл (критические правила) |
| | | `.ai-framework/docs/guides/ai-code-generation-master-workflow.md` — § Part 2: Stage 1 Prompt Validation |
| **Верификация промпта** | `roles/analyst/prompt-validation.md` | `.ai-framework/docs/guides/prompt-validation-guide.md` — § 10 обязательных полей, § Checklist |
| | | `.ai-framework/docs/reference/maturity-levels.md` — § Level 1-4 описания, § Time estimates |
| **Сбор требований** | `roles/analyst/requirements-gathering.md` | `.ai-framework/docs/reference/prompt-templates.md` — § Clarification templates |
| | | `.ai-framework/docs/guides/requirements-intake-template.md` — § Template structure, § Required sections |
| | | `.ai-framework/docs/guides/requirements-traceability-guide.md` — § Req ID format (FR-*, UI-*, NF-*) |
| **Формирование PRD** | `roles/analyst/prd-formation.md` | `.ai-framework/docs/guides/analyst-workflow.md` — § PRD structure, § Output format |
| | | `.ai-framework/docs/reference/aidd-roles-reference.md` — § Роль 1: Analyst, § PRD template |

---

### 3.3.2 Исследователь (Researcher)

| Функция | Файл роли | Файлы .ai-framework и разделы |
|---------|-----------|-------------------------------|
| **Анализ кодовой базы** | `roles/researcher/codebase-analysis.md` | `.ai-framework/docs/reference/project-structure.md` — § Canonical layout, § Directory descriptions |
| | | `.ai-framework/ARCHITECTURE.md` — § Improved Hybrid Approach, § Service Types |
| | | `.ai-framework/docs/guides/architecture-guide.md` — § Core principles, § Communication patterns |
| **Выявление паттернов** | `roles/researcher/pattern-identification.md` | `.ai-framework/docs/atomic/architecture/ddd-hexagonal-principles.md` — § Layer separation, § Domain patterns |
| | | `.ai-framework/docs/atomic/architecture/service-separation-principles.md` — § Business vs Data services |
| | | `.ai-framework/docs/atomic/architecture/data-access-architecture.md` — § HTTP-only rule, § Data flow |
| **Выявление ограничений** | `roles/researcher/constraint-identification.md` | `.ai-framework/docs/reference/tech_stack.md` — § Version constraints, § Platform limits |
| | | `.ai-framework/docs/atomic/architecture/event-loop-management.md` — § Single ownership rule |
| | | `.ai-framework/CLAUDE.md` — § Architecture Pre-Checks, § Mandatory rules |
| **Уточнение пайплайна** | `roles/researcher/pipeline-refinement.md` | `.ai-framework/docs/reference/aidd-roles-reference.md` — § Роль 2: Researcher |
| | | `.ai-framework/docs/reference/conditional-stage-rules.md` — § Level-based rules |

---

### 3.3.3 Архитектор (Architect)

| Функция | Файл роли | Файлы .ai-framework и разделы |
|---------|-----------|-------------------------------|
| **Проектирование архитектуры** | `roles/architect/architecture-design.md` | `.ai-framework/ARCHITECTURE.md` — § Overview, § Core Principles, § Service Types |
| | | `.ai-framework/docs/atomic/architecture/improved-hybrid-overview.md` — § Architecture diagram, § Communication flow |
| | | `.ai-framework/docs/atomic/architecture/ddd-hexagonal-principles.md` — § Hexagonal architecture, § Layer responsibilities |
| **Выбор по уровню зрелости** | `roles/architect/maturity-level-selection.md` | `.ai-framework/docs/reference/maturity-levels.md` — § Level features matrix |
| | | `.ai-framework/docs/reference/conditional-stage-rules.md` — § Sub-stage conditions, § Skip rules |
| | | `.ai-framework/docs/reference/ai-navigation-matrix.md` — § Stage 4.x sub-stages, § Required At Level |
| **Именование сервисов** | `roles/architect/service-naming.md` | `.ai-framework/docs/atomic/architecture/naming/README.md` — § 3-part naming, § 4-part criteria |
| | | `.ai-framework/docs/checklists/service-naming-checklist.md` — § Decision tree |
| | | `.ai-framework/docs/guides/template-naming-guide.md` — § Renaming rules |
| **Создание Implementation Plan** | `roles/architect/implementation-plan.md` | `.ai-framework/docs/guides/implementation-plan-template.md` — § Template structure, § Tasklist format |
| | | `.ai-framework/docs/guides/requirements-traceability-guide.md` — § RTM creation |
| | | `.ai-framework/docs/guides/use-case-implementation-guide.md` — § Use case delivery |
| **Определение контрактов API** | `roles/architect/api-contracts.md` | `.ai-framework/docs/atomic/services/fastapi/routing-patterns.md` — § Endpoint patterns |
| | | `.ai-framework/docs/atomic/services/fastapi/schema-validation.md` — § Request/Response schemas |
| | | `.ai-framework/docs/atomic/integrations/http-communication/business-to-data-calls.md` — § HTTP client patterns |

---

### 3.3.4 Реализатор (Implementer)

| Функция | Файл роли | Файлы .ai-framework и разделы |
|---------|-----------|-------------------------------|
| **Stage 4.1: Инфраструктура** | `roles/implementer/infrastructure-setup.md` | `.ai-framework/docs/reference/project-structure.md` — § Creating the Project Structure |
| | | `.ai-framework/docs/atomic/architecture/project-structure-patterns.md` — § Directory patterns |
| | | `.ai-framework/docs/atomic/infrastructure/containerization/docker-compose-setup.md` — § Service definitions |
| | | `.ai-framework/docs/atomic/infrastructure/containerization/dockerfile-patterns.md` — § Multi-stage builds |
| **Stage 4.2: Data Service** | `roles/implementer/data-service.md` | `.ai-framework/docs/atomic/services/data-services/postgres-service-setup.md` — § Service structure, § API endpoints |
| | | `.ai-framework/docs/atomic/databases/postgresql/sqlalchemy-integration.md` — § Models, § Sessions |
| | | `.ai-framework/docs/atomic/services/data-services/repository-patterns.md` — § CRUD patterns |
| | | `.ai-framework/docs/atomic/services/data-services/http-api-patterns.md` — § Data API structure |
| **Stage 4.3: Business API** | `roles/implementer/business-api.md` | `.ai-framework/docs/atomic/services/fastapi/application-factory.md` — § App factory pattern |
| | | `.ai-framework/docs/atomic/services/fastapi/routing-patterns.md` — § Router organization |
| | | `.ai-framework/docs/atomic/services/fastapi/dependency-injection.md` — § DI patterns |
| | | `.ai-framework/docs/atomic/services/fastapi/schema-validation.md` — § Pydantic schemas |
| | | `.ai-framework/docs/atomic/services/fastapi/error-handling.md` — § Exception hierarchy |
| | | `.ai-framework/docs/atomic/integrations/http-communication/business-to-data-calls.md` — § HTTP client usage |
| **Stage 4.4: Background Worker** | `roles/implementer/background-worker.md` | `.ai-framework/docs/atomic/services/asyncio-workers/basic-setup.md` — § Worker structure |
| | | `.ai-framework/docs/atomic/services/asyncio-workers/main-function-patterns.md` — § Entry point |
| | | `.ai-framework/docs/atomic/services/asyncio-workers/signal-handling.md` — § Graceful shutdown |
| | | `.ai-framework/docs/atomic/services/asyncio-workers/task-management.md` — § Task patterns |
| | | `.ai-framework/docs/atomic/integrations/rabbitmq/message-consuming.md` — § Consumer setup |
| **Stage 4.5: Telegram Bot** | `roles/implementer/telegram-bot.md` | `.ai-framework/docs/atomic/services/aiogram/basic-setup.md` — § Bot structure |
| | | `.ai-framework/docs/atomic/services/aiogram/bot-initialization.md` — § Dispatcher setup |
| | | `.ai-framework/docs/atomic/services/aiogram/handler-patterns.md` — § Command handlers |
| | | `.ai-framework/docs/atomic/services/aiogram/middleware-setup.md` — § Middleware chain |
| | | `.ai-framework/docs/atomic/services/aiogram/state-management.md` — § FSM patterns |
| | | `.ai-framework/docs/atomic/integrations/rabbitmq/aiogram-integration.md` — § Event handling |
| **Stage 4.6: Тестирование** | `roles/implementer/testing.md` | `.ai-framework/docs/atomic/testing/unit-testing/pytest-setup.md` — § pytest.ini, § conftest.py |
| | | `.ai-framework/docs/atomic/testing/unit-testing/fixture-patterns.md` — § Fixture patterns |
| | | `.ai-framework/docs/atomic/testing/unit-testing/mocking-strategies.md` — § Mock patterns |
| | | `.ai-framework/docs/atomic/testing/service-testing/fastapi-testing-patterns.md` — § TestClient usage |
| | | `.ai-framework/docs/atomic/testing/integration-testing/testcontainers-setup.md` — § Container fixtures |
| **Логирование (Level ≥ 2)** | `roles/implementer/logging.md` | `.ai-framework/docs/atomic/observability/logging/structured-logging.md` — § JSON format |
| | | `.ai-framework/docs/atomic/observability/logging/log-correlation.md` — § Request ID |
| **Метрики (Level ≥ 3)** | `roles/implementer/metrics.md` | `.ai-framework/docs/atomic/observability/metrics/prometheus-setup.md` — § Metrics endpoint |
| | | `.ai-framework/docs/atomic/observability/metrics/custom-metrics.md` — § Business metrics |
| **Nginx (Level ≥ 3)** | `roles/implementer/nginx.md` | `.ai-framework/docs/atomic/infrastructure/api-gateway/nginx-setup.md` — § Reverse proxy |
| | | `.ai-framework/docs/atomic/infrastructure/api-gateway/ssl-configuration.md` — § TLS setup |

**Шаблоны для копирования (Реализатор):**

| Тип | Шаблон в .ai-framework |
|-----|----------------------|
| Инфраструктура | `templates/infrastructure/docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.prod.yml`, `.env.example`, `Makefile` |
| Data Service | `templates/services/template_data_postgres_api/` |
| Business API | `templates/services/template_business_api/` |
| Worker | `templates/services/template_business_worker/` |
| Telegram Bot | `templates/services/template_business_bot/` |
| Shared Utils | `templates/shared/utils/logger.py`, `validators.py`, `exceptions.py`, `pagination.py`, `request_id.py` |
| HTTP Clients | `templates/shared/http_clients/data_api_client.py` |
| Тестирование | `templates/shared/testing/base_fixtures.py` |
| Nginx | `templates/nginx/nginx.conf`, `templates/nginx/conf.d/upstream.conf`, `api-gateway.conf` |

---

### 3.3.5 Ревьюер (Reviewer)

| Функция | Файл роли | Файлы .ai-framework и разделы |
|---------|-----------|-------------------------------|
| **Проверка архитектуры** | `roles/reviewer/architecture-compliance.md` | `.ai-framework/ARCHITECTURE.md` — § Mandatory constraints |
| | | `.ai-framework/CLAUDE.md` — § Code Quality Pre-Checks, § DRY/KISS/YAGNI |
| | | `.ai-framework/docs/guides/dry-kiss-yagni-principles.md` — § Violation examples |
| | | `.ai-framework/docs/atomic/architecture/service-separation-principles.md` — § HTTP-only rule |
| **Проверка конвенций** | `roles/reviewer/convention-compliance.md` | `.ai-framework/docs/atomic/architecture/naming/README.md` — § Naming rules |
| | | `.ai-framework/docs/atomic/architecture/quality-standards.md` — § Code standards |
| | | `.ai-framework/docs/atomic/testing/quality-assurance/linting-standards.md` — § Ruff, Mypy rules |
| **Создание Review Report** | `roles/reviewer/review-report.md` | `.ai-framework/docs/reference/aidd-roles-reference.md` — § Роль 5: Reviewer, § Review Report template |
| | | `.ai-framework/docs/atomic/testing/quality-assurance/code-review-checklist.md` — § Review checklist |

---

### 3.3.6 QA (Quality Assurance)

| Функция | Файл роли | Файлы .ai-framework и разделы |
|---------|-----------|-------------------------------|
| **Создание тестовых сценариев** | `roles/qa/test-scenarios.md` | `.ai-framework/docs/atomic/testing/end-to-end-testing/e2e-test-setup.md` — § Test structure |
| | | `.ai-framework/docs/atomic/testing/end-to-end-testing/user-journey-testing.md` — § Scenario patterns |
| **Выполнение тестов** | `roles/qa/test-execution.md` | `.ai-framework/docs/reference/agent-toolbox.md` — § Test commands |
| | | `.ai-framework/docs/guides/development-commands.md` — § pytest, coverage |
| **Верификация coverage** | `roles/qa/coverage-verification.md` | `.ai-framework/docs/reference/maturity-levels.md` — § Coverage thresholds per level |
| | | `.ai-framework/docs/guides/requirements-traceability-guide.md` — § Coverage verification |
| **Создание QA Report** | `roles/qa/qa-report.md` | `.ai-framework/docs/quality/qa-report-template.md` — § Report template |
| | | `.ai-framework/docs/reference/aidd-roles-reference.md` — § Роль 6: QA, § QA Report template |

---

### 3.3.7 Валидатор (Validator)

| Функция | Файл роли | Файлы .ai-framework и разделы |
|---------|-----------|-------------------------------|
| **Проверка quality gates** | `roles/validator/quality-gates.md` | `.ai-framework/docs/quality/agent-verification-checklist.md` — § All gates |
| | | `.ai-framework/docs/reference/aidd-roles-reference.md` — § Quality Gates |
| **Проверка артефактов** | `roles/validator/artifact-verification.md` | `.ai-framework/docs/reference/deliverables-catalog.md` — § Artifact paths |
| | | `.ai-framework/docs/guides/requirements-traceability-guide.md` — § 100% coverage check |
| **Создание Validation Report** | `roles/validator/validation-report.md` | `.ai-framework/docs/reference/aidd-roles-reference.md` — § Роль 8: Validator, § Validation Report template |

---

## 3.4 Детальное описание ролей

### Аналитик (Analyst)

**Основная задача**: Преобразование идеи пользователя в структурированный PRD документ.

> 🔀 **Режимы работы** (CREATE/FEATURE) см. [раздел 3.1](#31-единый-пайплайн-aidd-mvp-generator)
>
> 📚 **Документация .ai-framework** — см. [раздел 3.3.1](#331-аналитик-analyst)

**Что делает:**

#### 1. Верификация промпта

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Проверка полноты входных данных | `CLAUDE.md` — понимание контекста проекта | — |
| Определение типа запроса (CREATE/FEATURE) | `.claude/project-context.md` — текущее состояние проекта | — |
| Оценка реалистичности и scope | `ai-docs/docs/rtm.md` — существующие требования (для FEATURE) | — |

#### 2. Сбор требований через уточняющие вопросы

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Вопросы о целевой аудитории и бизнес-целях | `ai-docs/docs/prd/{project}-prd.md` — исходный PRD (для FEATURE) | — |
| Уточнение функциональных требований | `ai-docs/conventions.md` — соглашения проекта | — |
| Определение нефункциональных требований | `ai-docs/workflow.md` — процесс разработки | — |
| Выявление ограничений и допущений | — | — |
| Согласование критериев приёмки | — | — |

#### 3. Формирование PRD

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Создание структурированного документа | Шаблон PRD из фреймворка | 📝 `ai-docs/docs/prd/{name}-prd.md` |
| Присвоение ID требованиям (FR-001, NF-001) | `ai-docs/docs/rtm.md` — последние ID (для FEATURE) | 📝 `ai-docs/docs/prd/{name}-prd.md` |
| Определение приоритетов (MoSCoW) | — | 📝 `ai-docs/docs/prd/{name}-prd.md` |
| Фиксация открытых вопросов и рисков | — | 📝 `ai-docs/docs/prd/{name}-prd.md` |

#### 4. Валидация PRD

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Проверка заполненности секций | `ai-docs/docs/prd/{name}-prd.md` | — |
| Проверка на противоречия | `ai-docs/docs/prd/{name}-prd.md` | 📝 Исправления в PRD |
| Подтверждение критериев приёмки | `ai-docs/docs/prd/{name}-prd.md` | 📝 `ai-docs/docs/rtm.md` — начальная секция RTM |

**Итоговые артефакты:**
- 📝 `ai-docs/docs/prd/{name}-prd.md` — документ требований
- 📝 `ai-docs/docs/rtm.md` — обновление матрицы трассировки (добавление новых ID)

**Ворота**: `PRD_READY`

---

### Исследователь (Researcher)

**Основная задача**: Анализ существующей кодовой базы для понимания контекста.

> 🔀 **Режимы работы** (CREATE/FEATURE) см. [раздел 3.1](#31-единый-пайплайн-aidd-mvp-generator)
>
> 📚 **Документация .ai-framework** — см. [раздел 3.3.2](#332-исследователь-researcher)

**Что делает:**

#### 1. Анализ структуры проекта

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Сканирование директорий и файлов | Вся структура `services/`, `shared/` | — |
| Определение технологий и фреймворков | `services/*/requirements.txt`, `services/*/pyproject.toml` | — |
| Составление карты зависимостей | `services/*/src/infrastructure/http/` — HTTP клиенты | — |

#### 2. Изучение существующего кода

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Поиск релевантных файлов | `ai-docs/docs/prd/{feature}-prd.md` — требования для поиска | — |
| Анализ паттернов и соглашений | `ai-docs/conventions.md`, существующий код в `services/` | — |
| Определение точек интеграции | `services/*/src/api/v1/*.py` — эндпоинты | — |
| | `services/*/src/domain/entities/*.py` — модели | — |
| | `shared/schemas/*.py` — общие схемы | — |

#### 3. Документирование находок

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Составление списка затрагиваемых файлов | Результаты анализа | 📝 `ai-docs/docs/research/{feature}-research.md` |
| Описание существующих API и интерфейсов | `services/*/src/api/v1/*.py` | 📝 `ai-docs/docs/research/{feature}-research.md` |
| Выявление конфликтов и зависимостей | `docker-compose.yml`, `shared/` | 📝 `ai-docs/docs/research/{feature}-research.md` |

#### 4. Формирование рекомендаций

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Предложение места для новой функциональности | Структура `services/` | 📝 `ai-docs/docs/research/{feature}-research.md` |
| Указание на паттерны для соблюдения | `ai-docs/conventions.md`, существующий код | 📝 `ai-docs/docs/research/{feature}-research.md` |
| Отметка технического долга | Весь код проекта | 📝 `ai-docs/docs/research/{feature}-research.md` |

**Итоговые артефакты:**
- 📝 `ai-docs/docs/research/{feature}-research.md` — отчёт исследования с:
  - Списком затрагиваемых файлов
  - Точками интеграции (файл:строка)
  - Рекомендациями по реализации
  - Выявленным техническим долгом

**Ворота**: `RESEARCH_DONE` или `RESEARCH_SKIPPED`

---

### Архитектор (Architect)

**Основная задача**: Проектирование архитектуры системы или изменений.

> 🔀 **Режимы работы** (CREATE/FEATURE) см. [раздел 3.1](#31-единый-пайплайн-aidd-mvp-generator)
>
> 📚 **Документация .ai-framework** — см. [раздел 3.3.3](#333-архитектор-architect)

**Что делает:**

#### 1. Анализ требований

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Изучение PRD | `ai-docs/docs/prd/{name}-prd.md` | — |
| Выделение архитектурно-значимых требований | `ai-docs/docs/prd/{name}-prd.md` — секции FR, NF | — |
| Определение технических ограничений | `ai-docs/conventions.md`, `.claude/project-context.md` | — |
| Оценка интеграций (для FEATURE) | `ai-docs/docs/research/{feature}-research.md` | — |

#### 2. Выбор архитектурного решения

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Определение набора сервисов | Шаблоны из `templates/services/` фреймворка | 📝 План архитектуры |
| Выбор баз данных | `ai-docs/docs/prd/{name}-prd.md` — требования к данным | 📝 План архитектуры |
| Проектирование схемы взаимодействия | `ai-docs/docs/architecture/{project}-plan.md` (для FEATURE) | 📝 План архитектуры |
| Применение DDD/Hexagonal | `ai-docs/conventions.md` | 📝 План архитектуры |

#### 3. Детализация компонентов

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Описание структуры каждого сервиса | Шаблоны `templates/services/` | 📝 `ai-docs/docs/architecture/{name}-plan.md` |
| Определение контрактов API | `shared/schemas/` (для FEATURE) | 📝 `ai-docs/docs/architecture/{name}-plan.md` |
| Проектирование моделей данных | `services/*/src/models/` (для FEATURE) | 📝 `ai-docs/docs/architecture/{name}-plan.md` |
| Планирование инфраструктуры | `docker-compose.yml`, `nginx/` | 📝 `ai-docs/docs/architecture/{name}-plan.md` |

#### 4. Декомпозиция на задачи

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Разбиение на атомарные задачи | План архитектуры | 📝 `ai-docs/docs/architecture/{name}-plan.md` — секция Tasks |
| Определение порядка и зависимостей | — | 📝 `ai-docs/docs/architecture/{name}-plan.md` — секция Tasks |
| Формулирование критериев приёмки | `ai-docs/docs/prd/{name}-prd.md` | 📝 `ai-docs/docs/architecture/{name}-plan.md` — секция Tasks |

#### 5. Трассировка требований

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Связывание задач с требованиями | `ai-docs/docs/prd/{name}-prd.md` — ID требований | 📝 `ai-docs/docs/architecture/{name}-plan.md` — секция RTM |
| Заполнение RTM | `ai-docs/docs/rtm.md` — существующие связи | 📝 `ai-docs/docs/rtm.md` — обновление |

**Итоговые артефакты:**
- 📝 CREATE: `ai-docs/docs/architecture/{project}-plan.md`
- 📝 FEATURE: `ai-docs/docs/plans/{feature}-plan.md`
- 📝 `ai-docs/docs/rtm.md` — обновление матрицы (связь требований с задачами)

**Ворота**: `PLAN_APPROVED`

---

### Реализатор (Implementer)

**Основная задача**: Генерация production-ready кода по плану.

> 🔀 **Режимы работы** (CREATE/FEATURE) см. [раздел 3.1](#31-единый-пайплайн-aidd-mvp-generator)
>
> 📚 **Документация .ai-framework** — см. [раздел 3.3.4](#334-реализатор-implementer)
>
> 📦 **Шаблоны для копирования** — см. [раздел 3.3.4](#334-реализатор-implementer)

**Что делает:**

#### 1. Подготовка к генерации

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Изучение архитектурного плана | `ai-docs/docs/architecture/{name}-plan.md` или `ai-docs/docs/plans/{feature}-plan.md` | — |
| Загрузка шаблонов | Шаблоны из `templates/services/` фреймворка | — |
| Определение порядка создания файлов | План — секция Tasks | — |
| Изучение соглашений | `ai-docs/conventions.md` | — |

#### 2. Генерация кода

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Создание структуры директорий | Шаблон сервиса | 📝 `services/{service_name}/src/` |
| Генерация API слоя | `templates/services/*/src/api/` | 📝 `services/{service}/src/api/v1/*.py` |
| Генерация Application слоя | `templates/services/*/src/application/` | 📝 `services/{service}/src/application/services/*.py` |
| Генерация Domain слоя | `templates/services/*/src/domain/` | 📝 `services/{service}/src/domain/entities/*.py` |
| Генерация Infrastructure слоя | `templates/services/*/src/infrastructure/` | 📝 `services/{service}/src/infrastructure/` |
| Создание общих схем | `shared/schemas/` (для FEATURE) | 📝 `shared/schemas/{feature}.py` |
| Создание HTTP клиентов | `shared/http_clients/` (для FEATURE) | 📝 `shared/http_clients/{service}_client.py` |

#### 3. Написание тестов

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Создание unit-тестов | Сгенерированный код `src/` | 📝 `services/{service}/tests/unit/test_*.py` |
| Создание интеграционных тестов | API эндпоинты | 📝 `services/{service}/tests/integration/test_*.py` |
| Создание e2e тестов | Весь сервис | 📝 `tests/e2e/test_{feature}.py` |
| Создание conftest.py | — | 📝 `services/{service}/tests/conftest.py` |

#### 4. Создание инфраструктуры

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Генерация Dockerfile | `templates/infrastructure/docker/` | 📝 `services/{service}/Dockerfile` |
| Обновление docker-compose | `docker-compose.yml` | 📝 `docker-compose.yml` — добавление сервиса |
| Обновление docker-compose.dev | `docker-compose.dev.yml` | 📝 `docker-compose.dev.yml` |
| Обновление docker-compose.prod | `docker-compose.prod.yml` | 📝 `docker-compose.prod.yml` |
| Настройка Nginx | `nginx/nginx.conf` | 📝 `nginx/nginx.conf` — добавление роута |
| Создание CI/CD | `templates/infrastructure/github-actions/` | 📝 `.github/workflows/ci.yml`, `.github/workflows/cd.yml` |

#### 5. Документирование

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Добавление docstrings | Сгенерированный код | 📝 Все `.py` файлы |
| Создание README сервиса | — | 📝 `services/{service}/README.md` |
| Заполнение .env.example | `docker-compose.yml` | 📝 `.env.example` |
| Обновление requirements.txt | Используемые библиотеки | 📝 `services/{service}/requirements.txt` |

**Примечание**: Работает итеративно: задача → код → написание тестов → следующая задача. Каждая итерация проходит базовые проверки (синтаксис, импорты).

**Итоговые артефакты (CREATE):**
- 📝 `services/` — все микросервисы
- 📝 `shared/` — общие компоненты
- 📝 `tests/e2e/` — e2e тесты
- 📝 `docker-compose.yml`, `.env.example`, `nginx/`, `.github/`
- 📝 `README.md`

**Итоговые артефакты (FEATURE):**
- 📝 Новые/изменённые файлы в `services/`
- 📝 Новые/изменённые файлы в `shared/`
- 📝 Новые тесты
- 📝 Обновлённые `docker-compose.yml`, `nginx/nginx.conf`

**Ворота**: `IMPLEMENT_OK`

---

### Ревьюер (Reviewer)

**Основная задача**: Проверка качества сгенерированного кода.

> 🔀 **Режимы работы** (CREATE/FEATURE) см. [раздел 3.1](#31-единый-пайплайн-aidd-mvp-generator)
>
> 📚 **Документация .ai-framework** — см. [раздел 3.3.5](#335-ревьюер-reviewer)

**Что делает:**

#### 1. Статический анализ

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Запуск Ruff (стиль кода) | `services/**/*.py`, `shared/**/*.py` | 📝 Результаты в отчёт |
| Запуск Mypy (проверка типов) | `services/**/*.py`, `shared/**/*.py` | 📝 Результаты в отчёт |
| Запуск Bandit (безопасность) | `services/**/*.py`, `shared/**/*.py` | 📝 Результаты в отчёт |
| Проверка конфигов линтеров | `pyproject.toml`, `ruff.toml` | — |

#### 2. Ревью архитектуры

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Проверка соответствия плану | `ai-docs/docs/architecture/{name}-plan.md`, код в `services/` | 📝 `ai-docs/docs/reports/{name}-review.md` |
| Валидация структуры (DDD/Hexagonal) | `services/*/src/` — структура директорий | 📝 `ai-docs/docs/reports/{name}-review.md` |
| Проверка HTTP-only доступа к данным | `services/*/src/infrastructure/` — нет прямых БД вызовов | 📝 `ai-docs/docs/reports/{name}-review.md` |
| Проверка соглашений | `ai-docs/conventions.md`, код проекта | 📝 `ai-docs/docs/reports/{name}-review.md` |

#### 3. Ревью качества кода

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Оценка читаемости | Весь новый/изменённый код | 📝 `ai-docs/docs/reports/{name}-review.md` |
| Проверка DRY, KISS, YAGNI | Весь код | 📝 `ai-docs/docs/reports/{name}-review.md` |
| Поиск потенциальных багов | Весь код | 📝 `ai-docs/docs/reports/{name}-review.md` |
| Проверка обработки ошибок | `services/*/src/api/`, `services/*/src/application/` | 📝 `ai-docs/docs/reports/{name}-review.md` |

#### 4. Ревью безопасности

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Проверка валидации входных данных | `services/*/src/api/`, `shared/schemas/` | 📝 `ai-docs/docs/reports/{name}-review.md` |
| Поиск уязвимостей (OWASP Top 10) | Весь код | 📝 `ai-docs/docs/reports/{name}-review.md` |
| Проверка управления секретами | `.env.example`, `docker-compose.yml`, код | 📝 `ai-docs/docs/reports/{name}-review.md` |

#### 5. Формирование отчёта

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Классификация замечаний | Результаты всех проверок | 📝 `ai-docs/docs/reports/{name}-review.md` |
| Указание файлов и строк | — | 📝 `ai-docs/docs/reports/{name}-review.md` |
| Предложение исправлений | — | 📝 `ai-docs/docs/reports/{name}-review.md` |

**Итоговые артефакты:**
- 📝 `ai-docs/docs/reports/{name}-review.md` — отчёт ревью с секциями:
  - Результаты статического анализа (Ruff, Mypy, Bandit)
  - Замечания по архитектуре
  - Замечания по качеству кода
  - Замечания по безопасности
  - Классификация: Critical / Major / Minor / Suggestion

**Ворота**: `REVIEW_OK` (0 Critical и Major замечаний)

---

### QA (Quality Assurance)

**Основная задача**: Тестирование и проверка готовности к релизу.

> 🔀 **Режимы работы** (CREATE/FEATURE) см. [раздел 3.1](#31-единый-пайплайн-aidd-mvp-generator)
>
> 📚 **Документация .ai-framework** — см. [раздел 3.3.6](#336-qa-quality-assurance)

**Что делает:**

#### 1. Запуск тестов

| Действие | 📖 Читает/Выполняет | 📝 Создаёт/Обновляет |
|----------|---------------------|---------------------|
| Выполнение unit-тестов | `services/*/tests/unit/test_*.py` | 📝 Результаты в отчёт |
| Выполнение интеграционных тестов | `services/*/tests/integration/test_*.py` | 📝 Результаты в отчёт |
| Выполнение e2e тестов | `tests/e2e/test_*.py` | 📝 Результаты в отчёт |
| Проверка конфигурации тестов | `services/*/tests/conftest.py`, `pytest.ini` | — |

#### 2. Анализ покрытия

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Измерение code coverage | Результаты pytest-cov | 📝 `ai-docs/docs/reports/{name}-qa.md` — секция Coverage |
| Проверка порога ≥85% | Coverage report | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Выявление непокрытых путей | Coverage HTML report | 📝 `ai-docs/docs/reports/{name}-qa.md` |

#### 3. Функциональное тестирование

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Проверка реализации требований | `ai-docs/docs/prd/{name}-prd.md` — список FR/NF | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Тестирование happy path | API эндпоинты, бот команды | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Тестирование edge cases | Граничные условия | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Валидация критериев приёмки | `ai-docs/docs/prd/{name}-prd.md` — Acceptance Criteria | 📝 `ai-docs/docs/reports/{name}-qa.md` |

#### 4. Проверка инфраструктуры

| Действие | 📖 Читает/Выполняет | 📝 Создаёт/Обновляет |
|----------|---------------------|---------------------|
| Запуск docker-compose | `docker-compose.yml`, `docker-compose.dev.yml` | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Тестирование health check | `http://localhost:*/health` для всех сервисов | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Проверка nginx роутинга | `nginx/nginx.conf`, HTTP запросы | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Проверка переменных окружения | `.env.example`, `docker-compose.yml` | 📝 `ai-docs/docs/reports/{name}-qa.md` |

#### 5. Регрессионное тестирование (для FEATURE)

| Действие | 📖 Читает/Выполняет | 📝 Создаёт/Обновляет |
|----------|---------------------|---------------------|
| Запуск всех существующих тестов | Все `tests/` в проекте | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Проверка существующей функциональности | Существующие API эндпоинты | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Сравнение с предыдущими результатами | Предыдущие QA отчёты | 📝 `ai-docs/docs/reports/{name}-qa.md` |

#### 6. Формирование QA отчёта

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Составление списка тестов | Результаты всех тестов | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Документирование багов | Найденные проблемы | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Вердикт о готовности | Все результаты | 📝 `ai-docs/docs/reports/{name}-qa.md` |
| Обновление RTM | `ai-docs/docs/rtm.md` | 📝 `ai-docs/docs/rtm.md` — статус тестов |

**Итоговые артефакты:**
- 📝 `ai-docs/docs/reports/{name}-qa.md` — QA отчёт с секциями:
  - Результаты unit/integration/e2e тестов
  - Code coverage (% и непокрытые файлы)
  - Функциональное тестирование (требование → результат)
  - Инфраструктура (health checks, nginx)
  - Регрессия (для FEATURE)
  - Найденные баги (Critical/Major/Minor)
  - Вердикт: PASS / FAIL
- 📝 `ai-docs/docs/rtm.md` — обновление (статус тестов для каждого требования)

**Ворота**: `QA_PASSED` (все тесты проходят, покрытие ≥85%, 0 критических багов)

---

### Валидатор (Validator)

**Основная задача**: Проверка всех качественных ворот и финальное развёртывание.

> 🔀 **Режимы работы** (CREATE/FEATURE) см. [раздел 3.1](#31-единый-пайплайн-aidd-mvp-generator)
>
> 📚 **Документация .ai-framework** — см. [раздел 3.3.7](#337-валидатор-validator)

**Что делает:**

#### 1. Проверка ворот

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Проверка PRD_READY | `ai-docs/docs/prd/{name}-prd.md` — наличие и полнота | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Проверка RESEARCH_DONE | `ai-docs/docs/research/{name}-research.md` | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Проверка PLAN_APPROVED | `ai-docs/docs/architecture/{name}-plan.md` или `ai-docs/docs/plans/{name}-plan.md` | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Проверка IMPLEMENT_OK | Код в `services/`, `shared/`, тесты | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Проверка REVIEW_OK | `ai-docs/docs/reports/{name}-review.md` — 0 Critical/Major | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Проверка QA_PASSED | `ai-docs/docs/reports/{name}-qa.md` — все тесты ✅ | 📝 `ai-docs/docs/reports/{name}-validation.md` |

#### 2. Проверка трассировки требований

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Сверка RTM — все требования реализованы | `ai-docs/docs/rtm.md`, `ai-docs/docs/prd/{name}-prd.md` | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Проверка покрытия тестами | `ai-docs/docs/rtm.md` — колонка "Тест" | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Валидация соответствия плану | `ai-docs/docs/architecture/{name}-plan.md`, код | 📝 `ai-docs/docs/reports/{name}-validation.md` |

#### 3. Проверка готовности к развёртыванию

| Действие | 📖 Читает/Выполняет | 📝 Создаёт/Обновляет |
|----------|---------------------|---------------------|
| Сборка Docker образов | `services/*/Dockerfile` → `docker build` | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Проверка переменных окружения | `.env.example` — все переменные документированы | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Проверка CI/CD | `.github/workflows/ci.yml`, `.github/workflows/cd.yml` | 📝 `ai-docs/docs/reports/{name}-validation.md` |

#### 4. Развёртывание (команда /deploy)

| Действие | 📖 Читает/Выполняет | 📝 Создаёт/Обновляет |
|----------|---------------------|---------------------|
| Запуск docker-compose | `docker-compose.yml` → `docker-compose up -d` | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Проверка health checks | `http://localhost:*/health` для всех сервисов | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Валидация nginx | `nginx/nginx.conf`, HTTP запросы | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Smoke-тесты | Основные API эндпоинты | 📝 `ai-docs/docs/reports/{name}-validation.md` |

#### 5. Финальный отчёт

| Действие | 📖 Читает | 📝 Создаёт/Обновляет |
|----------|-----------|---------------------|
| Составление статуса ворот | Все артефакты | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Формирование итогового RTM | `ai-docs/docs/rtm.md` | 📝 `ai-docs/docs/rtm.md` — финальный статус |
| Документирование инструкций | — | 📝 `ai-docs/docs/reports/{name}-validation.md` |
| Обновление контекста проекта | — | 📝 `.claude/project-context.md` — добавление фичи |

**Итоговые артефакты:**
- 📝 `ai-docs/docs/reports/{name}-validation.md` — отчёт валидации:
  - Статус всех ворот (✅/❌)
  - Результаты проверки RTM (100% реализовано?)
  - Результаты сборки Docker
  - Результаты развёртывания
  - Инструкции по запуску
- 📝 `ai-docs/docs/rtm.md` — финальное обновление (все статусы)
- 📝 `.claude/project-context.md` — обновление контекста проекта

**Ворота**: `ALL_GATES_PASSED`, `DEPLOYED`

---

### Сводная таблица ролей

| Роль | Ответственность | CREATE | FEATURE |
|------|-----------------|--------|---------|
| **Аналитик** | Требования | Полный PRD проекта | Feature PRD |
| **Исследователь** | Контекст кода | ⏭️ Пропуск | ✅ Анализ кодовой базы |
| **Архитектор** | Проектирование | Полная архитектура | Дельта к архитектуре |
| **Реализатор** | Код | Генерация с нуля | Модификация кода |
| **Ревьюер** | Качество кода | Полное ревью | Дельта-ревью |
| **QA** | Тестирование | Полное тестирование | Тесты + регрессия |
| **Валидатор** | Качественные ворота | Первичное развёртывание | Инкрементальное развёртывание |

---

## 3.5 Структура MVP проекта

```
{project_name}/
├── CLAUDE.md                    # AI-инструкции (точка входа)
├── README.md                    # Документация проекта
│
├── docker-compose.yml           # Dev окружение
├── docker-compose.dev.yml       # Dev overrides
├── docker-compose.prod.yml      # Production
├── .env.example                 # Шаблон переменных окружения
├── Makefile                     # Команды проекта
│
├── nginx/                       # Конфигурация nginx
│   └── nginx.conf
│
├── .claude/                     # Конфигурация Claude Code
│   ├── settings.json            # Хуки и разрешения
│   └── project-context.md       # Контекст проекта для AI
│
├── ai-docs/                     # Документация для AI агентов
│   ├── conventions.md           # Соглашения о коде
│   ├── workflow.md              # Workflow разработки
│   │
│   └── docs/                    # Артефакты разработки
│       ├── prd/                 # Product Requirements Documents
│       │   └── {project}-prd.md
│       ├── architecture/        # Архитектурные решения
│       │   └── {project}-plan.md
│       ├── research/            # Технические исследования
│       ├── plans/               # Планы фич
│       ├── reports/             # QA и review отчёты
│       │   ├── {project}-review.md
│       │   └── {project}-qa.md
│       └── rtm.md               # Сводная матрица трассировки требований
│
├── services/                    # Микросервисы
│   ├── {context}_{domain}_api/      # Business API (FastAPI)
│   ├── {context}_{domain}_bot/      # Telegram Bot (Aiogram)
│   ├── {context}_{domain}_worker/   # Background Worker
│   ├── {context}_data_postgres/     # PostgreSQL Data API
│   └── {context}_data_mongo/        # MongoDB Data API
│
├── shared/                      # Общие компоненты
│   ├── utils/                   # Утилиты
│   ├── schemas/                 # Pydantic схемы
│   ├── http_clients/            # HTTP клиенты
│   └── events/                  # События
│
├── .github/                     # CI/CD
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
└── tests/                       # Интеграционные тесты
    └── e2e/
```

---

## 3.6 Хранение документов для AI-генерации

### Документы AIDD-MVP Generator (фреймворка)
Хранятся в корне фреймворка:

```
aidd-mvp-generator/
├── CLAUDE.md                    # Главные инструкции для AI
├── conventions.md               # Соглашения о коде
├── workflow.md                  # Описание процесса AIDD-MVP
│
├── .claude/
│   ├── agents/                  # Определения ролей агентов
│   │   ├── analyst.md           # Инструкции для Аналитика
│   │   ├── architect.md         # Инструкции для Архитектора
│   │   ├── implementer.md       # Инструкции для Реализатора
│   │   ├── reviewer.md          # Инструкции для Ревьюера
│   │   ├── qa.md                # Инструкции для QA
│   │   ├── researcher.md        # Инструкции для Исследователя
│   │   └── validator.md         # Инструкции для Валидатора
│   │
│   ├── commands/                # Slash-команды
│   │   ├── idea.md              # /idea — создание PRD
│   │   ├── plan.md              # /plan — архитектура
│   │   ├── generate.md          # /generate — генерация кода
│   │   ├── review.md            # /review — код-ревью
│   │   ├── test.md              # /test — тестирование
│   │   ├── validate.md          # /validate — проверка ворот
│   │   ├── deploy.md            # /deploy — развёртывание
│   │   ├── research.md          # /research — исследование кода
│   │   └── feature-plan.md      # /feature-plan — планирование фичи
│   │
│   └── settings.json            # Хуки для качественных ворот
│
├── templates/                   # Шаблоны для генерации
│   ├── services/                # Шаблоны сервисов
│   ├── infrastructure/          # Шаблоны инфраструктуры
│   └── shared/                  # Общие компоненты
│
├── knowledge/                   # База знаний для AI
│   ├── architecture/            # Архитектурные паттерны
│   ├── services/                # Паттерны сервисов
│   ├── integrations/            # Паттерны интеграций
│   └── quality/                 # Стандарты качества
│
├── roles/                       # Инструкции по функциям ролей
│   ├── analyst/                 # Функции Аналитика
│   │   ├── initialization.md        # Stage 0: Инициализация
│   │   ├── prompt-validation.md     # Верификация промпта
│   │   ├── requirements-gathering.md # Сбор требований
│   │   └── prd-formation.md         # Формирование PRD
│   │
│   ├── researcher/              # Функции Исследователя
│   │   ├── codebase-analysis.md     # Анализ кодовой базы
│   │   ├── pattern-identification.md # Выявление паттернов
│   │   ├── constraint-identification.md # Выявление ограничений
│   │   └── pipeline-refinement.md   # Уточнение пайплайна
│   │
│   ├── architect/               # Функции Архитектора
│   │   ├── architecture-design.md   # Проектирование архитектуры
│   │   ├── maturity-level-selection.md # Выбор по уровню зрелости
│   │   ├── service-naming.md        # Именование сервисов
│   │   ├── implementation-plan.md   # Создание Implementation Plan
│   │   └── api-contracts.md         # Определение контрактов API
│   │
│   ├── implementer/             # Функции Реализатора
│   │   ├── infrastructure-setup.md  # Stage 4.1: Инфраструктура
│   │   ├── data-service.md          # Stage 4.2: Data Service
│   │   ├── business-api.md          # Stage 4.3: Business API
│   │   ├── background-worker.md     # Stage 4.4: Background Worker
│   │   ├── telegram-bot.md          # Stage 4.5: Telegram Bot
│   │   ├── testing.md               # Stage 4.6: Тестирование
│   │   ├── logging.md               # Логирование (Level ≥ 2)
│   │   ├── metrics.md               # Метрики (Level ≥ 3)
│   │   └── nginx.md                 # Nginx (Level ≥ 3)
│   │
│   ├── reviewer/                # Функции Ревьюера
│   │   ├── architecture-compliance.md # Проверка архитектуры
│   │   ├── convention-compliance.md   # Проверка конвенций
│   │   └── review-report.md         # Создание Review Report
│   │
│   ├── qa/                      # Функции QA
│   │   ├── test-scenarios.md        # Создание тестовых сценариев
│   │   ├── test-execution.md        # Выполнение тестов
│   │   ├── coverage-verification.md # Верификация coverage
│   │   └── qa-report.md             # Создание QA Report
│   │
│   └── validator/               # Функции Валидатора
│       ├── quality-gates.md         # Проверка quality gates
│       ├── artifact-verification.md # Проверка артефактов
│       └── validation-report.md     # Создание Validation Report
│
└── docs/                        # Документация и шаблоны
    ├── prd/
    │   └── template.md          # Шаблон PRD
    ├── architecture/
    │   └── template.md          # Шаблон архитектуры
    ├── plans/
    │   └── template.md          # Шаблон плана фичи
    └── reports/
        └── template.md          # Шаблон отчёта
```

### Документы конкретного MVP проекта
Хранятся в `{project}/ai-docs/`:

| Тип документа | Путь | Создаётся на этапе |
|---------------|------|-------------------|
| PRD | `ai-docs/docs/prd/{project}-prd.md` | /idea |
| Архитектура | `ai-docs/docs/architecture/{project}-plan.md` | /plan |
| Исследование | `ai-docs/docs/research/{feature}-research.md` | /research |
| План фичи | `ai-docs/docs/plans/{feature}-plan.md` | /feature-plan |
| Ревью отчёт | `ai-docs/docs/reports/{name}-review.md` | /review |
| QA отчёт | `ai-docs/docs/reports/{name}-qa.md` | /test |
| Валидация | `ai-docs/docs/reports/{name}-validation.md` | /validate |
| RTM (сводка) | `ai-docs/docs/rtm.md` | /idea, обновляется на каждом этапе |
| Контекст для AI | `.claude/project-context.md` | /idea |

---

## 3.7 Матрица трассировки требований (RTM)

### Двойное хранение RTM:

**A) Секция RTM в каждом документе** (PRD, Plan, QA Report):
```markdown
## Матрица трассировки требований

| Req ID | Описание | Статус | Файл реализации | Тест |
|--------|----------|--------|-----------------|------|
| FR-001 | Регистрация пользователя | ✅ | api/v1/users.py:50 | test_users.py:20 |
| FR-002 | Авторизация | ✅ | api/v1/auth.py:30 | test_auth.py:15 |
```

**B) Сводный файл `ai-docs/docs/rtm.md`** (полная картина проекта):
```markdown
# Матрица трассировки требований проекта

## Статистика
- Всего требований: 25
- Реализовано: 23 (92%)
- В работе: 2 (8%)
- Исключено (descoped): 0

## FR — Функциональные требования
| Req ID | Описание | Источник | Статус | Реализация | Тест | Фича/Версия |
|--------|----------|----------|--------|------------|------|-------------|
| FR-001 | Регистрация | PRD v1.0 | ✅ | api/users.py:50 | test_users.py | MVP 1.0 |
| FR-010 | Уведомления | Feature-005 | 🔄 | - | - | MVP 1.1 |

## UI — UI/UX требования
...

## NF — Нефункциональные требования
...

## История изменений
| Дата | Req ID | Действие | Причина |
|------|--------|----------|---------|
| 2025-12-19 | FR-001 | Создано | PRD v1.0 |
| 2025-12-20 | FR-010 | Добавлено | Feature-005 |
```

**Правило 100%**: Все требования должны быть реализованы или официально исключены (descoped).

---

## 3.8 Workflow добавления фичи (детально)

**Пример**: Пользователь запрашивает "Добавить систему уведомлений"

| № | Команда | Агент | Действия | Выход | Ворота |
|---|---------|-------|----------|-------|--------|
| 1 | `/idea` | Аналитик | Верификация промпта, сбор требований к фиче, определение критериев приёмки | `ai-docs/docs/prd/notifications-prd.md` | PRD_READY |
| 2 | `/research` | Исследователь | Анализ существующего кода: какие сервисы затронуты, точки интеграции, используемые паттерны | `ai-docs/docs/research/notifications-research.md` | RESEARCH_DONE |
| 3 | `/feature-plan` | Архитектор | Планирование изменений: новые компоненты, изменения в существующих, миграции БД, новые тесты | `ai-docs/docs/plans/notifications-plan.md` | PLAN_APPROVED |
| 4 | `/generate` | Реализатор | Генерация кода по плану: создание новых файлов, модификация существующих, добавление тестов, обновление миграций | Изменения в коде | IMPLEMENT_OK |
| 5 | `/review` | Ревьюер | Проверка изменений: соответствие плану, качество кода (Ruff, Mypy), безопасность (Bandit) | `ai-docs/docs/reports/notifications-review.md` | REVIEW_OK |
| 6 | `/test` | QA | Запуск тестов: unit тесты, интеграционные тесты, проверка покрытия (≥85%) | `ai-docs/docs/reports/notifications-qa.md` | QA_PASSED |
| 7 | `/validate` | Валидатор | Проверка ВСЕХ ворот: PRD_READY, RESEARCH_DONE, PLAN_APPROVED, IMPLEMENT_OK, REVIEW_OK, QA_PASSED | `ai-docs/docs/reports/notifications-validation.md` | ALL_GATES_PASSED |
| 8 | `/deploy` | Валидатор | Развёртывание: запуск docker-compose, проверка health checks, обновление ai-docs/docs/rtm.md | Развёрнутый проект | DEPLOYED |

---

## 3.9 Список команд AIDD-MVP Generator

| Команда | Агент | Назначение | Пайплайн |
|---------|-------|------------|----------|
| `/idea` | Аналитик | Верификация промпта, сбор требований, создание PRD | CREATE, FEATURE |
| `/research` | Исследователь | Анализ существующего кода (в CREATE — пропуск) | CREATE, FEATURE |
| `/plan` | Архитектор | Планирование полной архитектуры MVP | CREATE |
| `/feature-plan` | Архитектор | Планирование дельты к архитектуре | FEATURE |
| `/generate` | Реализатор | Генерация/модификация кода | CREATE, FEATURE |
| `/review` | Ревьюер | Код-ревью и статический анализ | CREATE, FEATURE |
| `/test` | QA | Запуск тестов и проверка покрытия | CREATE, FEATURE |
| `/validate` | Валидатор | Проверка всех качественных ворот | CREATE, FEATURE |
| `/deploy` | Валидатор | Развёртывание проекта | CREATE, FEATURE |

---

# ЧАСТЬ 4: СХЕМА ПЕРЕНОСА В НОВЫЙ ФРЕЙМВОРК

## 4.1 Что берём из AIDD (статья)

| Компонент | Источник (AIDD) | Целевой файл | Описание |
|-----------|-----------------|--------------|----------|
| **Роли** | 8 ролей в статье → 7 в MVP | `.claude/agents/*.md` | Аналитик, Исследователь, Архитектор, Реализатор, Ревьюер, QA, Валидатор (без Техписца) |
| **Качественные ворота** | 8 ворот | `workflow.md` + `validator.md` | PRD_READY, RESEARCH_DONE, PLAN_APPROVED, IMPLEMENT_OK, REVIEW_OK, QA_PASSED, ALL_GATES_PASSED |
| **Slash-команды** | 9 команд | `.claude/commands/*.md` | /idea, /research, /plan, /feature-plan, /generate, /review, /test, /validate, /deploy |
| **Шаблоны артефактов** | docs/* | `docs/prd/template.md`, `docs/plans/template.md` | Шаблоны PRD, Архитектуры, Отчётов (в проекте: `ai-docs/docs/`) |
| **Хуки** | settings.json | `.claude/settings.json` | Блокировка нарушений ворот |
| **conventions.md** | Формат | `conventions.md` | Соглашения о коде |
| **CLAUDE.md** | Точка входа | `CLAUDE.md` | Инструкции для AI |
| **workflow.md** | Процесс | `workflow.md` | 5-этапный процесс AIDD-MVP |

## 4.2 Что берём из .ai-framework

| Компонент | Источник | Целевой файл | Описание |
|-----------|----------|--------------|----------|
| **Шаблон Business API** | `templates/services/template_business_api/` | `templates/services/fastapi_business_api/` | FastAPI + DDD структура |
| **Шаблон бота** | `templates/services/template_business_bot/` | `templates/services/aiogram_bot/` | Aiogram 3.x + обработчики |
| **Шаблон воркера** | `templates/services/template_business_worker/` | `templates/services/asyncio_worker/` | AsyncIO воркеры |
| **PostgreSQL Data API** | `templates/services/template_data_postgres_api/` | `templates/services/postgres_data_api/` | SQLAlchemy + Alembic |
| **MongoDB Data API** | `templates/services/template_data_mongo_api/` | `templates/services/mongo_data_api/` | Motor + репозитории |
| **Docker Compose** | `templates/infrastructure/` | `templates/infrastructure/docker-compose/` | Dev + Prod конфиги |
| **Nginx** | `templates/nginx/` | `templates/infrastructure/nginx/` | API Gateway |
| **CI/CD** | `.github/workflows/` | `templates/infrastructure/github-actions/` | GitHub Actions |
| **Принципы архитектуры** | `ARCHITECTURE.md` | `knowledge/architecture/` | HTTP-only, DDD |
| **Правила CLAUDE.md** | `CLAUDE.md` | Интегрировать в `CLAUDE.md` | Верификация перед действием |

## 4.3 Что создаём новое

| Компонент | Файл | Описание |
|-----------|------|----------|
| **Единый CLAUDE.md** | `CLAUDE.md` | Объединяет роли AIDD + правила .ai-framework |
| **AIDD-MVP workflow** | `workflow.md` | 5-этапный процесс вместо 7 |
| **Требования к продакшену** | `knowledge/quality/production-requirements.md` | Требования для каждого MVP |
| **Адаптированные агенты** | `.claude/agents/*.md` | 7 ролей (Аналитик, Исследователь, Архитектор, Реализатор, Ревьюер, QA, Валидатор) |
| **Упрощённые команды** | `.claude/commands/*.md` | 9 команд (/idea, /research, /plan, /feature-plan, /generate, /review, /test, /validate, /deploy) |
| **Общие компоненты** | `templates/shared/` | DTO, Схемы, Утилиты |
| **База знаний** | `knowledge/` | Архитектура, сервисы, интеграции, качество |

## 4.4 Маппинг файлов: Источник → Результат

### Из AIDD создаём:
```
Статья AIDD                    →  AIDD-MVP Generator
─────────────────────────────────────────────────────────
conventions.md (формат)        →  /conventions.md
CLAUDE.md (формат)             →  /CLAUDE.md (часть)
workflow.md (формат)           →  /workflow.md

# Агенты (7 ролей)
.claude/agents/analyst.md      →  /.claude/agents/analyst.md
.claude/agents/researcher.md   →  /.claude/agents/researcher.md
.claude/agents/planner.md      →  /.claude/agents/architect.md
.claude/agents/implementer.md  →  /.claude/agents/implementer.md
.claude/agents/reviewer.md     →  /.claude/agents/reviewer.md
.claude/agents/qa.md           →  /.claude/agents/qa.md
.claude/agents/validator.md    →  /.claude/agents/validator.md

# Команды (9 команд)
.claude/commands/idea.md       →  /.claude/commands/idea.md
.claude/commands/researcher.md →  /.claude/commands/research.md
.claude/commands/plan.md       →  /.claude/commands/plan.md
(новая)                        →  /.claude/commands/feature-plan.md
.claude/commands/implement.md  →  /.claude/commands/generate.md
.claude/commands/review.md     →  /.claude/commands/review.md
.claude/commands/qa.md         →  /.claude/commands/test.md
.claude/commands/validate.md   →  /.claude/commands/validate.md
(новая)                        →  /.claude/commands/deploy.md

# Настройки и шаблоны
.claude/hooks/settings.json    →  /.claude/settings.json
docs/prd/template              →  /docs/prd/template.md
docs/plan/template             →  /docs/architecture/template.md
reports/qa/template            →  /docs/reports/template.md
```

### Из .ai-framework копируем:
```
.ai-framework                              →  AIDD-MVP Generator
─────────────────────────────────────────────────────────────────────
templates/services/template_business_api/  →  /templates/services/fastapi_business_api/
templates/services/template_business_bot/  →  /templates/services/aiogram_bot/
templates/services/template_business_worker/ → /templates/services/asyncio_worker/
templates/services/template_data_postgres_api/ → /templates/services/postgres_data_api/
templates/services/template_data_mongo_api/ →  /templates/services/mongo_data_api/
templates/infrastructure/docker-compose.yml → /templates/infrastructure/docker-compose/
templates/infrastructure/.env.example      →  /templates/infrastructure/docker-compose/
templates/nginx/nginx.conf                 →  /templates/infrastructure/nginx/
.github/workflows/                         →  /templates/infrastructure/github-actions/
CLAUDE.md (правила верификации)            →  /CLAUDE.md (часть)
ARCHITECTURE.md                            →  /knowledge/architecture/improved-hybrid.md
docs/guides/dry-kiss-yagni-principles.md   →  /knowledge/quality/dry-kiss-yagni.md
docs/atomic/services/fastapi/*             →  /knowledge/services/fastapi/
docs/atomic/services/aiogram/*             →  /knowledge/services/aiogram/
docs/atomic/services/asyncio-workers/*     →  /knowledge/services/asyncio-workers/
docs/atomic/integrations/redis/*           →  /knowledge/integrations/redis/
docs/atomic/testing/*                      →  /knowledge/quality/testing/
```

---

## Структура проекта

> 📁 **Полная структура проекта** см. в [разделе 3.6](#36-хранение-документов-для-ai-генерации).
>
> MVP проекты создаются в любом месте. Структура каждого проекта соответствует [разделу 3.5](#35-структура-mvp-проекта).

---

## Фазы реализации

### Фаза 1: Основа фреймворка
**Файлы:**
- `/CLAUDE.md` - точка входа, правила верификации
- `/conventions.md` - соглашения о коде (snake_case, docstrings и т.д.)
- `/workflow.md` - описание 5-этапного процесса AIDD-MVP

### Фаза 2: Интеграция Claude Code (.claude/)
**Содержимое**: 7 агентов + 9 команд + settings.json

> Полный список файлов см. [раздел 3.6](#36-хранение-документов-для-ai-генерации), секция `.claude/`

### Фаза 3: Шаблоны сервисов (templates/services/)
**Адаптируем из .ai-framework**: 5 шаблонов сервисов

> Подробное описание см. [раздел 2.5](#25-шаблоны-в-ai-frameworktemplates), секция `services/`

### Фаза 4: Инфраструктура (templates/infrastructure/)
**Адаптируем из .ai-framework**: Docker, Nginx, GitHub Actions

> Подробное описание см. [раздел 2.5](#25-шаблоны-в-ai-frameworktemplates), секция `infrastructure/`

### Фаза 5: Общие компоненты
**Файлы:**
- `/templates/shared/dtos/` - базовые DTO классы
- `/templates/shared/schemas/` - общие Pydantic схемы
- `/templates/shared/utils/` - утилиты (логирование, конфиг и т.д.)

### Фаза 6: База знаний (knowledge/)
**Адаптируем из .ai-framework/docs:**
- `/knowledge/architecture/` - принципы архитектуры
- `/knowledge/services/` - паттерны сервисов
- `/knowledge/integrations/` - паттерны интеграций (Redis, HTTP)
- `/knowledge/infrastructure/` - Docker, Nginx, логирование
- `/knowledge/quality/` - тестирование, линтинг

### Фаза 7: Шаблоны документов (docs/)
**Шаблоны документов:**
- `/docs/prd/template.md` - шаблон PRD
- `/docs/architecture/template.md` - шаблон архитектуры
- `/docs/plans/template.md` - шаблон плана
- `/docs/tasklists/template.md` - шаблон чек-листа
- `/docs/reports/template.md` - шаблон QA отчёта
