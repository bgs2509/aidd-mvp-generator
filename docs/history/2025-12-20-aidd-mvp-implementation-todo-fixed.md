# TODO: Реализация AIDD-MVP Generator Framework (ИСПРАВЛЕННАЯ ВЕРСИЯ)

**Дата создания**: 2025-12-20
**Исходный документ**: docs/history/2025-12-19-aidd-mvp-implementation-todo.md
**Статус**: Исправленная версия с корректными форматами Claude Code API
**Последнее обновление**: 2025-12-20 — добавлены отметки о реализации

---

## ВАЖНО: Ограничения Claude Code

> **Этот раздел объясняет, что Claude Code поддерживает нативно, а что нужно реализовать самостоятельно.**

### Что Claude Code поддерживает нативно

| Функция | Как использовать |
|---------|------------------|
| **Кастомные команды** | `.claude/commands/*.md` — Markdown файлы с промптами |
| **Subagents** | `.claude/agents/*.md` — агенты для Task tool |
| **Permissions** | `settings.json` — разрешения на инструменты |
| **Hooks** | `settings.json` — события PreToolUse, PostToolUse и др. |

### Что НЕ поддерживается нативно (нужна внешняя реализация)

| Функция | Как реализовать |
|---------|-----------------|
| **Качественные ворота** | Внешние скрипты, вызываемые через хуки |
| **7 AI ролей** | Создать как subagents + slash-команды |
| **AIDD процесс** | Описать в промптах команд |
| **Автоматическая проверка PRD_READY** | Bash скрипт + PreToolUse hook |

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

| # | Статус | Файл | Описание | Зависит от |
|---|--------|------|----------|------------|
| 0.1.1 | [x] | `CLAUDE.md` | Главная точка входа для AI-агентов | — |
| 0.1.2 | [x] | `conventions.md` | Соглашения о коде | — |
| 0.1.3 | [x] | `workflow.md` | Описание 8-этапного процесса | — |
| 0.1.4 | [x] | `README.md` | Документация фреймворка | 0.1.1-0.1.3 |

### Детали задачи 0.1.1: CLAUDE.md

**Содержимое должно включать:**
```
- Описание фреймворка AIDD-MVP Generator
- Ссылки на ключевые файлы:
  - conventions.md
  - workflow.md
  - .claude/commands/ (slash-команды)
  - knowledge/ (база знаний)
- Правила верификации перед действием
- Архитектурные принципы (HTTP-only, DDD, Hexagonal)
- Порядок чтения документации для AI

ВАЖНО: НЕ ссылаться на несуществующие функции Claude Code!
```

---

# ФАЗА 1: ИНТЕГРАЦИЯ CLAUDE CODE (.claude/)

## 1.1 Настройки и хуки

| # | Статус | Файл | Описание | Зависит от |
|---|--------|------|----------|------------|
| 1.1.1 | [x] | `.claude/settings.json` | Permissions и hooks | — |

### Детали задачи 1.1.1: settings.json

> **ИСПРАВЛЕНО**: Правильный формат согласно документации Claude Code

**Правильное содержимое:**
```json
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Glob(**)",
      "Grep(**)",
      "Edit(**/*.py)",
      "Edit(**/*.md)",
      "Edit(**/*.yml)",
      "Edit(**/*.yaml)",
      "Edit(**/*.json)",
      "Edit(**/*.toml)",
      "Edit(**/Dockerfile)",
      "Edit(**/Makefile)",
      "Write(**/*.py)",
      "Write(**/*.md)",
      "Bash(git :*)",
      "Bash(make :*)",
      "Bash(docker :*)",
      "Bash(pytest :*)",
      "Bash(ls :*)",
      "Bash(mkdir :*)"
    ],
    "deny": [
      "Edit(**/.env)",
      "Edit(**/*.secret)",
      "Edit(**/*credentials*)",
      "Write(**/.env)",
      "Bash(rm -rf :*)",
      "Bash(sudo :*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Проверка перед редактированием файла'"
          }
        ]
      }
    ]
  }
}
```

**Ключевые правила синтаксиса:**
1. **Bash permissions** используют формат `Bash(prefix :*)` — двоеточие перед звёздочкой
2. **File permissions** используют формат `Tool(path/pattern)` — glob patterns в скобках
3. **Hooks** требуют `matcher` (regex для инструментов) и массив `hooks`
4. **Типы хуков**: `"command"` (bash) или `"prompt"` (LLM)

