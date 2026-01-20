# Testing Migration Mode (v2.4)

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-idea`, `/aidd-generate`, `/aidd-finalize`, `/aidd-feature-plan`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Цель**: Протестировать работу migration mode и убедиться что оба варианта команд (v2 и v3) работают корректно.

---

## Тест 1: Новый проект с v2 (default)

### Шаг 1: Создание проекта

```bash
mkdir test-v2-project
cd test-v2-project
git init
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd
```

### Шаг 2: Инициализация

```bash
claude
/aidd-init
```

**Ожидаемый результат**:
- Создан `.pipeline-state.json` с `naming_version: "v2"`
- Созданы папки: `ai-docs/docs/prd/`, `ai-docs/docs/research/`, `ai-docs/docs/architecture/`, `ai-docs/docs/reports/`

### Шаг 3: Выполнение команд (старые названия)

```bash
/aidd-idea "Тестовый проект для бронирования"
/aidd-research
/aidd-plan
```

**Ожидаемый результат**:
- ✅ `ai-docs/docs/prd/{date}_{FID}_{slug}-prd.md` создан
- ✅ `ai-docs/docs/research/{date}_{FID}_{slug}-research.md` создан
- ✅ `ai-docs/docs/architecture/{date}_{FID}_{slug}-plan.md` создан
- Имена файлов содержат дублирование (`-prd`, `-research`, `-plan`)

### Шаг 4: Выполнение команд (новые названия)

```bash
# Создать новую фичу
git checkout -b feature/F002-test
/aidd-analyze "Добавить уведомления"
/aidd-research
/aidd-plan-feature
```

**Ожидаемый результат**:
- ✅ Новые команды работают
- ✅ Артефакты создаются в тех же папках (v2)
- ✅ `prd/{date}_F002_{slug}-prd.md` создан
- ✅ `plans/{date}_F002_{slug}-plan.md` создан

### Чеклист Теста 1

- [ ] `.pipeline-state.json` содержит `naming_version: "v2"`
- [ ] Папки v2 созданы (`prd/`, `research/`, `architecture/`, `plans/`, `reports/`)
- [ ] Старые команды работают (`/aidd-idea`, `/aidd-generate`, `/aidd-finalize`)
- [ ] Новые команды работают (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`)
- [ ] Артефакты в правильных папках (v2)
- [ ] Имена файлов с дублированием (`-prd.md`, `-plan.md`)

---

## Тест 2: Новый проект с v3

### Шаг 1: Создание проекта

```bash
mkdir test-v3-project
cd test-v3-project
git init
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd
```

### Шаг 2: Инициализация с v3

```bash
claude
/aidd-init
```

**Действие**: При инициализации вручную отредактировать `.pipeline-state.json`:

```json
{
  "naming_version": "v3",
  ...
}
```

Или использовать скрипт (если добавлена поддержка флага):
```bash
/aidd-init --naming-version=v3
```

**Ожидаемый результат**:
- Создан `.pipeline-state.json` с `naming_version: "v3"`
- Созданы папки: `ai-docs/docs/_analysis/`, `ai-docs/docs/_research/`, `ai-docs/docs/_plans/mvp/`, `ai-docs/docs/_plans/features/`, `ai-docs/docs/_validation/`

### Шаг 3: Выполнение команд (новые названия)

```bash
/aidd-analyze "Тестовый проект для бронирования"
/aidd-research
/aidd-plan
```

**Ожидаемый результат**:
- ✅ `ai-docs/docs/_analysis/{date}_{FID}_{slug}.md` создан
- ✅ `ai-docs/docs/_research/{date}_{FID}_{slug}.md` создан
- ✅ `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}.md` создан
- Имена файлов БЕЗ дублирования (нет `-prd`, `-research`, `-plan`)

### Шаг 4: Выполнение команд (старые названия)

```bash
# Создать новую фичу
git checkout -b feature/F002-test
/aidd-idea "Добавить уведомления"
/aidd-research
/aidd-feature-plan
```

**Ожидаемый результат**:
- ✅ Старые команды работают
- ✅ Артефакты создаются в новых папках (v3)
- ✅ `_analysis/{date}_F002_{slug}.md` создан
- ✅ `_plans/features/{date}_F002_{slug}.md` создан

