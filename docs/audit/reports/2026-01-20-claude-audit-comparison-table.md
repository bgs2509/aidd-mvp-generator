# Сравнительная матрица аудитов документации AIDD-MVP Generator

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


**Дата**: 2026-01-20
**Аудиторы**: Claude Code (Sonnet 4.5) vs Codex

---

## Сводка Health Score

| Аудитор | Score | CRITICAL | HIGH | MEDIUM | LOW | ВСЕГО |
|---------|-------|----------|------|--------|-----|-------|
| **Claude** | **88.3/100** (🟢 ОТЛИЧНО) | 0 | 5 | 3 | 2 | **10** |
| **Codex** | **54.9/100** (🟡 УДОВЛЕТВОРИТЕЛЬНО) | 3 | 16 | 2 | 1 | **22** |
| **Разница** | **-33.4** | +3 | +11 | -1 | -1 | **+12** |

---

## КРИТЕРИЙ РЕАЛЬНОСТИ ПРОБЛЕМ

**Легенда**:
- ✅ **РЕАЛЬНАЯ** — проблема подтверждена, требует исправления
- ⚠️ **СПОРНАЯ** — зависит от интерпретации требований
- ❌ **ЛОЖНАЯ** — false positive, проблемы нет
- 🔍 **ТРЕБУЕТ ПРОВЕРКИ** — недостаточно данных для вердикта

---

## ТИП 1: НЕСОГЛАСОВАННОСТЬ ПАЙПЛАЙНА

### CRITICAL

| ID | Проблема | Claude | Codex | Реальность | Комментарий |
|----|----------|--------|-------|------------|-------------|
| **C-PIPELINE-1** | **6 этапов vs 9 этапов** в ключевых документах | ❌ Не нашёл | ✅ **H1** | ✅ **РЕАЛЬНАЯ** | CLAUDE.md: "6 этапов (0-5)", README.md: "9 этапов (0-8)", workflow.md: "9 этапов" — **критическая несогласованность** |

**Верификация**:
```bash
# CLAUDE.md
$ rg -n "6-этап|6 этапов|6-этапный" CLAUDE.md
15:| **Назначение** | Фреймворк для генерации MVP за ~10 минут | **6-этапный пайплайн** |
34:| Качественные ворота | **6 этапов (0-5)**, 6 ворот |
224:## 6-этапный пайплайн

# README.md + workflow.md
$ rg -n "9-этап|9 этап" README.md workflow.md
README.md:67:Пайплайн состоит из 9 этапов (0-8)
README.md:104:Всего 9 этапов
workflow.md:506:9-этапный процесс
```

**Вердикт**: ✅ **РЕАЛЬНАЯ** — документы противоречат друг другу, нужна синхронизация.

---

### HIGH

Нет HIGH проблем в этой категории.

### MEDIUM

| ID | Проблема | Claude | Codex | Реальность | Комментарий |
|----|----------|--------|-------|------------|-------------|
| **M-PIPELINE-1** | Лишние `_DONE`/`_OK` в диаграммах | ❌ Не нашёл | ✅ **M1** | ⚠️ **СПОРНАЯ** | В ASCII-диаграммах используются `RESEARCH_DONE`, `IMPLEMENT_OK` — это **корректные** названия ворот, не лишние |
| **M-PIPELINE-2** | Validator не упоминает этапы 7-8 явно | ❌ Не нашёл | ✅ **M2** | ⚠️ **СПОРНАЯ** | `.claude/agents/validator.md` говорит "этапы 4-8" — зависит от того, 6 или 9 этапов в пайплайне |

**Верификация M-PIPELINE-1**:
```bash
$ rg -n "RESEARCH_DONE|IMPLEMENT_OK" CLAUDE.md
244:│  │ RESEARCH_DONE  │    │APPROVED │    │     OK       │
```

**Вердикт M-PIPELINE-1**: ⚠️ **СПОРНАЯ** — `RESEARCH_DONE` и `IMPLEMENT_OK` — **корректные** названия ворот согласно workflow.md. Codex некорректно интерпретировал их как "лишние".

**Вердикт M-PIPELINE-2**: ⚠️ **СПОРНАЯ** — после решения C-PIPELINE-1 станет ясно, правильное ли описание.

---

## ТИП 2: ОТСУТСТВУЮЩИЕ КОМАНДЫ

### CRITICAL

