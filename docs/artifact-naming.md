# Система именования артефактов

> **Назначение**: Спецификация системы именования и организации артефактов в долгосрочных проектах.
> **Проблема**: В проектах с сотнями фич папка `ai-docs/docs/` превращается в хаос без понятной системы.

---

## TL;DR

```
Формат имени файла:
{YYYY-MM-DD}_{FID}_{slug}-{type}.md

Пример:
2024-01-15_F001_user-auth-prd.md
```

| Компонент | Описание | Пример |
|-----------|----------|--------|
| `YYYY-MM-DD` | Дата создания | `2024-01-15` |
| `FID` | Feature ID (уникальный) | `F001`, `F042` |
| `slug` | Краткое имя (kebab-case) | `user-auth` |
| `type` | Тип артефакта | `prd`, `plan`, `research` |

---

## 1. Проблема

### До: Хаос в долгосрочном проекте

```
ai-docs/docs/
├── prd/
│   ├── booking-prd.md          # Какая фича? Когда создан?
│   ├── notifications-prd.md    # Связана с booking?
│   ├── auth-prd.md             # Версия 1 или итерация?
│   ├── auth-v2-prd.md          # Связь с auth-prd.md?
│   ├── payments-prd.md         #
│   └── ... (100+ файлов)       # Полный хаос
├── architecture/
│   ├── booking-plan.md         # Тот же booking что в prd/?
│   └── ...
```

**Проблемы:**
- Нет связи между артефактами одной фичи
- Нет хронологии (что было раньше?)
- Нет версионирования (итерации над фичей)
- Поиск требует открытия каждого файла

### После: Структурированная система

```
ai-docs/docs/
├── FEATURES.md                              # Реестр всех фич
├── prd/
│   ├── 2024-01-15_F001_user-auth-prd.md
│   ├── 2024-02-20_F002_table-booking-prd.md
│   ├── 2024-03-10_F003_email-notify-prd.md
│   └── 2024-06-01_F001_user-auth-v2-prd.md  # Итерация F001!
├── architecture/
│   ├── 2024-01-16_F001_user-auth-plan.md
│   ├── 2024-02-21_F002_table-booking-plan.md
│   └── ...
```

**Преимущества:**
- Сортировка по дате = хронология
- FID связывает все артефакты фичи
- `grep F002` находит всё про booking
- FEATURES.md = оглавление проекта

---

## 2. Формат именования файлов

### 2.1 Структура имени

```
{YYYY-MM-DD}_{FID}_{slug}-{type}.md
     │        │      │      │
     │        │      │      └── Тип артефакта
     │        │      └── Краткое имя (≤30 символов, kebab-case)
     │        └── Feature ID (F001, F002, ...)
     └── Дата создания (ISO 8601)
```

### 2.2 Компоненты

| Компонент | Формат | Правила | Примеры |
|-----------|--------|---------|---------|
| **Дата** | `YYYY-MM-DD` | ISO 8601, дата создания | `2024-01-15` |
| **FID** | `F{NNN}` | Уникальный, автоинкремент | `F001`, `F042`, `F999` |
| **Slug** | `kebab-case` | ≤30 символов, только `a-z`, `0-9`, `-` | `user-auth`, `table-booking` |
| **Type** | `enum` | См. таблицу типов | `prd`, `plan`, `research` |

### 2.3 Типы артефактов

| Type | Полное имя | Папка | Этап |
|------|------------|-------|------|
| `prd` | Product Requirements Document | `prd/` | 1 |
| `research` | Research Report | `research/` | 2 |
| `plan` | Architecture/Feature Plan | `architecture/` или `plans/` | 3 |
| `review` | Review Report | `reports/` | 5 |
| `qa` | QA Report | `reports/` | 6 |
| `validation` | Validation Report | `reports/` | 7 |

### 2.4 Версионирование (итерации)

Для итераций над фичей добавляется суффикс `-v{N}`:

```
# Первоначальная фича
2024-01-15_F001_user-auth-prd.md

# Итерация (MFA)
2024-06-01_F001_user-auth-v2-prd.md

# Следующая итерация
2024-09-15_F001_user-auth-v3-prd.md
```

**Правила версионирования:**
- `v2`, `v3`, ... — крупные изменения/дополнения к существующей фиче
- Новая версия = новый файл (не перезапись!)
- FID остаётся тем же (это та же фича)
- Дата меняется на дату создания версии

---

## 3. Feature ID (FID)

### 3.1 Формат

```
F{NNN}

Где NNN — порядковый номер с ведущими нулями (001-999)
```

**Примеры:** `F001`, `F042`, `F123`, `F999`

### 3.2 Правила присвоения

