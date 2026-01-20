# Сравнение проблем из аудитов Claude vs Codex

Дата: 2026-01-20

Ниже — таблицы проблем, сгруппированные по типу, затем по важности.
Колонка "Реальность" фиксирует состояние по фактической проверке репозитория.

## Тип: Пайплайн и команды

### CRITICAL

| Проблема | Claude | Codex | Реальность |
|---|---|---|---|
| Audit-шаблон ожидает команды без префикса (`init/idea/...` вместо `aidd-*`) → Smoke Test 7 всегда "провален" | — | ✅ | реальная |
| В README и `docs/LINKS_REFERENCE.md` используются `/aidd-review`, `/aidd-test`, `/aidd-deploy`, но файлов команд нет | — | ✅ | реальная |

### HIGH

| Проблема | Claude | Codex | Реальность |
|---|---|---|---|
| Несогласованность 6 vs 9 этапов между `CLAUDE.md`, `README.md`, `workflow.md` | — | ✅ | реальная |

### MEDIUM

| Проблема | Claude | Codex | Реальность |
|---|---|---|---|
| `/aidd-init` не ссылается на роль | ✅ | — | ошибочная |
| Валидатор "не упоминает этапы 7–8" | — | ✅ | ошибочная |
| Лишние `_DONE`/`_OK` в диаграммах ворот | — | ✅ | ошибочная |

## Тип: Ссылки и навигация

### HIGH

| Проблема | Claude | Codex | Реальность |
|---|---|---|---|
| `aidd-idea.md` → ссылка на PRD `2024-12-23_F001_table-booking-prd.md`, файла нет | — | ✅ | реальная |
| `aidd-analyze.md` → ссылка на PRD `2024-12-23_F001_table-booking-prd.md`, файла нет | — | ✅ | реальная |
| `aidd-analyze.md` → ссылка на `_analysis/2024-12-23_F001_table-booking.md`, файла нет | — | ✅ | реальная |
| `aidd-research/plan/validate` → `_analysis/2024-12-23_F001_table-booking.md` | ✅ | — | спорная (JSON-ример, файл отсутствует) |
| `docs/history/2025-12-20-pipeline-integration-problem.md` — некорректный синтаксис ссылок в "Быстрый старт" | — | ✅ | реальная |
| `docs/history/2025-12-21-documentation-master-todo.md` — некорректный пример ссылки в блоке | — | ✅ | спорная (пример в code-block) |
| `docs/artifact-naming.md` → `prd/2024-12-20_F042_email-notify-prd.md` | — | ✅ | ошибочная (пример в YAML, не markdown-ссылка) |
| `docs/audit/templates/comprehensive-audit.md` → "битая ссылка" из regex в code-block | — | ✅ | ошибочная |
| `contributors/2025-01-13-comprehensive-audit-report-codex.md` → `../../CLAUDE.md` | — | ✅ | ошибочная (команда в code-block) |
| `docs/INDEX.md` → `templates/project/CLAUDE.md` и `README.md` | ✅ | — | ошибочная (фактически `*.template`) |
| `aidd-init.md` → `docs/PIPELINE-TREE.md` | ✅ | — | ошибочная (файл существует) |
| `contributors/2026-01-14-...` → ссылки на `aidd-review/test/deploy` | ✅ | — | ошибочная (упоминания, не markdown-ссылки) |
| `docs/history/...solution-checklist.md` → `2025-12-20-documentation-problems.md` | ✅ | — | ошибочная (файл существует) |

## Тип: Аудит-шаблон, правила качества, терминология

### CRITICAL

| Проблема | Claude | Codex | Реальность |
|---|---|---|---|
| Любые `legacy/deprecated` слова считаются критической ошибкой (Smoke Test 3) | ✅ (как LOW) | ✅ (как CRITICAL) | спорная (формально тест падает, по смыслу часто контекст) |

### MEDIUM

| Проблема | Claude | Codex | Реальность |
|---|---|---|---|
| Относительные пути `../../../` в audit-шаблоне | ✅ | — | ошибочная (пути корректны для текущего расположения) |

### LOW

| Проблема | Claude | Codex | Реальность |
|---|---|---|---|
| TODO/WIP/XXX маркеры в шаблонах | — | ✅ | спорная (placeholder-ы в шаблонах) |
