# Function: Initialization (Stage 0)

> **Purpose**: Loading the framework context and preparing for work.

---

## Goal

Before starting work, the Analyst MUST load the framework context
and prepare for processing the user's idea.

---

## Document Reading Order

```
1. CLAUDE.md
   └── Main framework rules
   └── Architectural principles
   └── Project structure

2. conventions.md
   └── Code conventions
   └── Documentation style
   └── Naming

3. workflow.md
   └── 9-stage process (0-8)
   └── Quality Gates
   └── Artifacts
```

---

## Determining the Work Mode

```
Check for existing code:

if exists(src/) or exists(services/):
    MODE = FEATURE
    → Create FEATURE_PRD
    → Account for existing architecture
else:
    MODE = CREATE
    → Create full PRD
    → Design from scratch
```

---

## Critical Rules

### 1. Context is Mandatory

```
❌ WRONG: Start working without reading CLAUDE.md
✅ CORRECT: Read CLAUDE.md → understand context → start working
```

### 2. Maturity Level

The AIDD-MVP Generator framework ALWAYS creates **Level 2 (MVP)**:
- Docker-compose + dev overrides
- Structured logging
- Test coverage ≥75%
- ~10 minutes for generation

### 3. Documentation Language

All artifacts are created in **Russian**:
- PRD in Russian
- Docstrings in Russian
- Comments in Russian

---

## Initialization Checklist

- [ ] CLAUDE.md read
- [ ] conventions.md read
- [ ] workflow.md read
- [ ] Work mode determined (CREATE/FEATURE)
- [ ] Maturity level understood (Level 2 MVP)
- [ ] Ready to process the idea

---

## Sources

| Document | Description |
|----------|-------------|
| [CLAUDE.md](../../CLAUDE.md) | Main framework entry point |
| [docs/initialization.md](../../docs/initialization.md) | Initialization algorithm (4 phases) |
