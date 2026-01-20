# Отчет о расхождениях: Шаблон комплексного аудита vs Фреймворк

**Дата анализа**: 2026-01-20
**Версия фреймворка**: После коммита `dc03f90`
**Версия шаблона**: `docs/audit/templates/comprehensive-audit.md`
**Анализируемый период**: 2025-12-20 — 2026-01-20

---

## Executive Summary

За последний месяц во фреймворке произошли **3 крупных изменения**, которые требуют обновления шаблона комплексного аудита:

1. **Migration Mode v2.4** (2026-01-19) — добавлены алиасы команд и ролей, поддержка naming_version
2. **Consolidation of Stage 5** (2026-01-19) — удалены 4 команды (/review, /test, /validate, /deploy), объединены в /aidd-finalize
3. **Completion Report** (2026-01-13) — новый единый артефакт вместо 4 отдельных отчетов

**Всего обнаружено**: **12 расхождений** (8 MEDIUM, 4 LOW)

**Health Score шаблона**: **100 - (0×4) - (0×2) - (8×0.5) - (4×0.1) = 95.6/100**

---

## Категория A: Структурные расхождения (Smoke Tests)

### 🟡 MEDIUM-1: Smoke Test 6 (Роли AI-агентов) — устаревший список

**Файл**: `comprehensive-audit.md:128-148`

**Проблема**:
```bash
ROLES=(analyst researcher architect planner implementer coder validator code-review-library testing-library)
```

Упоминаются роли `reviewer` и `qa`, которые были удалены при consolidation (2026-01-19).

**Факт**:
- ✅ Существующие файлы: `analyst.md`, `researcher.md`, `architect.md`, `planner.md`, `implementer.md`, `coder.md`, `validator.md`, `code-review-library.md`, `testing-library.md`
- ❌ НЕ существуют: `reviewer.md`, `qa.md` (консолидированы в `validator.md`)

**Исправление**:
```bash
# Обновить список ролей
ROLES=(analyst researcher architect planner implementer coder validator code-review-library testing-library)

# Обновить ожидание
echo "Итого: 9/9 файлов"
echo "(5 базовых ролей: analyst, researcher, planner, coder, validator)"
echo "(+ 2 дубликата: architect=planner, implementer=coder)"
echo "(+ 2 библиотеки: code-review-library, testing-library)"
```

**Влияние**: Smoke Test 6 будет падать, т.к. проверяет несуществующие файлы.

---

### 🟡 MEDIUM-2: Smoke Test 7 (Slash-команды) — устаревший список команд

**Файл**: `comprehensive-audit.md:150-170`

**Проблема**:
```bash
COMMANDS=(init idea analyze research plan feature-plan plan-feature generate code finalize validate)
```

Список корректен, но комментарий устарел:
```
# Consolidation: review, test, validate, deploy → /aidd-finalize (/aidd-validate)
```

**Факт**:
- ✅ Существующие команды: `init`, `idea`, `analyze`, `research`, `plan`, `feature-plan`, `plan-feature`, `generate`, `code`, `finalize`, `validate`
- ❌ НЕ существуют: `review`, `test`, `deploy` (удалены 2026-01-19, consolidation в `/aidd-finalize`)

**Команды устарели**:
- `/aidd-review` → удалена (шаг 1 `/aidd-finalize`)
- `/aidd-test` → удалена (шаг 2 `/aidd-finalize`)
- `/aidd-deploy` → удалена (шаг 4 `/aidd-finalize`)
- `/aidd-validate` — **НЕ удалена**, это алиас `/aidd-finalize` (добавлен в migration mode v2.4)

**Исправление**:
```bash
echo "Итого: 11/11 файлов команд"
echo "(6 уникальных команд: init, idea/analyze, research, plan/feature-plan/plan-feature, generate/code, finalize/validate)"
echo "(Consolidation: старые /review, /test, /deploy удалены, заменены на /aidd-finalize с 4 шагами)"
```

**Влияние**: Комментарий вводит в заблуждение (упоминает `validate` как часть consolidation, но это алиас).

---

### 🟡 MEDIUM-3: Smoke Test 9 (Шаблоны документов) — rtm-template.md не существует

