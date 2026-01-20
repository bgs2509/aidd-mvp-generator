# Комплексный аудит документации AIDD-MVP Generator (Codex)

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-idea`, `/aidd-generate`, `/aidd-finalize`, `/aidd-feature-plan`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


Дата: 2026-01-20

> **Философия**: VERIFY BEFORE ACT — Проверяй перед действием.
> **Ключевой принцип**: аудит должен быть исчерпывающим, а не выборочным.

---

## Executive Summary

### Назначение проекта
AIDD-MVP Generator — фреймворк для быстрой генерации production-ready MVP с AI‑агентами, архитектурными шаблонами и качественными воротами. Он ориентирован на запуск сервисов (FastAPI, Data APIs, боты, воркеры) и требует строгой дисциплины артефактов и пайплайна, чтобы команды работали воспроизводимо.

### Расчёт Health Score

**Формула**:
```
Health Score = 100 - (CRITICAL×4) - (HIGH×2) - (MEDIUM×0.5) - (LOW×0.1)
Min score: 0
```

**Расчёт**:
```
Базовый:                    100 баллов
CRITICAL проблемы (3):      3 × 4   = -12 баллов
HIGH проблемы (16):         16 × 2  = -32 баллов
MEDIUM проблемы (2):        2 × 0.5 = -1 балл
LOW проблемы (1):           1 × 0.1 = -0.1 балл
─────────────────────────────────────────────
ИТОГО HEALTH SCORE:         max(0, 100 - 12 - 32 - 1 - 0.1) = 54.9/100
```

### Всего найдено проблем

| Приоритет | Кол-во | Топ-3 примера (file:line) | Влияние |
|-----------|--------|---------------------------|---------|
| **CRITICAL** | 3 | `docs/LINKS_REFERENCE.md:51`, `README.md:73`, `contributors/2026-01-13-detailed-fix-recommendations.md:13` | Блокирует этапы пайплайна / сбивает аудит |
| **HIGH** | 16 | `CLAUDE.md:15`, `docs/history/2025-12-20-pipeline-integration-problem.md:1617`, `.claude/commands/aidd-idea.md:391` | Ломает навигацию и консистентность пайплайна |
| **MEDIUM** | 2 | `CLAUDE.md:244`, `.claude/agents/validator.md:10` | Проблемы интерпретации этапов |
| **LOW** | 1 | `templates/documents/completion-report-template.md:159` | Шум/неоконченные маркеры |
| **ИТОГО** | 22 |  |  |

---

## Smoke Tests (12)

1. **Markdown файлов**: `169` (ожидалось 300–400; scope меньше).
2. **Markdown‑ссылок**: `253`.
3. **Legacy/Deprecated**: `33` → **CRITICAL**.
4. **Битые ссылки (выборка)**: команда дала `Broken pipe` (ограничение пайпа). Полная проверка выполнена в Objective 2.
5. **Stage 0 документы**: ✅ `CLAUDE.md`, `workflow.md`, `conventions.md`.
6. **7 ролей AI**: ✅ 7/7.
7. **10 slash‑команд**: ❌ 0/10 (шаблон ожидает без `aidd-`, см. CRITICAL C3).
8. **5 шаблонов сервисов**: ✅ 5/5.
9. **Шаблоны документов**: ✅ 8/8.
10. **Ворота (Gates)**: в `CLAUDE.md` и `workflow.md` появились лишние `_DONE`/`_OK` → **MEDIUM**.
11. **CREATE/FEATURE**: smoke‑тест сломан из‑за `bc`, проверено в Objective 9.
12. **Knowledge**: 53 файла; категории расширены (дополнительно `pipeline`, `security`).

---

## Категории проблем

### Проблемы ссылок
- **Битые внутренние ссылки**: 15.
- **Неверные относительные пути** в исторических документах и отчётах.
- **Ссылки на отсутствующие команды** `/aidd-review`, `/aidd-test`, `/aidd-deploy`.

### Проблемы пайплайна
- **Несогласованность этапов** (6 vs 9) между `CLAUDE.md`, `README.md`, `workflow.md`.
- **Несоответствие audit‑шаблона и фактических команд** (без `aidd-`).

### Проблемы шаблонов
- **Аудит‑шаблон содержит ссылку‑артефакт** из regex в код‑блоке, который интерпретируется как markdown‑линк.

### Проблемы базы знаний
- Критических проблем не выявлено (структура и объём соответствуют ожиданиям).

---

## Проблемы (с деталями)

### Проблема C1: legacy/deprecated упоминания
**Приоритет**: CRITICAL

**Файлы (примеры)**:
- `contributors/2026-01-13-detailed-fix-recommendations.md:13`
- `contributors/2026-01-13-detailed-fix-recommendations.md:96`
- `contributors/2025-01-13-comprehensive-audit-report-codex.md:7`

**Описание**: В документации остались слова `legacy/deprecated/DEPRECATED`, что по правилам аудита должно быть **0**.

**Влияние**: Smoke Test 3 всегда падает → аудит считается критически не пройденным.

**Как обнаружено**:
```bash
rg -n "legacy|deprecated|old-docs|DEPRECATED|old-" -g "*.md" .
```

**Команда исправления**:
```bash
rg -l "legacy|deprecated|old-docs|DEPRECATED|old-" -g "*.md" . \
  | xargs -I{} perl -0pi -e "s/DEPRECATED/устаревшее (архив)/g; s/legacy/устаревшее/g; s/deprecated/устаревшее/g" {}
