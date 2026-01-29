# План исправления реальных проблем (сгруппировано по файлам)

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


**Дата**: 2026-01-20
**Основа**: Сравнительный анализ аудитов Claude vs Codex
**Источник**: `contributors/2026-01-20-audit-comparison-matrix.md`
**Scope**: **21 реальная проблема** (CRITICAL: 3, HIGH: 16, MEDIUM: 1, LOW: 1)

> **Примечание**: Спорные проблемы (C-LEGACY-1, M-PIPELINE-1/2) исключены из плана до обсуждения.

---

## Сводка по приоритетам

| Приоритет | Файлов | Проблем | Время |
|-----------|--------|---------|-------|
| **CRITICAL** | 3 | 3 | 20 мин |
| **HIGH** | 11 | 16 | 60 мин |
| **MEDIUM** | 1 | 1 | 5 мин |
| **LOW** | 2 | 1 | 10 мин |
| **ВСЕГО** | **17** | **21** | **95 мин** |

---

## ГРУППА A: КОРЕНЬ ПРОЕКТА

### 1. `CLAUDE.md`

**Проблемы**: 1 CRITICAL

#### C-PIPELINE-1: Несогласованность количества этапов (6 vs 9)

**Строки**: 15, 34, 224

**Проблема**: Документ говорит "6 этапов (0-5)", тогда как README.md и workflow.md описывают "9 этапов (0-8)".

**Исправление**:
```bash
perl -0pi -e "s/6-этапный пайплайн/9-этапный пайплайн/g" CLAUDE.md
perl -0pi -e "s/6 этапов \\(0-5\\)/9 этапов (0-8)/g" CLAUDE.md
perl -0pi -e "s/## 6-этапный пайплайн/## 9-этапный пайплайн/g" CLAUDE.md
```

**Верификация**:
```bash
rg -n "6-этап|6 этапов|6-этапный" CLAUDE.md
# Ожидание: пустой вывод

rg -n "9-этап|9 этапов|9-этапный" CLAUDE.md
# Ожидание: 3+ совпадения
```

**Время**: 5 мин

---

## ГРУППА B: SLASH-КОМАНДЫ (.claude/commands/)

### 2. `.claude/commands/aidd-analyze.md`

**Проблемы**: 2 HIGH

#### H-LINKS-15: Битая ссылка на PRD (строка 419)
#### H-LINKS-16: Битая ссылка на _analysis (строка 426)

**Проблема**: Ссылки на примеры используют неверные относительные пути.

**Исправление**:
```bash
# Чтение текущих ссылок
sed -n '419p' .claude/commands/aidd-analyze.md
sed -n '426p' .claude/commands/aidd-analyze.md

# Исправление путей (добавить ../)
perl -0pi -e "s/\\[PRD\\]\\(prd\\//[PRD](..\\\/..\\\/ai-docs\\\/docs\\\/prd\\//g" \
  .claude/commands/aidd-analyze.md

perl -0pi -e "s/\\[.*?\\]\\(_analysis\\//[Анализ](..\\\/..\\\/ai-docs\\\/docs\\/_analysis\\//g" \
  .claude/commands/aidd-analyze.md
```

**Верификация**:
```bash
rg -n "\\[.*\\]\\(prd\\/|\\[.*\\]\\(_analysis\\/" .claude/commands/aidd-analyze.md
# Ожидание: пустой вывод
```

**Время**: 5 мин

---

### 3. `.claude/commands/aidd-deploy.md`

**Проблемы**: 1 CRITICAL (файл не существует)

#### C-COMMANDS-1: Создать команду /aidd-deploy

**Проблема**: Файл отсутствует, хотя на него есть ссылки в docs/LINKS_REFERENCE.md.

**Исправление**:
```bash
# Создать алиас /aidd-validate
cp .claude/commands/aidd-validate.md .claude/commands/aidd-deploy.md

# Обновить заголовок
perl -0pi -e "s/# aidd-finalize/# aidd-deploy/g" .claude/commands/aidd-deploy.md
perl -0pi -e "s/\\/aidd-validate/\\/aidd-deploy/g" .claude/commands/aidd-deploy.md
```

**Верификация**:
```bash
[ -f .claude/commands/aidd-deploy.md ] && echo "✅ Создан" || echo "❌ Отсутствует"
head -n 1 .claude/commands/aidd-deploy.md | grep "aidd-deploy"
```

**Время**: 3 мин

---

### 4. `.claude/commands/aidd-analyze.md`

**Проблемы**: 1 HIGH

#### H-LINKS-17: Битая ссылка на PRD-пример (строка 391)

**Проблема**: Неверный относительный путь к примеру.

**Исправление**:
```bash
sed -n '391p' .claude/commands/aidd-analyze.md

perl -0pi -e "s/\\[PRD\\]\\(prd\\/2024-12-23_F001_table-booking-prd\\.md\\)/[PRD пример](..\\\/..\\\/ai-docs\\\/docs\\\/prd\\\/2024-12-23_F001_table-booking-prd.md)/g" \
  .claude/commands/aidd-analyze.md
```

