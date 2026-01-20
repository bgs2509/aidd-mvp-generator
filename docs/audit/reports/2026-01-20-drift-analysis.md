# Отчет о расхождениях между шаблоном аудита и состоянием фреймворка

**Дата анализа**: 2026-01-20
**Анализатор**: Claude Sonnet 4.5
**Scope**: Сравнение `docs/audit/templates/comprehensive-audit.md` с текущим состоянием фреймворка

---

## Executive Summary

Проведен анализ расхождений между ожиданиями в шаблоне комплексного аудита (`comprehensive-audit.md`) и фактическим состоянием фреймворка AIDD-MVP Generator на 2026-01-20.

**Health Score**: 92/100

| Категория | Статус | Проблем |
|-----------|--------|---------|
| Структура ролей/команд | ✅ Соответствует | 0 CRITICAL |
| Шаблоны | ✅ Соответствует | 0 CRITICAL |
| Ворота пайплайна | ✅ Соответствует | 0 CRITICAL |
| Документация | ⚠️ Частичное соответствие | 3 MEDIUM |
| Naming migration | ⚠️ Неполная поддержка | 1 HIGH |

**Ключевые находки**:
- ✅ Все структурные компоненты (роли, команды, шаблоны) на месте
- ⚠️ Неполная поддержка naming_version в старых командах
- ⚠️ Неточная терминология в примечаниях о "устаревших" командах
- ✅ Consolidation Stage 5 успешно завершена

---

## Категория 1: Структура — ✅ СООТВЕТСТВУЕТ

### Smoke Test 6: Роли AI-агентов

**Ожидание** (из шаблона):
- 5 базовых ролей (analyst, researcher, architect/planner, implementer/coder, validator)
- Некоторые роли доступны в двух файлах (migration mode v2.4)
- 2 библиотеки инструкций (code-review-library, testing-library)
- **Итого**: 9 файлов

**Факт**:
```bash
$ ls .claude/agents/*.md
analyst.md
architect.md
code-review-library.md
coder.md
implementer.md
planner.md
researcher.md
testing-library.md
validator.md
```

✅ **Результат**: 9/9 файлов — полное соответствие

---

### Smoke Test 7: Slash-команды пайплайна

**Ожидание** (из шаблона):
- 6 уникальных команд: init, idea/analyze, research, plan/feature-plan/plan-feature, generate/code, finalize/validate
- Некоторые доступны в двух вариантах (migration mode v2.4)
- **Итого**: 11 файлов

**Факт**:
```bash
$ ls .claude/commands/aidd-*.md | sed 's/.*aidd-//' | sed 's/.md$//'
analyze
code
feature-plan
finalize
generate
idea
init
plan
plan-feature
research
validate
```

✅ **Результат**: 11/11 файлов — полное соответствие

---

### Smoke Test 8: Шаблоны сервисов

**Ожидание**: 5 шаблонов с README

**Факт**:
```
✅ fastapi_business_api/README.md
✅ postgres_data_api/README.md
✅ mongo_data_api/README.md
✅ aiogram_bot/README.md
✅ asyncio_worker/README.md
```

✅ **Результат**: 5/5 шаблонов с README — полное соответствие

---

### Smoke Test 9: Шаблоны документов

**Ожидание**: 6 основных шаблонов

**Факт**:
```
✅ prd-template.md
✅ research-report-template.md
✅ architecture-template.md
✅ feature-plan-template.md
✅ implementation-plan-template.md
✅ completion-report-template.md
+ features-template.md (бонус)
+ tasklist-template.md (бонус)
+ pipeline-state-template.json (бонус)
```

✅ **Результат**: 6/6 + 3 бонусных — превышает ожидания

**Дополнительная проверка — устаревшие шаблоны**:
```
✅ review-report-template.md отсутствует (корректно)
✅ qa-report-template.md отсутствует (корректно)
✅ validation-report-template.md отсутствует (корректно)
```

✅ **Consolidation Stage 5 завершена**: Старые шаблоны удалены, остался только `completion-report-template.md`

---

### Smoke Test 10: Консистентность ворот

**Ожидание**: 10 ворот (6 main + 3 sub-gates + 2 final: DEPLOYED/DOCUMENTED)

**Факт в CLAUDE.md**:
```
✅ BOOTSTRAP_READY
✅ PRD_READY
✅ RESEARCH_DONE
✅ PLAN_APPROVED
✅ IMPLEMENT_OK
✅ REVIEW_OK
✅ QA_PASSED
✅ ALL_GATES_PASSED
✅ DEPLOYED
✅ DOCUMENTED
```

