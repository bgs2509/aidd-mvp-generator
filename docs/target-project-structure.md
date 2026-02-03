# Структура целевого проекта

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Назначение**: Описание структуры проекта, который СОЗДАЁТСЯ генератором.
> **ВАЖНО**: НЕ путать со структурой самого генератора (aidd-mvp-generator)!

---

## Концептуальное разделение

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ДВА РАЗНЫХ ПРОЕКТА                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  aidd-mvp-generator/          {project-name}/                           │
│  ─────────────────────        ─────────────────────                     │
│  ФРЕЙМВОРК                    ПРИЛОЖЕНИЕ                                │
│  (инструкции, шаблоны)        (создаётся генератором)                   │
│                                                                         │
│  Содержит:                    Содержит:                                 │
│  • CLAUDE.md                  • services/                               │
│  • workflow.md                • ai-docs/docs/                           │
│  • .claude/agents/            • docker-compose.yml                      │
│  • templates/                 • Makefile                                │
│  • knowledge/                 • .pipeline-state.json                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Структура целевого проекта

```
{project-name}/
│
├── .pipeline-state.json       ← Состояние пайплайна AIDD
├── CHANGELOG.md               ← Журнал изменений проекта
│
├── ai-docs/                   ← Артефакты AI-агентов
│   └── docs/
│       ├── FEATURES.md        ← Реестр всех фич (индекс)
│       │
│       ├── prd/               ← PRD документы
│       │   └── {YYYY-MM-DD}_{FID}_{slug}-prd.md
│       │
│       ├── architecture/      ← Архитектурные планы (CREATE)
│       │   └── {YYYY-MM-DD}_{FID}_{slug}-plan.md
│       │
│       ├── plans/             ← Планы фич (FEATURE)
│       │   └── {YYYY-MM-DD}_{FID}_{slug}-plan.md
│       │
│       ├── research/          ← Отчёты исследований
│       │   └── {YYYY-MM-DD}_{FID}_{slug}-research.md
│       │
│       └── reports/           ← Completion Reports
│           └── {YYYY-MM-DD}_{FID}_{slug}-completion.md
│
├── services/                  ← Код сервисов (DDD/Hexagonal)
│   ├── {name}_api/            ← Business API
│   │   ├── api/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── {name}_data/           ← Data API
│   │   ├── api/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   ├── {name}_bot/            ← Telegram Bot (опционально)
│   │   └── ...
│   │
│   └── {name}_worker/         ← Background Worker (опционально)
│       └── ...
│
├── docs/                      ← Публичная документация API
│   └── api/
│       └── openapi.yaml
│
├── nginx/                     ← Конфигурация API Gateway
│   ├── nginx.conf
│   └── conf.d/
│       └── api.conf
│
├── .claude/                   ← Локальные настройки Claude Code
│   └── settings.local.json    ← Персональные permissions (НЕ в git!)
│
├── docker-compose.yml         ← Оркестрация контейнеров
├── docker-compose.dev.yml     ← Для разработки
├── Makefile                   ← Команды управления
├── .env.example               ← Шаблон переменных окружения
├── .gitignore
└── README.md                  ← Документация проекта
```

---

## Таблица артефактов

> **Формат имени**: `{YYYY-MM-DD}_{FID}_{slug}-{type}.md`
> Подробнее: [artifact-naming.md](artifact-naming.md)

| Этап | Артефакт | Путь в целевом проекте |
|------|----------|------------------------|
| — | Реестр фич | `ai-docs/docs/FEATURES.md` |
| 1. Идея | PRD | `ai-docs/docs/_analysis/{date}_{FID}_{slug}-prd.md` |
| 2. Исследование | Отчёт исследования | `ai-docs/docs/research/{date}_{FID}_{slug}-research.md` |
| 3. Архитектура (CREATE) | План | `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}-plan.md` |
| 3. Архитектура (FEATURE) | План фичи | `ai-docs/docs/_plans/features/{date}_{FID}_{slug}-plan.md` |
| 4. Реализация | Код | `services/*/` |
| 5. Quality & Deploy | Completion Report | `ai-docs/docs/_validation/{date}_{FID}_{slug}-completion.md` |

### Примеры имён файлов

```
2024-12-23_F001_table-booking-prd.md
2024-12-23_F001_table-booking-research.md
2024-12-23_F001_table-booking-plan.md
2024-12-23_F001_table-booking-completion.md
```