**Поддерживаемые события хуков:**
- `PreToolUse` — перед вызовом инструмента
- `PostToolUse` — после вызова инструмента
- `UserPromptSubmit` — при отправке сообщения пользователем
- `PermissionRequest` — при запросе разрешения
- `SessionStart` — при запуске сессии
- `SessionEnd` — при завершении сессии
- `Notification` — при уведомлениях
- `Stop` — при остановке
- `PreCompact` — перед компактификацией контекста

---

## 1.2 Команды (9 файлов)

> **ИСПРАВЛЕНО**: Команды — это Markdown файлы с промптами, НЕ "вызывающие агентов"

| # | Статус | Файл | Команда | Описание | Зависит от |
|---|--------|------|---------|----------|------------|
| 1.2.1 | [x] | `.claude/commands/idea.md` | /idea | Создание PRD | — |
| 1.2.2 | [x] | `.claude/commands/research.md` | /research | Анализ кодовой базы | 1.2.1 |
| 1.2.3 | [x] | `.claude/commands/plan.md` | /plan | Архитектурный план | 1.2.2 |
| 1.2.4 | [x] | `.claude/commands/feature-plan.md` | /feature-plan | План фичи | 1.2.2 |
| 1.2.5 | [x] | `.claude/commands/generate.md` | /generate | Генерация кода | 1.2.3/1.2.4 |
| 1.2.6 | [x] | `.claude/commands/review.md` | /review | Код-ревью | 1.2.5 |
| 1.2.7 | [x] | `.claude/commands/test.md` | /test | Тестирование | 1.2.6 |
| 1.2.8 | [x] | `.claude/commands/validate.md` | /validate | Валидация | 1.2.7 |
| 1.2.9 | [x] | `.claude/commands/deploy.md` | /deploy | Деплой | 1.2.8 |

### Правильный формат команды (.claude/commands/*.md)

```markdown
---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.py), Bash(git :*)
argument-hint: "[описание идеи проекта]"
description: Создать PRD документ из идеи пользователя
---

# Роль: Аналитик

Ты — AI-аналитик в фреймворке AIDD-MVP Generator.

## Твоя задача

Создать PRD (Product Requirements Document) для идеи: $ARGUMENTS

## Порядок действий

1. Прочитай CLAUDE.md и conventions.md для понимания контекста
2. Проанализируй идею пользователя
3. Задай уточняющие вопросы если нужно
4. Создай файл ai-docs/docs/prd/{name}-prd.md по шаблону

## Шаблон PRD

[Вставить шаблон PRD]

## Критерии завершения

- [ ] Все секции PRD заполнены
- [ ] Требования имеют ID (FR-*, NF-*, UI-*)
- [ ] Нет блокирующих вопросов
```

**Ключевые элементы:**
1. **YAML frontmatter** с `---` в начале и конце
2. **allowed-tools** — какие инструменты доступны команде
3. **argument-hint** — подсказка для аргументов
4. **description** — описание команды
5. **$ARGUMENTS** — placeholder для аргументов пользователя

---

## 1.3 Subagents (7 файлов — РЕАЛИЗОВАНО)

> **ПРИМЕЧАНИЕ**: Вместо 3 предложенных агентов были созданы 7 ролевых агентов,
> соответствующих этапам AIDD-MVP пайплайна.

| # | Статус | Файл | Название | Описание | Зависит от |
|---|--------|------|----------|----------|------------|
| 1.3.1 | [x] | `.claude/agents/analyst.md` | analyst | Аналитик — создание PRD | — |
| 1.3.2 | [x] | `.claude/agents/researcher.md` | researcher | Исследователь — анализ кода | — |
| 1.3.3 | [x] | `.claude/agents/architect.md` | architect | Архитектор — проектирование | — |
| 1.3.4 | [x] | `.claude/agents/implementer.md` | implementer | Реализатор — генерация кода | — |
| 1.3.5 | [x] | `.claude/agents/reviewer.md` | reviewer | Ревьюер — код-ревью | — |
| 1.3.6 | [x] | `.claude/agents/qa.md` | qa | QA — тестирование | — |
| 1.3.7 | [x] | `.claude/agents/validator.md` | validator | Валидатор — проверка ворот | — |

### Правильный формат subagent (.claude/agents/*.md)