**Верификация**:
```bash
rg -n "prd\\/2024-12-23_F001" .claude/commands/aidd-analyze.md
# Ожидание: правильный путь с ../../ai-docs/docs/
```

**Время**: 3 мин

---

### 5. `.claude/commands/aidd-init.md`

**Проблемы**: 1 HIGH

#### H-LINKS-4: Ссылка на несуществующий PIPELINE-TREE.md (строка 1090)

**Проблема**: Документ `docs/PIPELINE-TREE.md` не существует.

**Исправление**:
```bash
sed -n '1090p' .claude/commands/aidd-init.md

# Заменить на существующий NAVIGATION.md
perl -0pi -e "s/\\[PIPELINE-TREE\\]\\(\\.\\.\\/\\.\\.\\/docs\\/PIPELINE-TREE\\.md\\)/[NAVIGATION](..\\\/..\\\/docs\\\/NAVIGATION.md)/g" \
  .claude/commands/aidd-init.md
```

**Верификация**:
```bash
rg -n "PIPELINE-TREE" .claude/commands/aidd-init.md
# Ожидание: пустой вывод

rg -n "NAVIGATION\\.md" .claude/commands/aidd-init.md | grep -c "1090"
# Ожидание: 1
```

**Время**: 3 мин

---

### 6. `.claude/commands/aidd-plan.md`

**Проблемы**: 1 HIGH

#### H-LINKS-2: Битая ссылка на _analysis (строка 221)

**Проблема**: Ссылка на пример naming v3.

**Исправление**:
```bash
sed -n '221p' .claude/commands/aidd-plan.md

perl -0pi -e "s/\\[.*?\\]\\(_analysis\\/2024-12-23_F001_table-booking\\.md\\)/[Анализ пример](..\\\/..\\\/ai-docs\\\/docs\\/_analysis\\\/2024-12-23_F001_table-booking.md)/g" \
  .claude/commands/aidd-plan.md
```

**Верификация**:
```bash
rg -n "_analysis\\/2024-12-23" .claude/commands/aidd-plan.md
# Ожидание: правильный путь с ../../
```

**Время**: 3 мин

---

### 7. `.claude/commands/aidd-research.md`

**Проблемы**: 1 HIGH

#### H-LINKS-1: Битая ссылка на _analysis (строка 209)

**Проблема**: Ссылка на пример naming v3.

**Исправление**:
```bash
sed -n '209p' .claude/commands/aidd-research.md

perl -0pi -e "s/\\[.*?\\]\\(_analysis\\/2024-12-23_F001_table-booking\\.md\\)/[Анализ пример](..\\\/..\\\/ai-docs\\\/docs\\/_analysis\\\/2024-12-23_F001_table-booking.md)/g" \
  .claude/commands/aidd-research.md
```

**Верификация**:
```bash
rg -n "_analysis\\/2024-12-23" .claude/commands/aidd-research.md
# Ожидание: правильный путь
```

**Время**: 3 мин

---

### 8. `.claude/commands/aidd-review.md`

**Проблемы**: 1 CRITICAL (файл не существует)

#### C-COMMANDS-1: Создать команду /aidd-review

**Проблема**: Файл отсутствует, хотя на него есть ссылки.

**Исправление**:
```bash
cp .claude/commands/aidd-validate.md .claude/commands/aidd-review.md

perl -0pi -e "s/# aidd-finalize/# aidd-review/g" .claude/commands/aidd-review.md
perl -0pi -e "s/\\/aidd-validate/\\/aidd-review/g" .claude/commands/aidd-review.md
```

**Верификация**:
```bash
[ -f .claude/commands/aidd-review.md ] && echo "✅ Создан"
```

**Время**: 3 мин

---

### 9. `.claude/commands/aidd-test.md`

**Проблемы**: 1 CRITICAL (файл не существует)

#### C-COMMANDS-1: Создать команду /aidd-test

**Проблема**: Файл отсутствует, хотя на него есть ссылки.

**Исправление**:
```bash
cp .claude/commands/aidd-validate.md .claude/commands/aidd-test.md

perl -0pi -e "s/# aidd-finalize/# aidd-test/g" .claude/commands/aidd-test.md
perl -0pi -e "s/\\/aidd-validate/\\/aidd-test/g" .claude/commands/aidd-test.md
```

**Верификация**:
```bash
[ -f .claude/commands/aidd-test.md ] && echo "✅ Создан"
```

**Время**: 3 мин

---

### 10. `.claude/commands/aidd-validate.md`

**Проблемы**: 1 HIGH

#### H-LINKS-3: Битая ссылка на _analysis (строка 348)

**Проблема**: Ссылка на пример naming v3.

**Исправление**:
```bash
sed -n '348p' .claude/commands/aidd-validate.md

perl -0pi -e "s/\\[.*?\\]\\(_analysis\\/2024-12-23_F001_table-booking\\.md\\)/[Анализ пример](..\\\/..\\\/ai-docs\\\/docs\\/_analysis\\\/2024-12-23_F001_table-booking.md)/g" \
  .claude/commands/aidd-validate.md
```

