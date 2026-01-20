# Template Drift Report: comprehensive-audit.md vs Текущий фреймворк

> **Дата аудита**: 2026-01-20
> **Проверенный документ**: `docs/audit/templates/comprehensive-audit.md`
> **Период изменений**: Декабрь 2025 — Январь 2026
> **Аудитор**: Claude AI (План: `/home/bgs/.claude/plans/tingly-wiggling-wren.md`)

---

## Executive Summary

### Общая оценка

Шаблон аудита `comprehensive-audit.md` **значительно устарел** относительно текущего состояния фреймворка AIDD-MVP Generator. Обнаружено **8 категорий расхождений**, включая 2 критических (CRITICAL), 1 высокоприоритетное (HIGH), 3 среднеприоритетных (MEDIUM) и 2 низкоприоритетных (LOW).

**Основная причина**: За последний месяц во фреймворке произошли **архитектурные изменения**:
- Consolidation команд (4 команды → 1)
- Unification этапов пайплайна (9 → 6)
- Naming Convention Migration v2.4 (введение migration mode)

### Критические проблемы

| Проблема | Влияние |
|----------|---------|
| Шаблон проверяет **9 этапов** вместо **6** | Smoke Tests и Objectives ищут несуществующие этапы 6-8 |
| Шаблон проверяет **10 команд** вместо **6** | False positive при отсутствии команд review, test, validate, deploy |
| Шаблон не учитывает **migration mode v2.4** | Пропускает проверку дубликатов команд/ролей и новых папок артефактов |

### Рекомендация

**ВЫСОКИЙ ПРИОРИТЕТ**: Обновить шаблон до версии 2.0 с учётом всех архитектурных изменений.

---

## Детальный анализ расхождений

### 1. CRITICAL: Количество этапов пайплайна (9 → 6)

**Локация в шаблоне**:
- Строки 286-293 (Objective 1: описание пайплайна)
- Строки 539-597 (Objective 6: консистентность этапов)
- Строки 206-223 (Smoke Test 10: ворота)

**Что написано в шаблоне**:
```markdown
| Параметр | Значение |
|----------|----------|
| Пайплайн | 9 этапов (0-8), 9 ворот |
```

```bash
# Smoke Test 10 проверяет 9 ворот
EXPECTED_GATES=(
  BOOTSTRAP_READY PRD_READY RESEARCH_DONE
  PLAN_APPROVED IMPLEMENT_OK REVIEW_OK
  QA_PASSED ALL_GATES_PASSED DEPLOYED
)
```

**Текущее состояние** (CLAUDE.md, workflow.md):
- **6 этапов (0-5)** с 6 основными воротами
- Этап 5 (Quality & Deploy) объединяет 4 sub-gates: REVIEW_OK, QA_PASSED, ALL_GATES_PASSED, DEPLOYED
- Quick режим добавляет ворота DOCUMENTED

**Коммит**: 6808beb "fix(docs): resolve C-PIPELINE-1 - unify pipeline stage count to 6 (0-5)"

**Влияние**:
- ❌ Smoke Test 10 будет искать 9 ворот и сообщать о расхождении
- ❌ Objective 6 будет проверять несуществующие этапы 6-8
- ❌ Команды валидации из Objective 6 вернут ошибки для этапов 6-8

**Исправление**:
```bash
# Строка 286 — обновить таблицу
| Пайплайн | 6 этапов (0-5), 6 ворот + 4 sub-gates (Этап 5) |

# Строки 539-597 — изменить цикл проверки
for stage in 0 1 2 3 4 5; do  # было: 0 1 2 3 4 5 6 7 8
  if grep -q "Этап $stage\\|Stage $stage\\|этап $stage" CLAUDE.md; then
    echo "✅ Этап $stage"
  else
    echo "❌ Этап $stage не найден"
  fi
done

# Строки 206-223 — обновить список ворот
EXPECTED_GATES=(
  "BOOTSTRAP_READY"   # Этап 0
  "PRD_READY"         # Этап 1
  "RESEARCH_DONE"     # Этап 2
  "PLAN_APPROVED"     # Этап 3
  "IMPLEMENT_OK"      # Этап 4
  "REVIEW_OK"         # Этап 5, sub-gate 1
  "QA_PASSED"         # Этап 5, sub-gate 2
  "ALL_GATES_PASSED"  # Этап 5, sub-gate 3
  "DEPLOYED"          # Этап 5, sub-gate 4
  "DOCUMENTED"        # Этап 5, Quick режим
)
```

