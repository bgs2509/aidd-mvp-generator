# Отчет о текущих расхождениях: Шаблон комплексного аудита vs Фреймворк

**Дата анализа**: 2026-01-20 (повторный после исправлений)
**Версия фреймворка**: После коммита `807fd2e`
**Версия шаблона**: `docs/audit/templates/comprehensive-audit.md`
**Анализируемый период**: 2025-12-20 — 2026-01-20

---

## Executive Summary

После применения исправлений из предыдущего drift analysis (коммиты `889c3cd`, `49258bd`) большинство **структурных расхождений устранено**. Однако обнаружены **3 оставшиеся проблемы**:

| Приоритет | Кол-во | Категория |
|-----------|--------|-----------|
| **CRITICAL** | 1 | Документация (некорректное примечание) |
| **MEDIUM** | 2 | Шаблоны (несоответствие проверок) |
| **LOW** | 0 | — |

**Health Score шаблона**: **100 - (1×4) - (2×2) = 92/100**

---

## Что было успешно исправлено ✅

### 1. Smoke Test 6 (Роли) — ИСПРАВЛЕНО
- Список ролей обновлён с учётом consolidation
- Удалены упоминания `reviewer.md` и `qa.md`
- Корректно описаны 9 файлов: 5 базовых ролей + 2 алиаса + 2 библиотеки

### 2. Smoke Test 7 (Команды) — ИСПРАВЛЕНО
- Список команд корректен (11 файлов)
- Добавлено пояснение о consolidation Stage 5

### 3. Smoke Test 9 (Шаблоны базовые) — ЧАСТИЧНО ИСПРАВЛЕНО
- Удалён несуществующий `rtm-template.md`
- Добавлен `research-report-template.md`
- **НО**: Проверяет только 6 шаблонов, фактически их 11 (см. проблему M-SMOKE-1 ниже)

### 4. Smoke Test 12 (База знаний) — ИСПРАВЛЕНО
- Добавлены категории `pipeline` и `security`
- Корректное ожидание: 7 категорий

### 5. Smoke Test 13 (naming_version) — ИСПРАВЛЕНО
- Проверяются все 10 команд (кроме init)
- Корректно описан migration mode v2.4

### 6. Objective 8 (Ворота) — ИСПРАВЛЕНО
- Список всех 10 ворот полный и корректный

### 7. Objective 12 (Шаблоны документов) — ЧАСТИЧНО ИСПРАВЛЕНО
- Добавлены `tasklist-template.md` и `pipeline-state-template.json`
- **НО**: Отсутствует `features-template.md` (см. проблему M-TEMPLATE-1 ниже)

---

## Оставшиеся проблемы

### 🔴 C-DOCS-1 (CRITICAL): Некорректное примечание о "устаревших" командах

**Файл**: `comprehensive-audit.md:3`

**Проблема**:
```markdown
**Примечание:** В этом документе встречаются устаревшие команды `/aidd-analyze`,
`/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Актуальные команды:
`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.
```

**Почему это CRITICAL**:
- Примечание **некорректно** называет команды "устаревшими"
- В migration mode v2.4 **ОБЕ версии команд работают одинаково**
- Создаёт ложное впечатление, что старые команды скоро будут удалены
- Вводит в заблуждение пользователей и AI-агентов

**Факт**:
```
Migration Mode v2.4 (активен до Phase 3, апрель 2026):
- /aidd-analyze и /aidd-analyze — оба работают идентично
- /aidd-code и /aidd-code — оба работают идентично
- /aidd-validate и /aidd-validate — оба работают идентично
- /aidd-plan-feature и /aidd-plan-feature — оба работают идентично
```