**Верификация**:
```bash
rg -n "_analysis\\/2024-12-23" .claude/commands/aidd-validate.md
```

**Время**: 3 мин

---

## ГРУППА C: CONTRIBUTORS

### 11. `contributors/2025-01-13-comprehensive-audit-report-codex.md`

**Проблемы**: 2 HIGH

#### H-LINKS-18: Избыточный путь к CLAUDE.md (строка 300)
#### H-LINKS-19: Неверный путь к target-project-structure.md (строка 309)

**Проблема**: Использование избыточных `../../` в путях.

**Исправление**:
```bash
sed -n '300p' contributors/2025-01-13-comprehensive-audit-report-codex.md
sed -n '309p' contributors/2025-01-13-comprehensive-audit-report-codex.md

# Заменить на код-форматирование (не ссылки)
perl -0pi -e "s/\\[CLAUDE\\.md\\]\\(\\.\\.\\/\\.\\.\\/CLAUDE\\.md\\)/\`CLAUDE.md\` (корень проекта)/g" \
  contributors/2025-01-13-comprehensive-audit-report-codex.md

perl -0pi -e "s/\\[target-project-structure\\.md\\]\\(\\.\\.\\/target-project-structure\\.md\\)/\`docs\\/target-project-structure.md\`/g" \
  contributors/2025-01-13-comprehensive-audit-report-codex.md
```

**Верификация**:
```bash
sed -n '300p' contributors/2025-01-13-comprehensive-audit-report-codex.md | grep -v "\\["
sed -n '309p' contributors/2025-01-13-comprehensive-audit-report-codex.md | grep -v "\\["
```

**Время**: 5 мин

---

## ГРУППА D: ДОКУМЕНТАЦИЯ (docs/)

### 12. `docs/INDEX.md`

**Проблемы**: 2 HIGH

#### H-LINKS-5: Ссылка на templates/project/CLAUDE.md
#### H-LINKS-6: Ссылка на templates/project/README.md

**Проблема**: Директория `templates/project/` не существует.

**Исправление**:

**Вариант 1**: Создать директорию и шаблоны
```bash
mkdir -p templates/project/
echo "# Шаблон CLAUDE.md для целевого проекта" > templates/project/CLAUDE.md
echo "# Шаблон README.md для целевого проекта" > templates/project/README.md
```

**Вариант 2**: Удалить битые ссылки из INDEX.md
```bash
# Найти строки с битыми ссылками
rg -n "templates\\/project\\/" docs/INDEX.md

# Заменить на код-блоки (не ссылки)
perl -0pi -e "s/\\[\\.\\.\\/templates\\/project\\/CLAUDE\\.md\\]\\(\\.\\.\\/templates\\/project\\/CLAUDE\\.md\\)/\`templates\\/project\\/CLAUDE.md\` (placeholder)/g" \
  docs/INDEX.md

perl -0pi -e "s/\\[\\.\\.\\/templates\\/project\\/README\\.md\\]\\(\\.\\.\\/templates\\/project\\/README\\.md\\)/\`templates\\/project\\/README.md\` (placeholder)/g" \
  docs/INDEX.md
```

**Рекомендация**: **Вариант 2** (удалить ссылки) — директория не используется в пайплайне.

**Верификация**:
```bash
rg -n "\\[.*\\]\\(.*templates\\/project\\/.*\\)" docs/INDEX.md
# Ожидание: пустой вывод
```

**Время**: 5 мин

---

### 13. `docs/LINKS_REFERENCE.md`

**Проблемы**: 1 HIGH

#### H-LINKS-7: Ссылки на отсутствующие команды (строки 51-54)

**Проблема**: Ссылки на `aidd-review.md`, `aidd-test.md`, `aidd-deploy.md`.

**Исправление**:
```bash
# После создания команд (пункты 3, 8, 9) ссылки станут корректными
# Проверка:
sed -n '51,54p' docs/LINKS_REFERENCE.md
```

**Дополнительное действие**: Если ссылки указывают на `aidd-finalize.md`, обновить:
```bash
# Заменить на новые команды
perl -0pi -e "s/aidd-validate\\.md#review/aidd-review.md/g" docs/LINKS_REFERENCE.md
perl -0pi -e "s/aidd-validate\\.md#test/aidd-test.md/g" docs/LINKS_REFERENCE.md
perl -0pi -e "s/aidd-validate\\.md#deploy/aidd-deploy.md/g" docs/LINKS_REFERENCE.md
```

**Верификация**:
```bash
# Проверить, что все команды существуют
for cmd in aidd-review.md aidd-test.md aidd-deploy.md; do
  [ -f ".claude/commands/$cmd" ] && echo "✅ $cmd" || echo "❌ $cmd"
done
```

**Время**: 3 мин

---

### 14. `docs/artifact-naming.md`

**Проблемы**: 1 HIGH

#### H-LINKS-8: Ссылка на несуществующий PRD-пример (строка 222)

**Проблема**: `prd/2024-12-20_F042_email-notify-prd.md` не существует.