---

## Состояние пайплайна

Файл `.pipeline-state.json` в корне целевого проекта:

```json
{
  "version": "2.0",
  "project_name": "booking-service",
  "mode": "CREATE",
  "created_at": "2025-12-21T10:00:00Z",
  "updated_at": "2025-12-21T10:30:00Z",

  "next_feature_id": 3,

  "global_gates": {
    "BOOTSTRAP_READY": { "passed": true, "passed_at": "2025-12-21T09:55:00Z" }
  },

  "active_pipelines": {
    "F002": {
      "branch": "feature/F002-email-notify",
      "name": "email-notify",
      "title": "Email-уведомления о бронированиях",
      "stage": "IMPLEMENT",
      "created": "2025-12-21",
      "gates": {
        "PRD_READY": { "passed": true, "passed_at": "2025-12-21T10:05:00Z" },
        "RESEARCH_DONE": { "passed": true, "passed_at": "2025-12-21T10:10:00Z" },
        "PLAN_APPROVED": { "passed": true, "passed_at": "2025-12-21T10:20:00Z", "approved_by": "user" },
        "IMPLEMENT_OK": { "passed": false }
      },
      "artifacts": {
        "prd": "prd/2025-12-21_F002_email-notify-prd.md",
        "research": "research/2025-12-21_F002_email-notify-research.md",
        "plan": "plans/2025-12-21_F002_email-notify-plan.md"
      }
    }
  },

  "features_registry": {
    "F001": {
      "name": "table-booking",
      "title": "Бронирование столиков",
      "status": "DEPLOYED",
      "created": "2025-12-20",
      "deployed": "2025-12-21",
      "artifacts": {
        "prd": "prd/2025-12-20_F001_table-booking-prd.md",
        "research": "research/2025-12-20_F001_table-booking-research.md",
        "plan": "architecture/2025-12-20_F001_table-booking-plan.md",
        "completion": "reports/2025-12-21_F001_table-booking-completion.md"
      },
      "services": ["booking_api", "booking_data"]
    }
  }
}
```

### Структура `active_pipelines[FID]`

| Поле | Тип | Описание |
|------|-----|----------|
| `branch` | string | Git-ветка фичи (feature/F001-name) |
| `name` | string | slug для имён файлов (kebab-case) |
| `title` | string | Человекочитаемое название |
| `stage` | string | Текущий этап (IDEA, RESEARCH, PLAN, IMPLEMENT, ...) |
| `created` | string | Дата создания (YYYY-MM-DD) |
| `gates` | object | Ворота фичи (изолированы от других пайплайнов) |
| `artifacts` | object | Карта артефактов (тип → путь) |

### Жизненный цикл фичи (v2)

```
1. /aidd-analyze создаёт active_pipelines[FID] с новым Feature ID
2. Каждый этап обновляет gates и artifacts в active_pipelines[FID]
3. /aidd-validate переносит фичу в features_registry (при DEPLOYED)
4. Запись удаляется из active_pipelines
5. Готово для следующей фичи (или параллельной разработки)
```

---

## Журнал изменений (CHANGELOG.md)

Файл `CHANGELOG.md` в корне целевого проекта:

### Назначение

**Единая точка входа** для понимания истории проекта. Содержит:
- Завершённые фичи (автоматически из Completion Reports)
- Критические изменения между фичами (вручную от AI)
- Хронология в обратном порядке (новые сверху)

### Структура

```markdown
# Changelog

> Автогенерируется AIDD-MVP Generator при `/aidd-validate` (DEPLOYED)
> Ручные записи добавляются AI при критических изменениях

---

## [Unreleased]

### Active Features (в разработке)
- **F002** — Email-уведомления (stage: IMPLEMENT)

### Recent Changes

#### 2025-12-22 - Hotfix: SQL injection в User API
**Security**
- `user_api/repository.py`: параметризованы SQL запросы

**Impact**: CRITICAL
**Rollback**: `git revert abc123`

---

## [F001] - 2025-12-21 — Бронирование столиков

> **Status**: DEPLOYED
> **Services**: `booking_api`, `booking_data`
> **Completion Report**: [ai-docs/docs/reports/2025-12-21_F001_table-booking-completion.md]

### Added
- Базовая функциональность бронирования
- Endpoints: POST /api/v1/bookings, GET /api/v1/bookings

### Architecture Decisions
- ADR-001: HTTP-only Data Access (DDD/Hexagonal)

---

**Версия**: 1.0
**Последнее обновление**: 2025-12-22
```