1. **Автоинкремент**: Каждая новая фича получает следующий номер
2. **Уникальность**: FID никогда не переиспользуется
3. **Неизменяемость**: FID присваивается один раз и не меняется
4. **Scope**: FID уникален в рамках одного проекта

### 3.3 Хранение

FID хранится в `.pipeline-state.json`:

```json
{
  "features_registry": {
    "F001": {
      "name": "user-auth",
      "title": "Аутентификация пользователей",
      "created": "2024-01-15",
      "status": "DEPLOYED",
      "services": ["auth_api", "auth_data"]
    },
    "F002": {
      "name": "table-booking",
      "title": "Бронирование столиков",
      "created": "2024-02-20",
      "status": "DEPLOYED",
      "services": ["booking_api", "booking_data"]
    }
  },
  "next_feature_id": 3
}
```

### 3.4 Генерация FID

```python
def generate_feature_id(state: dict) -> str:
    """Генерирует следующий FID."""
    next_id = state.get("next_feature_id", 1)
    fid = f"F{next_id:03d}"
    state["next_feature_id"] = next_id + 1
    return fid
```

---

## 4. Реестр фич (FEATURES.md)

### 4.1 Расположение

```
ai-docs/docs/FEATURES.md
```

### 4.2 Формат

```markdown
# Реестр фич проекта

> Автоматически обновляется при создании/завершении фич.
> Последнее обновление: 2024-12-23

---

## Статистика

| Метрика | Значение |
|---------|----------|
| Всего фич | 42 |
| Deployed | 38 |
| In Progress | 3 |
| Archived | 1 |

---

## Активные фичи

| FID | Название | Статус | Дата | Сервисы | Артефакты |
|-----|----------|--------|------|---------|-----------|
| F042 | Email-уведомления | IN_PROGRESS | 2024-12-20 | notify_worker | [PRD](prd/2024-12-20_F042_email-notify-prd.md) |
| F041 | Платёжная система | QA_PASSED | 2024-12-15 | payments_api | [PRD](...), [Plan](...) |

---

## Завершённые фичи

| FID | Название | Deployed | Сервисы | Артефакты |
|-----|----------|----------|---------|-----------|
| F001 | Аутентификация | 2024-01-20 | auth_api, auth_data | [PRD](...), [Plan](...), [v2](...) |
| F002 | Бронирование столиков | 2024-02-25 | booking_api, booking_data | [PRD](...), [Plan](...) |
| ... | ... | ... | ... | ... |

---

## Архивные фичи

| FID | Название | Причина архивации | Дата |
|-----|----------|-------------------|------|
| F010 | Интеграция с X | Отменена заказчиком | 2024-05-01 |
```

### 4.3 Автоматическое обновление

FEATURES.md обновляется автоматически командами:
- `/aidd-idea` — добавляет новую фичу (IN_PROGRESS)
- `/aidd-deploy` — обновляет статус на DEPLOYED
- При ручном архивировании — переносит в "Архивные"

---

## 5. YAML Frontmatter

### 5.1 Назначение

Каждый артефакт содержит YAML frontmatter с метаданными для:
- Машиночитаемости (AI-агенты)
- Связывания артефактов
- Быстрого поиска

### 5.2 Обязательные поля

```yaml
---
feature_id: F002
feature_name: table-booking
title: Бронирование столиков в ресторанах
created: 2024-02-20
author: AI (Analyst)
type: prd
status: PRD_READY
version: 1
---
```

### 5.3 Опциональные поля

```yaml
---
# ... обязательные поля ...

# Связи
related_features:
  - F001  # Зависит от аутентификации
  - F003  # Email уведомления
previous_version: null  # или путь к предыдущей версии
supersedes: null        # какой документ заменяет

# Контекст
services:
  - booking_api
  - booking_data
requirements_count: 12
mode: CREATE  # или FEATURE

# История
updated: 2024-02-21
approved_by: user
approved_at: 2024-02-21
---
```

### 5.4 Примеры по типам артефактов

**PRD:**
```yaml
---
feature_id: F002
feature_name: table-booking
title: Система бронирования столиков
created: 2024-02-20
author: AI (Analyst)
type: prd
status: PRD_READY
version: 1
mode: CREATE
requirements_count: 15
---
```

**Architecture Plan:**
```yaml
---
feature_id: F002
feature_name: table-booking
title: Архитектура системы бронирования
created: 2024-02-21
author: AI (Architect)
type: plan
status: PLAN_APPROVED
version: 1
prd_ref: prd/2024-02-20_F002_table-booking-prd.md
research_ref: research/2024-02-20_F002_table-booking-research.md
services:
  - booking_api
  - booking_data
approved_by: user
approved_at: 2024-02-21
---
```

