# Enhancement: Command Execution Enforcement Mechanism

**Date**: 2026-01-14
**Author**: AI Agent
**Type**: Enhancement Request
**Status**: PROPOSED
**Component**: `.aidd/CLAUDE.md`, `.aidd/.claude/commands/*.md`

---

## 1. Problem Description

### Observed Behavior

При выполнении команд `/aidd-*` AI-агент может пропускать обязательные шаги,
особенно "документационные" (создание отчётов, обновление артефактов).

### Root Cause Analysis

1. **Выборочное чтение**: AI читает файл команды частично, фокусируясь на
   "технических" шагах (docker build, code generation) и пропуская
   "документационные" (создание Completion Report, обновление RTM).

2. **Отсутствие трекинга**: AI не использует TodoWrite для систематического
   отслеживания всех шагов чеклиста.

3. **Неявные требования**: Чеклисты ворот есть в `workflow.md`, но не
   продублированы явно в файлах команд.

### Evidence: F007 Incident (2026-01-14)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ИНЦИДЕНТ: Пропуск Completion Report при /aidd-deploy F007              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ЧТО ПРОИЗОШЛО:                                                         │
│  1. AI выполнил /aidd-deploy F007                                       │
│  2. Docker контейнеры собраны ✅                                        │
│  3. Приложение запущено ✅                                              │
│  4. Health check пройден ✅                                             │
│  5. Completion Report НЕ создан ❌                                      │
│  6. Пользователь обнаружил пропуск вручную                              │
│                                                                         │
│  ПРИЧИНА:                                                               │
│  AI прочитал deploy.md выборочно — только секции с docker командами,    │
│  пропустив секцию "Создание Completion Report" (строки 202-210)         │
│                                                                         │
│  ПОСЛЕДСТВИЯ:                                                           │
│  - Артефакт пришлось создавать вручную                                  │
│  - Потеря времени пользователя                                          │
│  - Нарушение целостности документации                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Proposed Solution

### Core Mechanism: Mandatory Checklist Execution

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ПЕРЕД ЗАВЕРШЕНИЕМ ЛЮБОЙ КОМАНДЫ /aidd-* AI ОБЯЗАН:                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. ПРОЧИТАТЬ ВЕСЬ файл команды .aidd/.claude/commands/{cmd}.md         │
│     (не только технические шаги, но и секции документирования)          │
│                                                                         │
│  2. НАЙТИ секцию "Чеклист" или "Критерии прохождения ворот"             │
│                                                                         │
│  3. СОЗДАТЬ TodoWrite со ВСЕМИ пунктами чеклиста                        │
│                                                                         │
│  4. ВЫПОЛНИТЬ каждый пункт и отметить completed                         │
│                                                                         │
│  5. ТОЛЬКО ПОСЛЕ выполнения ВСЕХ пунктов — завершить команду            │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  ❌ ЗАПРЕЩЕНО: Считать команду завершённой если чеклист не выполнен     │
│  ❌ ЗАПРЕЩЕНО: Пропускать "документационные" шаги (reports, completion) │
└─────────────────────────────────────────────────────────────────────────┘
```

### Implementation Details

#### 2.1 Add to `.aidd/CLAUDE.md`

Добавить новую секцию "Критические правила выполнения команд":

```markdown
## Критические правила выполнения команд /aidd-*

> **Добавлено**: 2026-01-14 после инцидента F007

### Обязательный алгоритм

1. **Чтение команды**: Прочитать ВЕСЬ файл `.aidd/.claude/commands/{cmd}.md`
2. **Поиск чеклиста**: Найти секцию "Чеклист" или "Критерии ворот"
3. **TodoWrite**: Создать todo list со всеми пунктами
4. **Выполнение**: Последовательно выполнить каждый пункт
5. **Завершение**: Команда завершена только когда ВСЕ пункты ✅

### Запрещено

- Считать команду завершённой при невыполненном чеклисте
- Пропускать "документационные" шаги
- Выборочно читать файлы команд
```

#### 2.2 Add Explicit Checklists to Command Files

Каждый файл в `.aidd/.claude/commands/` должен содержать явный чеклист в конце:

**Пример для `aidd-deploy.md`:**

```markdown
## Чеклист ворот DEPLOYED

> ⚠️ AI ОБЯЗАН создать TodoWrite с этими пунктами и выполнить ВСЕ.

- [ ] Docker-контейнеры собраны
- [ ] Приложение запущено
- [ ] Health-check проходит
- [ ] Базовые сценарии работают
- [ ] **Completion Report создан** ← ОБЯЗАТЕЛЬНО!
- [ ] **Completion Report добавлен в artifacts**
- [ ] `.pipeline-state.json` обновлён (stage, gates, artifacts)
- [ ] Фича перенесена в `features_registry`
```

**Пример для `aidd-validate.md`:**

```markdown
## Чеклист ворот ALL_GATES_PASSED