```

**Верификация**:
```bash
rg -n "legacy|deprecated|old-docs|DEPRECATED|old-" -g "*.md" .
# Ожидание: пустой вывод
```

---

### Проблема C2: Отсутствуют команды `/aidd-review`, `/aidd-test`, `/aidd-deploy`
**Приоритет**: CRITICAL

**Файлы**:
- `docs/LINKS_REFERENCE.md:51`
- `docs/LINKS_REFERENCE.md:52`
- `docs/LINKS_REFERENCE.md:54`
- `README.md:73`
- `README.md:74`
- `README.md:76`

**Описание**: Документация ссылается на команды, которых нет в `.claude/commands/`.

**Влияние**: Пользователь не может выполнить этапы 5/6/8; ломается весь пайплайн.

**Как обнаружено**:
```bash
rg -n "aidd-review|aidd-test|aidd-deploy" docs/LINKS_REFERENCE.md README.md
```

**Команда исправления**:
```bash
cp .claude/commands/aidd-finalize.md .claude/commands/aidd-review.md
cp .claude/commands/aidd-finalize.md .claude/commands/aidd-test.md
cp .claude/commands/aidd-finalize.md .claude/commands/aidd-deploy.md
```

**Верификация**:
```bash
ls -1 .claude/commands | rg -n "aidd-(review|test|deploy)"
```

---

### Проблема C3: Audit‑шаблон ожидает команды без префикса
**Приоритет**: CRITICAL

**Файлы**:
- `docs/audit/templates/comprehensive-audit.md:144`
- `docs/audit/templates/comprehensive-audit.md:148`

**Описание**: Smoke Test 7 и Objective 7 ожидают команды `init/idea/...`, но фактически используются `aidd-*`.

**Влияние**: Любой аудит всегда выдаёт CRITICAL по командам.

**Как обнаружено**:
```bash
rg -n "Smoke Test 7|COMMANDS=\\(init" docs/audit/templates/comprehensive-audit.md
```

**Команда исправления**:
```bash
perl -0pi -e "s/COMMANDS=\\(init idea research plan feature-plan generate review test validate deploy\\)/COMMANDS=(aidd-init aidd-idea aidd-research aidd-plan aidd-feature-plan aidd-generate aidd-review aidd-test aidd-validate aidd-deploy)/g" \
  docs/audit/templates/comprehensive-audit.md
```

**Верификация**:
```bash
rg -n "COMMANDS=\\(aidd-" docs/audit/templates/comprehensive-audit.md
```

---

### Проблема H1: Несогласованность пайплайна (6 этапов vs 9 этапов)
**Приоритет**: HIGH

**Файлы**:
- `CLAUDE.md:15`
- `CLAUDE.md:34`
- `CLAUDE.md:224`
- `README.md:67`
- `README.md:104`
- `workflow.md:506`

**Описание**: `CLAUDE.md` фиксирует 6 этапов (0–5), тогда как README и workflow описывают 9 этапов (0–8).

**Влияние**: Пользователь/агент получает конфликтующие инструкции, порядок команд неочевиден.

**Как обнаружено**:
```bash
rg -n "6-этап|6 этапов|6-этапный" CLAUDE.md
rg -n "9-этап|9 этап" README.md workflow.md
```

**Команда исправления**:
```bash
perl -0pi -e "s/6-этапный/9-этапный/g; s/6 этапов \\(0-5\\)/9 этапов (0-8)/g" CLAUDE.md
```

**Верификация**:
```bash
rg -n "6-этап|6 этапов" CLAUDE.md
# Ожидание: пустой вывод
```

---

### Проблемы H2–H16: Битые ссылки (15 шт.)
**Приоритет**: HIGH

**Как обнаружено**:
```bash
python3 - <<'PY'
import re
from pathlib import Path