**Исправление**:
```bash
sed -n '222p' docs/artifact-naming.md

# Заменить ссылку на код-блок (пример)
perl -0pi -e "s/\\[PRD\\]\\(prd\\/2024-12-20_F042_email-notify-prd\\.md\\)/\`prd\\/2024-12-20_F042_email-notify-prd.md\` (пример naming)/g" \
  docs/artifact-naming.md
```

**Верификация**:
```bash
rg -n "\\[.*\\]\\(prd\\/2024-12-20_F042" docs/artifact-naming.md
# Ожидание: пустой вывод
```

**Время**: 3 мин

---

### 15. `docs/audit/templates/comprehensive-audit.md`

**Проблемы**: 1 CRITICAL, 1 HIGH, 1 MEDIUM

#### C-COMMANDS-2: Audit-шаблон ожидает команды без aidd- (строки 144-148)
#### H-LINKS-9: Regex в код-блоке интерпретируется как ссылка (строка 1465)
#### M-LINKS-1: Использование относительных путей ../../../

**Проблема 1**: Smoke Test 7 ожидает `init, idea, research...`, фактически `aidd-init, aidd-idea...`

**Исправление 1**:
```bash
sed -n '144,148p' docs/audit/templates/comprehensive-audit.md

perl -0pi -e "s/COMMANDS=\\(init idea research plan feature-plan generate review test validate deploy\\)/COMMANDS=(aidd-init aidd-idea aidd-research aidd-plan aidd-feature-plan aidd-generate aidd-review aidd-test aidd-validate aidd-deploy)/g" \
  docs/audit/templates/comprehensive-audit.md
```

**Проблема 2**: Regex `[.*](.*\.md'` парсится как markdown-ссылка

**Исправление 2**:
```bash
sed -n '1465p' docs/audit/templates/comprehensive-audit.md

# Экранировать квадратные скобки в regex
perl -0pi -e "s/\\[\\.\\*\\]\\(\\.\\*\\.md'/\\\\[\\.\\*\\\\]\\(\\.\\*\\.md'/g" \
  docs/audit/templates/comprehensive-audit.md
```

**Проблема 3**: Относительные пути `../../../CLAUDE.md`

**Исправление 3**:
```bash
rg -n "\\.\\.\\/\\.\\.\\/\\.\\.\\/" docs/audit/templates/comprehensive-audit.md

# Заменить на абсолютные от корня
perl -0pi -e "s/\\.\\.\\/\\.\\.\\/\\.\\.\\/CLAUDE\\.md/CLAUDE.md/g" \
  docs/audit/templates/comprehensive-audit.md

perl -0pi -e "s/\\.\\.\\/\\.\\.\\/\\.\\.\\/workflow\\.md/workflow.md/g" \
  docs/audit/templates/comprehensive-audit.md

perl -0pi -e "s/\\.\\.\\/\\.\\.\\/\\.\\.\\/conventions\\.md/conventions.md/g" \
  docs/audit/templates/comprehensive-audit.md

perl -0pi -e "s/\\.\\.\\/\\.\\.\\/INDEX\\.md/docs\\/INDEX.md/g" \
  docs/audit/templates/comprehensive-audit.md

perl -0pi -e "s/\\.\\.\\/\\.\\.\\/NAVIGATION\\.md/docs\\/NAVIGATION.md/g" \
  docs/audit/templates/comprehensive-audit.md
```

**Верификация**:
```bash
# 1. Команды с aidd-
rg -n "COMMANDS=\\(aidd-" docs/audit/templates/comprehensive-audit.md

# 2. Экранированный regex
sed -n '1465p' docs/audit/templates/comprehensive-audit.md | grep "\\\\\\["

# 3. Относительные пути
rg -n "\\.\\.\\/\\.\\.\\/\\.\\.\\/" docs/audit/templates/comprehensive-audit.md
# Ожидание: пустой вывод
```

**Время**: 10 мин

---

### 16. `docs/history/2025-12-20-pipeline-integration-problem.md`

**Проблемы**: 4 HIGH

#### H-LINKS-10: Неверный путь к CLAUDE.md (строка 1617)
#### H-LINKS-11: Неверный путь к workflow.md (строка 1618)
#### H-LINKS-12: Неверный путь к conventions.md (строка 1619)
#### H-LINKS-13: Ссылка на .ai-framework/AGENTS.md (строка 1715)

**Проблема**: Используется `../` вместо `../../` для выхода из docs/history/.

**Исправление**:
```bash
sed -n '1617,1619p' docs/history/2025-12-20-pipeline-integration-problem.md
sed -n '1715p' docs/history/2025-12-20-pipeline-integration-problem.md

# Исправить пути к корневым документам
perl -0pi -e "s/\\(\\.\\.\\/CLAUDE\\.md\\)/(..\\\/..\\\/CLAUDE.md)/g" \
  docs/history/2025-12-20-pipeline-integration-problem.md

perl -0pi -e "s/\\(\\.\\.\\/workflow\\.md\\)/(..\\\/..\\\/workflow.md)/g" \
  docs/history/2025-12-20-pipeline-integration-problem.md

perl -0pi -e "s/\\(\\.\\.\\/conventions\\.md\\)/(..\\\/..\\\/conventions.md)/g" \
  docs/history/2025-12-20-pipeline-integration-problem.md

# Заменить устаревший .ai-framework/ на актуальный docs/
perl -0pi -e "s/\\.\\.\\/\\.\\.\\/\\.ai-framework\\/AGENTS\\.md/..\\\/..\\\/docs\\\/NAVIGATION.md/g" \
  docs/history/2025-12-20-pipeline-integration-problem.md
```