- [ ] RTM (Requirements Traceability Matrix) создан
- [ ] Все требования FR-* покрыты тестами
- [ ] Coverage ≥ 75%
- [ ] Все предыдущие ворота пройдены
- [ ] `.pipeline-state.json` обновлён
```

#### 2.3 Add Reminder Header to Each Command File

В начало каждого файла команды добавить:

```markdown
> ⚠️ **ENFORCEMENT**: Перед завершением этой команды AI ОБЯЗАН:
> 1. Найти секцию "Чеклист" в конце файла
> 2. Создать TodoWrite со всеми пунктами
> 3. Выполнить ВСЕ пункты
> См. CLAUDE.md → "Критические правила выполнения команд"
```

---

## 3. Files to Modify

| File | Change | Priority |
|------|--------|----------|
| `.aidd/CLAUDE.md` | Add "Критические правила выполнения команд" section | HIGH |
| `.aidd/.claude/commands/aidd-deploy.md` | Add explicit DEPLOYED checklist + header | HIGH |
| `.aidd/.claude/commands/aidd-validate.md` | Add explicit ALL_GATES_PASSED checklist + header | HIGH |
| `.aidd/.claude/commands/aidd-review.md` | Add explicit REVIEW_OK checklist + header | MEDIUM |
| `.aidd/.claude/commands/aidd-test.md` | Add explicit QA_PASSED checklist + header | MEDIUM |
| `.aidd/.claude/commands/aidd-generate.md` | Add explicit IMPLEMENT_OK checklist + header | MEDIUM |
| `.aidd/.claude/commands/aidd-plan.md` | Add explicit PLAN_APPROVED checklist + header | MEDIUM |
| `.aidd/.claude/commands/aidd-feature-plan.md` | Add explicit PLAN_APPROVED checklist + header | MEDIUM |
| `.aidd/.claude/commands/aidd-research.md` | Add explicit RESEARCH_DONE checklist + header | LOW |
| `.aidd/.claude/commands/aidd-idea.md` | Add explicit PRD_READY checklist + header | LOW |

---

## 4. Expected Outcomes

### Before (Current Behavior)

```
AI выполняет /aidd-deploy:
1. Читает docker секции ✅
2. Собирает контейнеры ✅
3. Запускает приложение ✅
4. Обновляет state ✅
5. (Пропускает Completion Report) ❌
6. "Команда завершена" — НЕВЕРНО
```

### After (With Enforcement)

```
AI выполняет /aidd-deploy:
1. Читает ВЕСЬ файл deploy.md ✅
2. Находит чеклист ворот DEPLOYED ✅
3. Создаёт TodoWrite с 8 пунктами ✅
4. Выполняет:
   - [ ] Docker-контейнеры собраны → [x] ✅
   - [ ] Приложение запущено → [x] ✅
   - [ ] Health-check проходит → [x] ✅
   - [ ] Completion Report создан → [x] ✅  ← НЕ ПРОПУЩЕН!
   - ...
5. ВСЕ пункты выполнены → "Команда завершена" ✅
```

---

## 5. Metrics

| Metric | Before | After (Expected) |
|--------|--------|------------------|
| Пропущенные артефакты | ~10-20% | <1% |
| Неполные чеклисты | Частые | Редкие |
| Повторные запросы от пользователя | Частые | Минимальные |
| Время на исправление пропусков | ~15 мин/инцидент | 0 |

---

## 6. Risks and Mitigation

| Risk | Mitigation |
|------|------------|
| Увеличение длины файлов команд | Чеклисты компактные (5-10 строк) |
| AI игнорирует новые правила | Добавить в CLAUDE.md как "Критическое правило" |
| Дублирование с workflow.md | Sync-скрипт или ссылки вместо копирования |

---

## 7. Action Items

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | Document enhancement in contributors/ | AI | ✅ Done |
| 2 | Implement in target project CLAUDE.md | AI | ✅ Done (Prognosis) |
| 3 | Add to framework CLAUDE.md | Framework maintainer | ⏳ Pending |
| 4 | Add checklists to all command files | Framework maintainer | ⏳ Pending |
| 5 | Add enforcement headers to command files | Framework maintainer | ⏳ Pending |

---

## 8. References

- **Incident**: F007 Completion Report skip (2026-01-14)
- **Target project fix**: `Prognosis/CLAUDE.md` v1.1
- **Related issue**: `2026-01-13-aidd-issue-completion-report-gap.md`
- **workflow.md**: Gate criteria definitions (lines 444-470)
- **deploy.md**: Completion Report instructions (lines 202-210)

---

## 9. Appendix: Full Enforcement Rule Text

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚠️ КРИТИЧЕСКОЕ ПРАВИЛО: Выполнение команд /aidd-*                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ПЕРЕД ЗАВЕРШЕНИЕМ ЛЮБОЙ КОМАНДЫ /aidd-* AI ОБЯЗАН:                     │
│                                                                         │
│  1. ПРОЧИТАТЬ ВЕСЬ файл команды .aidd/.claude/commands/{cmd}.md         │
│     (не только технические шаги, но и секции документирования)          │
│                                                                         │
│  2. НАЙТИ секцию "Чеклист" или "Критерии прохождения ворот"             │
│                                                                         │
│  3. СОЗДАТЬ TodoWrite со ВСЕМИ пунктами чеклиста                        │
│                                                                         │
│  4. ВЫПОЛНИТЬ каждый пункт и отметить completed                         │
│                                                                         │
│  5. ТОЛЬКО ПОСЛЕ выполнения ВСЕХ пунктов — завершить команду            │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  ❌ ЗАПРЕЩЕНО: Считать команду завершённой если чеклист не выполнен     │
│  ❌ ЗАПРЕЩЕНО: Пропускать "документационные" шаги (reports, completion) │
└─────────────────────────────────────────────────────────────────────────┘

### Lesson Learned: F007 (2026-01-14)

При выполнении `/aidd-deploy F007` был пропущен Completion Report:
- AI прочитал только "технические" шаги (docker build/up)
- AI не прочитал секцию "Создание Completion Report"
- AI не использовал TodoWrite для трекинга чеклиста

Результат: Пользователь обнаружил отсутствие артефакта вручную.
```