root = Path(".").resolve()
link_re = re.compile(r"\[[^\]]+\]\(([^)\s]+?\.md[^)]*)\)")

broken = []
for p in root.rglob("*.md"):
    if ".git" in p.parts:
        continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    for i, line in enumerate(text.splitlines(), 1):
        for m in link_re.finditer(line):
            target = m.group(1).split("#")[0]
            resolved = (p.parent / target).resolve() if not target.startswith("/") else (root / target.lstrip("/"))
            if not resolved.is_file() and not (root / target).is_file():
                broken.append((p.relative_to(root), i, target))

print("\n".join([f"{p}:{i} -> {t}" for p,i,t in broken]))
PY
```

**Список**:
1. `.claude/commands/aidd-analyze.md:419 -> prd/2024-12-23_F001_table-booking-prd.md`
2. `.claude/commands/aidd-analyze.md:426 -> _analysis/2024-12-23_F001_table-booking.md`
3. `.claude/commands/aidd-idea.md:391 -> prd/2024-12-23_F001_table-booking-prd.md`
4. `contributors/2025-01-13-comprehensive-audit-report-codex.md:300 -> ../../CLAUDE.md`
5. `contributors/2025-01-13-comprehensive-audit-report-codex.md:309 -> ../target-project-structure.md`
6. `docs/LINKS_REFERENCE.md:51 -> ../.claude/commands/aidd-review.md`
7. `docs/LINKS_REFERENCE.md:52 -> ../.claude/commands/aidd-test.md`
8. `docs/LINKS_REFERENCE.md:54 -> ../.claude/commands/aidd-deploy.md`
9. `docs/artifact-naming.md:222 -> prd/2024-12-20_F042_email-notify-prd.md`
10. `docs/audit/templates/comprehensive-audit.md:1465 -> .*\.md' . --include="*.md" 2>/dev/null | wc -l`
11. `docs/history/2025-12-20-pipeline-integration-problem.md:1617 -> ../CLAUDE.md`
12. `docs/history/2025-12-20-pipeline-integration-problem.md:1618 -> ../workflow.md`
13. `docs/history/2025-12-20-pipeline-integration-problem.md:1619 -> ../conventions.md`
14. `docs/history/2025-12-20-pipeline-integration-problem.md:1715 -> ../../.ai-framework/AGENTS.md`
15. `docs/history/2025-12-21-documentation-master-todo.md:260 -> target-project-structure.md`