### Автоматическое обновление

| Событие | Действие |
|---------|----------|
| `/aidd-init` | Создаётся из шаблона (если нет истории) или генерируется из `features_registry` |
| `/aidd-validate` → DEPLOYED | Автоматически добавляется секция фичи из Completion Report |
| Критические изменения | AI вручную добавляет записи в `[Unreleased]` (см. CLAUDE.md ЦП) |

### Зачем AI читает CHANGELOG.md

**КРИТИЧНО**: AI ОБЯЗАН читать `CHANGELOG.md` ПЕРЕД началом работы (см. CLAUDE.md ЦП).

Это позволяет:
- Понять контекст проекта за 30 секунд
- Не дублировать функциональность
- Учесть известные ограничения (Known Limitations)
- Понять зависимости между фичами
- Следовать архитектурным решениям (ADR)

---

## Настройки Claude Code (.claude/)

> **ВАЖНО**: Директория `.claude/` содержит локальные настройки Claude Code для целевого проекта.

### Два типа файлов настроек

| Файл | Расположение | В git? | Назначение |
|------|--------------|--------|------------|
| `settings.json` | `.aidd/.claude/settings.json` | Да (в submodule) | Общие permissions и hooks фреймворка |
| `settings.local.json` | `./.claude/settings.local.json` | **Нет** | Персональные локальные permissions |

### settings.local.json

Файл для персональных настроек разработчика, которые **НЕ должны коммититься в git**.

**Назначение**:
- Дополнительные permissions для bash-команд (npm, cargo, poetry)
- Доверенные домены для WebFetch (docs.python.org, etc.)
- Локальные override настроек

**Шаблон**:
```json
{
  "permissions": {
    "allow": [
      "WebFetch(domain:docs.python.org)",
      "WebFetch(domain:fastapi.tiangolo.com)",
      "Bash(npm:*)",
      "Bash(poetry:*)"
    ]
  }
}
```

**Создание**:
```bash
# Скопировать шаблон из фреймворка
mkdir -p .claude
cp .aidd/templates/project/.claude/settings.local.json.example .claude/settings.local.json
```

> **Примечание**: Файл добавлен в `.gitignore` шаблона проекта.

---

## Важные соглашения

### Формат имён артефактов

```
{YYYY-MM-DD}_{FID}_{slug}-{type}.md

Где:
- YYYY-MM-DD — дата создания
- FID — Feature ID (F001, F002, ...)
- slug — kebab-case название (≤30 символов)
- type — тип артефакта
```

### Суффиксы типов

| Тип | Суффикс | Пример |
|-----|---------|--------|
| PRD | `-prd.md` | `2024-12-23_F001_table-booking-prd.md` |
| План архитектуры | `-plan.md` | `2024-12-23_F001_table-booking-plan.md` |
| План фичи | `-plan.md` | `2024-12-23_F042_email-notify-plan.md` |
| Исследование | `-research.md` | `2024-12-23_F001_table-booking-research.md` |
| Completion Report | `-completion.md` | `2024-12-23_F001_table-booking-completion.md` |

> Подробная спецификация: [artifact-naming.md](artifact-naming.md)

### Именование сервисов

```
{контекст}_{домен}_{тип}

Примеры:
- booking_restaurant_api      ← Business API
- booking_restaurant_data     ← Data API
- booking_restaurant_bot      ← Telegram Bot
- booking_restaurant_worker   ← Background Worker
```

---

## Bootstrap: Инициализация структуры

При первом запуске `/aidd-analyze` в пустой директории создаётся:

```bash
mkdir -p ai-docs/docs/{prd,architecture,plans,reports,research}
echo '{"version":"2.0","project_name":"","mode":"CREATE","global_gates":{},"active_pipelines":{},"next_feature_id":1}' > .pipeline-state.json
```

---

## См. также

- [CLAUDE.md](../CLAUDE.md) — Структура генератора
- [workflow.md](../workflow.md) — Процесс разработки
- [conventions.md](../conventions.md) — Соглашения о коде

---

**Версия**: 2.0
**Создан**: 2025-12-21
**Обновлён**: 2025-12-23
