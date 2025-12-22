# Каталог артефактов AIDD-MVP

> **Назначение**: Полный каталог всех артефактов, создаваемых в процессе генерации MVP.
> Для каждого артефакта указаны шаблон, путь и критерии готовности.

---

## Обзор

```
ГЕНЕРАТОР (шаблоны)              →    ЦЕЛЕВОЙ ПРОЕКТ (артефакты)
templates/documents/prd-template.md   →    ai-docs/docs/prd/{name}-prd.md
templates/documents/research-report-template.md →    ai-docs/docs/research/{name}-research.md
templates/documents/architecture-*.md →    ai-docs/docs/architecture/{name}-plan.md
templates/services/*             →    services/{name}_{type}/
```

---

## Этап 1: Идея (PRD)

### PRD документ

| Параметр | Значение |
|----------|----------|
| **Команда** | `/idea` |
| **Агент** | Аналитик |
| **Шаблон (генератор)** | `templates/documents/prd-template.md` |
| **Путь (целевой проект)** | `ai-docs/docs/prd/{name}-prd.md` |
| **Ворота** | `PRD_READY` |

**Критерии готовности**:
- [ ] Все секции заполнены
- [ ] Требования имеют ID (FR-*, NF-*, UI-*)
- [ ] Критерии приёмки определены
- [ ] Нет блокирующих Open вопросов

**Пример имени файла**: `booking-restaurant-prd.md`

---

## Этап 2: Исследование

### Research Report

| Параметр | Значение |
|----------|----------|
| **Команда** | `/research` |
| **Агент** | Исследователь |
| **Шаблон (генератор)** | `templates/documents/research-report-template.md` |
| **Путь (целевой проект)** | `ai-docs/docs/research/{name}-research.md` |
| **Ворота** | `RESEARCH_DONE` |

**Критерии готовности**:
- [ ] Код и/или требования проанализированы
- [ ] Паттерны и ограничения описаны в отчёте
- [ ] Рекомендации по интеграции сформулированы
- [ ] `.pipeline-state.json` обновлён (`RESEARCH_DONE`)

---

## Этап 3: Архитектура

### План архитектуры (CREATE)

| Параметр | Значение |
|----------|----------|
| **Команда** | `/plan` |
| **Агент** | Архитектор |
| **Шаблон (генератор)** | `templates/documents/architecture-template.md` |
| **Путь (целевой проект)** | `ai-docs/docs/architecture/{name}-plan.md` |
| **Ворота** | `PLAN_APPROVED` |

### План фичи (FEATURE)

| Параметр | Значение |
|----------|----------|
| **Команда** | `/feature-plan` |
| **Агент** | Архитектор |
| **Шаблон (генератор)** | `templates/documents/feature-plan-template.md` |
| **Путь (целевой проект)** | `ai-docs/docs/plans/{feature}-plan.md` |
| **Ворота** | `PLAN_APPROVED` |

**Критерии готовности**:
- [ ] Компоненты системы определены
- [ ] API контракты описаны
- [ ] NFR учтены
- [ ] **План утверждён пользователем**

**Пример имени файла**: `booking-restaurant-plan.md`, `notifications-plan.md`

---

## Этап 4: Реализация

### Инфраструктура

| Артефакт | Шаблон (генератор) | Путь (целевой проект) |
|----------|--------------------|-----------------------|
| Docker Compose | `templates/infrastructure/docker-compose.yml` | `docker-compose.yml` |
| Docker Dev | `templates/infrastructure/docker-compose.dev.yml` | `docker-compose.dev.yml` |
| Makefile | `templates/infrastructure/Makefile` | `Makefile` |
| .env | `templates/infrastructure/.env.example` | `.env.example` |
| CI/CD | `templates/infrastructure/github-actions/` | `.github/workflows/` |

### Сервисы

| Тип сервиса | Шаблон (генератор) | Путь (целевой проект) |
|-------------|--------------------|-----------------------|
| Business API | `templates/services/fastapi_business_api/` | `services/{name}_api/` |
| Telegram Bot | `templates/services/aiogram_bot/` | `services/{name}_bot/` |
| Background Worker | `templates/services/asyncio_worker/` | `services/{name}_worker/` |
| Data API (PostgreSQL) | `templates/services/postgres_data_api/` | `services/{name}_data/` |
| Data API (MongoDB) | `templates/services/mongo_data_api/` | `services/{name}_data/` |

