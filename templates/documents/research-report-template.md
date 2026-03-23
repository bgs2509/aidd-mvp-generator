---
# === YAML Frontmatter (machine-readable metadata) ===
feature_id: "{FID}"
feature_name: "{slug}"
title: "Research: {Project Name}"
created: "{YYYY-MM-DD}"
author: "AI (Researcher)"
type: "research"
status: "RESEARCH_DONE"
version: 1
mode: "{CREATE|FEATURE}"

# Links to related artifacts
prd_ref: "prd/{YYYY-MM-DD}_{FID}_{slug}-prd.md"

# Optional
related_features: []
findings_count: 0                      # Number of key findings
---

# Research Report: {Project Name}

**Feature ID**: {FID}
**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Author**: AI Agent (Researcher)

---

## 1. Context

- **PRD link**: `ai-docs/docs/_analysis/{name}-prd.md`
- **Mode**: {CREATE or FEATURE}
- **Research goals**: {What needs to be determined}

## 2. Requirements Summary

| ID | Type | Brief Description | Criticality |
|----|------|-------------------|-------------|
| FR-001 | FR | {Description} | Must |
| NF-001 | NF | {Description} | High |

## 3. Current State Analysis (FEATURE)

> Filled in if the project already contains code / infrastructure.

### 3.1 Services and Responsibilities

| Service | Purpose | Dependencies |
|---------|---------|--------------|
| {service_name} | {description} | {deps} |

### 3.2 API / Contracts

| Method | Path | Status | Comment |
|--------|------|--------|---------|
| GET | /api/v1/... | OK/Needs change | {notes} |

### 3.3 Data and Storage

- PostgreSQL: {schema/tables}
- MongoDB: {collections}
- Queues / brokers: {description}

### 3.4 Identified Patterns

- DDD/Hexagonal: {Yes/No + where violated}
- CQRS/Event Sourcing: {if present}
- Async workers: {brief}

### 3.5 Constraints and Debt

- {Constraint 1}
- {Constraint 2}

### 3.6 Existing Tests Analysis (FEATURE)

#### 3.6.1 Current State

| Type | Found | Coverage | Path |
|------|-------|----------|------|
| Smoke | {count} | {%} | services/{service}/tests/smoke/ |
| Unit | {count} | {%} | services/{service}/tests/unit/ |
| Integration | {count} | {%} | services/{service}/tests/integration/ |
| E2E | {count} | {%} | tests/e2e/ |

#### 3.6.2 Gaps (what needs to be added)

Based on PRD section 6.5:

| TRQ | Requirement | Current | Needed | Gap |
|-----|-------------|---------|--------|-----|
| TRQ-001 | 100% endpoints smoke | {X}% | 100% | +{Y} tests |
| TRQ-002 | Containers start | {OK/Fail} | OK | {gap} |
| TRQ-003 | Health checks 200 | {X}/{Y} | 100% | +{Y} tests |
| TRQ-004 | Databases accessible | {OK/Fail} | OK | {gap} |
| TRQ-005 | Coverage >= {threshold} | {X}% | {threshold}% | +{Y} tests |
| TRQ-006 | Critical pipelines | {X}/{Y} | 100% | +{Y} tests |
| TRQ-007 | End-to-end scenarios | {X}/{Y} | 100% | +{Y} tests |

#### 3.6.3 Recommendations

- {Which modules need tests}
- {Which dependencies need to be mocked}
- {Which pipelines are critical for integration}

## 4. Technology Conclusions (CREATE)

- Recommended services: {api/bot/data/...}
- DBs and caches: {PostgreSQL/MongoDB/Redis}
- Communication protocol: {HTTP, gRPC is prohibited}

## 5. Integration Recommendations

- {Integration point 1}
- {Integration point 2}

## 6. Risks and Assumptions

- **Risk**: {Description} → {Mitigation measure}
- **Assumption**: {What must be true}

## 7. Next Steps

- [ ] Update `.pipeline-state.json` (`RESEARCH_DONE`)
- [ ] Pass link to architect (`ai-docs/docs/research/{name}-research.md`)

---

**Appendices**: links to branches, diagrams, additional materials.