```markdown
---
name: code-reviewer
description: Эксперт по ревью кода Python
tools: Read, Grep, Glob
model: inherit
---

# Роль

Ты — эксперт по ревью кода. Анализируй код и предоставляй обратную связь.

## Что проверять

1. Соответствие conventions.md
2. Архитектурные принципы DDD/Hexagonal
3. Типобезопасность (type hints)
4. Тесты и покрытие

## Формат ответа

Предоставь структурированный отчёт с:
- Критическими проблемами
- Предупреждениями
- Рекомендациями
```

**Ключевые элементы:**
1. **name** — идентификатор агента
2. **description** — краткое описание
3. **tools** — доступные инструменты (Read, Grep, Glob, Edit, Write, Bash)
4. **model** — `inherit` (наследовать) или конкретная модель

---

# ФАЗА 2: ИНСТРУКЦИИ РОЛЕЙ (roles/)

> **ПРИМЕЧАНИЕ**: Папка `roles/` содержит детальные инструкции для каждой роли.
> Эти инструкции читаются AI из промптов команд, НЕ автоматически.

## 2.1 Аналитик (4 файла)

| # | Статус | Файл | Функция | Зависит от |
|---|--------|------|---------|------------|
| 2.1.1 | [x] | `roles/analyst/initialization.md` | Инициализация | — |
| 2.1.2 | [x] | `roles/analyst/prompt-validation.md` | Верификация промпта | 2.1.1 |
| 2.1.3 | [x] | `roles/analyst/requirements-gathering.md` | Сбор требований | 2.1.2 |
| 2.1.4 | [x] | `roles/analyst/prd-formation.md` | Формирование PRD | 2.1.3 |

## 2.2 Исследователь (4 файла)

| # | Статус | Файл | Функция | Зависит от |
|---|--------|------|---------|------------|
| 2.2.1 | [x] | `roles/researcher/codebase-analysis.md` | Анализ кодовой базы | — |
| 2.2.2 | [x] | `roles/researcher/pattern-identification.md` | Выявление паттернов | 2.2.1 |
| 2.2.3 | [x] | `roles/researcher/constraint-identification.md` | Выявление ограничений | 2.2.2 |
| 2.2.4 | [x] | `roles/researcher/pipeline-refinement.md` | Уточнение пайплайна | 2.2.3 |

## 2.3 Архитектор (5 файлов)

| # | Статус | Файл | Функция | Зависит от |
|---|--------|------|---------|------------|
| 2.3.1 | [x] | `roles/architect/architecture-design.md` | Проектирование архитектуры | — |
| 2.3.2 | [x] | `roles/architect/maturity-level-selection.md` | Выбор по уровню зрелости | 2.3.1 |
| 2.3.3 | [x] | `roles/architect/service-naming.md` | Именование сервисов | 2.3.2 |
| 2.3.4 | [x] | `roles/architect/implementation-plan.md` | Создание Implementation Plan | 2.3.3 |
| 2.3.5 | [x] | `roles/architect/api-contracts.md` | Определение контрактов API | 2.3.4 |

## 2.4 Реализатор (8 файлов)

| # | Статус | Файл | Функция | Зависит от |
|---|--------|------|---------|------------|
| 2.4.1 | [x] | `roles/implementer/infrastructure-setup.md` | Stage 4.1: Инфраструктура | — |
| 2.4.2 | [x] | `roles/implementer/data-service.md` | Stage 4.2: Data Service | 2.4.1 |
| 2.4.3 | [x] | `roles/implementer/business-api.md` | Stage 4.3: Business API | 2.4.2 |
| 2.4.4 | [x] | `roles/implementer/background-worker.md` | Stage 4.4: Background Worker | 2.4.3 |
| 2.4.5 | [x] | `roles/implementer/telegram-bot.md` | Stage 4.5: Telegram Bot | 2.4.3 |
| 2.4.6 | [x] | `roles/implementer/testing.md` | Stage 4.6: Тестирование | 2.4.1-2.4.5 |
| 2.4.7 | [x] | `roles/implementer/logging.md` | Логирование | 2.4.1 |
| 2.4.8 | [x] | `roles/implementer/nginx.md` | Nginx | 2.4.1 |

## 2.5 Ревьюер (3 файла)

| # | Статус | Файл | Функция | Зависит от |
|---|--------|------|---------|------------|
| 2.5.1 | [x] | `roles/reviewer/architecture-compliance.md` | Проверка архитектуры | — |
| 2.5.2 | [x] | `roles/reviewer/convention-compliance.md` | Проверка конвенций | 2.5.1 |
| 2.5.3 | [x] | `roles/reviewer/review-report.md` | Создание Review Report | 2.5.2 |