**Файл**: `comprehensive-audit.md:192-212`

**Проблема**:
```bash
TEMPLATES=(prd-template.md architecture-template.md feature-plan-template.md \
           implementation-plan-template.md completion-report-template.md \
           rtm-template.md)
```

Шаблон проверяет `rtm-template.md`, которого нет в фактической структуре.

**Факт**:
```bash
$ ls templates/documents/
architecture-template.md
completion-report-template.md
feature-plan-template.md
features-template.md
implementation-plan-template.md
pipeline-state-template.json
prd-template.md
README.md
research-report-template.md
tasklist-template.md
template-map.md
```

❌ `rtm-template.md` отсутствует

**Исправление**:
```bash
TEMPLATES=(prd-template.md architecture-template.md feature-plan-template.md \
           implementation-plan-template.md completion-report-template.md \
           research-report-template.md tasklist-template.md \
           pipeline-state-template.json)

echo "Итого: $count/8 шаблонов"
# Примечание: rtm-template.md не реализован
```

**Влияние**: Smoke Test 9 будет показывать 5/6 вместо 6/6.

---

### 🟡 MEDIUM-4: Smoke Test 10 (Ворота) — неполный список, отсутствует DOCUMENTED

**Файл**: `comprehensive-audit.md:214-236`

**Проблема**:
```python
EXPECTED_GATES = [
  "BOOTSTRAP_READY",      # Этап 0
  "PRD_READY",            # Этап 1
  "RESEARCH_DONE",        # Этап 2
  "PLAN_APPROVED",        # Этап 3
  "IMPLEMENT_OK",         # Этап 4
  "REVIEW_OK",            # Этап 5, sub-gate 1 (Full)
  "QA_PASSED",            # Этап 5, sub-gate 2 (Full)
  "ALL_GATES_PASSED",     # Этап 5, sub-gate 3 (Full)
  "DEPLOYED",             # Этап 5, sub-gate 4 (Full)
  "DOCUMENTED"            # Этап 5, Quick режим (вместо DEPLOYED)
]
```

Список корректен, но комментарий устарел:
- Ворота `REVIEW_OK`, `QA_PASSED` больше не являются отдельными воротами, а являются **sub-gates** этапа 5.

**Факт** (после consolidation 2026-01-19):
```
Этап 5: /aidd-finalize (Full mode):
  Шаг 1: Code Review → REVIEW_OK ✓
  Шаг 2: Testing → QA_PASSED ✓
  Шаг 3: Validation → ALL_GATES_PASSED ✓
  Шаг 4: Deploy + Completion Report → DEPLOYED ✓

Этап 5: /aidd-finalize (Quick mode):
  Шаг 1: Static Analysis → DOCUMENTED ✓
```

**Исправление**:
```bash
echo "Ворота (6 основных + 4 sub-gates + 1 Quick):"
echo "  Этап 0: BOOTSTRAP_READY"
echo "  Этап 1: PRD_READY"
echo "  Этап 2: RESEARCH_DONE"
echo "  Этап 3: PLAN_APPROVED"
echo "  Этап 4: IMPLEMENT_OK"
echo "  Этап 5 (Full): REVIEW_OK → QA_PASSED → ALL_GATES_PASSED → DEPLOYED"
echo "  Этап 5 (Quick): DOCUMENTED (вместо DEPLOYED)"
```

**Влияние**: Пояснение к воротам не отражает новую структуру (sub-gates).

---

### 🟡 MEDIUM-5: Smoke Test 12 (База знаний) — неполный список категорий

**Файл**: `comprehensive-audit.md:254-265`

**Проблема**:
```bash
# Ожидание: architecture, services, quality, infrastructure, integrations
```

**Факт**:
```bash
$ ls -d knowledge/*/
knowledge/architecture/
knowledge/infrastructure/
knowledge/integrations/
knowledge/pipeline/
knowledge/quality/
knowledge/security/
knowledge/services/
```

❌ Отсутствуют в шаблоне: `pipeline`, `security`

**Исправление**:
```bash
echo "Категории:"
ls -d knowledge/*/ 2>/dev/null | xargs -I{} basename {}
# Ожидание: architecture, services, quality, infrastructure, integrations, pipeline, security
```