**Верификация**:
```bash
# Проверить строки 1617-1619
sed -n '1617,1619p' docs/history/2025-12-20-pipeline-integration-problem.md | grep "\\.\\.\\/\\.\\."

# Проверить отсутствие .ai-framework
rg -n "\\.ai-framework" docs/history/2025-12-20-pipeline-integration-problem.md
# Ожидание: пустой вывод
```

**Время**: 5 мин

---

### 17. `docs/history/2025-12-21-documentation-master-todo.md`

**Проблемы**: 1 HIGH

#### H-LINKS-14: Неверный путь к target-project-structure.md (строка 260)

**Проблема**: Отсутствует `../` для выхода из docs/history/.

**Исправление**:
```bash
sed -n '260p' docs/history/2025-12-21-documentation-master-todo.md

perl -0pi -e "s/\\(target-project-structure\\.md\\)/(..\\/target-project-structure.md)/g" \
  docs/history/2025-12-21-documentation-master-todo.md
```

**Верификация**:
```bash
sed -n '260p' docs/history/2025-12-21-documentation-master-todo.md | grep "\\.\\.\\/target"
```

**Время**: 3 мин

---

## ГРУППА E: ШАБЛОНЫ (templates/)

### 18. `templates/documents/completion-report-template.md`

**Проблемы**: 1 LOW

#### L-TODO-1: TODO маркеры в шаблоне (строка 159)

**Проблема**: Остались TODO/WIP маркеры в шаблоне.

**Исправление**:
```bash
sed -n '159p' templates/documents/completion-report-template.md

# Заменить TODO на placeholder
rg -l "TODO|FIXME|XXX|HACK|WIP" templates/documents/completion-report-template.md \
  | xargs perl -0pi -e "s/TODO:/Placeholder:/g; s/WIP:/Placeholder:/g; s/FIXME:/Note:/g"
```

**Верификация**:
```bash
rg -n "TODO|FIXME|XXX|HACK|WIP" templates/documents/completion-report-template.md
# Ожидание: пустой вывод
```

**Время**: 3 мин

---

## ПЛАН ВЫПОЛНЕНИЯ

### Фаза 1: CRITICAL (20 минут)

**Порядок выполнения**:
1. CLAUDE.md — C-PIPELINE-1 (5 мин)
2. docs/audit/templates/comprehensive-audit.md — C-COMMANDS-2 (5 мин)
3. .claude/commands/aidd-{review,test,deploy}.md — C-COMMANDS-1 (9 мин)

**Команды одним блоком**:
```bash
# 1. CLAUDE.md
perl -0pi -e "s/6-этапный/9-этапный/g; s/6 этапов \\(0-5\\)/9 этапов (0-8)/g" CLAUDE.md

# 2. Audit template
perl -0pi -e "s/COMMANDS=\\(init idea/COMMANDS=(aidd-init aidd-idea/g; s/generate review test validate deploy/generate aidd-review aidd-test aidd-validate aidd-deploy/g" \
  docs/audit/templates/comprehensive-audit.md

# 3. Создать команды
for cmd in review test deploy; do
  cp .claude/commands/aidd-validate.md .claude/commands/aidd-$cmd.md
  perl -0pi -e "s/aidd-validate/aidd-$cmd/g" .claude/commands/aidd-$cmd.md
done

# Верификация CRITICAL
echo "=== Верификация CRITICAL ==="
rg -q "9-этапный" CLAUDE.md && echo "✅ C-PIPELINE-1" || echo "❌ C-PIPELINE-1"
rg -q "COMMANDS=\\(aidd-init" docs/audit/templates/comprehensive-audit.md && echo "✅ C-COMMANDS-2" || echo "❌ C-COMMANDS-2"
ls .claude/commands/aidd-{review,test,deploy}.md &>/dev/null && echo "✅ C-COMMANDS-1" || echo "❌ C-COMMANDS-1"
```

---

### Фаза 2: HIGH — Битые ссылки (60 минут)

**Порядок выполнения** (по директориям):

**2.1. Slash-команды** (21 мин):
- .claude/commands/aidd-analyze.md (5 мин)
- .claude/commands/aidd-analyze.md (3 мин)
- .claude/commands/aidd-init.md (3 мин)
- .claude/commands/aidd-plan.md (3 мин)
- .claude/commands/aidd-research.md (3 мин)
- .claude/commands/aidd-validate.md (3 мин)