## 2.6 QA (4 файла)

| # | Статус | Файл | Функция | Зависит от |
|---|--------|------|---------|------------|
| 2.6.1 | [x] | `roles/qa/test-scenarios.md` | Создание тестовых сценариев | — |
| 2.6.2 | [x] | `roles/qa/test-execution.md` | Выполнение тестов | 2.6.1 |
| 2.6.3 | [x] | `roles/qa/coverage-verification.md` | Верификация coverage | 2.6.2 |
| 2.6.4 | [x] | `roles/qa/qa-report.md` | Создание QA Report | 2.6.3 |

## 2.7 Валидатор (3 файла)

| # | Статус | Файл | Функция | Зависит от |
|---|--------|------|---------|------------|
| 2.7.1 | [x] | `roles/validator/quality-gates.md` | Проверка quality gates | — |
| 2.7.2 | [x] | `roles/validator/artifact-verification.md` | Проверка артефактов | 2.7.1 |
| 2.7.3 | [x] | `roles/validator/validation-report.md` | Создание Validation Report | 2.7.2 |

---

# ФАЗА 3: БАЗА ЗНАНИЙ (knowledge/)

## 3.1 Архитектура

| # | Статус | Файл | Описание |
|---|--------|------|----------|
| 3.1.1 | [x] | `knowledge/architecture/improved-hybrid.md` | Гибридная архитектура |
| 3.1.2 | [x] | `knowledge/architecture/ddd-hexagonal.md` | DDD и Hexagonal принципы |
| 3.1.3 | [x] | `knowledge/architecture/data-access.md` | HTTP-only доступ к данным |
| 3.1.4 | [x] | `knowledge/architecture/service-separation.md` | Разделение сервисов |
| 3.1.5 | [x] | `knowledge/architecture/event-loop.md` | Управление event loop |
| 3.1.6 | [x] | `knowledge/architecture/naming/README.md` | Соглашения об именовании |
| 3.1.7 | [x] | `knowledge/architecture/naming/services.md` | Именование сервисов |
| 3.1.8 | [x] | `knowledge/architecture/naming/python.md` | Именование в Python |
| 3.1.9 | [x] | `knowledge/architecture/quality-standards.md` | Стандарты качества |
| 3.1.10 | [x] | `knowledge/architecture/project-structure.md` | Структура проекта |

## 3.2 Сервисы

| # | Статус | Файл | Описание |
|---|--------|------|----------|
| 3.2.1 | [x] | `knowledge/services/fastapi/application-factory.md` | Фабрика приложений |
| 3.2.2 | [x] | `knowledge/services/fastapi/routing-patterns.md` | Паттерны маршрутизации |
| 3.2.3 | [x] | `knowledge/services/fastapi/dependency-injection.md` | Внедрение зависимостей |
| 3.2.4 | [x] | `knowledge/services/fastapi/schema-validation.md` | Валидация схем |
| 3.2.5 | [x] | `knowledge/services/fastapi/error-handling.md` | Обработка ошибок |
| 3.2.6 | [x] | `knowledge/services/aiogram/basic-setup.md` | Базовая настройка бота |
| 3.2.7 | [x] | `knowledge/services/aiogram/handler-patterns.md` | Паттерны обработчиков |
| 3.2.8 | [x] | `knowledge/services/aiogram/middleware-setup.md` | Настройка middleware |
| 3.2.9 | [x] | `knowledge/services/aiogram/state-management.md` | Управление состоянием |
| 3.2.10 | [x] | `knowledge/services/asyncio-workers/basic-setup.md` | Базовая настройка воркера |
| 3.2.11 | [x] | `knowledge/services/asyncio-workers/task-management.md` | Управление задачами |
| 3.2.12 | [x] | `knowledge/services/asyncio-workers/signal-handling.md` | Обработка сигналов |
| 3.2.13 | [x] | `knowledge/services/data-services/postgres-setup.md` | Настройка PostgreSQL |
| 3.2.14 | [x] | `knowledge/services/data-services/repository-patterns.md` | Паттерны репозиториев |

## 3.3 Интеграции