**Исправление**:
```markdown
**Примечание (Migration Mode v2.4):** Фреймворк поддерживает обе версии команд —
legacy naming (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`)
и new naming (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`)
работают идентично. Используйте любой вариант.
```

**Команда исправления**:
```bash
sed -i '3s/устаревшие команды/обе версии команд — legacy naming/' \
  docs/audit/templates/comprehensive-audit.md
sed -i '3s/Актуальные команды:/и new naming/' \
  docs/audit/templates/comprehensive-audit.md
sed -i '3s/$/ работают идентично/' \
  docs/audit/templates/comprehensive-audit.md
```

**Верификация**:
```bash
head -5 docs/audit/templates/comprehensive-audit.md | grep "Migration Mode"
# Ожидание: Примечание упоминает "Migration Mode" и "работают идентично"
```

**Влияние**: Пользователи могут избегать "устаревших" команд, хотя они полностью поддерживаются.

---

### 🟡 M-SMOKE-1 (MEDIUM): Smoke Test 9 проверяет только 6 базовых шаблонов из 11

**Файл**: `comprehensive-audit.md:192-212`

**Проблема**:
Smoke Test 9 проверяет **минимальный набор** (6 шаблонов):
```bash
TEMPLATES=(prd-template.md research-report-template.md architecture-template.md \
           feature-plan-template.md implementation-plan-template.md \
           completion-report-template.md)
```

**Факт** (11 файлов в `templates/documents/`):
```bash
$ ls templates/documents/
architecture-template.md          ← Smoke Test 9 ✓
completion-report-template.md     ← Smoke Test 9 ✓
feature-plan-template.md          ← Smoke Test 9 ✓
features-template.md              ← НЕ проверяется ❌
implementation-plan-template.md   ← Smoke Test 9 ✓
pipeline-state-template.json      ← НЕ проверяется ❌
prd-template.md                   ← Smoke Test 9 ✓
README.md                         ← НЕ проверяется ❌
research-report-template.md       ← Smoke Test 9 ✓
tasklist-template.md              ← НЕ проверяется ❌
template-map.md                   ← НЕ проверяется ❌
```

**Несоответствие**:
- **Smoke Test 9** (быстрая проверка): 6 шаблонов
- **Objective 12** (полная проверка): 8 шаблонов (`tasklist`, `pipeline-state.json` включены)
- **Фактически**: 11 файлов (`features-template.md`, `README.md`, `template-map.md` не проверяются вообще)

**Исправление**:

**Вариант 1** (рекомендуется): Явно описать, что Smoke Test 9 — базовый набор:
```bash
# Smoke Test 9: Минимальный набор (6 основных шаблонов)
TEMPLATES=(prd-template.md research-report-template.md architecture-template.md \
           feature-plan-template.md implementation-plan-template.md \
           completion-report-template.md)
count=0
for tpl in "${TEMPLATES[@]}"; do
  # ... проверка ...
done
echo "Итого: $count/6 основных шаблонов"
echo "(Полная проверка всех 11 файлов в Objective 12)"
```

**Вариант 2**: Добавить все 11 файлов в Smoke Test 9:
```bash
TEMPLATES=(prd-template.md research-report-template.md architecture-template.md \
           feature-plan-template.md features-template.md \
           implementation-plan-template.md completion-report-template.md \
           tasklist-template.md pipeline-state-template.json \
           README.md template-map.md)
```

**Влияние**: Smoke Test 9 не обнаружит отсутствие 5 файлов (если они будут удалены).

---

### 🟡 M-TEMPLATE-1 (MEDIUM): features-template.md существует, но не упоминается

**Файл**: `comprehensive-audit.md:1022-1043` (Objective 12)

**Проблема**:
`features-template.md` существует в `templates/documents/`, но не упоминается ни в одной проверке.

**Факт**:
```bash
$ head -10 templates/documents/features-template.md
# Реестр фич проекта

> Автоматически обновляется при создании/завершении фич.
> Последнее обновление: {YYYY-MM-DD}
```

Это **Feature Registry** — автоматически обновляемый список всех фич в проекте.

**Исправление** (добавить в Objective 12):
```bash
TEMPLATES=(
  "prd-template.md:PRD:Этап 1"
  "research-report-template.md:Research Report:Этап 2"
  "architecture-template.md:Архитектура:Этап 3 (CREATE)"
  "feature-plan-template.md:План фичи:Этап 3 (FEATURE)"
  "features-template.md:Реестр фич:Автоматический"  # ← ДОБАВИТЬ
  "implementation-plan-template.md:План реализации:Этап 3"
  "completion-report-template.md:Completion Report:Этап 5"
  "tasklist-template.md:Список задач:Опционально"
  "pipeline-state-template.json:Состояние пайплайна:Этап 0"
)
```

**Команда исправления**:
```bash
# Найти строку с implementation-plan-template.md и добавить features-template.md перед ней
sed -i '/implementation-plan-template.md/i\  "features-template.md:Реестр фич:Автоматический"' \
  docs/audit/templates/comprehensive-audit.md
```

**Верификация**:
```bash
grep -n "features-template" docs/audit/templates/comprehensive-audit.md
# Ожидание: Найдена строка в Objective 12
```

**Влияние**: Аудит не проверяет наличие Feature Registry (новый артефакт).

---

## Статистика изменений

### Коммиты с исправлениями (последние 2 недели)

```bash
807fd2e docs(audit): update drift analysis with applied fixes
889c3cd fix(docs): resolve C-DOCS-1 and M-CLAUDE-1 from drift analysis
2a5413e docs(audit): add drift analysis report for comprehensive-audit template
49258bd fix(docs): address all drift analysis issues
caa2c6c docs(audit): sync comprehensive-audit template with framework changes
```

### Исправлено проблем: 9 из 12

| Категория | Было | Исправлено | Осталось |
|-----------|------|------------|----------|
| Структурные (Smoke Tests) | 6 | 5 | 1 (M-SMOKE-1) |
| Семантические (Objectives) | 4 | 3 | 1 (M-TEMPLATE-1) |
| Документация | 2 | 1 | 1 (C-DOCS-1) |
| **ИТОГО** | **12** | **9** | **3** |

---

## Рекомендации

### Немедленно (сегодня)

1. **Исправить C-DOCS-1** — примечание о "устаревших" командах вводит в заблуждение

### Краткосрочно (на этой неделе)

2. **Решить M-SMOKE-1** — выбрать стратегию: базовый набор (6) или полный (11)
3. **Исправить M-TEMPLATE-1** — добавить `features-template.md` в Objective 12

### Долгосрочно (к Phase 3, апрель 2026)

4. **Обновить примечание** после Phase 3 (Deprecation) — когда старые команды будут действительно удалены

---

## Итоговая оценка

| Метрика | Значение |
|---------|----------|
| **Health Score шаблона** | **92/100** |
| Критические проблемы | 1 (вводящее в заблуждение примечание) |
| Проблемы средней важности | 2 (неполные проверки) |
| Низкоприоритетные | 0 |
| **Статус** | ✅ Готов к использованию с минорными улучшениями |

**Вывод**: Шаблон комплексного аудита **готов к использованию**, но требует трёх финальных исправлений для полного соответствия текущему состоянию фреймворка.

---

## Spot Checks (Верификация реальности проблем)

### Spot Check 1: Проверка примечания (C-DOCS-1)

**Выполненная команда**:
```bash
head -5 docs/audit/templates/comprehensive-audit.md
```

**Вывод**:
```
# Шаблон комплексного аудита документации AIDD-MVP Generator

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-analyze`,
`/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Актуальные команды:
`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.
```

**Верификация**: ✅ Проблема подтверждена — слово "устаревшие" некорректно.

---

### Spot Check 2: Проверка Smoke Test 9 (M-SMOKE-1)

**Выполненная команда**:
```bash
sed -n '196,210p' docs/audit/templates/comprehensive-audit.md
```

**Вывод**:
```bash
TEMPLATES=(prd-template.md research-report-template.md architecture-template.md \
           feature-plan-template.md implementation-plan-template.md \
           completion-report-template.md)
```

**Верификация**: ✅ Проблема подтверждена — 6 шаблонов, но фактически 11 файлов.

---

### Spot Check 3: Проверка features-template.md (M-TEMPLATE-1)

**Выполненная команда**:
```bash
ls -1 templates/documents/ | grep features
```

**Вывод**:
```
features-template.md
```

**Верификация**: ✅ Проблема подтверждена — файл существует, но не упоминается в аудите.

---

**Дата составления**: 2026-01-20
**Автор**: Claude Sonnet 4.5
**Статус**: Итоговый отчёт после применения исправлений