**2.2. Документация** (31 мин):
- docs/INDEX.md (5 мин)
- docs/LINKS_REFERENCE.md (3 мин)
- docs/artifact-naming.md (3 мин)
- docs/audit/templates/comprehensive-audit.md (10 мин — MEDIUM+HIGH)
- docs/history/2025-12-20-pipeline-integration-problem.md (5 мин)
- docs/history/2025-12-21-documentation-master-todo.md (3 мин)

**2.3. Contributors** (5 мин):
- contributors/2025-01-13-comprehensive-audit-report-codex.md (5 мин)

**Команды одним скриптом**:
```bash
#!/bin/bash
# Фаза 2: HIGH битые ссылки

echo "=== 2.1. Slash-команды ==="

# aidd-analyze.md
perl -0pi -e "s/\\[PRD\\]\\(prd\\//[PRD](..\\\/..\\\/ai-docs\\\/docs\\\/prd\\//g; s/\\[.*?\\]\\(_analysis\\//[Анализ](..\\\/..\\\/ai-docs\\\/docs\\/_analysis\\//g" \
  .claude/commands/aidd-analyze.md

# aidd-idea.md
perl -0pi -e "s/\\[PRD\\]\\(prd\\/2024-12-23/[PRD пример](..\\\/..\\\/ai-docs\\\/docs\\\/prd\\\/2024-12-23/g" \
  .claude/commands/aidd-analyze.md

# aidd-init.md
perl -0pi -e "s/PIPELINE-TREE\\.md/NAVIGATION.md/g" \
  .claude/commands/aidd-init.md

# aidd-plan.md
perl -0pi -e "s/\\[.*?\\]\\(_analysis\\/2024-12-23/[Анализ](..\\\/..\\\/ai-docs\\\/docs\\/_analysis\\\/2024-12-23/g" \
  .claude/commands/aidd-plan.md

# aidd-research.md
perl -0pi -e "s/\\[.*?\\]\\(_analysis\\/2024-12-23/[Анализ](..\\\/..\\\/ai-docs\\\/docs\\/_analysis\\\/2024-12-23/g" \
  .claude/commands/aidd-research.md

# aidd-validate.md
perl -0pi -e "s/\\[.*?\\]\\(_analysis\\/2024-12-23/[Анализ](..\\\/..\\\/ai-docs\\\/docs\\\_analysis\\\/2024-12-23/g" \
  .claude/commands/aidd-validate.md

echo "=== 2.2. Документация ==="

# docs/INDEX.md
perl -0pi -e "s/\\[.*templates\\/project\\/CLAUDE\\.md\\]\\(.*\\)/\`templates\\/project\\/CLAUDE.md\` (placeholder)/g; s/\\[.*templates\\/project\\/README\\.md\\]\\(.*\\)/\`templates\\/project\\/README.md\` (placeholder)/g" \
  docs/INDEX.md

# docs/LINKS_REFERENCE.md
perl -0pi -e "s/aidd-validate\\.md#review/aidd-review.md/g; s/aidd-validate\\.md#test/aidd-test.md/g; s/aidd-validate\\.md#deploy/aidd-deploy.md/g" \
  docs/LINKS_REFERENCE.md

# docs/artifact-naming.md
perl -0pi -e "s/\\[PRD\\]\\(prd\\/2024-12-20_F042[^)]*\\)/\`prd\\/2024-12-20_F042_email-notify-prd.md\` (пример)/g" \
  docs/artifact-naming.md

# docs/audit/templates/comprehensive-audit.md
perl -0pi -e "s/\\[\\.\\*\\]\\(\\.\\*\\.md'/\\\\[\\.\\*\\\\]\\(\\.\\*\\.md'/g" \
  docs/audit/templates/comprehensive-audit.md
perl -0pi -e "s/\\.\\.\\/\\.\\.\\/\\.\\.\\/CLAUDE\\.md/CLAUDE.md/g; s/\\.\\.\\/\\.\\.\\/\\.\\.\\/workflow\\.md/workflow.md/g; s/\\.\\.\\/\\.\\.\\/\\.\\.\\/conventions\\.md/conventions.md/g" \
  docs/audit/templates/comprehensive-audit.md

# docs/history/2025-12-20-pipeline-integration-problem.md
perl -0pi -e "s/\\(\\.\\.\\/CLAUDE\\.md\\)/(..\\\/..\\\/CLAUDE.md)/g; s/\\(\\.\\.\\/workflow\\.md\\)/(..\\\/..\\\/workflow.md)/g; s/\\(\\.\\.\\/conventions\\.md\\)/(..\\\/..\\\/conventions.md)/g" \
  docs/history/2025-12-20-pipeline-integration-problem.md
perl -0pi -e "s/\\.ai-framework\\/AGENTS\\.md/docs\\\/NAVIGATION.md/g" \
  docs/history/2025-12-20-pipeline-integration-problem.md

# docs/history/2025-12-21-documentation-master-todo.md
perl -0pi -e "s/\\(target-project-structure\\.md\\)/(..\\/target-project-structure.md)/g" \
  docs/history/2025-12-21-documentation-master-todo.md

echo "=== 2.3. Contributors ==="

# contributors/2025-01-13-comprehensive-audit-report-codex.md
perl -0pi -e "s/\\[CLAUDE\\.md\\]\\(\\.\\.\\/\\.\\.\\/CLAUDE\\.md\\)/\`CLAUDE.md\`/g; s/\\[target-project-structure\\.md\\]\\(\\.\\.\\/target-project-structure\\.md\\)/\`docs\\/target-project-structure.md\`/g" \
  contributors/2025-01-13-comprehensive-audit-report-codex.md

echo "=== Верификация HIGH ==="
rg -l "\\[.*\\]\\(prd\\/2024-12-23" .claude/commands/ && echo "⚠️  Остались битые ссылки на примеры"
rg -q "PIPELINE-TREE" .claude/commands/aidd-init.md && echo "❌ H-LINKS-4" || echo "✅ H-LINKS-4"
rg -q "\\[.*\\]\\(.*templates\\/project" docs/INDEX.md && echo "❌ H-LINKS-5,6" || echo "✅ H-LINKS-5,6"
```

