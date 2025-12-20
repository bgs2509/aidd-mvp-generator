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

Команда `/generate` создаёт код на основе утверждённого плана:
- Инфраструктуру (Docker, CI/CD)
- Data Services
- Business Services
- Тесты

---

## Агент

**Реализатор** (`.claude/agents/implementer.md`)

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

---

## Выходные артефакты

| Артефакт | Путь |
|----------|------|
| Сервисы | `services/{name}_api/`, `services/{name}_data/` |
| Инфраструктура | `docker-compose.yml`, `Makefile` |
| CI/CD | `.github/workflows/` |
| Тесты | `services/*/tests/` |

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