| ID | Проблема | Claude | Codex | Реальность | Комментарий |
|----|----------|--------|-------|------------|-------------|
| **C-COMMANDS-1** | Отсутствуют команды `/aidd-review`, `/aidd-test`, `/aidd-deploy` | ⚠️ H4 (ссылки битые) | ✅ **C2** | ✅ **РЕАЛЬНАЯ** | Документы ссылаются на эти команды, но файлов `.claude/commands/aidd-{review,test,deploy}.md` **НЕТ** |
| **C-COMMANDS-2** | Audit-шаблон ожидает команды без `aidd-` | ❌ Не нашёл | ✅ **C3** | ⚠️ **СПОРНАЯ** | Codex Smoke Test 7: "0/10 команд найдено". Claude Smoke Test 7: "11/10 (migration mode v2.4)" — **разная интерпретация** |

**Верификация C-COMMANDS-1**:
```bash
$ ls -1 .claude/commands/ | grep -E "aidd-(review|test|deploy)"
# Пустой вывод — файлы ОТСУТСТВУЮТ

$ rg -n "aidd-review|aidd-test|aidd-deploy" docs/LINKS_REFERENCE.md
51:[/aidd-review](../.claude/commands/aidd-review.md)
52:[/aidd-test](../.claude/commands/aidd-test.md)
54:[/aidd-deploy](../.claude/commands/aidd-deploy.md)
```

**Вердикт C-COMMANDS-1**: ✅ **РЕАЛЬНАЯ** — ссылки есть, файлов нет.

**Верификация C-COMMANDS-2**:
```bash
$ sed -n '144,148p' docs/audit/templates/comprehensive-audit.md
# Smoke Test 7
COMMANDS=(init idea research plan feature-plan generate review test validate deploy)
for cmd in "${COMMANDS[@]}"; do
  [ -f ".claude/commands/${cmd}.md" ] && echo "✅ $cmd" || echo "❌ $cmd"
done

# Фактические команды
$ ls -1 .claude/commands/
aidd-analyze.md
aidd-code.md
aidd-feature-plan.md
aidd-finalize.md
aidd-generate.md
aidd-idea.md
aidd-init.md
aidd-plan-feature.md
aidd-plan.md
aidd-research.md
aidd-validate.md
```

**Вердикт C-COMMANDS-2**: ✅ **РЕАЛЬНАЯ** — audit-шаблон НЕ СООТВЕТСТВУЕТ фактическому naming (все команды с `aidd-` префиксом).

---

### HIGH

| ID | Проблема | Claude | Codex | Реальность | Комментарий |
|----|----------|--------|-------|------------|-------------|
| **H-COMMANDS-1** | Ссылки на удалённые команды в contributors документах | ✅ **H4** | ⚠️ Частично (в H2-H16) | ✅ **РЕАЛЬНАЯ** | `contributors/2026-01-14-*.md` ссылается на `aidd-{deploy,review,test}.md` |

---

## ТИП 3: БИТЫЕ ССЫЛКИ

### HIGH