**Feature Plan (режим FEATURE):**
```yaml
---
feature_id: F042
feature_name: email-notify
title: Добавление email-уведомлений
created: 2024-12-20
author: AI (Architect)
type: feature-plan
status: PLAN_APPROVED
version: 1
mode: FEATURE
prd_ref: prd/2024-12-20_F042_email-notify-prd.md
affected_services:
  - booking_api      # Модификация
  - notify_worker    # Создание
related_features:
  - F002  # Бронирование
---
```

---

## 6. Структура папок

### 6.1 Полная структура

```
ai-docs/docs/
│
├── FEATURES.md                    # Главный реестр фич
│
├── prd/                           # PRD документы
│   ├── 2024-01-15_F001_user-auth-prd.md
│   ├── 2024-02-20_F002_table-booking-prd.md
│   ├── 2024-06-01_F001_user-auth-v2-prd.md
│   └── ...
│
├── research/                      # Research reports
│   ├── 2024-01-15_F001_user-auth-research.md
│   ├── 2024-02-20_F002_table-booking-research.md
│   └── ...
│
├── architecture/                  # Архитектурные планы (CREATE mode)
│   ├── 2024-01-16_F001_user-auth-plan.md
│   ├── 2024-02-21_F002_table-booking-plan.md
│   └── ...
│
├── plans/                         # Feature планы (FEATURE mode)
│   ├── 2024-06-02_F001_user-auth-v2-plan.md
│   ├── 2024-12-20_F042_email-notify-plan.md
│   └── ...
│
├── reports/                       # Отчёты этапов
│   ├── review/
│   │   ├── 2024-01-18_F001_user-auth-review.md
│   │   └── ...
│   ├── qa/
│   │   ├── 2024-01-19_F001_user-auth-qa.md
│   │   └── ...
│   └── validation/
│       ├── 2024-01-20_F001_user-auth-validation.md
│       └── ...
│
└── archive/                       # Устаревшие/отменённые фичи
    └── F010_integration-x/
        ├── 2024-04-01_F010_integration-x-prd.md
        └── ARCHIVED.md            # Причина архивации
```

### 6.2 Правила организации

| Правило | Описание |
|---------|----------|
| По типам | Артефакты в папках по типу (prd/, architecture/, ...) |
| Хронология | Файлы сортируются по дате (ISO формат) |
| Связь через FID | Все артефакты фичи имеют одинаковый FID |
| Архивация | Отменённые фичи перемещаются в archive/ |

---

## 7. Расширение .pipeline-state.json

### 7.1 Новая структура

```json
{
  "project_name": "booking-service",
  "mode": "CREATE",
  "current_stage": 4,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-12-23T15:30:00Z",

  "current_feature": {
    "id": "F042",
    "name": "email-notify",
    "title": "Email-уведомления",
    "created": "2024-12-20",
    "stage": "QA",
    "artifacts": {
      "prd": "prd/2024-12-20_F042_email-notify-prd.md",
      "research": "research/2024-12-20_F042_email-notify-research.md",
      "plan": "plans/2024-12-20_F042_email-notify-plan.md"
    }
  },

  "features_registry": {
    "F001": {
      "name": "user-auth",
      "title": "Аутентификация пользователей",
      "created": "2024-01-15",
      "status": "DEPLOYED",
      "deployed_at": "2024-01-20",
      "services": ["auth_api", "auth_data"],
      "versions": [
        {"version": 1, "date": "2024-01-15"},
        {"version": 2, "date": "2024-06-01", "note": "MFA"}
      ]
    },
    "F002": {
      "name": "table-booking",
      "title": "Бронирование столиков",
      "created": "2024-02-20",
      "status": "DEPLOYED",
      "deployed_at": "2024-02-25",
      "services": ["booking_api", "booking_data"]
    },
    "F042": {
      "name": "email-notify",
      "title": "Email-уведомления",
      "created": "2024-12-20",
      "status": "IN_PROGRESS",
      "services": ["notify_worker"]
    }
  },

  "next_feature_id": 43,

  "gates": {
    "BOOTSTRAP_READY": {"passed": true, "passed_at": "2024-01-15T10:00:00Z"},
    "PRD_READY": {"passed": true, "passed_at": "2024-12-20T10:05:00Z"},
    "RESEARCH_DONE": {"passed": true, "passed_at": "2024-12-20T10:10:00Z"},
    "PLAN_APPROVED": {"passed": true, "passed_at": "2024-12-20T10:20:00Z"},
    "IMPLEMENT_OK": {"passed": true, "passed_at": "2024-12-21T14:00:00Z"},
    "REVIEW_OK": {"passed": true, "passed_at": "2024-12-22T10:00:00Z"},
    "QA_PASSED": {"passed": false}
  }
}
```

