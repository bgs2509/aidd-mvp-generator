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
│       ├── prd/               ← PRD документы
│       │   └── {name}-prd.md
│       │
│       ├── architecture/      ← Архитектурные планы
│       │   └── {name}-plan.md
│       │
│       ├── plans/             ← Планы фич (режим FEATURE)
│       │   └── {feature}-plan.md
│       │
│       ├── research/          ← Отчёты исследований
│       │   └── {name}-research.md
│       │
│       ├── reports/           ← Отчёты этапов
│       │   ├── review-report.md
│       │   ├── qa-report.md
│       │   └── validation-report.md
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

| Этап | Артефакт | Путь в целевом проекте |
|------|----------|------------------------|
| 1. Идея | PRD | `ai-docs/docs/prd/{name}-prd.md` |
| 2. Исследование | Отчёт исследования | `ai-docs/docs/research/{name}-research.md` |
| 3. Архитектура (CREATE) | План | `ai-docs/docs/architecture/{name}-plan.md` |
| 3. Архитектура (FEATURE) | План фичи | `ai-docs/docs/plans/{feature}-plan.md` |
| 4. Реализация | Код | `services/*/` |
| 5. Ревью | Отчёт | `ai-docs/docs/reports/review-report.md` |
| 6. QA | Отчёт | `ai-docs/docs/reports/qa-report.md` |
| 7. Валидация | RTM | `ai-docs/docs/rtm.md` |
| 7. Валидация | Отчёт | `ai-docs/docs/reports/validation-report.md` |
| 8. Деплой | — | — |

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
  "gates": {
    "PRD_READY": {
      "passed": true,
      "passed_at": "2025-12-21T10:05:00Z",
      "artifact": "ai-docs/docs/prd/booking-prd.md"
    },
    "RESEARCH_DONE": {
      "passed": true,
      "passed_at": "2025-12-21T10:10:00Z",
      "artifact": "ai-docs/docs/research/booking-research.md"
    },
    "PLAN_APPROVED": {
      "passed": true,
      "passed_at": "2025-12-21T10:20:00Z",
      "artifact": "ai-docs/docs/architecture/booking-plan.md",
      "approved_by": "user"
    },
    "IMPLEMENT_OK": {
      "passed": false
    }
  },
  "artifacts": {
    "prd": "ai-docs/docs/prd/booking-prd.md",
    "research": "ai-docs/docs/research/booking-research.md",
    "plan": "ai-docs/docs/architecture/booking-plan.md"
  }
}
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

### Пути артефактов

| Тип | Суффикс | Пример |
|-----|---------|--------|
| PRD | `-prd.md` | `booking-prd.md` |
| План архитектуры | `-plan.md` | `booking-plan.md` |
| План фичи | `-plan.md` | `notifications-plan.md` |
| Отчёт ревью | `review-*.md` | `review-report.md` |
| Отчёт QA | `qa-*.md` | `qa-report.md` |

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

При первом запуске `/idea` в пустой директории создаётся:

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

**Версия**: 1.0
**Создан**: 2025-12-21