---

### 2. CRITICAL: Consolidation команд (10 → 6 уникальных)

**Локация в шаблоне**:
- Строки 146-164 (Smoke Test 7)
- Строки 600-681 (Objective 7: соответствие команд/ролей)

**Что написано в шаблоне**:
```bash
# Smoke Test 7: Ожидает 10 команд
COMMANDS=(init idea research plan feature-plan generate review test validate deploy)
```

**Текущее состояние**:
- Команды **review, test, validate, deploy удалены** (коммит 7b4907d)
- Всё объединено в `/aidd-finalize` (или `/aidd-validate`)
- **6 уникальных команд** с алиасами (migration mode v2.4):
  1. `init`
  2. `idea` / `analyze`
  3. `research`
  4. `plan` / (для CREATE)
  5. `feature-plan` / `plan-feature` (для FEATURE)
  6. `generate` / `code`
  7. `finalize` / `validate`

**Фактически**: 11 файлов команд (.md), но это дубликаты — норма для migration mode

**Влияние**:
- ❌ Smoke Test 7 сообщит об отсутствии команд review, test, validate, deploy (false positive)
- ❌ Objective 7 будет искать несуществующие файлы `.claude/commands/review.md`, etc.

**Исправление**:
```bash
# Строки 146-164 — обновить список команд
echo "=== SMOKE TEST 7: Slash-команды (Migration Mode) ==="
COMMANDS=(init idea analyze research plan feature-plan plan-feature generate code finalize validate)
missing=0
for cmd in "${COMMANDS[@]}"; do
  if [ -f ".claude/commands/aidd-$cmd.md" ]; then
    echo "✅ /aidd-$cmd"
  else
    echo "🚨 MISSING: /aidd-$cmd"
    missing=$((missing + 1))
  fi
done
echo "Итого: $((11 - missing))/11 файлов команд"
# Ожидание: 11/11 (дубликаты — это норма в migration mode v2.4)
```

**Примечание**: Добавить пояснение о migration mode:
```markdown
> **Migration Mode (v2.4+)**: Все команды доступны в двух вариантах — старые и новые названия.
> Это норма. Ожидается **11 файлов** команд вместо 6, так как:
> - `idea` + `analyze` (дубликаты)
> - `feature-plan` + `plan-feature` (дубликаты)
> - `generate` + `code` (дубликаты)
> - `finalize` + `validate` (дубликаты)
```

---

### 3. HIGH: Naming Convention Migration v2.4 не учтена

**Локация в шаблоне**: Весь документ (не упоминается migration mode)

**Что отсутствует в шаблоне**:
- Проверка поля `naming_version` в `.pipeline-state.json`
- Проверка папок артефактов v3: `_analysis/`, `_research/`, `_plans/mvp/`, `_plans/features/`, `_validation/`
- Smoke Test для naming_version support в командах

**Текущее состояние** (Phase 2 завершена 2026-01-19):
- Все команды и роли доступны в двух вариантах
- Артефакты создаются в разных папках в зависимости от `naming_version`:
  - **v2** (по умолчанию): `prd/`, `architecture/`, `plans/`, `reports/`, `research/`
  - **v3** (после миграции): `_analysis/`, `_research/`, `_plans/mvp/`, `_plans/features/`, `_validation/`

**Влияние**:
- ⚠️ Objective 2 (валидация ссылок) пропустит файлы в папках v3 (`_analysis/`, etc.)
- ⚠️ Smoke Test 6-7 покажут больше файлов, чем ожидается (дубликаты)

**Исправление**:

