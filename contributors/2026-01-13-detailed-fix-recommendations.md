# Детальные рекомендации по исправлению расхождений

**Дата**: 2026-01-13
**Автор**: AI Agent
**Тип**: Документация / План исправлений

---

## 1. Разница между `current_feature` и `active_pipelines[FID]`

### Исторический контекст

#### v1 (старый формат, DEPRECATED)

```json
{
  "version": "1.0",
  "current_feature": {
    "id": "F001",
    "name": "table-booking",
    "stage": "IMPLEMENT",
    "artifacts": {
      "prd": "prd/2024-12-23_F001_table-booking-prd.md"
    }
  },
  "gates": {
    "PRD_READY": {"passed": true},
    "RESEARCH_DONE": {"passed": true},
    "PLAN_APPROVED": {"passed": true}
  }
}
```

**Проблемы v1**:
- ❌ Только одна активная фича одновременно
- ❌ Ворота всех фич смешаны в одном объекте `gates`
- ❌ Невозможна параллельная разработка нескольких фич
- ❌ Конфликты при одновременной работе нескольких AI-агентов
- ❌ Невозможно отследить прогресс каждой фичи отдельно

#### v2 (новый формат, текущий)

```json
{
  "version": "2.0",
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Бронирование столиков",
      "stage": "IMPLEMENT",
      "created": "2024-12-23",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": true, "passed_at": "2024-12-23T11:00:00Z"},
        "PLAN_APPROVED": {"passed": true, "passed_at": "2024-12-23T12:00:00Z"}
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md"
      }
    },
    "F042": {
      "branch": "feature/F042-oauth",
      "name": "oauth-auth",
      "stage": "RESEARCH",
      "gates": {...},
      "artifacts": {...}
    }
  },
  "global_gates": {
    "BOOTSTRAP_READY": {"passed": true}
  }
}
```

**Преимущества v2**:
- ✅ Поддержка параллельной разработки нескольких фич
- ✅ Изоляция ворот для каждой фичи (`active_pipelines[FID].gates`)
- ✅ Определение контекста по git ветке
- ✅ Нет конфликтов между фичами
- ✅ Каждая фича имеет свою git ветку

### Почему так получилось?

1. **Изначально был v1** с простой структурой для одной фичи
2. **Потребовалась параллельная разработка** - несколько фич одновременно
3. **Была создана v2** с поддержкой `active_pipelines`
4. **Автомиграция** автоматически переносит v1 → v2 при первом запуске
5. **Некоторые команды не были обновлены** - остались примеры с `current_feature`

### Можно ли менять?

**ДА, ОБЯЗАТЕЛЬНО нужно менять**, потому что:

1. **`current_feature` помечен как DEPRECATED** в v2 (см. `knowledge/pipeline/state-v2.md` строка 303)
2. **Автомиграция** автоматически переносит `current_feature` → `active_pipelines[FID]` при первом запуске команды
3. **Примеры кода в командах должны соответствовать реальному формату**, который используется в runtime
4. **Использование `current_feature` в примерах вводит AI-агента в заблуждение** - он может попытаться использовать deprecated формат

### Что именно менять?

#### Неправильно (текущее состояние в некоторых командах):

```python
# ❌ Устаревший формат v1
fid = state["current_feature"]["id"]
slug = state["current_feature"]["name"]
artifacts = state["current_feature"]["artifacts"]
gates = state["gates"]  # Общие ворота для всех фич
```

#### Правильно (как должно быть):

```python
# ✅ Формат v2
fid, pipeline = get_current_feature_context(state)
if not fid:
    print("❌ Не удалось определить контекст фичи")
    return None

slug = pipeline["name"]
artifacts = pipeline["artifacts"]
gates = pipeline["gates"]  # Ворота конкретной фичи
```

**Функция `get_current_feature_context()`**:
- Определяет FID по текущей git ветке
- Возвращает `(fid, pipeline)` или `None`
- Используется во всех командах, которые уже обновлены (aidd-idea.md, aidd-generate.md, aidd-deploy.md)

---

## 2. Конкретные исправления

### Исправление 1: Замена `current_feature` на `active_pipelines[FID]`

#### Файлы для исправления:

1. **`aidd-research.md`** (строки 135-164)
2. **`aidd-plan.md`** (строки 145-175)
3. **`aidd-feature-plan.md`** (строки 151-181)
4. **`aidd-review.md`** (строки 130-161)
5. **`aidd-test.md`** (строки 129-161)
6. **`aidd-validate.md`** (строки 141-174)

#### Действие для каждого файла:

**Найти раздел "Именование артефакта" или "Обновление .pipeline-state.json"** и заменить:

**Было**:
```python
# Получить данные из state
fid = state["current_feature"]["id"]      # F001
slug = state["current_feature"]["name"]    # table-booking
date = datetime.now().strftime("%Y-%m-%d") # 2024-12-23

# Сформировать имя файла
filename = f"{date}_{fid}_{slug}-research.md"
```

**Стало**:
```python
# Получить данные из state (v2)
fid, pipeline = get_current_feature_context(state)
if not fid:
    print("❌ Не удалось определить контекст фичи")
    return None

slug = pipeline["name"]  # table-booking
date = datetime.now().strftime("%Y-%m-%d")  # 2024-12-23

# Сформировать имя файла
filename = f"{date}_{fid}_{slug}-research.md"
```

**Также заменить примеры JSON**:

**Было**:
```json
{
  "current_feature": {
    "id": "F001",
    "name": "table-booking",
    "stage": "RESEARCH",
    "artifacts": {
      "prd": "prd/2024-12-23_F001_table-booking-prd.md",
      "research": "research/2024-12-23_F001_table-booking-research.md"
    }
  }
}
```

**Стало**:
```json
{
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Бронирование столиков",
      "stage": "RESEARCH",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md"
      }
    }
  }
}
```

---

### Исправление 2: Унификация пути к шаблону Completion Report

#### Проблема:

В `aidd-deploy.md` есть два разных пути к одному шаблону:

- **Строка 236**: `.aidd/templates/documents/completion-report-template.md` ✅ Правильно
- **Строка 392**: `templates/documents/completion-report-template.md` ❌ Неправильно

#### Действие:

**Заменить строку 392** в `aidd-deploy.md`:

```markdown
# Было:
Использовать шаблон: `templates/documents/completion-report-template.md`

# Стало:
Использовать шаблон: `.aidd/templates/documents/completion-report-template.md`
```

**Обоснование**: Фреймворк находится в `.aidd/` директории, шаблоны находятся в `.aidd/templates/`. Путь должен быть относительно корня целевого проекта.

---

### Исправление 3: Синхронизация критериев DEPLOYED

#### Расхождение:

**workflow.md** (строка 445):
```
- [ ] Docker-контейнеры собраны
```

**aidd-deploy.md** (строка 316):
```
| Контейнеры | Docker-контейнеры запущены |
```

#### Анализ:

Оба критерия важны, но описывают разные этапы:
1. **"Собраны"** - означает успешную сборку образов (`docker-compose build` или `make build`)
2. **"Запущены"** - означает успешный запуск контейнеров (`docker-compose up` или `make up`)

В процессе деплоя сначала нужно собрать, потом запустить. Оба шага обязательны.

#### Действие:

**1. Обновить workflow.md строку 445**:

```markdown
# Было:
- [ ] Docker-контейнеры собраны

# Стало:
- [ ] Docker-контейнеры собраны и запущены
```

**2. Обновить aidd-deploy.md строку 316**:

```markdown
# Было:
| Контейнеры | Docker-контейнеры запущены |

# Стало:
| Контейнеры | Docker-контейнеры собраны и запущены |
```

**3. Добавить критерий "Логи" в workflow.md** (после строки 448):

```markdown
- [ ] Базовые сценарии работают
- [ ] Нет ошибок в логах контейнеров
- [ ] **Completion Report создан**
```

**Обоснование**: Критерий "Логи" есть в команде и является важной проверкой работоспособности. Его нужно добавить в workflow.md для согласованности.

---

### Исправление 4: Добавление проверки сохранения отчёта в RESEARCH_DONE

#### Расхождение:

**workflow.md** (строка 284):
```
- [ ] Отчёт исследования сохранён в `ai-docs/docs/research/{name}-research.md`
```

**aidd-research.md** (строки 172-178): Нет явной проверки сохранения файла.

#### Действие:

**Добавить в aidd-research.md** в раздел "Качественные ворота" (после строки 178):

