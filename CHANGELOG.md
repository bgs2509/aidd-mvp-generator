# Changelog

All notable changes to AIDD-MVP Generator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### 💥 Breaking Changes

#### Обновление команд v2 → v3

Все slash-команды теперь используют префикс `/aidd-*` для лучшей совместимости и идентификации.

**Миграция команд**:
- `/init` → `/aidd-init`
- `/idea` → `/aidd-analyze`
- `/research` → `/aidd-research`
- `/plan` → `/aidd-plan`
- `/feature-plan` → `/aidd-plan-feature`
- `/generate` → `/aidd-code`
- `/review`, `/test`, `/deploy`, `/finalize` → `/aidd-validate` (объединено)

**Обновлённые файлы**:
- 8 файлов команд (`.claude/commands/aidd-*.md`) — заголовки и примеры
- `templates/project/CLAUDE.md.template` — таблица команд (9 → 6)
- `docs/PIPELINE-TREE.md`, `docs/initialization.md` — документация
- `knowledge/quality/quality-cascade.md` — диаграммы
- `.claude/agents/analyst.md` — примеры

**Commit**: 072ce34

### ✨ Added

#### CHANGELOG.md для целевых проектов

Реализован автоматический механизм ведения журнала изменений в целевых проектах.

**Ключевые возможности**:
- **Автоматическая генерация** при `/aidd-init`:
  - Создание из шаблона для новых проектов
  - Генерация из `features_registry` для существующих проектов
- **Автоматическое обновление** при `/aidd-validate` → DEPLOYED:
  - Извлечение данных из Completion Report
  - Добавление секции фичи в обратной хронологии
  - Обновление секции `[Unreleased]`
- **Ручные записи** для критических изменений:
  - Breaking Changes
  - Security Fixes
  - Hotfix
  - Database Migrations
  - Dependency Updates
  - Configuration Changes
  - Значительный Refactoring
- **Обязательное чтение** AI перед любой работой (правило в CLAUDE.md ЦП)

**Новые файлы**:
- `templates/documents/changelog-template.md` — базовый шаблон
- `templates/documents/changelog-entry-template.md` — 7 шаблонов записей

**Обновлённые файлы**:
- `templates/project/CLAUDE.md.template` — добавлены правила ведения CHANGELOG
- `.claude/commands/aidd-init.md` — создание CHANGELOG.md
- `.claude/commands/aidd-validate.md` — автоматическое обновление
- `docs/target-project-structure.md` — документация структуры
- `CLAUDE.md` — описание концепции

**Формат**: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

**Commit**: e82a8c6

---

## [4.0.0] - 2026-01-29

### 🔥 Removed - Immediate Deprecation (BREAKING CHANGES)

**Phase 3 Complete**: All legacy naming removed. Unified system based on 5 keywords:
**analyst, researcher, planner, coder, validator**

#### Removed Legacy Commands
- ❌ `/aidd-idea` → Use `/aidd-analyze`
- ❌ `/aidd-generate` → Use `/aidd-code`
- ❌ `/aidd-finalize` → Use `/aidd-validate`
- ❌ `/aidd-feature-plan` → Use `/aidd-plan-feature`

#### Removed Legacy Agent Files
- ❌ `architect.md` → Use `planner.md`
- ❌ `implementer.md` → Use `coder.md`

#### Changed Default Naming Version
- **v3 is now default** for all new projects
- `naming_version: "v3"` in `.pipeline-state.json`
- New artifact structure: `_analysis/`, `_research/`, `_plans/`, `_validation/`
- Removed file name duplication: `{name}.md` instead of `{name}-prd.md`

#### Removed Migration Support
- ❌ `gate_aliases` removed from `.pipeline-state.json` (no longer needed)
- Migration Mode (v2.4) documentation removed
- Dual naming references removed from all documentation

### 🔄 Changed