1. **Добавить Smoke Test 13** (после Smoke Test 12):
```bash
### Smoke Test 13: Naming Version Support

echo "=== SMOKE TEST 13: Naming Version Support (Migration Mode v2.4) ==="

# 1. Проверить наличие naming_version в .pipeline-state.json
if [ -f ".pipeline-state.json" ]; then
  NAMING_VERSION=$(jq -r '.naming_version // "v2"' .pipeline-state.json)
  echo "naming_version: $NAMING_VERSION"
else
  echo "⚠️ .pipeline-state.json не найден (норма для фреймворка)"
  NAMING_VERSION="v2"
fi

# 2. Проверить что все команды поддерживают naming_version
echo ""
echo "Команды с поддержкой naming_version:"
for cmd in analyze research plan plan-feature code validate; do
  if grep -q "naming_version" ".claude/commands/aidd-$cmd.md" 2>/dev/null; then
    echo "✅ /aidd-$cmd supports naming_version"
  else
    echo "⚠️ /aidd-$cmd missing naming_version support"
  fi
done

# 3. Проверить структуру артефактов
echo ""
echo "Структура артефактов ($NAMING_VERSION):"
if [ "$NAMING_VERSION" = "v3" ]; then
  # v3 ожидает папки с префиксом _
  for dir in _analysis _research _plans _validation; do
    [ -d "ai-docs/docs/$dir" ] && echo "✅ $dir/" || echo "⚠️ $dir/ (ожидается для v3)"
  done
else
  # v2 ожидает стандартные папки
  for dir in prd research architecture plans reports; do
    [ -d "ai-docs/docs/$dir" ] && echo "✅ $dir/" || echo "⚠️ $dir/ (ожидается для v2)"
  done
fi
```

2. **Objective 2**: Добавить паттерны для v3 в проверку ссылок (строки 296-376):
```bash
# ШАГ 2: Извлечение ВСЕХ markdown ссылок (учёт v2 и v3)
echo "Шаг 2: Извлечение всех markdown ссылок..."
grep -rno '\[.*\](.*\.md' . --include="*.md" 2>/dev/null > /tmp/all_links.txt

# Добавить проверку папок v3
if [ -d "ai-docs/docs/_analysis" ] || [ -d "ai-docs/docs/_validation" ]; then
  echo "Обнаружена структура v3 (naming_version=v3)"
fi
```

---

### 4. MEDIUM: Количество ролей (7 → 5 базовых)

**Локация в шаблоне**:
- Строки 128-145 (Smoke Test 6)
- Строки 600-681 (Objective 7)

**Что написано в шаблоне**:
```bash
# Smoke Test 6 ожидает 7 ролей
ROLES=(analyst researcher architect implementer reviewer qa validator)
```

**Текущее состояние**:
- Роли **reviewer** и **qa удалены** (коммит 7b4907d)
- Их функции переданы роли **validator**
- **5 базовых ролей** + дубликаты + библиотеки:
  - `analyst.md`
  - `researcher.md`
  - `architect.md` / `planner.md` (дубликаты)
  - `implementer.md` / `coder.md` (дубликаты)
  - `validator.md` (объединяет reviewer + qa)
  - `code-review-library.md` (библиотека, не роль)
  - `testing-library.md` (библиотека, не роль)

**Фактически**: 9 файлов в `.claude/agents/`

**Влияние**:
- ⚠️ Smoke Test 6 сообщит об отсутствии ролей reviewer, qa
- ⚠️ Но покажет 9 файлов вместо 7 (из-за дубликатов и библиотек)

**Исправление**:
```bash
# Строки 128-145 — обновить список ролей
echo "=== SMOKE TEST 6: AI-агенты (Migration Mode) ==="
ROLES=(analyst researcher architect planner implementer coder validator code-review-library testing-library)
missing=0
for role in "${ROLES[@]}"; do
  if [ -f ".claude/agents/$role.md" ]; then
    echo "✅ $role.md"
  else
    echo "🚨 MISSING: $role.md"
    missing=$((missing + 1))
  fi
done
echo "Итого: $((9 - missing))/9 файлов агентов"
# Ожидание: 9/9 (5 базовых × 2 варианта - дубликаты + 2 библиотеки)
```

**Примечание**: Добавить пояснение:
```markdown
> **Migration Mode (v2.4+)**: Роли доступны в двух вариантах названий (architect/planner, implementer/coder).
> Ожидается **9 файлов** вместо 7:
> - 5 базовых ролей (analyst, researcher, architect/planner, implementer/coder, validator)
> - 2 библиотеки инструкций (code-review-library, testing-library)
```

---

### 5. MEDIUM: Артефакты (4 отчёта → 1 Completion Report)

**Локация в шаблоне**:
- Строки 186-204 (Smoke Test 9: шаблоны документов)
- Строки 927-971 (Objective 12: целостность шаблонов документов)

**Что написано в шаблоне**:
```bash
# Smoke Test 9 ожидает 8 шаблонов, включая:
review-report-template.md
qa-report-template.md
validation-report-template.md
(deployment-report не упомянут)
```

