# CHANGELOG.md Entry Templates

## Template 1: Completed Feature (DEPLOYED) — automatic generation

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

## Template 2: Critical Change (manual AI entry)

### Variant A: Breaking Change

```markdown
### YYYY-MM-DD - Breaking Change: Brief description (up to 80 characters)

**Changed**
- Specific change 1
- Specific change 2

**Impact**: HIGH
**Migration Guide**: [docs/migrations/name.md]
**Affected**: Description of who is affected (API clients, services, etc.)
**Commit**: <commit-hash>
**Details**: Issue #N, PR #M

---
```

### Variant B: Security Fix

```markdown
### YYYY-MM-DD - Security Fix: Brief vulnerability description

**Security**
- Specific fix 1
- Specific fix 2

**Impact**: CRITICAL
**Severity**: HIGH (CVSSv3: X.X)
**Affected Services**: `service_name_1`, `service_name_2`
**Affected Versions**: <= FID or <= version
**Rollback**: `git revert <commit-hash>`
**Details**: Issue #N, Commit <hash>, CVE-YYYY-NNNNN (if applicable)

---
```

### Variant C: Hotfix

```markdown
### YYYY-MM-DD - Hotfix: Brief problem description

**Fixed**
- Specific fix 1
- Specific fix 2

**Impact**: CRITICAL
**Affected Services**: `service_name_1`, `service_name_2`
**Rollback**: `git revert <commit-hash>`
**Root Cause**: Brief description of the root cause
**Details**: Issue #N, Commit <hash>

---
```

### Variant D: Database Migration

```markdown
### YYYY-MM-DD - Database Migration: Brief description

**Changed**
- Database: added table `table_name`
- Database: added index on `column_name`

**Impact**: MEDIUM
**Migration Script**: `migrations/YYYYMMDD_name.sql`
**Rollback Script**: `migrations/YYYYMMDD_name_rollback.sql`
**Affected Services**: `service_name_data`
**Downtime Required**: Yes/No
**Details**: Commit <hash>

---
```

### Variant E: Dependency Update

```markdown
### YYYY-MM-DD - Dependency Update: package-name X.Y.Z → A.B.C

**Changed**
- Updated dependency `package-name`: X.Y.Z → A.B.C
- [Optional] Adapted code for new API

**Impact**: LOW/MEDIUM/HIGH
**Breaking Changes**: Yes/No (describe if any)
**Changelog Link**: https://github.com/org/package/releases/tag/vA.B.C
**Affected Services**: `service_name_1`, `service_name_2`
**Details**: Commit <hash>

---
```

### Variant F: Configuration Change

```markdown
### YYYY-MM-DD - Configuration: Description of configuration change

**Changed**
- Added env variable `NEW_VAR_NAME`
- Changed default value of `EXISTING_VAR`: old → new

**Impact**: MEDIUM
**Required Env Vars**: `NEW_VAR_NAME=default_value`
**Default Values**: See `.env.example`
**Affected Services**: `service_name_1`, `service_name_2`
**Migration**: Update `.env` file in production
**Details**: Commit <hash>

---
```

### Variant G: Refactoring (significant)

```markdown
### YYYY-MM-DD - Refactoring: Brief refactoring description

**Changed**
- Renamed module `old_name` → `new_name`
- Changed directory structure: `old/path` → `new/path`

**Impact**: MEDIUM
**Affected Files**: List of key affected files
**Migration**: [docs/refactoring/name.md] (if needed)
**Breaking**: Yes/No (for internal imports)
**Details**: Commit <hash>

---
```

## Template Selection Criteria

| Change Type | Template | Impact | Required |
|-------------|----------|--------|----------|
| Breaks backward compatibility | Breaking Change | HIGH/CRITICAL | MUST |
| Vulnerability fix | Security Fix | CRITICAL | MUST |
| Critical production bug | Hotfix | CRITICAL | MUST |
| DB schema change | Database Migration | MEDIUM/HIGH | MUST |
| Dependency update (major/minor) | Dependency Update | MEDIUM | MUST |
| New/changed env variables | Configuration Change | MEDIUM | MUST |
| Module/structure renaming | Refactoring | MEDIUM | SHOULD |
| Regular bugfix | — | LOW | OPTIONAL |
| Documentation | — | LOW | OPTIONAL |
