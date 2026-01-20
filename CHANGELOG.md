# Changelog

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-idea`, `/aidd-generate`, `/aidd-finalize`, `/aidd-feature-plan`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


All notable changes to AIDD-MVP Generator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned for v4.0 (April 2026)
- **BREAKING**: Remove old command names (`/aidd-idea`, `/aidd-generate`, `/aidd-finalize`)
- **BREAKING**: Remove old role files (`architect.md`, `implementer.md`)
- **BREAKING**: Only v3 naming conventions supported
- Require migration to v3 before upgrade

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
- `planner.md` - alias for `architect.md`
- `coder.md` - alias for `implementer.md`

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