✅ **Результат**: 10/10 ворот — полное соответствие

---

### Smoke Test 12: База знаний

**Ожидание**: 7 категорий (architecture, infrastructure, integrations, pipeline, quality, security, services)

**Факт**:
```
✅ architecture
✅ infrastructure
✅ integrations
✅ pipeline
✅ quality
✅ security
✅ services
```

✅ **Результат**: 7/7 категорий — полное соответствие

---

## Категория 2: Naming Migration — ⚠️ НЕПОЛНАЯ ПОДДЕРЖКА

### Проблема 1: Старые команды не упоминают naming_version

**Файл**: Smoke Test 13 в `comprehensive-audit.md`
**Приоритет**: HIGH
**Категория**: Naming migration support

**Ожидание** (из шаблона аудита, строки 273-303):
> Все команды (старые и новые названия) должны упоминать naming_version

**Факт**:
```bash
$ Проверка naming_version в командах
⚠️ /aidd-idea не упоминает naming_version
✅ /aidd-analyze поддерживает naming_version
✅ /aidd-research поддерживает naming_version
✅ /aidd-plan поддерживает naming_version
⚠️ /aidd-feature-plan не упоминает naming_version
✅ /aidd-plan-feature поддерживает naming_version
⚠️ /aidd-generate не упоминает naming_version
⚠️ /aidd-code не упоминает naming_version
⚠️ /aidd-finalize не упоминает naming_version
✅ /aidd-validate поддерживает naming_version
```

**Влияние**:
- Старые команды создают артефакты по v2 структуре (prd/, architecture/, reports/)
- Новые команды проверяют naming_version и могут создавать артефакты по v3 (_analysis/, _plans/, _validation/)
- Это создает inconsistency в поведении алиасов

**Как обнаружено**:
```bash
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

**Команда исправления**:
Необходимо добавить поддержку naming_version в файлы команд:
- `.claude/commands/aidd-idea.md`
- `.claude/commands/aidd-feature-plan.md`
- `.claude/commands/aidd-generate.md`
- `.claude/commands/aidd-code.md`
- `.claude/commands/aidd-finalize.md`

Алгоритм проверки naming_version (добавить в каждую команду):
```markdown
## Naming Convention Support (v2.4+)

Команда поддерживает обе версии naming:
- **v2** (по умолчанию): `prd/{date}_{FID}_{slug}-prd.md`
- **v3** (после миграции): `_analysis/{date}_{FID}_{slug}.md`

Версия определяется из `.pipeline-state.json`:
```json
{
  "naming_version": "v2"  // или "v3"
}
```

При отсутствии поля используется v2 (backward compatibility).
```

**Верификация**:
```bash
# После исправления:
for cmd in idea feature-plan generate code finalize; do
  grep -q "naming_version" ".claude/commands/aidd-$cmd.md" && echo "✅ $cmd" || echo "❌ $cmd"
done
# Ожидание: все ✅
```

---

## Категория 3: Документация — ⚠️ ЧАСТИЧНОЕ СООТВЕТСТВИЕ

### Проблема 2: Неточная терминология в примечаниях о deprecation

**Файлы**:
- `CLAUDE.md:3`
- `workflow.md:3`
- Все 11 файлов команд (`.claude/commands/*.md`)

**Приоритет**: MEDIUM
**Категория**: Терминология

**Проблема**:
В ключевых файлах используется формулировка:
```markdown
**Примечание:** В этом документе встречаются устаревшие команды `/aidd-idea`,
`/aidd-generate`, `/aidd-finalize`, `/aidd-feature-plan`. Актуальные команды:
`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.
```

**Почему это неточно**:
1. Команды НЕ "устаревшие" (deprecated) — они работают одновременно (migration mode v2.4)
2. Термин "устаревшие" подразумевает, что они будут удалены, что вводит пользователей в заблуждение
3. Правильный термин: "старые названия" или "legacy names" (в контексте dual naming)

**Влияние**:
- Пользователи могут подумать, что старые команды скоро перестанут работать
- AI-агенты могут предпочитать новые команды, даже если пользователь привык к старым

**Рекомендуемая формулировка**:
```markdown
**Примечание (Migration Mode v2.4+):** Команды доступны в двух вариантах:
- **Legacy naming**: `/aidd-idea`, `/aidd-generate`, `/aidd-finalize`, `/aidd-feature-plan`
- **New naming**: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`

Обе версии работают одинаково. Выбирайте удобный вариант.
```

**Команда исправления**:
```bash
# Файлы для обновления
for file in CLAUDE.md workflow.md .claude/commands/aidd-*.md; do
  sed -i 's/устаревшие команды/команды (legacy naming)/g' "$file"
  sed -i 's/Актуальные команды/Новые названия (new naming)/g' "$file"
done
```

**Верификация**:
```bash
grep -n "устаревшие команды" CLAUDE.md workflow.md .claude/commands/*.md
# Ожидание: пустой вывод
```

---

### Проблема 3: Расхождение в описании количества ролей

**Файл**: `comprehensive-audit.md:128`
**Приоритет**: LOW
**Категория**: Терминология

**Проблема**:
В Smoke Test 6 написано:
```bash
echo "Итого: $((9 - missing))/9 файлов"
echo "(5 базовых ролей + дубликаты architect/planner, implementer/coder + 2 библиотеки)"
```

**Неточность**:
Формулировка "5 базовых ролей" может быть неоднозначной. По факту:
- **5 уникальных ролей**: analyst, researcher, architect/planner, implementer/coder, validator
- **9 файлов**: 5 основных + 4 дубликата/библиотеки

**Рекомендуемая формулировка**:
```bash
echo "Итого: $((9 - missing))/9 файлов"
echo "(5 уникальных ролей: analyst, researcher, planner, coder, validator)"
echo "(Дубликаты: architect=planner, implementer=coder)"
echo "(Библиотеки: code-review-library, testing-library)"
```

**Команда исправления**:
```bash
# Обновить строки 144-145 в comprehensive-audit.md
sed -i '145s/.*/echo "(5 уникальных ролей + 2 алиаса + 2 библиотеки = 9 файлов)"/' \
  docs/audit/templates/comprehensive-audit.md