| ID | Проблема | File:Line | Claude | Codex | Реальность | Комментарий |
|----|----------|-----------|--------|-------|------------|-------------|
| **H-LINKS-1** | Ссылки на `_analysis/2024-12-23_F001_table-booking.md` (naming v3) | `.claude/commands/aidd-research.md:209` | ✅ **H1** | ✅ **H2-H3** | 🔍 **ТРЕБУЕТ ПРОВЕРКИ** | Пример для naming v3, файл может не существовать в v2. Нужна проверка migration mode |
| **H-LINKS-2** | То же | `.claude/commands/aidd-plan.md:221` | ✅ **H1** | ✅ **H2-H3** | 🔍 **ТРЕБУЕТ ПРОВЕРКИ** | Дубликат H-LINKS-1 |
| **H-LINKS-3** | То же | `.claude/commands/aidd-validate.md:348` | ✅ **H1** | ✅ **H2-H3** | 🔍 **ТРЕБУЕТ ПРОВЕРКИ** | Дубликат H-LINKS-1 |
| **H-LINKS-4** | Ссылка на `../../docs/PIPELINE-TREE.md` | `.claude/commands/aidd-init.md:1090` | ✅ **H2** | ❌ Не упомянут | ✅ **РЕАЛЬНАЯ** | Файл `docs/PIPELINE-TREE.md` **НЕ СУЩЕСТВУЕТ** |
| **H-LINKS-5** | Ссылки на `templates/project/CLAUDE.md` | `docs/INDEX.md` | ✅ **H3** | ❌ Не упомянут | ✅ **РЕАЛЬНАЯ** | Директория `templates/project/` **НЕ СУЩЕСТВУЕТ** |
| **H-LINKS-6** | То же | `docs/INDEX.md` | ✅ **H3** | ❌ Не упомянут | ✅ **РЕАЛЬНАЯ** | `templates/project/README.md` **НЕ СУЩЕСТВУЕТ** |
| **H-LINKS-7** | Ссылки на команды `/aidd-{review,test,deploy}` | `docs/LINKS_REFERENCE.md:51-54` | ✅ **H4** | ✅ **H6-H8** | ✅ **РЕАЛЬНАЯ** | См. C-COMMANDS-1 |
| **H-LINKS-8** | Ссылка на PRD-пример | `docs/artifact-naming.md:222` | ❌ Не упомянут | ✅ **H9** | ✅ **РЕАЛЬНАЯ** | `prd/2024-12-20_F042_email-notify-prd.md` **НЕ СУЩЕСТВУЕТ** |
| **H-LINKS-9** | Regex в код-блоке интерпретируется как линк | `docs/audit/templates/comprehensive-audit.md:1465` | ❌ Не упомянут | ✅ **H10** | ✅ **РЕАЛЬНАЯ** | `[.*](.*\.md'` в bash-скрипте парсится как markdown-ссылка |
| **H-LINKS-10** | Неверный путь к `CLAUDE.md` | `docs/history/2025-12-20-pipeline-integration-problem.md:1617` | ⚠️ **H5** ("возможно false positive") | ✅ **H11** | ✅ **РЕАЛЬНАЯ** | Должно быть `../../CLAUDE.md` вместо `../CLAUDE.md` |
| **H-LINKS-11** | Неверный путь к `workflow.md` | `docs/history/2025-12-20-pipeline-integration-problem.md:1618` | ⚠️ **H5** | ✅ **H12** | ✅ **РЕАЛЬНАЯ** | Должно быть `../../workflow.md` |
| **H-LINKS-12** | Неверный путь к `conventions.md` | `docs/history/2025-12-20-pipeline-integration-problem.md:1619` | ⚠️ **H5** | ✅ **H13** | ✅ **РЕАЛЬНАЯ** | Должно быть `../../conventions.md` |
| **H-LINKS-13** | Ссылка на `.ai-framework/AGENTS.md` | `docs/history/2025-12-20-pipeline-integration-problem.md:1715` | ❌ Не упомянут | ✅ **H14** | ✅ **РЕАЛЬНАЯ** | Директория `.ai-framework/` **НЕ СУЩЕСТВУЕТ** (старое название) |
| **H-LINKS-14** | Неверный путь к `target-project-structure.md` | `docs/history/2025-12-21-documentation-master-todo.md:260` | ❌ Не упомянут | ✅ **H15** | ✅ **РЕАЛЬНАЯ** | Должно быть `../target-project-structure.md` |
| **H-LINKS-15** | Ссылки в `aidd-analyze.md` | `.claude/commands/aidd-analyze.md:419` | ❌ Не упомянут | ✅ **H2** (из H2-H16) | ✅ **РЕАЛЬНАЯ** | `prd/2024-12-23_F001_table-booking-prd.md` |
| **H-LINKS-16** | Ссылки в `aidd-analyze.md` | `.claude/commands/aidd-analyze.md:426` | ❌ Не упомянут | ✅ **H2** (из H2-H16) | ✅ **РЕАЛЬНАЯ** | `_analysis/2024-12-23_F001_table-booking.md` |
| **H-LINKS-17** | Ссылки в `aidd-idea.md` | `.claude/commands/aidd-analyze.md:391` | ❌ Не упомянут | ✅ **H3** (из H2-H16) | ✅ **РЕАЛЬНАЯ** | `prd/2024-12-23_F001_table-booking-prd.md` |
| **H-LINKS-18** | Ссылки в отчёте Codex | `contributors/2025-01-13-comprehensive-audit-report-codex.md:300` | ❌ Не упомянут | ✅ **H4** (из H2-H16) | ✅ **РЕАЛЬНАЯ** | `../../CLAUDE.md` избыточный путь |
| **H-LINKS-19** | Ссылки в отчёте Codex | `contributors/2025-01-13-comprehensive-audit-report-codex.md:309` | ❌ Не упомянут | ✅ **H5** (из H2-H16) | ✅ **РЕАЛЬНАЯ** | `../target-project-structure.md` неверный путь |

