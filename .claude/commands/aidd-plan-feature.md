---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(git :*), Bash(python3 :*)
description: Создать план реализации новой фичи в существующем проекте
---

**Примечание (Migration Mode v2.4):** Фреймворк поддерживает обе версии команд — legacy naming (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`) и new naming (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`) работают идентично.


> ⚠️ **ENFORCEMENT**: Перед завершением этой команды AI ОБЯЗАН:
> 1. Найти секцию "Чеклист ворот" в конце этого файла
> 2. Создать TodoWrite со ВСЕМИ пунктами (особенно 🔴)
> 3. Выполнить ВСЕ пункты и отметить completed
> 4. Команда завершена ТОЛЬКО когда все 🔴 пункты ✅
>
> Правила: `.aidd/CLAUDE.md` → "Выполнение команд /aidd-*"

# Команда: /feature-plan

> Запускает Архитектора для планирования фичи (режим FEATURE).
> **Pipeline State v2**: Поддержка параллельных пайплайнов.

---

## Синтаксис

```bash
/feature-plan
```

---

## Описание

Команда `/aidd-plan-feature` создаёт план реализации новой функции
в существующем проекте. Учитывает текущую архитектуру и паттерны.

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Архитектор** (`.claude/agents/planner.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | Режим, этап, ворота |
| 3 | `./ai-docs/docs/_analysis/*.md` | Обязательно | Требования фичи |
| 4 | `./ai-docs/docs/_plans/mvp/*.md` | Обязательно | Существующая архитектура |
| 5 | `./services/` | Обязательно | Существующий код |

### Фаза 2: Автомиграция и предусловия

> **Важно**: Перед выполнением команды проверить версию `.pipeline-state.json`
> и выполнить миграцию v1 → v2 если требуется (см. `knowledge/pipeline/automigration.md`).

| Ворота | Проверка (v2) |
|--------|---------------|
| `mode` | `.pipeline-state.json → mode == "FEATURE"` |
| `PRD_READY` | `active_pipelines[FID].gates.PRD_READY.passed == true` |
| `RESEARCH_DONE` | `active_pipelines[FID].gates.RESEARCH_DONE.passed == true` |

> **Примечание v2**: FID определяется по текущей git ветке.

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 6 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 7 | `.aidd/workflow.md` | Процесс и ворота |
| 8 | `.aidd/.claude/commands/feature-plan.md` | Этот файл |
| 9 | `.aidd/.claude/agents/planner.md` | Инструкции роли |

### Фаза 4: База знаний

| # | Файл | Условие |
|---|------|---------|
| 10 | `.aidd/knowledge/architecture/*.md` | По необходимости |

---

## Режимы

Только **FEATURE** — для существующих проектов.

Для нового проекта используйте `/aidd-plan`.

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `PRD_READY` | FEATURE_PRD документ существует |
| `RESEARCH_DONE` | Код проанализирован |

### Алгоритм проверки (v2)

```python
def check_feature_plan_preconditions() -> tuple[str, dict] | None:
    """
    Проверить предусловия для /feature-plan.

    v2: Определяем FID по git ветке, проверяем active_pipelines[fid].gates
    """
    # 1. Проверить и мигрировать state
    state = ensure_v2_state()  # см. knowledge/pipeline/automigration.md
    if not state:
        print("❌ Пайплайн не инициализирован → /aidd-analyze")
        return None

    # 2. Проверить режим
    if state.get("mode") != "FEATURE":
        print("⚠️  Режим CREATE — используйте /aidd-plan вместо /aidd-plan-feature")
        return None

    # 3. Определить FID по текущей git ветке
    fid, pipeline = get_current_feature_context(state)
    if not fid:
        print("❌ Не удалось определить контекст фичи")
        return None

    gates = pipeline.get("gates", {})

    # 4. Проверить PRD_READY
    if not gates.get("PRD_READY", {}).get("passed"):
        print(f"❌ Ворота PRD_READY не пройдены для {fid}")
        print("   → Сначала выполните /aidd-analyze")
        return None

    # 5. Проверить RESEARCH_DONE
    if not gates.get("RESEARCH_DONE", {}).get("passed"):
        print(f"❌ Ворота RESEARCH_DONE не пройдены для {fid}")
        print("   → Сначала выполните /aidd-research")
        return None

    print(f"✓ Фича {fid}: {pipeline.get('title')}")
    return (fid, pipeline)
```

---

## Выходные артефакты (в целевом проекте)

| Артефакт | Путь (v2) | Путь (v3) |
|----------|-----------|-----------|
| План фичи | `ai-docs/docs/_plans/features/{YYYY-MM-DD}_{FID}_{slug}-plan.md` | `ai-docs/docs/_plans/features/{YYYY-MM-DD}_{FID}_{slug}.md` |

> **Примечание (v2.4+)**:
> - **v2** (по умолчанию): Старая структура `plans/`, имя с дублированием `{name}-plan.md`
> - **v3** (после миграции): Новая структура `_plans/features/`, имя без дублирования `{name}.md`
> - Режим определяется из `.pipeline-state.json → naming_version`

### Именование артефакта

FID и slug берутся из `active_pipelines[FID]` в `.pipeline-state.json` (v2):

```python
# Получить данные из state (v2)
fid, pipeline = get_current_feature_context(state)
if not fid:
    print("❌ Не удалось определить контекст фичи")
    return None

slug = pipeline["name"]  # email-notify
date = datetime.now().strftime("%Y-%m-%d")  # 2024-12-23

# Определить naming_version и структуру артефактов
naming_version = state.get("naming_version", "v2")

if naming_version == "v3":
    folder = "_plans/features"
    filename = f"{date}_{fid}_{slug}.md"  # Без дублирования
else:
    folder = "plans"
    filename = f"{date}_{fid}_{slug}-plan.md"  # С дублированием

artifact_path = f"{folder}/{filename}"
# v2: plans/2024-12-23_F042_email-notify-plan.md
# v3: _plans/features/2024-12-23_F042_email-notify.md
```

### Обновление .pipeline-state.json

После создания плана обновить `active_pipelines[FID].artifacts` (v2):

**Пример для v2 (по умолчанию)**:
```json
{
  "naming_version": "v2",
  "active_pipelines": {
    "F042": {
      "branch": "feature/F042-email-notify",
      "name": "email-notify",
      "title": "Email уведомления",
      "stage": "PLAN",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": true, "passed_at": "2024-12-23T11:00:00Z"},
        "PLAN_APPROVED": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F042_email-notify-prd.md",
        "research": "research/2024-12-23_F042_email-notify-research.md",
        "plan": "plans/2024-12-23_F042_email-notify-plan.md"
      }
    }
  }
}
```

**Пример для v3 (после миграции)**:
```json
{
  "naming_version": "v3",
  "active_pipelines": {
    "F042": {
      "artifacts": {
        "prd": "_analysis/2024-12-23_F042_email-notify.md",
        "research": "_research/2024-12-23_F042_email-notify.md",
        "plan": "_plans/features/2024-12-23_F042_email-notify.md"
      }
    }
  }
}
```

---

## Качественные ворота

### PLAN_APPROVED

| Критерий | Описание |
|----------|----------|
| Интеграция | Точки интеграции определены |
| Изменения | Необходимые изменения описаны |
| Риски | Потенциальные риски учтены |
| **Утверждение** | План утверждён пользователем |

**ВАЖНО**: Требуется явное подтверждение от пользователя!

---

## Примеры использования

```bash
# После /aidd-research (для фичи)
/feature-plan
```

---

## Отличия от /plan

| Аспект | /aidd-plan (CREATE) | /aidd-plan-feature (FEATURE) |
|--------|----------------|-------------------------|
| Цель | Полная архитектура системы | План интеграции фичи |
| Артефакт (v2) | `architecture/{name}-plan.md` | `plans/{feature}-plan.md` |
| Артефакт (v3) | `_plans/mvp/{name}.md` | `_plans/features/{name}.md` |
| Фокус | Компоненты с нуля | Точки расширения |
| Изменения | Создание нового | Минимизация изменений |

---

## Шаблон плана фичи

План фичи должен содержать:

```markdown
# План фичи: {Название}

## 1. Обзор
- Краткое описание
- Связь с существующим функционалом

## 2. Анализ существующего кода
- Затронутые сервисы
- Точки интеграции
- Существующие зависимости

## 3. План изменений

### 3.1 Новые компоненты
| Компонент | Расположение | Описание |

### 3.2 Модификации существующего кода
| Файл | Изменение | Причина |

### 3.3 Новые зависимости
| Зависимость | Версия | Назначение |

## 4. API контракты (если есть)

## 5. Влияние на существующие тесты

## 6. План интеграции
| # | Шаг | Зависимости |

## 7. Риски и митигация
| Риск | Вероятность | Митигация |
```

---

## Интеграционные соображения

При создании плана фичи учитывать:

### 1. Минимизация изменений
```
✓ Добавить новый модуль
✗ Переписывать существующий модуль

✓ Расширить интерфейс
✗ Менять сигнатуры существующих методов

✓ Добавить новый эндпоинт
✗ Менять URL существующих эндпоинтов
```

### 2. Обратная совместимость
- Существующие API должны работать без изменений
- Новые поля должны быть опциональными
- Миграции БД должны быть обратимыми

### 3. Тестирование
- Существующие тесты не должны ломаться
- Новые тесты изолированы от старых
- Интеграционные тесты покрывают точки соединения

---

## Чеклист ворот PLAN_APPROVED

> ⚠️ AI ОБЯЗАН создать TodoWrite с этими пунктами.

- [ ] 🔴 Feature Plan создан в правильной папке:
  - v2: `ai-docs/docs/_plans/features/{feature}-plan.md`
  - v3: `ai-docs/docs/_plans/features/{feature}.md`
- [ ] 🔴 Интеграция с существующим кодом описана
- [ ] 🔴 **Пользователь утвердил план** ← КРИТИЧЕСКИ ВАЖНО
- [ ] 🔴 `.pipeline-state.json` обновлён (gate: PLAN_APPROVED, artifact path соответствует naming_version)
- [ ] 🟡 Breaking changes определены
- [ ] 🟡 Миграции БД описаны (если применимо)

---

## Следующий шаг

После прохождения ворот `PLAN_APPROVED`:

```bash
/generate
```