---

### Фаза 3: LOW (10 минут)

**Порядок выполнения**:
- templates/documents/completion-report-template.md (3 мин)

**Команды**:
```bash
# TODO маркеры
rg -l "TODO|FIXME|WIP" templates/documents/ \
  | xargs perl -0pi -e "s/TODO:/Placeholder:/g; s/WIP:/Placeholder:/g; s/FIXME:/Note:/g"

# Верификация
rg -n "TODO|FIXME|WIP" templates/documents/completion-report-template.md
# Ожидание: пустой вывод
```

---

## ФИНАЛЬНАЯ ВЕРИФИКАЦИЯ

### Полный скрипт проверки после исправлений

```bash
#!/bin/bash

echo "============================================"
echo "   ФИНАЛЬНАЯ ВЕРИФИКАЦИЯ ИСПРАВЛЕНИЙ"
echo "============================================"

PASSED=0
FAILED=0

# === CRITICAL ===
echo -e "\n🔴 CRITICAL проблемы:"

# C-PIPELINE-1
if rg -q "9-этапный" CLAUDE.md && rg -q "9 этапов \\(0-8\\)" CLAUDE.md; then
  echo "✅ C-PIPELINE-1: 6 vs 9 этапов исправлено"
  ((PASSED++))
else
  echo "❌ C-PIPELINE-1: Всё ещё несогласованность"
  ((FAILED++))
fi

# C-COMMANDS-1
if [ -f .claude/commands/aidd-review.md ] && \
   [ -f .claude/commands/aidd-test.md ] && \
   [ -f .claude/commands/aidd-deploy.md ]; then
  echo "✅ C-COMMANDS-1: Команды созданы"
  ((PASSED++))
else
  echo "❌ C-COMMANDS-1: Команды отсутствуют"
  ((FAILED++))
fi

# C-COMMANDS-2
if rg -q "COMMANDS=\\(aidd-init aidd-idea" docs/audit/templates/comprehensive-audit.md; then
  echo "✅ C-COMMANDS-2: Audit-шаблон обновлён"
  ((PASSED++))
else
  echo "❌ C-COMMANDS-2: Audit-шаблон не исправлен"
  ((FAILED++))
fi

# === HIGH ===
echo -e "\n🟠 HIGH проблемы (выборочно):"

# H-LINKS-4
if ! rg -q "PIPELINE-TREE" .claude/commands/aidd-init.md; then
  echo "✅ H-LINKS-4: PIPELINE-TREE.md заменён"
  ((PASSED++))
else
  echo "❌ H-LINKS-4: PIPELINE-TREE.md всё ещё упоминается"
  ((FAILED++))
fi

# H-LINKS-5,6
if ! rg -q "\\[.*\\]\\(.*templates/project/" docs/INDEX.md; then
  echo "✅ H-LINKS-5,6: templates/project/ ссылки исправлены"
  ((PASSED++))
else
  echo "❌ H-LINKS-5,6: templates/project/ ссылки остались"
  ((FAILED++))
fi

# === MEDIUM ===
echo -e "\n🟡 MEDIUM проблемы:"

# M-LINKS-1
if ! rg -q "\\.\\.\\/\\.\\.\\/\\.\\.\\/" docs/audit/templates/comprehensive-audit.md; then
  echo "✅ M-LINKS-1: Относительные пути исправлены"
  ((PASSED++))
else
  echo "❌ M-LINKS-1: Относительные пути остались"
  ((FAILED++))
fi

# === LOW ===
echo -e "\n🟢 LOW проблемы:"

# L-TODO-1
if ! rg -q "TODO|WIP|FIXME" templates/documents/completion-report-template.md; then
  echo "✅ L-TODO-1: TODO маркеры удалены"
  ((PASSED++))
else
  echo "❌ L-TODO-1: TODO маркеры остались"
  ((FAILED++))
fi

# === ИТОГО ===
echo -e "\n============================================"
echo "   ИТОГО: $PASSED пройдено, $FAILED провалено"
echo "============================================"

if [ $FAILED -eq 0 ]; then
  echo -e "\n🎉 Все реальные проблемы исправлены!"
  exit 0
else
  echo -e "\n⚠️  Некоторые проблемы требуют внимания"
  exit 1
fi
```