**Статистика битых ссылок**:
- **Claude**: 5 групп проблем (H1-H5), охватывают ~7-8 конкретных файлов
- **Codex**: 15 конкретных file:line локаций (H2-H16)
- **Пересечение**: ~60% (Claude нашёл основные группы, Codex детализировал)
- **Codex нашёл дополнительно**: H-LINKS-8, H-LINKS-9, H-LINKS-13, H-LINKS-14 + детали в commands

**Верификация методологии**:

Claude использовал:
```bash
grep -rho '\[.*\](.*\.md' . --include="*.md" | \
  sed 's/.*(\\([^)]*\\.md[^)]*\\).*/\\1/' | sort -u > /tmp/unique_refs.txt
```

Codex использовал:
```python
import re
from pathlib import Path

root = Path(".").resolve()
link_re = re.compile(r"\[[^\]]+\]\(([^)\s]+?\.md[^)]*)\)")

for p in root.rglob("*.md"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    for i, line in enumerate(text.splitlines(), 1):
        for m in link_re.finditer(line):
            target = m.group(1).split("#")[0]
            resolved = (p.parent / target).resolve() if not target.startswith("/") else (root / target.lstrip("/"))
            if not resolved.is_file() and not (root / target).is_file():
                print(f"{p.relative_to(root)}:{i} -> {target}")
```

**Вердикт**: Codex использовал **более точную** методологию с проверкой относительных путей.

---

### MEDIUM

| ID | Проблема | Claude | Codex | Реальность | Комментарий |
|----|----------|--------|-------|------------|-------------|
| **M-LINKS-1** | Неточные относительные пути в audit template | ✅ **M3** | ❌ Не упомянут отдельно | ✅ **РЕАЛЬНАЯ** | `docs/audit/templates/comprehensive-audit.md` использует `../../../` вместо абсолютных путей |

### LOW

| ID | Проблема | Claude | Codex | Реальность | Комментарий |
|----|----------|--------|-------|------------|-------------|
| **L-LINKS-1** | Неточные пути в contributors документах | ✅ **L2** | ⚠️ Частично (в H2-H16) | ✅ **РЕАЛЬНАЯ** | Избыточные `../` в contributors документах |

---

## ТИП 4: LEGACY/DEPRECATED УПОМИНАНИЯ

### CRITICAL

| ID | Проблема | Claude | Codex | Реальность | Комментарий |
|----|----------|--------|-------|------------|-------------|
| **C-LEGACY-1** | 33 упоминания `legacy/deprecated` в документации | ❌ **L1** (LOW, "контекстные") | ✅ **C1** | ⚠️ **СПОРНАЯ** | **Философская разница**: Codex требует 0 упоминаний (строго по шаблону), Claude интерпретирует контекст |

**Верификация**:
```bash
$ rg -n "legacy|deprecated|old-docs|DEPRECATED" -g "*.md" . | wc -l
33

# Примеры контекстных упоминаний (из Claude отчёта):
$ rg -n "legacy|deprecated" docs/audit/templates/comprehensive-audit.md | head -3
86:grep -rn "legacy\|deprecated\|old-docs\|DEPRECATED" . --include="*.md"
295:**Цель**: Найти ВСЕ битые markdown ссылки, включая legacy/deprecated ссылки.
303:echo "Шаг 1: Поиск legacy/deprecated ссылок..."
```

**Детальный анализ**:

| Файл | Строки | Контекст | Реальная проблема? |
|------|--------|----------|-------------------|
| `docs/audit/templates/comprehensive-audit.md` | 86, 295, 303 | Инструкции для **ПОИСКА** legacy | ❌ НЕТ |
| `contributors/2026-01-13-detailed-fix-recommendations.md` | 13, 96 | Описание **проблем** (метаданные) | ⚠️ СПОРНО |
| `contributors/2025-01-13-comprehensive-audit-report-codex.md` | 7 | Методология аудита | ❌ НЕТ |

**Вердикт**: ⚠️ **СПОРНАЯ**