### 7.2 Статусы фич

| Статус | Описание | После этапа |
|--------|----------|-------------|
| `IN_PROGRESS` | Фича в разработке | 1 (PRD_READY) |
| `PLAN_APPROVED` | План утверждён | 3 |
| `IMPLEMENTED` | Код написан | 4 |
| `REVIEW_OK` | Код проверен | 5 |
| `QA_PASSED` | Тесты пройдены | 6 |
| `VALIDATED` | Все ворота пройдены | 7 |
| `DEPLOYED` | В продакшене | 8 |
| `ARCHIVED` | Отменена/устарела | — |

---

## 8. Поиск артефактов

### 8.1 По FID

```bash
# Найти все артефакты фичи F002
grep -r "F002" ai-docs/docs/
find ai-docs/docs -name "*F002*"

# Или через filename
ls ai-docs/docs/**/\*F002\*
```

### 8.2 По дате

```bash
# Артефакты за декабрь 2024
ls ai-docs/docs/*/2024-12-*

# Последние 10 артефактов
ls -t ai-docs/docs/**/*.md | head -10
```

### 8.3 По типу

```bash
# Все PRD
ls ai-docs/docs/prd/

# Все планы
ls ai-docs/docs/architecture/ ai-docs/docs/plans/
```

### 8.4 Через frontmatter (для AI)

```python
def find_artifacts_by_feature(docs_dir: Path, fid: str) -> list[Path]:
    """Найти все артефакты фичи через frontmatter."""
    import yaml

    artifacts = []
    for md_file in docs_dir.rglob("*.md"):
        content = md_file.read_text()
        if content.startswith("---"):
            # Извлечь frontmatter
            _, fm, _ = content.split("---", 2)
            meta = yaml.safe_load(fm)
            if meta.get("feature_id") == fid:
                artifacts.append(md_file)
    return artifacts
```

---

## 9. Миграция существующих артефактов

### 9.1 Стратегия

1. **Анализ**: Прочитать существующие файлы
2. **Группировка**: Сгруппировать по фичам (эвристика)
3. **Присвоение FID**: Назначить уникальные ID
4. **Переименование**: Добавить дату и FID
5. **Frontmatter**: Добавить YAML метаданные
6. **FEATURES.md**: Сгенерировать реестр

### 9.2 Скрипт миграции

См. файл `scripts/migrate_artifacts.py` (создаётся отдельно).

### 9.3 Пример миграции

**До:**
```
ai-docs/docs/prd/booking-prd.md
```

**После:**
```
ai-docs/docs/prd/2024-02-20_F002_table-booking-prd.md
```

**Добавленный frontmatter:**
```yaml
---
feature_id: F002
feature_name: table-booking
title: Система бронирования столиков
created: 2024-02-20  # Из git log
author: AI (Analyst)
type: prd
status: DEPLOYED
version: 1
migrated_from: booking-prd.md
migrated_at: 2024-12-23
---
```

---

## 10. Интеграция с командами

### 10.1 /aidd-idea

```python
# При создании PRD:
1. Сгенерировать FID (или взять existing для FEATURE mode)
2. Создать slug из названия
3. Сформировать имя файла: {date}_{FID}_{slug}-prd.md
4. Добавить frontmatter
5. Обновить .pipeline-state.json (features_registry, current_feature)
6. Обновить FEATURES.md
```

### 10.2 /aidd-plan и /aidd-feature-plan

```python
# При создании плана:
1. Взять FID из current_feature
2. Сформировать имя: {date}_{FID}_{slug}-plan.md
3. Добавить frontmatter с ссылками на PRD и research
4. Сохранить путь в current_feature.artifacts.plan
```

### 10.3 /aidd-deploy

```python
# При успешном деплое:
1. Обновить статус фичи в features_registry → DEPLOYED
2. Добавить deployed_at
3. Обновить FEATURES.md (перенести в "Завершённые")
4. Очистить current_feature
```

---

## 11. Качественные ворота

### Checklist для нового артефакта

- [ ] Имя файла соответствует формату `{date}_{FID}_{slug}-{type}.md`
- [ ] YAML frontmatter содержит все обязательные поля
- [ ] FID уникален и зарегистрирован в .pipeline-state.json
- [ ] FEATURES.md обновлён
- [ ] Артефакт в правильной папке

---

## См. также

- [target-project-structure.md](target-project-structure.md) — Структура целевого проекта
- [workflow.md](../workflow.md) — 9-этапный пайплайн
- [NAVIGATION.md](NAVIGATION.md) — Навигационная матрица

---

**Версия**: 1.0
**Создан**: 2024-12-23