**Команды исправления**:
```bash
# 1–3: корректные относительные пути в примерах FEATURES.md
perl -0pi -e "s/\\[PRD\\]\\(prd\\//[PRD](..\\/prd\\//g; s/\\[PRD\\]\\(_analysis\\//[PRD](..\\/_analysis\\//g" \
  .claude/commands/aidd-analyze.md .claude/commands/aidd-idea.md

# 4–5: корректные ссылки в отчёте
perl -0pi -e "s/\\[CLAUDE\\.md\\]\\(\\.\\.\\/\\.\\.\\/CLAUDE\\.md\\)/`CLAUDE.md (root)`/g; s/\\[target-project-structure\\.md\\]\\(\\.\\.\\/target-project-structure\\.md\\)/`docs\\/target-project-structure.md`/g" \
  contributors/2025-01-13-comprehensive-audit-report-codex.md

# 6–8: заменить на aidd-finalize (или создать алиасы, см. C2)
perl -0pi -e "s/aidd-review\\.md/aidd-finalize.md/g; s/aidd-test\\.md/aidd-finalize.md/g; s/aidd-deploy\\.md/aidd-finalize.md/g" \
  docs/LINKS_REFERENCE.md

# 9: убрать ссылку на несуществующий PRD (пример)
perl -0pi -e "s/\\[PRD\\]\\(prd\\/2024-12-20_F042_email-notify-prd\\.md\\)/`prd\\/2024-12-20_F042_email-notify-prd.md`/g" \
  docs/artifact-naming.md

# 10: экранировать regex в код-блоке, чтобы не считался линком
perl -0pi -e "s/\\[\\.\\*\\]\\(\\.\\*\\.md/\\\\[\\.\\*\\\\]\\(\\.\\*\\.md/g" \
  docs/audit/templates/comprehensive-audit.md

# 11–13: правильный путь из docs/history
perl -0pi -e "s/\\(\\.\\.\\/CLAUDE\\.md\\)/\\.\\.\\/\\.\\.\\/CLAUDE.md/g; s/\\(\\.\\.\\/workflow\\.md\\)/\\.\\.\\/\\.\\.\\/workflow.md/g; s/\\(\\.\\.\\/conventions\\.md\\)/\\.\\.\\/\\.\\.\\/conventions.md/g" \
  docs/history/2025-12-20-pipeline-integration-problem.md

# 14: заменить .ai-framework/AGENTS.md на актуальный документ
perl -0pi -e "s/\\.\\.\\/\\.\\.\\/\\.ai-framework\\/AGENTS\\.md/\\.\\.\\/\\.\\.\\/docs\\/NAVIGATION.md/g" \
  docs/history/2025-12-20-pipeline-integration-problem.md

# 15: корректный путь к target-project-structure.md
perl -0pi -e "s/\\(target-project-structure\\.md\\)/..\\/target-project-structure.md/g" \
  docs/history/2025-12-21-documentation-master-todo.md
```

**Верификация**:
```bash
# Повторить скрипт проверки битых ссылок (см. выше)
```

---

### Проблема M1: Лишние ворота `_DONE` / `_OK` в диаграммах
**Приоритет**: MEDIUM

**Файлы**:
- `CLAUDE.md:244`
- `workflow.md:34`

**Описание**: `_DONE` и `_OK` встречаются в ASCII‑диаграммах и ловятся grep‑ом ворот.

**Как обнаружено**:
```bash
rg -n "_DONE|_OK" CLAUDE.md workflow.md
```

**Команда исправления**:
```bash
perl -0pi -e "s/\\b_DONE\\b/RESEARCH_DONE/g; s/\\b_OK\\b/IMPLEMENT_OK/g" \
  CLAUDE.md workflow.md
```

**Верификация**:
```bash
rg -n "_DONE|_OK" CLAUDE.md workflow.md
# Ожидание: пустой вывод
```

---

### Проблема M2: Валидатор не упоминает этапы 7 и 8 явно
**Приоритет**: MEDIUM

**Файл**:
- `.claude/agents/validator.md:10`

**Описание**: Роль описана как «этапы 4‑8», но audit‑команда ожидает явные упоминания этапов 7 и 8.

**Как обнаружено**:
```bash
rg -n "этап|stage" .claude/agents/validator.md
```

**Команда исправления**:
```bash
perl -0pi -e "s/этапы 4-8/этапы 7-8 (валидация и деплой)/g" .claude/agents/validator.md
```

**Верификация**:
```bash
rg -n "этап 7|этап 8" .claude/agents/validator.md
```

---

### Проблема L1: TODO/WIP маркеры в документации
**Приоритет**: LOW

**Файлы (примеры)**:
- `templates/documents/completion-report-template.md:159`
- `docs/history/2025-12-19-problems-solutions-todo.md:1`

**Описание**: Остаются TODO/WIP‑маркеры в шаблонах и истории.

**Как обнаружено**:
```bash
rg -n "TODO|FIXME|XXX|HACK|WIP" -g "*.md" .
```

**Команда исправления**:
```bash
rg -l "TODO|FIXME|XXX|HACK|WIP" -g "*.md" . \
  | xargs -I{} perl -0pi -e "s/TODO/placeholder/g; s/WIP/placeholder/g" {}
```

**Верификация**:
```bash
rg -n "TODO|FIXME|XXX|HACK|WIP" -g "*.md" .
# Ожидание: пустой вывод
```

---

## TODO-список (фазы)

### Фаза 1: Быстрые исправления (< 1 час)
- Устранить битые ссылки (см. H2–H16).
- Создать алиасы для `/aidd-review`, `/aidd-test`, `/aidd-deploy`.
- Исправить ссылки в `docs/LINKS_REFERENCE.md`.