| # | Статус | Файл | Описание |
|---|--------|------|----------|
| 3.3.1 | [x] | `knowledge/integrations/http/business-to-data.md` | HTTP вызовы между сервисами |
| 3.3.2 | [x] | `knowledge/integrations/http/client-patterns.md` | Паттерны HTTP клиентов |
| 3.3.3 | [x] | `knowledge/integrations/http/error-handling.md` | Обработка ошибок HTTP |
| 3.3.4 | [x] | `knowledge/integrations/redis/caching.md` | Стратегии кэширования |
| 3.3.5 | [x] | `knowledge/integrations/redis/connection.md` | Управление соединениями |

## 3.4 Инфраструктура

| # | Статус | Файл | Описание |
|---|--------|------|----------|
| 3.4.1 | [x] | `knowledge/infrastructure/docker-compose.md` | Настройка Docker Compose |
| 3.4.2 | [x] | `knowledge/infrastructure/dockerfile.md` | Паттерны Dockerfile |
| 3.4.3 | [x] | `knowledge/infrastructure/nginx.md` | Настройка Nginx |
| 3.4.4 | [x] | `knowledge/infrastructure/ssl.md` | Конфигурация SSL |
| 3.4.5 | [x] | `knowledge/infrastructure/ci-cd.md` | Паттерны CI/CD |

## 3.5 Качество

| # | Статус | Файл | Описание |
|---|--------|------|----------|
| 3.5.1 | [x] | `knowledge/quality/dry-kiss-yagni.md` | Принципы DRY/KISS/YAGNI |
| 3.5.2 | [x] | `knowledge/quality/testing/pytest-setup.md` | Настройка pytest |
| 3.5.3 | [x] | `knowledge/quality/testing/fixture-patterns.md` | Паттерны фикстур |
| 3.5.4 | [x] | `knowledge/quality/testing/mocking.md` | Стратегии мокирования |
| 3.5.5 | [x] | `knowledge/quality/testing/fastapi-testing.md` | Тестирование FastAPI |
| 3.5.6 | [x] | `knowledge/quality/testing/testcontainers.md` | Использование Testcontainers |
| 3.5.7 | [x] | `knowledge/quality/logging/structured.md` | Структурированное логирование |
| 3.5.8 | [x] | `knowledge/quality/logging/correlation.md` | Корреляция логов |
| 3.5.9 | [x] | `knowledge/quality/production-requirements.md` | Требования к продакшену |

---

# ФАЗА 4-7: ШАБЛОНЫ И ДОКУМЕНТЫ

> Фазы 4-7 содержат templates/ и docs/ — проверено, существует 136+ файлов.
> См. оригинальный файл `2025-12-19-aidd-mvp-implementation-todo.md` для деталей.

**Статус**: [x] Реализовано (136 файлов в templates/, 8 файлов в docs/templates/)

---

# СВОДКА

## Общее количество файлов

| Фаза | Категория | План | Факт | Статус |
|------|-----------|------|------|--------|
| 0 | Корневые файлы | 4 | 4 | ✅ 100% |
| 1 | .claude/ (settings, commands, agents) | 10 | 17 | ✅ 170% |
| 2 | roles/ | 31 | 31 | ✅ 100% |
| 3 | knowledge/ | 43 | 43 | ✅ 100% |
| 4-7 | templates/ + docs/ | ~81 | 144+ | ✅ >100% |
| **ИТОГО** | | **~169** | **239+** | **✅ 100%** |

---

## Что осталось сделать

**Все файлы реализованы! 169 из 169 — 100% завершено** ✅

*Последний файл `knowledge/quality/production-requirements.md` создан 2025-12-20*

---

## Критический путь (Минимальный набор для работы)

1. `CLAUDE.md` — без него AI не поймёт контекст ✅
2. `conventions.md` — соглашения о коде ✅
3. `.claude/commands/idea.md` — первая команда пайплайна ✅
4. `docs/templates/prd-template.md` — шаблон для генерации PRD ✅

**Критический путь полностью реализован!**

---

## Изменения относительно оригинального файла

| Раздел | Что изменено |
|--------|--------------|
| **Новая секция** | Добавлен раздел "Ограничения Claude Code" |
| **1.1.1 settings.json** | Исправлен формат на правильный Claude Code API |
| **1.2 Команды** | Исправлен формат на YAML frontmatter |
| **1.3 Агенты** | Переименовано в "Subagents", создано 7 ролевых агентов |
| **Убрано** | Концепция "команды вызывают агентов" |
| **Убрано** | "Качественные ворота" как встроенная функция |
| **2025-12-20** | Добавлены отметки [x] для всех реализованных пунктов |
