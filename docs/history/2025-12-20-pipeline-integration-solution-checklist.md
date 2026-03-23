# Pipeline Integration Problem Solution Checklist

**Version**: 1.0
**Created**: 2025-12-21
**Related document**: [2025-12-20-pipeline-integration-problem.md](2025-12-20-pipeline-integration-problem.md)
**Chosen option**: C — Extracting the useful (recommended)

---

## Overall Progress

```
Completed: 0/28 tasks (0%)
```

---

## STAGE 1: Creating Missing Files

### 1.1 Create docs/INDEX.md

**Goal**: A unified documentation index for quick AI agent navigation

| # | Task | Status | Date |
|---|------|--------|------|
| 1.1.1 | [ ] Create file `docs/INDEX.md` | Pending | |
| 1.1.2 | [ ] Add "Quick Start" section (CLAUDE.md, workflow.md, conventions.md) | Pending | |
| 1.1.3 | [ ] Add "Agent Roles" section (links to .claude/agents/*.md) | Pending | |
| 1.1.4 | [ ] Add "Slash Commands" section (links to .claude/commands/*.md) | Pending | |
| 1.1.5 | [ ] Add "Knowledge Base" section (links to knowledge/*) | Pending | |
| 1.1.6 | [ ] Add "Templates" section (links to templates/*) | Pending | |
| 1.1.7 | [ ] Add "Project Documents" section (prd/, architecture/, reports/) | Pending | |
| 1.1.8 | [ ] Validate all links in INDEX.md | Pending | |

**Completion criterion**: AI agent can find any document in 2 steps (CLAUDE.md → INDEX.md → file)

---

### 1.2 Create docs/LINKS_REFERENCE.md

**Goal**: Table of all internal links and aliases

| # | Task | Status | Date |
|---|------|--------|------|
| 1.2.1 | [ ] Create file `docs/LINKS_REFERENCE.md` | Pending | |
| 1.2.2 | [ ] Add alias table (short name → full path) | Pending | |
| 1.2.3 | [ ] Add link categorization by topics | Pending | |
| 1.2.4 | [ ] Add usage instructions for AI agent | Pending | |

**Completion criterion**: Unified reference of all file paths

---

### 1.3 Create docs/reference/deliverables-catalog.md

**Goal**: Catalog of all artifacts with templates and readiness criteria

| # | Task | Status | Date |
|---|------|--------|------|
| 1.3.1 | [ ] Create directory `docs/reference/` (if doesn't exist) | Pending | |
| 1.3.2 | [ ] Create file `docs/reference/deliverables-catalog.md` | Pending | |
| 1.3.3 | [ ] Add "Idea" stage artifacts (PRD) | Pending | |
| 1.3.4 | [ ] Add "Architecture" stage artifacts (plan) | Pending | |
| 1.3.5 | [ ] Add "Implementation" stage artifacts (code, tests) | Pending | |
| 1.3.6 | [ ] Add "Review" stage artifacts (report) | Pending | |
| 1.3.7 | [ ] Add "QA" stage artifacts (qa-report) | Pending | |
| 1.3.8 | [ ] Add "Validation" stage artifacts (RTM, validation-report) | Pending | |
| 1.3.9 | [ ] For each artifact specify: template, readiness criteria, example | Pending | |

**Completion criterion**: AI agent knows what artifacts to create at each stage

---

## STAGE 2: Extending workflow.md

### 2.1 Add Navigation Matrix

**Goal**: Explicit table "role → which documents to read → which to create"

| # | Task | Status | Date |
|---|------|--------|------|
| 2.1.1 | [ ] Add Navigation Matrix for Analyst role | Pending | |
| 2.1.2 | [ ] Add Navigation Matrix for Researcher role | Pending | |
| 2.1.3 | [ ] Add Navigation Matrix for Architect role | Pending | |
| 2.1.4 | [ ] Add Navigation Matrix for Implementer role | Pending | |
| 2.1.5 | [ ] Add Navigation Matrix for Reviewer role | Pending | |
| 2.1.6 | [ ] Add Navigation Matrix for QA role | Pending | |
| 2.1.7 | [ ] Add Navigation Matrix for Validator role | Pending | |

**Navigation Matrix format**:
```
| Command | Role | Reads | Creates | Gates |
|---------|------|-------|---------|-------|
| /idea   | Analyst | CLAUDE.md, conventions.md, ... | docs/prd/{name}-prd.md | PRD_READY |
```

**Completion criterion**: Each slash command has an explicit file list

---

## STAGE 3: Updating CLAUDE.md

### 3.1 Add INDEX Links

| # | Task | Status | Date |
|---|------|--------|------|
| 3.1.1 | [ ] Add INDEX.md link to "Reading Order" | Pending | |
| 3.1.2 | [ ] Add "How to Find the Right Document" section | Pending | |
| 3.1.3 | [ ] Add LINKS_REFERENCE.md link | Pending | |
| 3.1.4 | [ ] Add deliverables-catalog.md link | Pending | |

**Completion criterion**: CLAUDE.md contains paths to all key references

---

## STAGE 4: Decision on .ai-framework

### 4.1 Determine fate of .ai-framework/

| # | Task | Status | Date |
|---|------|--------|------|
| 4.1.1 | [ ] Verify all useful content has been extracted | Pending | |
| 4.1.2 | [ ] DECISION: Keep as reference OR remove | Pending | |
| 4.1.3 | [ ] If keeping: mark as "advanced reference" in CLAUDE.md | Pending | |
| 4.1.4 | [ ] If removing: execute `rm -rf .ai-framework/` | Pending | |

**Completion criterion**: No framework duplication, unambiguous source of truth

---

## STAGE 5: Validation and Testing

### 5.1 Integrity Check

| # | Task | Status | Date |
|---|------|--------|------|
| 5.1.1 | [ ] Validate all internal links (no broken ones) | Pending | |
| 5.1.2 | [ ] Verify AI agent finds files in 2 steps | Pending | |
| 5.1.3 | [ ] Update docs/history/2025-12-20-documentation-problems.md | Pending | |
| 5.1.4 | [ ] Close related issues | Pending | |

**Completion criterion**: All problems from pipeline-integration-problem.md resolved

---

## Successful Completion Criteria

After completing all tasks, the following results must be achieved:

| # | Criterion | Check | Status |
|---|-----------|-------|--------|
| 1 | [ ] AI agent can find any file in 2 steps | CLAUDE.md → INDEX.md → file | |
| 2 | [ ] Pipeline is unambiguous | Navigation Matrix for each command | |
| 3 | [ ] No duplication | Single source of truth | |
| 4 | [ ] Gates are verifiable | Measurable criteria in deliverables-catalog | |
| 5 | [ ] All links valid | No 404 on navigation | |

---

## Execution Priorities

```
HIGH PRIORITY (blocks AI work):
├── 1.1 INDEX.md
├── 2.1 Navigation Matrix
└── 3.1 Updating CLAUDE.md

MEDIUM PRIORITY (improves quality):
├── 1.2 LINKS_REFERENCE.md
└── 1.3 deliverables-catalog.md

LOW PRIORITY (finishing actions):
├── 4.1 Decision on .ai-framework
└── 5.1 Validation
```

---

## Change History

| Date | Author | Change |
|------|--------|--------|
| 2025-12-21 | AI Agent | Checklist created |

---

## How to Mark Completed Tasks

1. Change `[ ]` to `[x]` in the corresponding line
2. Change `Pending` to `Done`
3. Add completion date to the "Date" column
4. Update the progress bar at the beginning of the document

**Example**:
```markdown
Before:  | 1.1.1 | [ ] Create file docs/INDEX.md | Pending | |
After:   | 1.1.1 | [x] Create file docs/INDEX.md | Done | 2025-12-21 |
```