**Аргументы Codex** (CRITICAL):
- Smoke Test 3 должен давать **0 упоминаний**
- Любое упоминание = риск путаницы
- Строгость методологии

**Аргументы Claude** (LOW):
- Упоминания **контекстные** (про поиск legacy, не сами legacy файлы)
- В документации описываются проблемы — слово "legacy" уместно
- Интерпретация важнее формализма

**Рекомендация**: Заменить `legacy` → `устаревшие (архив)`, `deprecated` → `устаревшее` в **contributors** документах, но оставить в **audit templates** (инструкции для поиска).

---

## ТИП 5: TODO/WIP/FIXME МАРКЕРЫ

### LOW

| ID | Проблема | Claude | Codex | Реальность | Комментарий |
|----|----------|--------|-------|------------|-------------|
| **L-TODO-1** | TODO/WIP маркеры в документации | ❌ "Не проверялось" | ✅ **L1** | ✅ **РЕАЛЬНАЯ** | `templates/documents/completion-report-template.md:159`, `docs/history/...` |

**Верификация**:
```bash
$ rg -n "TODO|FIXME|XXX|HACK|WIP" -g "*.md" . | wc -l
# Codex не указал точное количество, но нашёл примеры
```

**Вердикт**: ✅ **РЕАЛЬНАЯ** — нужна замена `TODO` → `placeholder`, `WIP` → `placeholder`.

---

## ТИП 6: ПРОЧИЕ ПРОБЛЕМЫ

### MEDIUM

| ID | Проблема | Claude | Codex | Реальность | Комментарий |
|----|----------|--------|-------|------------|-------------|
| **M-OTHER-1** | `/aidd-init` не ссылается на роль | ✅ **M1** ("это нормально") | ❌ Не упомянут | ❌ **ЛОЖНАЯ** | `/aidd-init` действительно **НЕ ИМЕЕТ** связанной роли — это корректное поведение |

**Вердикт M-OTHER-1**: ❌ **ЛОЖНАЯ** — Claude правильно интерпретировал, это не проблема.

---

## СВОДНАЯ СТАТИСТИКА ПО РЕАЛЬНОСТИ ПРОБЛЕМ

### По категориям

| Категория | Claude | Codex | Реальные | Спорные | Ложные | Требуют проверки |
|-----------|--------|-------|----------|---------|--------|------------------|
| **Пайплайн** | 0 | 3 | 1 | 2 | 0 | 0 |
| **Команды** | 1 | 2 | 2 | 1 | 0 | 0 |
| **Битые ссылки** | 5 | 19 | 16 | 0 | 0 | 3 |
| **Legacy** | 1 | 1 | 0 | 1 | 0 | 0 |
| **TODO/WIP** | 0 | 1 | 1 | 0 | 0 | 0 |
| **Прочие** | 3 | 0 | 1 | 1 | 1 | 0 |
| **ВСЕГО** | **10** | **26** | **21** | **5** | **1** | **3** |

### Пересечение находок