**Текущее состояние** (workflow.md:54, 439-450):
- Шаблоны review/qa/validation-report **больше не используются**
- Вместо них один шаблон: `completion-report-template.md`
- **1 единый Completion Report** вместо 4 файлов
- Путь: `reports/{YYYY-MM-DD}_{FID}_{slug}-completion.md`

**Влияние**:
- ⚠️ Smoke Test 9 и Objective 12 будут искать несуществующие шаблоны

**Исправление**:
```bash
# Строки 186-204 и 927-971 — обновить список шаблонов
TEMPLATES=(
  "prd-template.md:PRD:Этап 1"
  "architecture-template.md:Архитектура:Этап 3"
  "feature-plan-template.md:План фичи:Этап 3 FEATURE"
  "implementation-plan-template.md:План реализации:Этап 3"
  "completion-report-template.md:Completion Report:Этап 5"  # ⬅️ ИЗМЕНЕНИЕ
  "rtm-template.md:RTM:Все этапы"
  "tasklist-template.md:Список задач:Опционально"
  "pipeline-state-template.json:Состояние пайплайна:Этап 0"
)
```

**Примечание**: Удалить строки про review/qa/validation-report-template.

---

### 6. MEDIUM: Два режима /aidd-finalize (Full vs Quick)

**Локация в шаблоне**: Не упоминается

**Что отсутствует**:
- Проверка режимов работы `/aidd-finalize` (Full vs Quick)
- Ворота `DOCUMENTED` для Quick режима

**Текущее состояние** (workflow.md:416-427):
- **Full режим** (по умолчанию): Review → Test → Validate → Deploy → `DEPLOYED`
- **Quick режим** (`/aidd-finalize --mode=quick`): Static analysis + DRAFT отчёт → `DOCUMENTED`

**Влияние**:
- ⚠️ Smoke Test 10 (ворота) не учитывает ворота `DOCUMENTED`
- ⚠️ Objective 8 (консистентность ворот) пропустит `DOCUMENTED`

**Исправление**:

Добавить в Smoke Test 10 (после строки 223):
```bash
# Проверка режимов /aidd-finalize
echo ""
echo "=== Режимы /aidd-finalize ===\"
echo "Full режим: REVIEW_OK → QA_PASSED → ALL_GATES_PASSED → DEPLOYED"
echo "Quick режим: DOCUMENTED (static analysis only)"

# Проверить что ворота DOCUMENTED упомянуты (для Quick mode)
if grep -q "DOCUMENTED" workflow.md 2>/dev/null; then
  echo "✅ Ворота DOCUMENTED описаны"
else
  echo "⚠️ Ворота DOCUMENTED не упомянуты"
fi
```

---

### 7. LOW: Smoke Test 8 — шаблоны сервисов

**Локация в шаблоне**: Строки 166-184

**Что написано в шаблоне**:
```bash
# Ожидает 5 шаблонов сервисов
SERVICES=(fastapi_business_api postgres_data_api mongo_data_api aiogram_bot asyncio_worker)
```

**Текущее состояние**: Вероятно актуально (требует проверки)

**Влияние**: LOW — скорее всего проверка корректна

**Рекомендация**: Выполнить Smoke Test 8 для подтверждения

---

### 8. LOW: Smoke Test 9 — шаблоны документов (дубликат 5)

См. расхождение #5 (артефакты).

---

## Сводная таблица расхождений

| # | Категория | Приоритет | Затронутые секции | Файлы | Требуемое действие |
|---|-----------|-----------|------------------|-------|-------------------|
| 1 | Количество этапов | **CRITICAL** | Smoke Test 10<br>Objective 6 | comprehensive-audit.md:286-293,<br>539-597, 206-223 | Изменить 9 этапов → 6 этапов<br>Обновить список ворот |
| 2 | Consolidation команд | **CRITICAL** | Smoke Test 7<br>Objective 7 | comprehensive-audit.md:146-164,<br>600-681 | Удалить review/test/validate/deploy<br>Добавить алиасы команд |
| 3 | Naming migration | **HIGH** | Все Smoke Tests<br>Objectives 2,7,11-12 | Весь документ | Добавить Smoke Test 13<br>Обновить Objective 2 |
| 4 | Количество ролей | MEDIUM | Smoke Test 6<br>Objective 7 | comprehensive-audit.md:128-145 | Изменить 7 ролей → 5 (+ библиотеки)<br>Добавить дубликаты |
| 5 | Артефакты | MEDIUM | Smoke Test 9<br>Objective 12 | comprehensive-audit.md:186-204,<br>927-971 | Удалить review/qa/validation-report<br>Добавить completion-report |
| 6 | Режимы finalize | MEDIUM | Smoke Test 10<br>Objective 8 | comprehensive-audit.md:206-223 | Добавить ворота DOCUMENTED<br>Пояснить Full vs Quick |
| 7 | Шаблоны сервисов | LOW | Smoke Test 8 | comprehensive-audit.md:166-184 | Проверить актуальность |
| 8 | Шаблоны документов | LOW | Smoke Test 9 | comprehensive-audit.md:186-204 | См. расхождение #5 |