#### Documentation (82 files updated)
- Updated all command references to new naming
- Updated all role names: Архитектор → Планировщик, Реализатор → Программист
- Updated all artifact paths to v3 structure
- Removed migration mode disclaimers
- Simplified all tables (no dual naming columns)

#### Critical Files Updated
- `CLAUDE.md` - Main entry point (migration mode section removed)
- `README.md` - Project README (deprecation notice removed)
- `workflow.md` - 6-stage process (all v2 references removed)
- `docs/INDEX.md` - Navigation hub (role names updated)
- `templates/documents/pipeline-state-template.json` - v3 as default

### ✅ Migration Path

**For existing projects:**

**Option 1: Continue with v2 (deprecated but functional)**
```bash
# Just update commands:
# /aidd-idea → /aidd-analyze
# /aidd-generate → /aidd-code
# /aidd-finalize → /aidd-validate
```

**Option 2: Migrate to v3 (recommended)**
```bash
python3 .aidd/scripts/migrate-naming-v3.py
```

**For new projects:**
- v3 is default
- Only new commands available
- Clean artifact structure from the start

### 📚 Documentation

- Added migration guide: `docs/migration-guide-v4.md`
- Updated: `CLAUDE.md`, `README.md`, `workflow.md`, `docs/INDEX.md`
- Automated replacement: 82 markdown files (942 insertions, 942 deletions)

### 📊 Metrics

- **6 files** deleted (4 commands + 2 agents)
- **82 files** updated (automated sed replacement)
- **5 files** manually reviewed (CLAUDE.md, README.md, workflow.md, docs/INDEX.md, pipeline-state-template.json)
- **~2800 lines** of legacy code removed
- **~2000 lines** of documentation updated

### 🔗 References

- Migration guide: `docs/migration-guide-v4.md`
- Phase 3 plan: `/home/bgs/.claude/plans/zazzy-wishing-panda.md`
- Previous migration completion: `contributors/2026-01-19-phase2-completion-summary.md`

### ⚠️ Breaking Changes

**This release contains BREAKING CHANGES. All users must update their workflows:**

1. **Legacy commands removed** - update all scripts and documentation
2. **Legacy agent files removed** - framework will use only new names
3. **v3 is default** - new projects use new naming automatically
4. **No backward compatibility** - old command names will not work

**Upgrade carefully and test thoroughly!**

---

## [2.4.0] - 2026-01-19

### ✨ Added - Migration Mode

**Phase 2 Complete**: Full migration mode support for naming conventions

#### New Commands (aliases, fully functional)
- `/aidd-analyze` - alias for `/aidd-idea` (PRD creation)
- `/aidd-code` - alias for `/aidd-generate` (code generation)
- `/aidd-validate` - alias for `/aidd-finalize` (quality & deploy)
- `/aidd-plan-feature` - alias for `/aidd-feature-plan` (feature planning)

#### New Agent Roles (aliases, fully functional)
- `planner.md` - alias for `planner.md`
- `coder.md` - alias for `coder.md`

#### Artifact Structure Versioning
- `naming_version` field in `.pipeline-state.json` controls artifact paths
- **v2 (default)**: Old structure - `prd/`, `architecture/`, `plans/`, `reports/`
- **v3 (opt-in)**: New structure - `_analysis/`, `_plans/`, `_validation/`

#### Migration Tools
- `scripts/migrate-naming-v3.py` - automated migration from v2 to v3
  - Renames artifact folders
  - Removes duplication in filenames (`{name}-prd.md` → `{name}.md`)
  - Updates `.pipeline-state.json`
  - Updates references in documents

#### Documentation
- Updated all command files to support `naming_version`
- Added migration guide: `docs/naming-v3-implementation.md`
- Added completion summary: `contributors/2026-01-19-phase2-completion-summary.md`
- Updated roles map: `contributors/2026-01-19-aidd-roles-commands-artifacts-map.md`
- Updated `CLAUDE.md` with migration mode section

### 🔄 Changed

