# Шаблоны записей в CHANGELOG.md

## Шаблон 1: Завершённая фича (DEPLOYED) — автоматическая генерация

```markdown
## [{{FID}}] - {{DEPLOYED_DATE}} — {{TITLE}}

> **Status**: DEPLOYED
> **Services**: {{SERVICES_LIST}}
> **Completion Report**: [{{COMPLETION_REPORT_PATH}}]

### Added
{{#each ADDED}}
- {{this}}
{{/each}}

{{#if CHANGED}}
### Changed
{{#each CHANGED}}
- {{this}}
{{/each}}
{{/if}}

{{#if ADR}}
### Architecture Decisions
{{#each ADR}}
- {{this}}
{{/each}}
{{/if}}

{{#if KNOWN_LIMITATIONS}}
### Known Limitations
{{#each KNOWN_LIMITATIONS}}
- {{this}}
{{/each}}
{{/if}}

{{#if TECH_DEBT}}
### Technical Debt
{{#each TECH_DEBT}}
- {{this}}
{{/each}}
{{/if}}

---
```

## Шаблон 2: Критическое изменение (ручное добавление AI)

### Вариант A: Breaking Change

```markdown
### YYYY-MM-DD - Breaking Change: Краткое описание (до 80 символов)

**Changed**
- Конкретное изменение 1
- Конкретное изменение 2

**Impact**: HIGH
**Migration Guide**: [docs/migrations/название.md]
**Affected**: Описание кто затронут (клиенты API, сервисы и т.д.)
**Commit**: <commit-hash>
**Details**: Issue #N, PR #M

---
```

### Вариант B: Security Fix

```markdown
### YYYY-MM-DD - Security Fix: Краткое описание уязвимости

**Security**
- Конкретное исправление 1
- Конкретное исправление 2

**Impact**: CRITICAL
**Severity**: HIGH (CVSSv3: X.X)
**Affected Services**: `service_name_1`, `service_name_2`
**Affected Versions**: <= FID или <= версия
**Rollback**: `git revert <commit-hash>`
**Details**: Issue #N, Commit <hash>, CVE-YYYY-NNNNN (если есть)

---
```

### Вариант C: Hotfix

```markdown
### YYYY-MM-DD - Hotfix: Краткое описание проблемы

**Fixed**
- Конкретное исправление 1
- Конкретное исправление 2

**Impact**: CRITICAL
**Affected Services**: `service_name_1`, `service_name_2`
**Rollback**: `git revert <commit-hash>`
**Root Cause**: Краткое описание причины
**Details**: Issue #N, Commit <hash>

---
```

### Вариант D: Database Migration

```markdown
### YYYY-MM-DD - Database Migration: Краткое описание

**Changed**
- База данных: добавлена таблица `table_name`
- База данных: добавлен индекс на `column_name`

**Impact**: MEDIUM
**Migration Script**: `migrations/YYYYMMDD_название.sql`
**Rollback Script**: `migrations/YYYYMMDD_название_rollback.sql`
**Affected Services**: `service_name_data`
**Downtime Required**: Yes/No
**Details**: Commit <hash>

---
```

### Вариант E: Dependency Update

```markdown
### YYYY-MM-DD - Dependency Update: package-name X.Y.Z → A.B.C

**Changed**
- Обновлена зависимость `package-name`: X.Y.Z → A.B.C
- [Опционально] Адаптирован код под новое API

**Impact**: LOW/MEDIUM/HIGH
**Breaking Changes**: Yes/No (описать если есть)
**Changelog Link**: https://github.com/org/package/releases/tag/vA.B.C
**Affected Services**: `service_name_1`, `service_name_2`
**Details**: Commit <hash>

---
```

### Вариант F: Configuration Change

```markdown
### YYYY-MM-DD - Configuration: Описание изменения конфигурации

**Changed**
- Добавлена env-переменная `NEW_VAR_NAME`
- Изменено значение по умолчанию `EXISTING_VAR`: old → new

**Impact**: MEDIUM
**Required Env Vars**: `NEW_VAR_NAME=default_value`
**Default Values**: См. `.env.example`
**Affected Services**: `service_name_1`, `service_name_2`
**Migration**: Обновить `.env` файл в продакшене
**Details**: Commit <hash>

---
```

### Вариант G: Refactoring (значительный)

```markdown
### YYYY-MM-DD - Refactoring: Краткое описание рефакторинга

**Changed**
- Переименован модуль `old_name` → `new_name`
- Изменена структура директорий: `old/path` → `new/path`

**Impact**: MEDIUM
**Affected Files**: Список ключевых затронутых файлов
**Migration**: [docs/refactoring/название.md] (если нужна)
**Breaking**: Yes/No (для внутренних импортов)
**Details**: Commit <hash>

---
```

## Критерии выбора шаблона

| Тип изменения | Шаблон | Impact | Обязательность |
|---------------|--------|--------|----------------|
| Ломает обратную совместимость | Breaking Change | HIGH/CRITICAL | MUST |
| Исправление уязвимости | Security Fix | CRITICAL | MUST |
| Критический баг в продакшене | Hotfix | CRITICAL | MUST |
| Изменение схемы БД | Database Migration | MEDIUM/HIGH | MUST |
| Обновление зависимости (major/minor) | Dependency Update | MEDIUM | MUST |
| Новые/изменённые env-переменные | Configuration Change | MEDIUM | MUST |
| Переименование модулей/структуры | Refactoring | MEDIUM | SHOULD |
| Обычный bugfix | — | LOW | OPTIONAL |
| Документация | — | LOW | OPTIONAL |