---

## Рекомендации по обновлению

### Приоритет 1: КРИТИЧЕСКИЕ (немедленно)

1. ✅ **Обновить Smoke Test 10** — список ворот (6 основных + 4 sub + 1 quick)
2. ✅ **Обновить Smoke Test 7** — список команд (6 уникальных + алиасы = 11 файлов)
3. ✅ **Обновить Objective 6** — проверка этапов (0-5, не 0-8)
4. ✅ **Обновить Objective 7** — соответствие команд/ролей (учёт дубликатов)

### Приоритет 2: ВЫСОКИЙ (в течение недели)

5. ✅ **Добавить Smoke Test 13** — проверка naming_version support
6. ✅ **Обновить Objective 2** — валидация ссылок с учётом папок v3
7. ✅ **Обновить Smoke Test 6** — список ролей (5 базовых + библиотеки = 9 файлов)

### Приоритет 3: СРЕДНИЙ (в течение месяца)

8. ✅ **Обновить Smoke Test 9 и Objective 12** — шаблоны документов (completion-report)
9. ✅ **Добавить описание режимов** — Full vs Quick для /aidd-finalize
10. ✅ **Обновить таблицу команд** (строка 286) — 6 этапов, а не 9

### Приоритет 4: НИЗКИЙ (когда появится время)

11. ⚪ **Проверить Smoke Test 8** — актуальность шаблонов сервисов

---

## Верификация после обновления

После внесения изменений выполнить:

```bash
# 1. Проверить корректность Smoke Tests
cd /home/bgs/Henry_Bud_GitHub/aidd-mvp-generator
bash -x docs/audit/templates/comprehensive-audit.md 2>&1 | grep -E "SMOKE TEST|✅|❌|🚨"

# 2. Проверить что несуществующие команды/роли больше не упоминаются
grep -n "reviewer\|qa\|review-report\|qa-report" docs/audit/templates/comprehensive-audit.md
# Ожидание: Только комментарии о том, что они удалены

# 3. Проверить упоминание migration mode
grep -c "migration mode\|naming_version" docs/audit/templates/comprehensive-audit.md
# Ожидание: >= 5 упоминаний

# 4. Проверить актуальность списка этапов
grep -E "этап [6-8]|stage [6-8]" docs/audit/templates/comprehensive-audit.md
# Ожидание: 0 совпадений (этапы 6-8 больше не существуют)
```

---

## Связанные документы

- **План работы**: `/home/bgs/.claude/plans/tingly-wiggling-wren.md`
- **Шаблон аудита**: `docs/audit/templates/comprehensive-audit.md`
- **CLAUDE.md**: Описание текущего пайплайна (6 этапов)
- **workflow.md**: Процесс и ворота
- **Phase 2 Completion**: `contributors/2026-01-19-phase2-completion-summary.md`
- **Ключевые коммиты**:
  - 7b4907d: "refactor: remove obsolete commands, consolidate to /aidd-finalize"
  - 6808beb: "fix(docs): resolve C-PIPELINE-1 - unify pipeline stage count to 6 (0-5)"

---

## Следующие шаги

1. ✅ Создан отчёт о расхождениях (текущий документ)
2. ⏭️ Обновить `comprehensive-audit.md` согласно рекомендациям
3. ⏭️ Протестировать обновлённый шаблон на актуальном фреймворке
4. ⏭️ Выполнить comprehensive audit с обновлённым шаблоном

---

**Версия отчёта**: 1.0
**Автор**: Claude AI
**Дата**: 2026-01-20
**Статус**: ✅ Готов к использованию
**Обнаружено расхождений**: 8 (2 CRITICAL, 1 HIGH, 3 MEDIUM, 2 LOW)