**Влияние**: Smoke Test 12 не проверяет две важные категории (pipeline, security).

---

### 🟡 MEDIUM-6: Smoke Test 13 (naming_version) — новый smoke test, но неполный

**Файл**: `comprehensive-audit.md:267-301`

**Проблема**:
Smoke Test 13 был добавлен недавно (после 2026-01-19), но он не проверяет все команды.

**Список команд для проверки**:
```bash
for cmd in analyze research plan plan-feature code validate; do
```

❌ Отсутствуют: `idea`, `feature-plan`, `generate`, `finalize`

**Факт**: Все 11 команд должны поддерживать `naming_version`:
- `init` (специальная логика — создаёт `.pipeline-state.json` с `naming_version`)
- `idea` / `analyze` (дубликаты, оба поддерживают)
- `research`
- `plan` / `feature-plan` / `plan-feature` (дубликаты)
- `generate` / `code` (дубликаты)
- `finalize` / `validate` (дубликаты)

**Исправление**:
```bash
# Проверяем ВСЕ команды (без init)
for cmd in idea analyze research plan feature-plan plan-feature generate code finalize validate; do
  if [ -f ".claude/commands/aidd-$cmd.md" ]; then
    if grep -q "naming_version" ".claude/commands/aidd-$cmd.md" 2>/dev/null; then
      echo "✅ /aidd-$cmd поддерживает naming_version"
    else
      echo "⚠️ /aidd-$cmd не упоминает naming_version"
    fi
  fi
done
```

**Влияние**: Неполная проверка (50% команд не проверяются).

---

### 🟡 MEDIUM-7: Objective 7 (Роли и команды) — упоминаются удалённые роли

**Файл**: `comprehensive-audit.md:665-753`

**Проблема**:
```bash
declare -A ROLE_STAGES=(
  ["analyst"]="1"
  ["researcher"]="2"
  ["architect"]="3"     # или planner.md (дубликат)
  ["planner"]="3"       # алиас architect
  ["implementer"]="4"   # или coder.md (дубликат)
  ["coder"]="4"         # алиас implementer
  ["validator"]="5"     # консолидирует reviewer + qa + validation
)
```

Комментарий:
```
["validator"]="5"     # консолидирует reviewer + qa + validation
```

❌ `reviewer` и `qa` — удалённые роли (консолидированы 2026-01-19), но упомянуты как существующие.

**Исправление**:
```bash
["validator"]="5"     # консолидирует 4 шага: Review → Test → Validate → Deploy
```

**Влияние**: Создаёт впечатление, что `reviewer` и `qa` ещё существуют.

---

### 🟡 MEDIUM-8: Objective 12 (Шаблоны документов) — rtm-template.md не существует

**Файл**: `comprehensive-audit.md:1003-1064`

**Проблема**:
```bash
TEMPLATES=(
  "prd-template.md:PRD:Этап 1"
  "architecture-template.md:Архитектура:Этап 3 (CREATE)"
  "feature-plan-template.md:План фичи:Этап 3 (FEATURE)"
  "implementation-plan-template.md:План реализации:Этап 3"
  "completion-report-template.md:Completion Report:Этап 5 (заменяет review/qa/validation-report)"
  "rtm-template.md:RTM:Все этапы"
  "tasklist-template.md:Список задач:Опционально"
  "pipeline-state-template.json:Состояние пайплайна:Этап 0"
)
```

❌ `rtm-template.md` не существует (см. MEDIUM-3).

**Исправление**:
```bash
TEMPLATES=(
  # ... (без rtm-template.md)
  "research-report-template.md:Research Report:Этап 2"
)

# Проверка устаревших шаблонов (не должны существовать)
DEPRECATED=(
  "review-report-template.md"
  "qa-report-template.md"
  "validation-report-template.md"
  "rtm-template.md"  # НЕ реализован
)
```

**Влияние**: Проверка будет показывать 7/8 вместо 8/8.

---

## Категория B: Семантические расхождения

### ⚪ LOW-1: Objective 1 (Таблица характеристик) — устаревшее описание пайплайна