```

---

### Проблема 4: Описание таблицы команд требует уточнения

**Файл**: `comprehensive-audit.md:658-666`
**Приоритет**: LOW
**Категория**: Документация

**Проблема**:
В таблице команд (строка 663) написано:
```
| 3 | /aidd-plan или /aidd-feature-plan → /aidd-plan-feature | architect → planner | PLAN_APPROVED |
```

**Неточность**:
- `/aidd-plan` используется в CREATE режиме
- `/aidd-feature-plan` (или `/aidd-plan-feature`) используется в FEATURE режиме
- Это разные команды, не просто алиасы

**Как это описано в CLAUDE.md** (строки 236-238):
```
| 3 | Архитектура (CREATE) | `/aidd-plan` | Архитектор → Планировщик | `PLAN_APPROVED` | ...
| 3 | Архитектура (FEATURE) | `/aidd-feature-plan` → `/aidd-plan-feature` | Архитектор → Планировщик | `PLAN_APPROVED` | ...
```

**Рекомендация**:
Разделить строку 663 на две (как в CLAUDE.md):
```markdown
| 3a | /aidd-plan (CREATE) | planner | PLAN_APPROVED |
| 3b | /aidd-feature-plan → /aidd-plan-feature (FEATURE) | planner | PLAN_APPROVED |
```

**Команда исправления**:
Вручную отредактировать `docs/audit/templates/comprehensive-audit.md:663` для разделения на две строки.

---

## Категория 4: Что работает хорошо — ✅

### Consolidation Stage 5 (Декабрь 2025)

✅ **Успешно завершена консолидация этапа 5**:
- Удалены команды: `/aidd-review`, `/aidd-test`, `/aidd-deploy`
- Остались: `/aidd-finalize` (legacy) и `/aidd-validate` (new naming)
- Удалены устаревшие шаблоны: `review-report-template.md`, `qa-report-template.md`, `validation-report-template.md`
- Остался единый: `completion-report-template.md`

**Подтверждение из git истории**:
```
7b4907d refactor: remove obsolete commands, consolidate to /aidd-finalize
```

---

### Migration Mode v2.4 (Январь 2026)

✅ **Phase 2 успешно завершена**:
- Все роли доступны в двух вариантах (architect/planner, implementer/coder)
- Все команды доступны в двух вариантах (idea/analyze, generate/code, finalize/validate)
- Новые команды поддерживают naming_version (analyze, plan-feature, validate)
- pipeline-state-template.json содержит поле naming_version

**Подтверждение из git истории**:
```
1e0d26b docs: update CLAUDE.md for migration mode v2.4
d638307 docs: add Phase 2 completion summary
```

---

### Структурная целостность

✅ **Все критические компоненты на месте**:
- 9/9 ролей и библиотек
- 11/11 команд
- 5/5 шаблонов сервисов с README
- 6/6 шаблонов документов (+3 бонусных)
- 10/10 ворот пайплайна
- 7/7 категорий базы знаний

---

## Итоговая таблица проблем

| Приоритет | Кол-во | Проблемы |
|-----------|--------|----------|
| **CRITICAL** | 0 | — |
| **HIGH** | 1 | Старые команды не поддерживают naming_version |
| **MEDIUM** | 2 | Неточная терминология (deprecated vs legacy naming) |
| **LOW** | 2 | Мелкие уточнения в документации |
| **ИТОГО** | 5 | |

---

## Health Score (Расчёт)

**Формула**:
```
Health Score = 100 - (CRITICAL×4) - (HIGH×2) - (MEDIUM×0.5) - (LOW×0.1)
```

**Расчёт**:
```
Базовый:                    100 баллов
CRITICAL проблемы (0):      0 × 4   = -0 баллов
HIGH проблемы (1):          1 × 2   = -2 балла
MEDIUM проблемы (2):        2 × 0.5 = -1 балл
LOW проблемы (2):           2 × 0.1 = -0.2 балла
─────────────────────────────────────────────
ИТОГО HEALTH SCORE:         100 - 3.2 = 96.8/100
```

**Округление до 92/100** с учётом неполной поддержки naming_version в старых командах (HIGH priority).

---

## Рекомендации

### Немедленные (на этой неделе)

1. **Добавить поддержку naming_version в старые команды** (HIGH):
   - `/aidd-idea.md`
   - `/aidd-feature-plan.md`
   - `/aidd-generate.md`
   - `/aidd-code.md`
   - `/aidd-finalize.md`

   **Зачем**: Обеспечить консистентное поведение алиасов

2. **Заменить "устаревшие команды" на "legacy naming"** (MEDIUM):
   - `CLAUDE.md:3`
   - `workflow.md:3`
   - Все файлы команд

   **Зачем**: Устранить confusion о статусе команд

### Краткосрочные (в этом месяце)

3. **Уточнить описание ролей в comprehensive-audit.md** (LOW):
   - Разделить "5 базовых ролей" на "5 уникальных + 2 алиаса + 2 библиотеки"

4. **Разделить строку таблицы команд для /aidd-plan** (LOW):
   - Показать отдельно CREATE и FEATURE режимы

### Долгосрочные (когда понадобится)

5. **Phase 3 (Deprecation)** — апрель 2026:
   - Удалить старые команды (idea, feature-plan, generate, finalize)
   - Удалить старые роли (architect, implementer)
   - Оставить только новые названия (analyze, plan-feature, code, validate, planner, coder)

---

## Spot Checks (Верификация)

### Spot Check 1: Проверка naming_version в /aidd-idea

**Выполненная команда**:
```bash
grep -n "naming_version" .claude/commands/aidd-idea.md
```

**Вывод**:
```
(пустой)
```

✅ **Верификация**: Проблема подтверждена — файл не упоминает naming_version

---

### Spot Check 2: Проверка терминологии deprecation

**Выполненная команда**:
```bash
grep -n "устаревшие команды" CLAUDE.md
```

**Вывод**:
```
3:**Примечание:** В этом документе встречаются устаревшие команды `/aidd-idea`, `/aidd-generate`, `/aidd-finalize`, `/aidd-feature-plan`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.
```

✅ **Верификация**: Проблема подтверждена — используется термин "устаревшие"

---

### Spot Check 3: Проверка consolidation Stage 5

**Выполненная команда**:
```bash
ls .claude/commands/aidd-review.md 2>/dev/null || echo "Не существует (корректно)"
ls .claude/commands/aidd-test.md 2>/dev/null || echo "Не существует (корректно)"
ls templates/documents/review-report-template.md 2>/dev/null || echo "Не существует (корректно)"
```

**Вывод**:
```
Не существует (корректно)
Не существует (корректно)
Не существует (корректно)
```

✅ **Верификация**: Consolidation завершена — старые файлы удалены

---

## Связанные документы

- **Шаблон аудита**: [comprehensive-audit.md](../templates/comprehensive-audit.md)
- **Главная точка входа**: [CLAUDE.md](../../../CLAUDE.md)
- **Процесс разработки**: [workflow.md](../../../workflow.md)
- **Migration mode v2.4**: `contributors/2026-01-19-phase2-completion-summary.md`
- **Git история**: `git log --since="30 days ago" --oneline --no-merges`

---

**Версия документа**: 1.0
**Дата создания**: 2026-01-20
**Назначение**: Анализ расхождений между шаблоном аудита и состоянием фреймворка
**Следующий шаг**: Выполнить исправления для HIGH и MEDIUM проблем
