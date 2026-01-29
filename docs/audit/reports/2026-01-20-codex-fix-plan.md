# План исправления (только реальные проблемы)

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


Дата: 2026-01-20

Ниже — план исправлений, сгруппированный и отсортированный по именам файлов, которые нужно править.

## .claude/commands/aidd-analyze.md

- Удалить или заменить ссылки на несуществующие артефакты:
  - `../prd/2024-12-23_F001_table-booking-prd.md`
  - `../_analysis/2024-12-23_F001_table-booking.md`
- Вариант исправления: заменить на реально существующий пример или на нейтральный placeholder без markdown‑ссылки (например, кодовый путь в inline‑коде).
- Верификация: `rg -n "2024-12-23_F001_table-booking" .claude/commands/aidd-analyze.md`

## .claude/commands/aidd-analyze.md

- Заменить ссылку на несуществующий PRD `../prd/2024-12-23_F001_table-booking-prd.md`.
- Вариант исправления: указать существующий пример или сделать ссылку текстом без markdown.
- Верификация: `rg -n "2024-12-23_F001_table-booking-prd" .claude/commands/aidd-analyze.md`

## CLAUDE.md

- Согласовать описание этапов с фактическим процессом (6 этапов 0–5) или обновить на 9 этапов (0–8) в зависимости от принятой схемы.
- Верификация: `rg -n "6-этап|6 этапов|9-этап|9 этап" ../../../CLAUDE.md`

## README.md

- Устранить упоминания `/aidd-review`, `/aidd-test`, `/aidd-deploy` или добавить официальные алиасы (если решено поддерживать эти команды).
- Согласовать описание этапов с выбранной схемой (6 или 9).
- Верификация:
  - `rg -n "aidd-review|aidd-test|aidd-deploy" README.md`
  - `rg -n "6-этап|6 этапов|9-этап|9 этап" README.md`

## docs/audit/templates/comprehensive-audit.md

- Исправить Smoke Test 7: ожидать команды с префиксом `aidd-`, соответствующие текущей структуре `.claude/commands/`.
- Верификация: `rg -n "COMMANDS=\\(|Smoke Test 7" docs/audit/templates/comprehensive-audit.md`

## docs/history/2025-12-20-pipeline-integration-problem.md

- Исправить синтаксис ссылок в секции "Быстрый старт" (сейчас ` [CLAUDE.md]../../CLAUDE.md ` без круглых скобок).
- Привести ссылки к корректному markdown‑виду: `[CLAUDE.md](../../CLAUDE.md)` и аналогично для `workflow.md`, `conventions.md`.
- Верификация: визуальный просмотр секции + `rg -n "\\[CLAUDE.md\\]\\(" docs/history/2025-12-20-pipeline-integration-problem.md`

## docs/LINKS_REFERENCE.md

- Устранить расхождение команд: либо заменить `/aidd-review`, `/aidd-test`, `/aidd-deploy` на `/aidd-validate`, либо добавить явное объяснение, что это стадии одной команды.
- Верификация: `rg -n "aidd-review|aidd-test|aidd-deploy" docs/LINKS_REFERENCE.md`

## workflow.md

- Согласовать описание этапов с выбранной схемой (6 или 9).
- Если оставлять 6 этапов, пересмотреть секции, где используются `/aidd-review`, `/aidd-test`, `/aidd-deploy`, чтобы отражали один этап 5 (`/aidd-validate`).
- Верификация:
  - `rg -n "6-этап|6 этапов|9-этап|9 этап" workflow.md`
  - `rg -n "aidd-review|aidd-test|aidd-deploy" workflow.md`