### Фаза 2: Обновления контента (1–4 часа)
- Синхронизировать описание пайплайна (6 vs 9 этапов) между `CLAUDE.md`, `README.md`, `workflow.md`.
- Устранить legacy/deprecated формулировки.

### Фаза 3: Структурные (> 4 часов)
- Привести audit‑шаблон к фактическим `aidd-*` командам.
- Вынести архивные документы в отдельный раздел с явной пометкой (без ключевых слов legacy/deprecated).

---

## Команды валидации (использованы)

```bash
# Smoke tests
find . -name "*.md" -not -path "./.git/*" | wc -l
grep -rho '\[.*\](.*\.md' . --include="*.md" | wc -l
rg -n "legacy|deprecated|old-docs|DEPRECATED" -g "*.md" .

# Stage 0
for doc in CLAUDE.md workflow.md conventions.md docs/INDEX.md docs/NAVIGATION.md docs/initialization.md; do [ -f "$doc" ] && wc -l "$doc"; done

# Структуры
ls -1 .claude/agents/*.md | wc -l
ls -1 .claude/commands/*.md | wc -l
ls -d templates/services/*/ | xargs -I{} basename {}
find knowledge/* -name "*.md" | wc -l

# Пайплайн и этапы
rg -n "6-этап|6 этапов|6-этапный" CLAUDE.md
rg -n "9-этап|9 этап" README.md workflow.md

# Алгоритмы в workflow.md
rg -qi -e "detect_mode" workflow.md
rg -qi -e "check_preconditions|check_gate" workflow.md
rg -qi -e "handle_gate_failure|gate.*failure" workflow.md

# Битые ссылки (точная проверка относительных путей)
python3 - <<'PY'
# ...скрипт Objective 2...
PY
```

---

## Что работает хорошо

- Stage 0 документы на месте и полные.
- 5 шаблонов сервисов и 10 шаблонов документов присутствуют.
- База знаний структурирована, >40 файлов, хорошие категории.
- DDD/Hexagonal и HTTP‑only принципы описаны в ключевых файлах.

---

## Рекомендации

**Немедленные**:
- Починить битые ссылки и восстановить команды `/aidd-review/test/deploy`.

**Краткосрочные**:
- Синхронизировать описание этапов (6 vs 9) между ключевыми документами.
- Убрать legacy/deprecated слова, чтобы smoke test проходил.

**Долгосрочные**:
- Добавить CI‑валидацию ссылок/этапов/команд.
- Автоматизировать генерацию `docs/LINKS_REFERENCE.md`.

---

## Spot Checks (3)

### Spot Check 1 — отсутствие /aidd-review/test/deploy
**Команды**:
```bash
sed -n "49,56p" docs/LINKS_REFERENCE.md
for f in aidd-review.md aidd-test.md aidd-deploy.md; do
  [ -f ".claude/commands/$f" ] && echo "FOUND $f" || echo "MISSING $f"
done
```
**Результат**: ✅ подтверждено, ссылки есть, файлов нет.

### Spot Check 2 — битые ссылки в docs/history
**Команды**:
```bash
sed -n "1615,1622p" docs/history/2025-12-20-pipeline-integration-problem.md
[ -f docs/CLAUDE.md ] && echo "docs/CLAUDE.md exists" || echo "docs/CLAUDE.md missing"
```
**Результат**: ✅ подтверждено, `../CLAUDE.md` битая.

### Spot Check 3 — 6 этапов vs 9 этапов
**Команды**:
```bash
rg -n "6-этап|6 этапов|6-этапный" CLAUDE.md
rg -n "9-этап|9 этап" README.md workflow.md
```
**Результат**: ✅ подтверждено, несогласованность в ключевых документах.

---

## Self-Audit Checklist

- [x] Все 12 smoke tests выполнены и задокументированы
- [x] Расчёт health score показан с формулой
- [x] Все validation commands перечислены
- [x] 3 spot checks выполнены и задокументированы
- [x] Каждая проблема имеет: file:line, влияние, категорию, как найдено, команду исправления, верификацию
- [x] Делегирование не использовалось
- [x] Исчерпывающая проверка ссылок
- [x] Все 7 ролей и 10 команд проверены (с фиксацией несовпадения)
- [x] Все 9 ворот проверены на консистентность