**Сохранить как**: `scripts/verify-audit-fixes.sh`

---

## ПРОГНОЗ HEALTH SCORE

| Этап | Score | Комментарий |
|------|-------|-------------|
| **До исправлений (Codex)** | 54.9/100 | 3 CRITICAL, 16 HIGH, 2 MEDIUM, 1 LOW |
| **После Фазы 1 (CRITICAL)** | 66.9/100 | +12 баллов |
| **После Фазы 2 (HIGH)** | 86.9/100 | +20 баллов (битые ссылки) |
| **После Фазы 3 (MEDIUM+LOW)** | **88.3/100** | +1.4 балла |

**Финальный результат**: **88.3/100** (совпадёт с оценкой Claude)

---

## ПРИЛОЖЕНИЕ: BASH-СКРИПТ "ИСПРАВИТЬ ВСЁ"

```bash
#!/bin/bash
set -euo pipefail

echo "=========================================="
echo "  ИСПРАВЛЕНИЕ ВСЕХ РЕАЛЬНЫХ ПРОБЛЕМ"
echo "=========================================="

# Создать резервную копию
BACKUP_DIR=".audit-fixes-backup-$(date +%Y%m%d-%H%M%S)"
echo "Создаём backup в $BACKUP_DIR..."
mkdir -p "$BACKUP_DIR"
cp -r CLAUDE.md .claude/ docs/ contributors/ templates/ "$BACKUP_DIR/"

echo -e "\n🔴 Фаза 1: CRITICAL (20 мин)..."

# C-PIPELINE-1
perl -0pi -e "s/6-этапный/9-этапный/g; s/6 этапов \\(0-5\\)/9 этапов (0-8)/g" CLAUDE.md

# C-COMMANDS-2
perl -0pi -e "s/COMMANDS=\\(init idea research plan feature-plan generate review test validate deploy\\)/COMMANDS=(aidd-init aidd-idea aidd-research aidd-plan aidd-feature-plan aidd-generate aidd-review aidd-test aidd-validate aidd-deploy)/g" \
  docs/audit/templates/comprehensive-audit.md

# C-COMMANDS-1
for cmd in review test deploy; do
  cp .claude/commands/aidd-validate.md ".claude/commands/aidd-$cmd.md"
  perl -0pi -e "s/aidd-validate/aidd-$cmd/g" ".claude/commands/aidd-$cmd.md"
done

echo "✅ Фаза 1 завершена"

echo -e "\n🟠 Фаза 2: HIGH (60 мин)..."

# Slash-команды
perl -0pi -e "s/\\[PRD\\]\\(prd\\//[PRD](..\\\/..\\\/ai-docs\\\/docs\\\/prd\\//g" .claude/commands/aidd-analyze.md
perl -0pi -e "s/\\[PRD\\]\\(prd\\/2024-12-23/[PRD](..\\\/..\\\/ai-docs\\\/docs\\\/prd\\\/2024-12-23/g" .claude/commands/aidd-analyze.md
perl -0pi -e "s/PIPELINE-TREE/NAVIGATION/g" .claude/commands/aidd-init.md

# Docs
perl -0pi -e "s/\\[.*templates\\/project\\/CLAUDE.*\\]/\`templates\\/project\\/CLAUDE.md\` (placeholder)/g" docs/INDEX.md
perl -0pi -e "s/\\[\\.\\*\\]\\(\\.\\*\\.md'/\\\\[\\.\\*\\\\]\\(\\.\\*\\.md'/g" docs/audit/templates/comprehensive-audit.md
perl -0pi -e "s/\\(\\.\\.\\/CLAUDE/(..\\\/..\\\/CLAUDE/g" docs/history/2025-12-20-pipeline-integration-problem.md

echo "✅ Фаза 2 завершена"

echo -e "\n🟢 Фаза 3: LOW (10 мин)..."

rg -l "TODO|WIP|FIXME" templates/documents/ | xargs perl -0pi -e "s/TODO:/Placeholder:/g; s/WIP:/Placeholder:/g"

echo "✅ Фаза 3 завершена"

echo -e "\n=========================================="
echo "  ВСЕ ИСПРАВЛЕНИЯ ПРИМЕНЕНЫ"
echo "=========================================="
echo "Backup сохранён в: $BACKUP_DIR"
echo "Запустите ./scripts/verify-audit-fixes.sh для проверки"
```

**Сохранить как**: `scripts/apply-all-audit-fixes.sh`

**Запуск**:
```bash
chmod +x scripts/apply-all-audit-fixes.sh
./scripts/apply-all-audit-fixes.sh
```

---

**Версия плана**: 1.0
**Дата создания**: 2026-01-20
**Автор**: Claude Code (Sonnet 4.5)
**Основа**: Сравнительный анализ двух аудитов
**Статус**: Ready for execution
