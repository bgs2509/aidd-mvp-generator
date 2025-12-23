---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**), Write(**), Bash(make :*), Bash(docker :*), Bash(pytest :*)
description: Генерация кода на основе утверждённого плана
---

# Команда: /generate

> Запускает Реализатора для генерации кода.

---

## Синтаксис

```bash
/generate
```

---

## Описание

Команда `/aidd-generate` создаёт код на основе утверждённого плана:
- Инфраструктуру (Docker, CI/CD)
- Data Services
- Business Services
- Тесты

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Реализатор** (`.claude/agents/implementer.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | Режим, этап, ворота |
| 3 | `./ai-docs/docs/prd/*.md` | Обязательно | Требования |
| 4 | `./ai-docs/docs/architecture/*.md` | Для CREATE | Архитектурный план |
| 5 | `./ai-docs/docs/plans/*.md` | Для FEATURE | План фичи |
| 6 | `./services/` | Для FEATURE | Существующий код |

### Фаза 2: Предусловия

| Ворота | Проверка |
|--------|----------|
| `PLAN_APPROVED` | `.pipeline-state.json → gates.PLAN_APPROVED.passed == true` |
| `approved_by` | `.pipeline-state.json → gates.PLAN_APPROVED.approved_by != null` |

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 7 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 8 | `.aidd/workflow.md` | Процесс и ворота |
| 9 | `.aidd/conventions.md` | Соглашения о коде |
| 10 | `.aidd/.claude/commands/generate.md` | Этот файл |
| 11 | `.aidd/.claude/agents/implementer.md` | Инструкции роли |

### Фаза 4: Шаблоны

| # | Файл | Условие |
|---|------|---------|
| 12 | `.aidd/templates/services/*.md` | Шаблоны сервисов |
| 13 | `.aidd/templates/infrastructure/*.md` | Инфраструктура |

---

## Режимы

| Режим | Поведение |
|-------|-----------|
| **CREATE** | Создаёт полную структуру проекта |
| **FEATURE** | Добавляет код в существующий проект |

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `PLAN_APPROVED` | План утверждён пользователем |

### Алгоритм проверки

```
1. Проверить существование .pipeline-state.json
2. Если файл отсутствует:
   ❌ Пайплайн не инициализирован
   → Сначала выполните /idea
3. Проверить gates.PLAN_APPROVED.passed == true
4. Если ворота не пройдены:
   ❌ Ворота PLAN_APPROVED не пройдены
   → Сначала выполните /aidd-plan или /feature-plan
5. Проверить gates.PLAN_APPROVED.approved_by != null
6. Если план не утверждён пользователем:
   ⚠️ План требует явного утверждения пользователем
7. Продолжить выполнение
```

---

## Выходные артефакты (в целевом проекте)

| Артефакт | Путь |
|----------|------|
| Сервисы | `services/{name}_api/`, `services/{name}_data/` |
| Инфраструктура | `docker-compose.yml`, `Makefile` |
| CI/CD | `.github/workflows/` |
| Тесты | `services/*/tests/` |
| Состояние | `.pipeline-state.json` (обновляется) |

---

## Качественные ворота

### IMPLEMENT_OK

| Критерий | Описание |
|----------|----------|
| Код | Написан согласно плану |
| Структура | DDD/Hexagonal соблюдена |
| Типы | Type hints везде |
| Документация | Docstrings на русском |
| Тесты | Unit-тесты проходят |

---

## Порядок генерации

```
1. Инфраструктура (docker-compose, Makefile, CI/CD)
2. Data Service (модели, репозитории, API)
3. Business API (сервисы, API, HTTP клиенты)
4. Background Worker (если нужен)
5. Telegram Bot (если нужен)
6. Тесты
```

---

## Примеры использования

```bash
# После утверждения плана
/generate
```

---

## Следующий шаг

После прохождения ворот `IMPLEMENT_OK`:

```bash
/review
```