**Файл**: `comprehensive-audit.md:334-342`

**Проблема**:
```markdown
| Пайплайн | 6 этапов (0-5), 6 ворот + 4 sub-gates (Этап 5) |
```

**Факт**: После consolidation (2026-01-19):
```
Пайплайн: 6 этапов (0-5), 6 ворот (BOOTSTRAP_READY, PRD_READY, RESEARCH_DONE,
          PLAN_APPROVED, IMPLEMENT_OK, DEPLOYED/DOCUMENTED)
```

Ворота `REVIEW_OK`, `QA_PASSED`, `ALL_GATES_PASSED` больше не являются отдельными воротами, а являются **sub-gates** этапа 5.

**Исправление**:
```markdown
| Пайплайн | 6 этапов (0-5), 6 основных ворот + 4 sub-gates (Этап 5 Full) |
```

**Влияние**: Незначительная неточность в описании.

---

### ⚪ LOW-2: Objective 6 (Таблица команд и ворот) — устаревшие команды в таблице

**Файл**: `comprehensive-audit.md:654-662`

**Проблема**:
Таблица упоминает старые команды:
```markdown
| 5 | Quality & Deploy | /aidd-finalize → /aidd-validate | validator | **Full**: REVIEW_OK → QA_PASSED → ALL_GATES_PASSED → DEPLOYED <br> **Quick**: DOCUMENTED | reports/{name}-completion.md → _validation/{name}.md |
```

**Факт**:
- Старые команды `/aidd-review`, `/aidd-test`, `/aidd-deploy` удалены
- Вместо них — единая команда `/aidd-finalize` с 4 шагами (Full) или 1 шагом (Quick)

**Исправление**:
Таблица корректна, но нужно добавить примечание:
```markdown
> **Примечание**: Этап 5 выполняется ОДНОЙ командой `/aidd-finalize` (или алиас `/aidd-validate`).
> Старые команды `/aidd-review`, `/aidd-test`, `/aidd-deploy` удалены (consolidation 2026-01-19).
```

**Влияние**: Создаёт впечатление, что ворота — это отдельные команды.

---

### ⚪ LOW-3: Objective 8 (Ворота) — комментарий о Quick режиме устарел

**Файл**: `comprehensive-audit.md:756-823`

**Проблема**:
```bash
echo "Примечание: Ворота DOCUMENTED — для Quick режима /aidd-finalize (--mode=quick)"
```

**Факт**: Quick режим НЕ требует `--mode=quick`, а определяется автоматически:
```bash
# Quick mode (явное указание)
/aidd-finalize --mode=quick

# Full mode (по умолчанию, если IMPLEMENT_OK пройден)
/aidd-finalize
```

**Исправление**:
```bash
echo "Примечание: Ворота DOCUMENTED — для Quick режима /aidd-finalize --mode=quick"
echo "           (без предусловий, создаёт DRAFT Completion Report)"
```

**Влияние**: Незначительная неточность в описании.

---

### ⚪ LOW-4: Objective 13 (База знаний) — неполный список категорий

**Файл**: `comprehensive-audit.md:1068-1115`

**Проблема**:
```bash
CATEGORIES=(
  "architecture:Архитектура и паттерны"
  "services:Шаблоны сервисов (FastAPI, Aiogram, etc.)"
  "quality:Тестирование и качество"
  "infrastructure:Docker, CI/CD, Nginx"
  "integrations:HTTP, Redis, etc."
)
```

❌ Отсутствуют: `pipeline`, `security`

**Исправление**:
```bash
CATEGORIES=(
  "architecture:Архитектура и паттерны"
  "services:Шаблоны сервисов (FastAPI, Aiogram, etc.)"
  "quality:Тестирование и качество"
  "infrastructure:Docker, CI/CD, Nginx"
  "integrations:HTTP, Redis, etc."
  "pipeline:Pipeline State, Git Integration, Gates"
  "security:Secrets Management, Local-Only Execution"
)
```

**Влияние**: Две категории не проверяются.

---

## Сводная таблица расхождений