### Тесты

| Артефакт | Путь (целевой проект) |
|----------|-----------------------|
| Unit тесты | `services/{name}/tests/unit/` |
| Integration тесты | `services/{name}/tests/integration/` |
| conftest.py | `services/{name}/tests/conftest.py` |

**Критерии готовности (IMPLEMENT_OK)**:
- [ ] Код написан согласно плану
- [ ] Структура соответствует DDD/Hexagonal
- [ ] Type hints присутствуют
- [ ] Все unit-тесты проходят

---

## Этап 5: Ревью

### Отчёт ревью

| Параметр | Значение |
|----------|----------|
| **Команда** | `/review` |
| **Агент** | Ревьюер |
| **Путь (целевой проект)** | `ai-docs/docs/reports/review-report.md` |
| **Ворота** | `REVIEW_OK` |

**Критерии готовности**:
- [ ] Код соответствует conventions.md
- [ ] Архитектура соответствует плану
- [ ] Нет Blocker/Critical замечаний
- [ ] DRY/KISS/YAGNI соблюдены

---

## Этап 6: QA

### Отчёт QA

| Параметр | Значение |
|----------|----------|
| **Команда** | `/test` |
| **Агент** | QA |
| **Путь (целевой проект)** | `ai-docs/docs/reports/qa-report.md` |
| **Ворота** | `QA_PASSED` |

**Критерии готовности**:
- [ ] Все тесты проходят
- [ ] Coverage ≥75%
- [ ] Нет Critical/Blocker багов
- [ ] Требования из PRD верифицированы

---

## Этап 7: Валидация

### Отчёт валидации

| Параметр | Значение |
|----------|----------|
| **Команда** | `/validate` |
| **Агент** | Валидатор |
| **Путь (целевой проект)** | `ai-docs/docs/reports/validation-report.md` |
| **Ворота** | `ALL_GATES_PASSED` |

### RTM (Requirements Traceability Matrix)

| Параметр | Значение |
|----------|----------|
| **Шаблон (генератор)** | `templates/documents/rtm-template.md` |
| **Путь (целевой проект)** | `ai-docs/docs/rtm.md` |

**Критерии готовности**:
- [ ] Все предыдущие ворота пройдены
- [ ] Все артефакты существуют
- [ ] RTM актуальна
- [ ] Проект готов к деплою

---

## Этап 8: Деплой

### Работающее приложение

| Параметр | Значение |
|----------|----------|
| **Команда** | `/deploy` |
| **Агент** | Валидатор |
| **Ворота** | `DEPLOYED` |

**Критерии готовности**:
- [ ] Docker-контейнеры собраны
- [ ] Приложение запущено
- [ ] Health-check проходит
- [ ] Базовые сценарии работают

---

## Служебные артефакты

### Pipeline State

| Параметр | Значение |
|----------|----------|
| **Шаблон (генератор)** | `templates/documents/pipeline-state-template.json` |
| **Путь (целевой проект)** | `.pipeline-state.json` |

**Назначение**: Хранит текущее состояние пайплайна, пройденные ворота, пути артефактов.

---

## Сводная таблица

| Этап | Артефакт | Путь в целевом проекте | Ворота |
|------|----------|------------------------|--------|
| 1 | PRD | `ai-docs/docs/prd/{name}-prd.md` | PRD_READY |
| 2 | Research Report | `ai-docs/docs/research/{name}-research.md` | RESEARCH_DONE |
| 3 | План | `ai-docs/docs/architecture/{name}-plan.md` | PLAN_APPROVED |
| 4 | Код | `services/`, `docker-compose.yml` | IMPLEMENT_OK |
| 5 | Ревью | `ai-docs/docs/reports/review-report.md` | REVIEW_OK |
| 6 | QA | `ai-docs/docs/reports/qa-report.md` | QA_PASSED |
| 7 | Валидация | `ai-docs/docs/reports/validation-report.md`, `rtm.md` | ALL_GATES_PASSED |
| 8 | Деплой | Работающее приложение | DEPLOYED |

---

**Версия**: 1.0
**Создан**: 2025-12-21
