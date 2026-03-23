# Function: PRD Formation

> **Purpose**: Creating the final PRD document.

---

## Goal

Collect all requirements into a structured PRD document,
ready for handoff to the architecture stage.

---

## PRD Structure (11 sections)

```markdown
# PRD: {Project Name}

**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Author**: AI Agent (Analyst)
**Status**: Draft | Review | Approved

---

## 1. Overview
### 1.1 Problem
### 1.2 Solution
### 1.3 Target Audience
### 1.4 MVP Scope

## 2. Functional Requirements
| ID | Name | Description | Priority | Acceptance Criteria |

## 3. User Stories
### US-001: {Name}

## 4. Pipelines
### 4.0 Change Type
### 4.1 Business Pipeline
### 4.2 Data Pipeline
### 4.3 Integration Pipeline
### 4.4 Impact on Existing Pipelines

## 5. UI/UX Requirements
| ID | Name | Description | Priority |

## 6. Non-Functional Requirements
| ID | Name | Description | Metric |

## 7. Technical Constraints
## 8. Assumptions and Risks
## 9. Open Questions
## 10. Glossary
## 11. Change History

## Quality Gates
### PRD_READY Checklist
```

---

## Formation Rules

### 1. Overview (Section 1)

```
1.1 Problem:
- Describe the user's pain point
- Why current solutions are inadequate

1.2 Solution:
- How the project solves the problem
- Key advantages

1.3 Target Audience:
- Primary users
- Their characteristics

1.4 MVP Scope:
- What IS INCLUDED in the MVP
- What is NOT INCLUDED (consciously deferred)
```

### 2. Functional Requirements (Section 2)

```
Each requirement:
- Unique ID (FR-001, FR-002, ...)
- Short name
- Detailed description
- Priority (Must/Should/Could)
- Measurable acceptance criteria
```

### 3. Pipelines (Section 4)

```
4.0 Change Type:
- Mode: CREATE (new) / FEATURE (modification)
- Affected pipelines

4.1 Business Pipeline:
- Main operations flow
- Entity states and transitions
- Conditions for transitions between stages

4.2 Data Pipeline:
- Data flow diagram (ASCII)
- Table: source → destination → data → format
- Data transformations

4.3 Integration Pipeline:
- Service map (ASCII)
- Integration points (INT-001, INT-002, ...)
- API contracts (Request/Response/Errors)

4.4 Impact on Existing Pipelines:
- For CREATE: "New system"
- For FEATURE: change table, breaking changes
```

### 4. Non-Functional Requirements (Section 6)

```
Standard set for MVP:
- NF-001: Response time (<500ms)
- NF-002: Availability (99%)
- NF-003: Test coverage (≥75%)
- NF-004: Security (authorization, validation)
```

### 5. Open Questions (Section 9)

```
Questions requiring clarification.
Statuses:
- Open: Requires resolution
- Resolved: Resolved (specify the resolution)

Blocking questions MUST be resolved
before passing the PRD_READY gate.
```

### 6. Change History (Section 11)

```
Document versioning.
Record all significant PRD changes.
```

---

## Save Path (in Target Project)

```
ai-docs/docs/_analysis/{project-name}-prd.md

Examples:
- ai-docs/docs/_analysis/booking-restaurant-prd.md
- ai-docs/docs/_analysis/personal-finance-prd.md
```

For FEATURE mode:
```
ai-docs/docs/_analysis/{feature-name}-feature-prd.md
```

---

## PRD_READY Checklist

- [ ] Section 1 (Overview) filled in
- [ ] Section 2 (FR) contains all requirements
- [ ] Section 3 (User Stories) linked to FR
- [ ] Section 4 (Pipelines) filled in:
  - [ ] Business pipeline described (flow, states)
  - [ ] Data Pipeline described (diagram, transformations)
  - [ ] Integration pipeline described (map, contracts)
  - [ ] Impact on existing pipelines specified
- [ ] Section 5 (UI/UX) filled in (if applicable)
- [ ] Section 6 (NF) contains standard requirements
- [ ] Section 7 (Technical Constraints) filled in
- [ ] Section 8 (Assumptions and Risks) filled in
- [ ] Section 9 (Questions) has no Open blockers
- [ ] All IDs are unique (FR-*, NF-*, UI-*, INT-*)
- [ ] All Must requirements have acceptance criteria
- [ ] Document saved to `ai-docs/docs/_analysis/` (Target Project)

---

## Sources

| Document | Description |
|----------|-------------|
| `.ai-framework/docs/workflows/analyst-workflow.md` | Analyst workflow |
| `.ai-framework/docs/reference/aidd-roles-reference.md` | Roles reference |
| `templates/documents/prd-template.md` | PRD Template |