### Чеклист Теста 2

- [ ] `.pipeline-state.json` содержит `naming_version: "v3"`
- [ ] Папки v3 созданы (`_analysis/`, `_research/`, `_plans/mvp/`, `_plans/features/`, `_validation/`)
- [ ] Новые команды работают (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`)
- [ ] Старые команды работают (`/aidd-idea`, `/aidd-generate`, `/aidd-finalize`)
- [ ] Артефакты в правильных папках (v3)
- [ ] Имена файлов без дублирования (`.md` вместо `-prd.md`)

---

## Тест 3: Миграция v2 → v3

### Предусловие

Выполнен **Тест 1** и создан проект с v2.

### Шаг 1: Проверка перед миграцией

```bash
cd test-v2-project

# Проверить структуру
ls -la ai-docs/docs/
# Должны быть: prd/, research/, architecture/, plans/, reports/

# Проверить naming_version
cat .pipeline-state.json | grep naming_version
# Должно быть: "naming_version": "v2"

# Проверить имена файлов
ls ai-docs/docs/prd/
# Должны быть файлы с дублированием: *-prd.md
```

### Шаг 2: Запуск миграции

```bash
python3 .aidd/scripts/migrate-naming-v3.py
```

**Ожидаемый вывод**:
```
🔄 Migration v2 → v3 started...

📁 Step 1: Renaming folders...
  ✓ prd/ → _analysis/
  ✓ research/ → _research/
  ✓ architecture/ → _plans/mvp/
  ✓ plans/ → _plans/features/
  ✓ reports/ → _validation/

📝 Step 2: Renaming files (removing duplication)...
  ✓ Renamed 5 files in _analysis/
  ✓ Renamed 3 files in _research/
  ✓ Renamed 2 files in _plans/mvp/
  ✓ Renamed 1 file in _plans/features/

🔧 Step 3: Updating .pipeline-state.json...
  ✓ Set naming_version: "v3"
  ✓ Updated artifact paths in active_pipelines
  ✓ Updated artifact paths in features_registry

🔗 Step 4: Updating references in documents...
  ✓ Updated 12 references

✅ Migration complete!
```

### Шаг 3: Проверка после миграции

```bash
# Проверить структуру
ls -la ai-docs/docs/
# Должны быть: _analysis/, _research/, _plans/, _validation/

# Проверить naming_version
cat .pipeline-state.json | grep naming_version
# Должно быть: "naming_version": "v3"

# Проверить имена файлов
ls ai-docs/docs/_analysis/
# Должны быть файлы без дублирования: *.md (не *-prd.md)

# Проверить содержимое .pipeline-state.json
cat .pipeline-state.json | jq '.active_pipelines[].artifacts'
# Пути должны быть обновлены на v3 (_analysis/, _plans/, etc.)
```

### Шаг 4: Проверка работы команд после миграции

```bash
# Создать новую фичу
git checkout -b feature/F003-test-after-migration
/aidd-analyze "Тест после миграции"
/aidd-research
```

**Ожидаемый результат**:
- ✅ Команды работают
- ✅ Артефакты создаются в новых папках (v3)
- ✅ `_analysis/{date}_F003_{slug}.md` создан
- ✅ `_research/{date}_F003_{slug}.md` создан

### Чеклист Теста 3

- [ ] Миграционный скрипт выполнен без ошибок
- [ ] Папки переименованы: `prd/` → `_analysis/`, `architecture/` → `_plans/mvp/`, etc.
- [ ] Файлы переименованы: `{name}-prd.md` → `{name}.md`
- [ ] `.pipeline-state.json` обновлён: `naming_version: "v3"`
- [ ] Artifact paths в `.pipeline-state.json` обновлены
- [ ] Команды работают после миграции
- [ ] Новые артефакты создаются в v3 папках

---

## Тест 4: Backward Compatibility (смешанное использование)

### Цель

Убедиться что можно использовать старые и новые команды вперемешку.

### Сценарий

```bash
cd test-v2-project  # или test-v3-project

# Использовать старую команду
/aidd-idea "Фича 1"

# Использовать новую команду
/aidd-research

# Использовать старую команду
/aidd-feature-plan

# Использовать новую команду
/aidd-code

# Использовать старую команду
/aidd-finalize
```

**Ожидаемый результат**:
- ✅ Все команды работают
- ✅ Артефакты создаются корректно
- ✅ Ворота проходятся правильно
- ✅ Нет ошибок или предупреждений

### Чеклист Теста 4

- [ ] Старые команды работают в любом порядке
- [ ] Новые команды работают в любом порядке
- [ ] Смешанное использование работает
- [ ] Нет конфликтов между командами
- [ ] Артефакты корректны

---

## Тест 5: Edge Cases

### Тест 5.1: Отсутствие naming_version

**Сценарий**: Удалить `naming_version` из `.pipeline-state.json`

```bash
# Отредактировать .pipeline-state.json, удалить поле naming_version
/aidd-analyze "Тест без naming_version"
```

**Ожидаемый результат**:
- ✅ Команда использует v2 по умолчанию (fallback)
- ✅ Артефакты создаются в `prd/` (v2)
- ✅ Нет ошибок

### Тест 5.2: Некорректное значение naming_version

**Сценарий**: Установить `naming_version: "v99"`

```bash
# Отредактировать .pipeline-state.json
{
  "naming_version": "v99",
  ...
}

/aidd-analyze "Тест с некорректной версией"
```

**Ожидаемый результат**:
- ✅ Команда использует v2 по умолчанию (fallback)
- ✅ Или показывает ошибку с инструкциями
- ✅ Система не падает

### Чеклист Теста 5

- [ ] Отсутствие `naming_version` обрабатывается (fallback to v2)
- [ ] Некорректное значение обрабатывается
- [ ] Нет критических ошибок
- [ ] Система продолжает работать

---

## Итоговый чеклист

### Функциональность

- [ ] ✅ Тест 1: v2 проект работает
- [ ] ✅ Тест 2: v3 проект работает
- [ ] ✅ Тест 3: Миграция v2 → v3 работает
- [ ] ✅ Тест 4: Backward compatibility работает
- [ ] ✅ Тест 5: Edge cases обработаны

### Команды

- [ ] Все старые команды работают (`/aidd-idea`, `/aidd-generate`, `/aidd-finalize`, `/aidd-feature-plan`)
- [ ] Все новые команды работают (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`)
- [ ] Смешанное использование работает