#### Commands
All commands now check `naming_version` and create artifacts accordingly:
- `/aidd-analyze` (ea568ca) - `prd/` → `_analysis/`
- `/aidd-research` (c0ec969) - `research/` → `_research/`
- `/aidd-plan` (f9c810e) - `architecture/` → `_plans/mvp/`
- `/aidd-plan-feature` (6e84bbc) - `plans/` → `_plans/features/`
- `/aidd-validate` (e56630d) - `reports/` → `_validation/`

#### File Naming Convention
- **v2**: Duplication in names - `{date}_{FID}_{slug}-prd.md`, `{slug}-plan.md`
- **v3**: No duplication - `{date}_{FID}_{slug}.md`

### ✅ Backward Compatibility

- **100% backward compatible** - no breaking changes
- All old commands continue to work
- All old role files continue to work
- Existing v2 projects work without modification
- Can use old and new command names interchangeably

### 📊 Metrics

- **5/5 commands** support dual-mode (100%)
- **2/2 roles** have aliases (planner, coder)
- **6 commits** in Phase 2.3
- **~300+ lines** of documentation updated
- **8 files** modified (5 commands + 2 docs + 1 script)

### 🔗 References

- Full plan: `/home/bgs/.claude/plans/idempotent-drifting-wirth.md`
- Implementation guide: `docs/naming-v3-implementation.md`
- Phase 2 summary: `contributors/2026-01-19-phase2-completion-summary.md`

---

## [2.3.0] - 2026-01-14

### Added
- Completion Report (single document instead of 4 separate files)
- Two modes for `/aidd-finalize`: Full (production-ready) and Quick (draft)
- Plan verification procedure in implementer role
- Documentation on validator Quick and Full modes

### Changed
- Consolidated review-report, qa-report, rtm, and documentation into single Completion Report
- Updated workflow to support starting new features without waiting for DEPLOYED gate

### Documentation
- Updated CLAUDE.md and workflow.md for two-mode `/aidd-finalize`
- Added Quick and Full modes description to validator documentation
- Updated pipeline documentation

---

## [2.2.0] - 2025-12-25

### Added
- Pipeline State v2: Support for parallel pipelines
- Git integration: Feature-based branching (feature/{FID}-{slug})
- Features registry: Deployed features tracking
- Gate isolation: `active_pipelines[FID].gates` instead of global `gates`
- Context auto-detection by current git branch

### Changed
- `.pipeline-state.json` structure: Added `active_pipelines` and `features_registry`
- All commands now work with parallel features
- Feature context determined automatically from git branch

### Documentation
- Added `knowledge/pipeline/git-integration.md`
- Added `knowledge/pipeline/state-v2.md`
- Updated workflow documentation for parallel development

---

## [2.1.0] - 2025-12-23

### Added
- HTTP-only architecture enforcement in Data APIs
- Log-driven design documentation
- Security checklist
- Secrets management guidelines

### Changed
- Business APIs must use Data API via HTTP (no direct DB access)
- Enhanced validator role with security checks

---

## [2.0.0] - 2025-12-15

### Added
- 6-stage pipeline with quality gates
- 7 AI agent roles (Analyst, Researcher, Architect, Implementer, Validator, Reviewer, QA)
- Quality Cascade (16 checks across roles)
- DDD/Hexagonal architecture
- HTTP-only data access pattern
- Template system for services
- Knowledge base system

### Changed
- Complete rewrite of generation system
- Maturity level fixed at Level 2 (MVP)
- Unified conventions and documentation

---

## [1.0.0] - 2025-11-01

Initial release with basic MVP generation capabilities.

---

## Legend

- ✨ Added - New features
- 🔄 Changed - Changes in existing functionality
- 🐛 Fixed - Bug fixes
- ⚠️ Deprecated - Soon-to-be removed features
- 🔥 Removed - Removed features
- 🔒 Security - Security fixes
- 📊 Metrics - Performance or quality metrics
- 🔗 References - Links to related documents
- ✅ Backward Compatibility - Compatibility notes
