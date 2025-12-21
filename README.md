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
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd
git submodule update --init --recursive

# 3. Создать точку входа для AI
echo "# Restaurant Booking\n\nСм. .aidd/CLAUDE.md для работы с AI." > CLAUDE.md

# 4. Запустить Claude Code
claude
/idea "Создать сервис бронирования столиков в ресторанах"

# 5. Следовать 9-этапному процессу (этапы 0-8)
# /init → /idea → /research → /plan → /generate → /review → /test → /validate → /deploy

# 6. Запустить сгенерированный проект
make build && make up
```

### Добавление фичи в существующий проект

```bash
# 1. Перейти в директорию проекта (где уже есть .aidd/)
cd my-existing-project

# 2. Запустить Claude Code
claude

# 3. Описать фичу
/idea "Добавить систему уведомлений по email"

# Claude Code определит режим FEATURE и адаптирует процесс
```

---

## Процесс разработки

9-этапный пайплайн (этапы 0-8) с качественными воротами:

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  ИДЕЯ   │───▶│ИССЛЕДО- │───▶│АРХИТЕК- │───▶│РЕАЛИЗА- │
│         │    │ ВАНИЕ   │    │  ТУРА   │    │   ЦИЯ   │
│ /idea   │    │/research│    │ /plan   │    │/generate│
└────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
     │              │              │              │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
│PRD_READY│    │RESEARCH │    │  PLAN   │    │IMPLEMENT│
│         │    │  _DONE  │    │APPROVED │    │   _OK   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘

┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  РЕВЬЮ  │───▶│   QA    │───▶│ВАЛИДА-  │───▶│ ДЕПЛОЙ  │
│         │    │         │    │   ЦИЯ   │    │         │
│ /review │    │  /test  │    │/validate│    │ /deploy │
└────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
     │              │              │              │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
│ REVIEW  │    │   QA    │    │ALL_GATES│    │DEPLOYED │
│   _OK   │    │ PASSED  │    │ PASSED  │    │         │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
```

---

## 7 AI-ролей

| Роль | Команда | Задача |
|------|---------|--------|
| **Аналитик** | `/idea` | Создание PRD из идеи |
| **Исследователь** | `/research` | Анализ кода и технологий |
| **Архитектор** | `/plan` | Проектирование системы |
| **Реализатор** | `/generate` | Генерация кода |
| **Ревьюер** | `/review` | Код-ревью |
| **QA** | `/test` | Тестирование |
| **Валидатор** | `/validate` | Проверка качества |

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