```markdown
| Критерий | Описание |
|----------|----------|
| Анализ кода | Существующий код изучен (для FEATURE) |
| Паттерны | Архитектурные паттерны выявлены |
| Ограничения | Технические ограничения определены |
| Рекомендации | Сформулированы рекомендации |
| Файл сохранён | Отчёт сохранён в `ai-docs/docs/research/{YYYY-MM-DD}_{FID}_{slug}-research.md` |
```

**Обоснование**: workflow.md явно требует проверку сохранения файла, команда должна это отражать.

---

### Исправление 5: Обновление workflow.md с критериями Log-Driven Design

#### Расхождение:

**aidd-review.md** (строки 176-192) и **aidd-validate.md** (строки 197-210) содержат проверки Log-Driven Design, которых нет в workflow.md.

#### Действие:

**1. Добавить в workflow.md** в раздел "Этап 5: Ревью" (после строки 371):

```markdown
- [ ] DRY/KISS/YAGNI соблюдены
- [ ] Log-Driven Design соблюдён (см. knowledge/quality/logging/log-driven-design.md)
```

**2. Добавить в workflow.md** в раздел "Этап 7: Валидация" (после строки 421):

```markdown
- [ ] RTM (Requirements Traceability Matrix) актуальна
- [ ] Проект готов к деплою
- [ ] Log-Driven Design проверен (middleware, tracing, JSON logs, нет секретов в логах)
```

**Обоснование**: Log-Driven Design является важным критерием качества кода и должен быть отражён в workflow.md.

---

### Исправление 6: Уточнение путей артефактов

#### Расхождение:

**workflow.md** (строка 456):
```
Completion Report | `reports/{date}_{FID}_{slug}-completion.md`
```

**aidd-deploy.md** (строки 237, 390, 466):
```
ai-docs/docs/reports/{YYYY-MM-DD}_{FID}_{slug}-completion.md
```

#### Анализ:

Все остальные артефакты в workflow.md указаны с полным путём `ai-docs/docs/...`:
- PRD: `ai-docs/docs/prd/{name}-prd.md` (строка 264)
- Research: `ai-docs/docs/research/{name}-research.md` (строка 293)
- Plan: `ai-docs/docs/architecture/{name}-plan.md` (строка 321)

Completion Report должен быть согласован с остальными.

#### Действие:

**Обновить workflow.md строку 456**:

```markdown
# Было:
| **Completion Report** | `reports/{date}_{FID}_{slug}-completion.md` | Итоговый отчёт |

# Стало:
| **Completion Report** | `ai-docs/docs/reports/{date}_{FID}_{slug}-completion.md` | Итоговый отчёт |
```

**Обоснование**: Для согласованности со всеми остальными артефактами.

---

## Итоговый чеклист исправлений

### Приоритет 1 (Критично)

- [ ] `aidd-research.md`: заменить `current_feature` на `get_current_feature_context()`
- [ ] `aidd-plan.md`: заменить `current_feature` на `get_current_feature_context()`
- [ ] `aidd-feature-plan.md`: заменить `current_feature` на `get_current_feature_context()`
- [ ] `aidd-review.md`: заменить `current_feature` на `get_current_feature_context()`
- [ ] `aidd-test.md`: заменить `current_feature` на `get_current_feature_context()`
- [ ] `aidd-validate.md`: заменить `current_feature` на `get_current_feature_context()`
- [ ] `aidd-deploy.md` строка 392: добавить `.aidd/` к пути шаблона

### Приоритет 2 (Важно)

- [ ] `workflow.md` строка 445: изменить на "собраны и запущены"
- [ ] `aidd-deploy.md` строка 316: изменить на "собраны и запущены"
- [ ] `workflow.md`: добавить критерий "Нет ошибок в логах" после строки 448
- [ ] `aidd-research.md`: добавить критерий "Файл сохранён" в таблицу RESEARCH_DONE
- [ ] `workflow.md` этап 5: добавить критерий Log-Driven Design
- [ ] `workflow.md` этап 7: добавить критерий Log-Driven Design

### Приоритет 3 (Желательно)

- [ ] `workflow.md` строка 456: добавить префикс `ai-docs/docs/` к Completion Report

---

## Связанные документы

- `knowledge/pipeline/state-v2.md` - Спецификация Pipeline State v2
- `knowledge/pipeline/automigration.md` - Автомиграция v1 → v2
- `contributors/2026-01-13-aidd-issue-completion-report-gap.md` - Исходный issue

