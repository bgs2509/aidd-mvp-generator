# Migration Guide: v3.x → v4.0

> **Дата**: 2026-01-29
> **Версия**: v4.0 (Immediate Deprecation)

---

## Executive Summary

В v4.0 фреймворк AIDD-MVP Generator полностью перешёл на унифицированную систему именования на базе 5 ключевых слов:

**analyst, researcher, planner, coder, validator**

Все legacy команды и агенты удалены.

---

## Что изменилось

### Удалённые команды

| Legacy (УДАЛЕНО) | New (ОБЯЗАТЕЛЬНО) | Описание |
|------------------|-------------------|----------|
| `/aidd-idea` | `/aidd-analyze` | Анализ идеи → PRD |
| `/aidd-feature-plan` | `/aidd-plan-feature` | Планирование фичи |
| `/aidd-generate` | `/aidd-code` | Генерация кода |
| `/aidd-finalize` | `/aidd-validate` | Quality & Deploy |

### Удалённые агенты

| Legacy (УДАЛЕНО) | New (ОБЯЗАТЕЛЬНО) |
|------------------|-------------------|
| `planner.md` | `planner.md` |
| `coder.md` | `coder.md` |

### Изменения в артефактах

**v3 теперь default**:

| v2 (deprecated) | v3 (default) |
|-----------------|--------------|
| `prd/{name}-prd.md` | `_analysis/{name}.md` |
| `architecture/{name}-plan.md` | `_plans/mvp/{name}.md` |
| `plans/{name}-plan.md` | `_plans/features/{name}.md` |
| `reports/{name}-completion.md` | `_validation/{name}.md` |
| `research/{name}-research.md` | `_research/{name}.md` |

---

## Для существующих проектов

### Вариант 1: Продолжить с v2 (deprecated)

Если вы хотите сохранить текущую структуру артефактов (prd/, architecture/, etc.):

```bash
# ТРЕБУЕТСЯ: Обновить команды на новые
# Старые команды больше НЕ работают!

/aidd-idea        → /aidd-analyze       ❌ Command not found
/aidd-generate    → /aidd-code          ❌ Command not found
/aidd-finalize    → /aidd-validate      ❌ Command not found
/aidd-feature-plan → /aidd-plan-feature ❌ Command not found
```

**Что нужно сделать**:
1. Обновить все скрипты и документацию на новые команды
2. Убедиться что `.pipeline-state.json` содержит `"naming_version": "v2"`
3. Продолжить работу с новыми командами

**Ограничения**:
- v2 структура **deprecated** (не рекомендуется для новых проектов)
- Legacy команды **удалены** (невозможно вызвать)
- Поддержка v2 будет убрана в будущих версиях

### Вариант 2: Мигрировать на v3 (рекомендуется)

Для перехода на новую структуру артефактов (_analysis/, _plans/, etc.):

```bash
# Перейти в корень проекта
cd your-project/

# Запустить migration script
python3 .aidd/scripts/migrate-naming-v3.py
```

**Что делает скрипт**:
1. Переименовывает папки артефактов:
   - `prd/` → `_analysis/`
   - `architecture/` → `_plans/mvp/`
   - `plans/` → `_plans/features/`
   - `reports/` → `_validation/`
   - `research/` → `_research/`

2. Удаляет дублирование в именах файлов:
   - `{name}-prd.md` → `{name}.md`
   - `{name}-plan.md` → `{name}.md`
   - `{name}-completion.md` → `{name}.md`

3. Обновляет `.pipeline-state.json`:
   - `"naming_version": "v2"` → `"v3"`
   - Обновляет пути артефактов в `active_pipelines` и `features_registry`

4. (Опционально) Обновляет ссылки в markdown документах

**Пример**:

```bash
# До миграции
ai-docs/docs/
├── prd/
│   └── 2026-01-15_F001_booking-prd.md
├── architecture/
│   └── 2026-01-15_F001_booking-plan.md
└── reports/
    └── 2026-01-20_F001_booking-completion.md

# После миграции
ai-docs/docs/
├── _analysis/
│   └── 2026-01-15_F001_booking.md
├── _plans/
│   └── mvp/
│       └── 2026-01-15_F001_booking.md
└── _validation/
    └── 2026-01-20_F001_booking.md
```

