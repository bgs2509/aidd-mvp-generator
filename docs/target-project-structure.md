# Структура целевого проекта

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
│       ├── reports/           ← Отчёты этапов
│       │   ├── {YYYY-MM-DD}_{FID}_{slug}-review.md
│       │   ├── {YYYY-MM-DD}_{FID}_{slug}-qa.md
│       │   └── {YYYY-MM-DD}_{FID}_{slug}-validation.md
│       │
│       └── rtm.md             ← Requirements Traceability Matrix
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
| 1. Идея | PRD | `ai-docs/docs/prd/{date}_{FID}_{slug}-prd.md` |
| 2. Исследование | Отчёт исследования | `ai-docs/docs/research/{date}_{FID}_{slug}-research.md` |
| 3. Архитектура (CREATE) | План | `ai-docs/docs/architecture/{date}_{FID}_{slug}-plan.md` |
| 3. Архитектура (FEATURE) | План фичи | `ai-docs/docs/plans/{date}_{FID}_{slug}-plan.md` |
| 4. Реализация | Код | `services/*/` |
| 5. Ревью | Отчёт | `ai-docs/docs/reports/{date}_{FID}_{slug}-review.md` |
| 6. QA | Отчёт | `ai-docs/docs/reports/{date}_{FID}_{slug}-qa.md` |
| 7. Валидация | RTM | `ai-docs/docs/rtm.md` |
| 7. Валидация | Отчёт | `ai-docs/docs/reports/{date}_{FID}_{slug}-validation.md` |
| 8. Деплой | — | — |

### Примеры имён файлов

```
2024-12-23_F001_table-booking-prd.md
2024-12-23_F001_table-booking-research.md
2024-12-23_F001_table-booking-plan.md
2024-12-23_F001_table-booking-review.md
2024-12-23_F001_table-booking-qa.md
2024-12-23_F001_table-booking-validation.md
```

---

## Состояние пайплайна

Файл `.pipeline-state.json` в корне целевого проекта:

```json
{
  "project_name": "booking-service",
  "mode": "CREATE",
  "current_stage": 4,
  "created_at": "2025-12-21T10:00:00Z",
  "updated_at": "2025-12-21T10:30:00Z",

  "next_feature_id": 3,

  "current_feature": {
    "id": "F002",
    "name": "email-notify",
    "title": "Email-уведомления о бронированиях",
    "stage": "IMPLEMENT",
    "created": "2025-12-21",
    "artifacts": {
      "prd": "prd/2025-12-21_F002_email-notify-prd.md",
      "research": "research/2025-12-21_F002_email-notify-research.md",
      "plan": "plans/2025-12-21_F002_email-notify-plan.md"
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
        "review": "reports/2025-12-20_F001_table-booking-review.md",
        "qa": "reports/2025-12-20_F001_table-booking-qa.md",
        "validation": "reports/2025-12-21_F001_table-booking-validation.md"
      },
      "services": ["booking_api", "booking_data"]
    }
  },

  "gates": {
    "PRD_READY": {
      "passed": true,
      "passed_at": "2025-12-21T10:05:00Z"
    },
    "RESEARCH_DONE": {
      "passed": true,
      "passed_at": "2025-12-21T10:10:00Z"
    },
    "PLAN_APPROVED": {
      "passed": true,
      "passed_at": "2025-12-21T10:20:00Z",
      "approved_by": "user"
    },
    "IMPLEMENT_OK": {
      "passed": false
    }
  }
}
```

### Структура `current_feature`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Feature ID (F001, F002, ...) |
| `name` | string | slug для имён файлов (kebab-case) |
| `title` | string | Человекочитаемое название |
| `stage` | string | Текущий этап (PRD, RESEARCH, PLAN, IMPLEMENT, ...) |
| `created` | string | Дата создания (YYYY-MM-DD) |
| `artifacts` | object | Карта артефактов (тип → путь) |
| `services` | array | Список созданных сервисов (после IMPLEMENT) |

### Жизненный цикл фичи

```
1. /aidd-idea создаёт current_feature с новым FID
2. Каждый этап добавляет артефакт в current_feature.artifacts
3. /aidd-deploy переносит фичу в features_registry
4. current_feature очищается (null)
5. Готово для следующей фичи
```

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
| Отчёт ревью | `-review.md` | `2024-12-23_F001_table-booking-review.md` |
| Отчёт QA | `-qa.md` | `2024-12-23_F001_table-booking-qa.md` |
| Отчёт валидации | `-validation.md` | `2024-12-23_F001_table-booking-validation.md` |

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

При первом запуске `/aidd-idea` в пустой директории создаётся:

```bash
mkdir -p ai-docs/docs/{prd,architecture,plans,reports,research}
echo '{"project_name":"","mode":"CREATE","current_stage":1,"gates":{}}' > .pipeline-state.json
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
