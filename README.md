# AIDD-MVP Generator

> Фреймворк для быстрой генерации production-ready MVP проектов
> с использованием методологии AI-Driven Development (AIDD)

---

## Что это?

**AIDD-MVP Generator** объединяет:
- **Методологию AIDD** — структурированный процесс разработки с AI-агентами
- **Архитектурные шаблоны** — готовые паттерны для микросервисов
- **Качественные ворота** — автоматическая проверка качества на каждом этапе

**Результат**: Production-ready MVP за ~10 минут.

---

## Характеристики

| Параметр | Значение |
|----------|----------|
| Уровень зрелости | Level 2 (MVP) |
| Покрытие тестами | ≥75% |
| Архитектура | DDD/Hexagonal, HTTP-only |
| Сервисы | FastAPI, Aiogram, AsyncIO Workers |
| Базы данных | PostgreSQL, MongoDB |
| Инфраструктура | Docker, Nginx, CI/CD |

---

## Быстрый старт

### Требования

- Python 3.11+
- Docker & Docker Compose
- Claude Code CLI
- Git 2.40+

### Установка фреймворка (рекомендуется)

```bash
# 1. Создать и инициализировать целевой проект
mkdir restaurant-booking && cd restaurant-booking
git init

# 2. Подключить фреймворк как Git Submodule
git submodule add git@github.com:bgs2509/aidd-mvp-generator.git .aidd
git submodule update --init --recursive

# 3. Запустить Claude Code
claude
```

```bash
# 4. Инициализировать фреймворк (создаёт CLAUDE.md, регистрирует /aidd-* команды)
/aidd-init

# /aidd-init выполняет:
#   - Создаёт CLAUDE.md с инструкциями для AI
#   - Копирует команды в .claude/commands/
#   - Создаёт структуру проекта (ai-docs/, .pipeline-state.json)
```

```bash
# 5. Следовать 9-этапному процессу (этапы 1-8)
/aidd-idea "Создать сервис бронирования столиков в ресторанах"
/aidd-research
/aidd-plan
# ... утвердить план ...
/aidd-generate
/aidd-review
/aidd-test
/aidd-validate
/aidd-deploy

# 6. Запустить сгенерированный проект
make build && make up
```

### Добавление фичи в существующий проект

```bash
# 1. Перейти в директорию проекта (где уже есть .aidd/)
cd my-existing-project

# 2. Запустить Claude Code
claude

# 3. Если команды /aidd-* ещё не зарегистрированы — инициализировать
/aidd-init

# 4. Описать фичу (Claude автоматически определит режим FEATURE)
/aidd-idea "Добавить систему уведомлений по email"

# 5. Следовать пайплайну: /aidd-research → /aidd-feature-plan → /aidd-generate → ...
```

---

## Процесс разработки

9-этапный пайплайн (этапы 0-8) с качественными воротами.

**Этап 0 — Bootstrap (`/aidd-init`)**: Регистрирует `/aidd-*` команды, создаёт структуру проекта.
Без этого этапа остальные команды **не будут работать**.

```
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│   ИДЕЯ    │─▶│ ИССЛЕДО-  │─▶│ АРХИТЕК-  │─▶│ РЕАЛИЗА-  │
│           │  │   ВАНИЕ   │  │   ТУРА    │  │    ЦИЯ    │
│/aidd-idea │  │ /aidd-    │  │  /aidd-   │  │  /aidd-   │
│           │  │ research  │  │   plan    │  │ generate  │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │              │
┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
│ PRD_READY │  │ RESEARCH  │  │   PLAN    │  │IMPLEMENT  │
│           │  │   _DONE   │  │ APPROVED  │  │   _OK     │
└───────────┘  └───────────┘  └───────────┘  └───────────┘

┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│   РЕВЬЮ   │─▶│    QA     │─▶│  ВАЛИДА-  │─▶│  ДЕПЛОЙ   │
│           │  │           │  │    ЦИЯ    │  │           │
│  /aidd-   │  │  /aidd-   │  │  /aidd-   │  │  /aidd-   │
│  review   │  │   test    │  │ validate  │  │  deploy   │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │              │
┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
│ REVIEW_OK │  │ QA_PASSED │  │ALL_GATES  │  │ DEPLOYED  │
│           │  │           │  │  PASSED   │  │           │
└───────────┘  └───────────┘  └───────────┘  └───────────┘
```

---

## 7 AI-ролей

| Роль | Команда | Задача |
|------|---------|--------|
| **Аналитик** | `/aidd-idea` | Создание PRD из идеи |
| **Исследователь** | `/aidd-research` | Анализ кода и технологий |
| **Архитектор** | `/aidd-plan` | Проектирование системы |
| **Реализатор** | `/aidd-generate` | Генерация кода |
| **Ревьюер** | `/aidd-review` | Код-ревью |
| **QA** | `/aidd-test` | Тестирование |
| **Валидатор** | `/aidd-validate` | Проверка качества |

---

## Типы генерируемых сервисов

| Тип | Технология | Описание |
|-----|------------|----------|
| **Business API** | FastAPI | REST API |
| **Business Bot** | Aiogram | Telegram бот |
| **Background Worker** | AsyncIO | Фоновые задачи |
| **Data API PostgreSQL** | FastAPI + SQLAlchemy | CRUD для PostgreSQL |
| **Data API MongoDB** | FastAPI + Motor | CRUD для MongoDB |

---

## Структура проекта

```
aidd-mvp-generator/
│
├── CLAUDE.md              # Точка входа для AI
├── conventions.md         # Соглашения о коде
├── workflow.md            # Процесс разработки
├── README.md              # Этот файл
│
├── .claude/               # Интеграция Claude Code
│   ├── agents/            # 7 AI-ролей
│   └── commands/          # 9 slash-команд
│
├── roles/                 # Детальные инструкции ролей
├── knowledge/             # База знаний
├── templates/             # Шаблоны сервисов
│   ├── services/          # FastAPI, Aiogram, Workers
│   ├── shared/            # Общие компоненты
│   └── infrastructure/    # Docker, Nginx, CI/CD
│
└── docs/                  # Шаблоны документов
```

---

## Документация

| Документ | Описание |
|----------|----------|
| [CLAUDE.md](CLAUDE.md) | Главная точка входа для AI-агентов |
| [conventions.md](conventions.md) | Соглашения о коде и стиле |
| [workflow.md](workflow.md) | 9-этапный процесс разработки (этапы 0-8) |

---

## Архитектурные принципы

- **HTTP-only доступ к данным** — бизнес-сервисы не обращаются к БД напрямую
- **DDD/Hexagonal** — разделение на слои (api/application/domain/infrastructure)
- **Async-First** — все I/O операции асинхронные
- **Типобезопасность** — полные type hints для всех функций

---

## Лицензия

MIT

---

## Авторы

Создано с использованием методологии AIDD
(AI-Driven Development)