---

## Для CI/CD скриптов

Если у вас есть скрипты автоматизации, обновите команды:

```bash
# ❌ Старый скрипт (НЕ работает)
#!/bin/bash
/aidd-idea "New feature"
/aidd-research
/aidd-plan
/aidd-generate
/aidd-finalize

# ✅ Новый скрипт (работает)
#!/bin/bash
/aidd-analyze "New feature"
/aidd-research
/aidd-plan
/aidd-code
/aidd-validate
```

---

## Для новых проектов

Новые проекты автоматически создаются с v3:

```bash
# Создать новый проект
mkdir my-new-mvp && cd my-new-mvp
git init
git submodule add <framework-repo> .aidd

# Запустить Claude Code
claude

# Инициализировать проект
/aidd-init
# → naming_version = "v3" (по умолчанию)

# Начать разработку (только новые команды!)
/aidd-analyze "Your MVP idea"
/aidd-research
/aidd-plan
/aidd-code
/aidd-validate
```

---

## Breaking Changes в деталях

### 1. Legacy команды удалены

**Попытка вызова**:
```bash
/aidd-idea "test"
# → Error: Command not found
```

**Решение**: Используйте `/aidd-analyze`

### 2. Legacy агенты удалены

**Файлы удалены**:
- `.claude/agents/planner.md`
- `.claude/agents/coder.md`

**Заменены на**:
- `.claude/agents/planner.md`
- `.claude/agents/coder.md`

### 3. Default naming_version изменён

**Было** (v3.x):
```json
{
  "naming_version": "v2"  // default
}
```

**Стало** (v4.0):
```json
{
  "naming_version": "v3"  // default
}
```

**Что это означает**:
- Новые проекты создаются с v3
- Существующие проекты с v2 продолжают работать (deprecated)

---

## FAQ

### Q: Мои старые команды не работают. Что делать?

**A**: Обновите на новые команды (см. таблицу в начале документа). Legacy команды удалены в v4.0.

### Q: Могу ли я продолжать использовать v2 структуру?

**A**: Да, но:
1. Вам нужно использовать **только новые команды** (`/aidd-analyze`, `/aidd-code`, etc.)
2. v2 структура **deprecated** и будет удалена в будущих версиях
3. Рекомендуется мигрировать на v3

### Q: Как мигрировать на v3?

**A**: Запустите `python3 .aidd/scripts/migrate-naming-v3.py` в корне проекта.

### Q: Что если миграция сломает мой проект?

**A**: Migration script создаёт backup. Если что-то пошло не так:
```bash
# Откатиться на предыдущий коммит
git log --oneline | head -5
git reset --hard <commit-before-migration>
```

### Q: Нужно ли обновлять документацию в моём проекте?

**A**: Да, если вы используете legacy команды в README или других документах:
- Замените `/aidd-idea` → `/aidd-analyze`
- Замените `/aidd-generate` → `/aidd-code`
- Замените `/aidd-finalize` → `/aidd-validate`
- Замените `/aidd-feature-plan` → `/aidd-plan-feature`

### Q: Что делать с CI/CD пайплайнами?

**A**: Обновите скрипты на новые команды (см. раздел "Для CI/CD скриптов").

---

## Поддержка

Если у вас возникли проблемы с миграцией:

1. **Проверьте CHANGELOG.md** — там описаны все изменения v4.0
2. **Прочитайте этот гайд** — большинство проблем решаются здесь
3. **Создайте issue** (если публичный репозиторий)
4. **Откатитесь на v3.x** — если v4.0 критически сломал ваш проект

---

## Timeline

- **2026-01-19**: Phase 2 завершена — Migration Mode активен
- **2026-01-29**: v4.0 выпущен — Immediate Deprecation (legacy удалено)

---

**Версия документа**: 1.0
**Обновлён**: 2026-01-29
**Применяется к**: v4.0+