| ID | Категория | Файл:строка | Проблема | Приоритет | Влияние |
|----|-----------|-------------|----------|-----------|---------|
| **MEDIUM-1** | Smoke Test 6 | :128-148 | Проверяет несуществующие роли `reviewer`, `qa` | MEDIUM | Smoke Test будет падать |
| **MEDIUM-2** | Smoke Test 7 | :150-170 | Комментарий упоминает `validate` как часть consolidation | MEDIUM | Вводит в заблуждение |
| **MEDIUM-3** | Smoke Test 9 | :192-212 | Проверяет несуществующий `rtm-template.md` | MEDIUM | Smoke Test будет показывать 5/6 |
| **MEDIUM-4** | Smoke Test 10 | :214-236 | Комментарий не отражает sub-gates | MEDIUM | Неточное описание |
| **MEDIUM-5** | Smoke Test 12 | :254-265 | Не проверяет `pipeline`, `security` | MEDIUM | Неполная проверка |
| **MEDIUM-6** | Smoke Test 13 | :267-301 | Не проверяет все команды (50%) | MEDIUM | Неполная проверка |
| **MEDIUM-7** | Objective 7 | :665-753 | Упоминает удалённые роли `reviewer`, `qa` | MEDIUM | Создаёт впечатление существования |
| **MEDIUM-8** | Objective 12 | :1003-1064 | Проверяет несуществующий `rtm-template.md` | MEDIUM | Проверка будет показывать 7/8 |
| **LOW-1** | Objective 1 | :334-342 | Устаревшее описание пайплайна | LOW | Незначительная неточность |
| **LOW-2** | Objective 6 | :654-662 | Нет примечания о consolidation | LOW | Создаёт впечатление, что ворота — это команды |
| **LOW-3** | Objective 8 | :756-823 | Неточный комментарий о Quick режиме | LOW | Незначительная неточность |
| **LOW-4** | Objective 13 | :1068-1115 | Не проверяет `pipeline`, `security` | LOW | Две категории не проверяются |

---

## Рекомендуемые действия

### Немедленные (сегодня)

1. **MEDIUM-1**: Обновить список ролей в Smoke Test 6
   - Удалить `reviewer`, `qa`
   - Оставить `analyst`, `researcher`, `architect`, `planner`, `implementer`, `coder`, `validator`, `code-review-library`, `testing-library`

2. **MEDIUM-3**: Удалить `rtm-template.md` из Smoke Test 9 и Objective 12
   - Добавить `research-report-template.md`

3. **MEDIUM-5**: Добавить `pipeline`, `security` в Smoke Test 12 и Objective 13

4. **MEDIUM-6**: Расширить Smoke Test 13 на все команды

### Краткосрочные (на этой неделе)

5. **MEDIUM-2**: Уточнить комментарий в Smoke Test 7
   - Упомянуть, что `validate` — алиас `finalize`, а не часть consolidation

6. **MEDIUM-4**: Добавить пояснение о sub-gates в Smoke Test 10

7. **MEDIUM-7**: Обновить комментарий в Objective 7
   - Убрать упоминание `reviewer` и `qa` как существующих ролей

8. **MEDIUM-8**: Убрать `rtm-template.md` из Objective 12

### Долгосрочные (в этом месяце)

9. **LOW-1, LOW-2, LOW-3, LOW-4**: Уточнить описания и комментарии

10. **Добавить новый Smoke Test 14**: Проверка consolidation
    - Проверить, что `/aidd-finalize` выполняет все 4 шага (Review → Test → Validate → Deploy)
    - Проверить наличие Completion Report после DEPLOYED

---

## Заключение

Шаблон комплексного аудита в целом актуален, но требует **8 среднеприоритетных** и **4 низкоприоритетных** обновлений для синхронизации с изменениями во фреймворке за последний месяц.

**Основная причина расхождений**:
- Consolidation of Stage 5 (2026-01-19) — удаление 4 команд и 2 ролей
- Migration Mode v2.4 (2026-01-19) — добавление алиасов и dual naming

**Рекомендация**: Обновить шаблон аудита **сегодня**, чтобы избежать ложных срабатываний при следующем аудите.

---

**Версия отчета**: 1.0
**Автор**: Claude (AI-агент)
**Статус**: DRAFT — требует проверки