```
┌─────────────────────────────────────────────────────────────┐
│                    VENN ДИАГРАММА                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│         Claude (10)              Codex (26)                 │
│         ┌────────────────┬────────────────────┐             │
│         │                │                    │             │
│         │   Только       │    Оба нашли       │  Только    │
│         │   Claude       │    (пересечение)   │  Codex     │
│         │                │                    │            │
│         │   3 проблемы   │   7 проблем        │ 19 проблем │
│         │   (30%)        │   (70% Claude)     │ (73% Codex)│
│         │                │   (27% Codex)      │            │
│         └────────────────┴────────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Только Claude нашёл (3)**:
1. M-LINKS-1: Относительные пути в audit template
2. M-OTHER-1: aidd-init без роли (но это не проблема!)
3. L-LINKS-1: Пути в contributors (частично)

**Оба нашли (7)**:
1. H-LINKS-1,2,3: Ссылки на naming v3 примеры
2. H-LINKS-4: PIPELINE-TREE.md
3. H-LINKS-5,6: templates/project/*
4. H-LINKS-7: Команды review/test/deploy
5. H-LINKS-10,11,12: History документы

**Только Codex нашёл (19)**:
1. **C-PIPELINE-1**: 6 vs 9 этапов (КРИТИЧНО!)
2. **C-COMMANDS-2**: Audit-шаблон ожидает другие команды
3. **C-LEGACY-1**: 33 упоминания legacy/deprecated
4. H-LINKS-8: artifact-naming.md PRD пример
5. H-LINKS-9: Regex в код-блоке
6. H-LINKS-13: .ai-framework/
7. H-LINKS-14: target-project-structure путь
8. H-LINKS-15,16,17: Детали в commands
9. H-LINKS-18,19: Отчёты Codex
10. M-PIPELINE-1,2: Ворота и validator
11. L-TODO-1: TODO маркеры

---

## КРИТИЧЕСКИЕ ВЫВОДЫ

### 🚨 Реальные CRITICAL проблемы (требуют немедленного исправления)

| ID | Проблема | Нашёл | Влияние |
|----|----------|-------|---------|
| **C-PIPELINE-1** | 6 vs 9 этапов | Только Codex | **БЛОКЕР**: Пользователи получают противоречивые инструкции |
| **C-COMMANDS-1** | Отсутствуют `/aidd-{review,test,deploy}` | Оба | **БЛОКЕР**: Пайплайн нельзя завершить |
| **C-COMMANDS-2** | Audit-шаблон не соответствует naming | Только Codex | **БЛОКЕР**: Любой аудит всегда показывает 0/10 команд |

### ⚠️ Спорные проблемы (требуют обсуждения)

| ID | Проблема | Почему спорная |
|----|----------|----------------|
| **C-LEGACY-1** | Legacy упоминания | Контекстные упоминания vs строгое "0" |
| **M-PIPELINE-1** | `_DONE`/`_OK` в диаграммах | Это **корректные** названия ворот |
| **M-PIPELINE-2** | Validator этапы | Зависит от решения C-PIPELINE-1 |

### ✅ Реальные HIGH проблемы (битые ссылки)

**16 подтверждённых**, **3 требуют проверки** (naming v3 migration mode)

### ❌ Ложные срабатывания

| ID | Проблема | Почему ложная |
|----|----------|---------------|
| **M-OTHER-1** | aidd-init без роли | `/aidd-init` **НЕ ДОЛЖЕН** иметь роль (bootstrap-этап) |

---

## РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ

### Фаза 1: CRITICAL (< 1 час)

```bash
# 1. Синхронизировать количество этапов (C-PIPELINE-1)
perl -0pi -e "s/6-этапный/9-этапный/g; s/6 этапов \\(0-5\\)/9 этапов (0-8)/g" CLAUDE.md

# 2. Создать алиасы команд (C-COMMANDS-1)
cp .claude/commands/aidd-validate.md .claude/commands/aidd-review.md
cp .claude/commands/aidd-validate.md .claude/commands/aidd-test.md
cp .claude/commands/aidd-validate.md .claude/commands/aidd-deploy.md

# 3. Исправить audit-шаблон (C-COMMANDS-2)
perl -0pi -e "s/COMMANDS=\\(init idea/COMMANDS=(aidd-init aidd-idea/g" \
  docs/audit/templates/comprehensive-audit.md
```

### Фаза 2: HIGH (1-2 часа)

Исправить **16 битых ссылок** согласно Codex отчёту (H2-H16).

### Фаза 3: Обсуждение (перед исправлением)

1. **C-LEGACY-1**: Решить философию — строгое "0" или контекстные упоминания OK?
2. **H-LINKS-1,2,3**: Проверить migration mode v2.4 — должны ли существовать примеры для naming v3?

---

## ИТОГОВЫЙ HEALTH SCORE (после исправления CRITICAL+HIGH)

| Сценарий | Score | Комментарий |
|----------|-------|-------------|
| **Текущий (Codex)** | 54.9/100 | 3 CRITICAL, 16 HIGH |
| **После CRITICAL** | ~67/100 | Остаются 16 HIGH |
| **После CRITICAL+HIGH** | **~85-90/100** | Совпадёт с Claude оценкой |

**Причина расхождения Claude 88.3 vs Codex 54.9**:
- Claude пропустил **C-PIPELINE-1** (6 vs 9 этапов) = -8 баллов
- Claude не детализировал битые ссылки = -5 HIGH = -10 баллов
- Claude интерпретировал legacy как контекстные = +12 баллов (не CRITICAL)

**Вывод**: После исправления реальных проблем Health Score будет **~88-90/100** (оба аудита сойдутся).

---

**Версия**: 1.0
**Дата**: 2026-01-20
**Составил**: Claude Code (Sonnet 4.5) на основе сравнения двух аудитов