### Артефакты

- [ ] v2 артефакты создаются в правильных папках (`prd/`, `architecture/`, etc.)
- [ ] v3 артефакты создаются в правильных папках (`_analysis/`, `_plans/`, etc.)
- [ ] v2 имена файлов с дублированием (`-prd.md`, `-plan.md`)
- [ ] v3 имена файлов без дублирования (`.md`)

### Миграция

- [ ] Скрипт миграции работает без ошибок
- [ ] Папки переименованы корректно
- [ ] Файлы переименованы корректно
- [ ] `.pipeline-state.json` обновлён корректно
- [ ] Команды работают после миграции

---

## Отчёт о тестировании

После прохождения всех тестов заполните отчёт:

```markdown
# Migration Mode Testing Report

**Дата**: YYYY-MM-DD
**Тестировщик**: [Имя]
**Версия фреймворка**: v2.4.0

## Результаты

- [ ] Тест 1: v2 проект - ✅ PASSED / ❌ FAILED
- [ ] Тест 2: v3 проект - ✅ PASSED / ❌ FAILED
- [ ] Тест 3: Миграция - ✅ PASSED / ❌ FAILED
- [ ] Тест 4: Backward compat - ✅ PASSED / ❌ FAILED
- [ ] Тест 5: Edge cases - ✅ PASSED / ❌ FAILED

## Найденные проблемы

1. [Описание проблемы]
   - Критичность: HIGH / MEDIUM / LOW
   - Шаги воспроизведения: ...
   - Ожидаемое поведение: ...
   - Фактическое поведение: ...

## Рекомендации

[Ваши рекомендации]

## Заключение

✅ Migration mode готов к production
❌ Требуются доработки
```

---

**Версия документа**: 1.0
**Дата создания**: 2026-01-19
