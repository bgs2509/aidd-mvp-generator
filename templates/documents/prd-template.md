---
# === YAML Frontmatter (machine-readable metadata) ===
# Filled automatically when the artifact is created

feature_id: "{FID}"                    # F001, F002, ... (auto-generated)
feature_name: "{slug}"                 # kebab-case, <=30 characters
title: "{Project/Feature Name}"
created: "{YYYY-MM-DD}"                # Creation date
author: "AI (Analyst)"
type: "prd"
status: "PRD_READY"                    # Draft → PRD_READY
version: 1
mode: "{CREATE|FEATURE}"

# Optional (filled as work progresses)
related_features: []                   # [F001, F003] — related features
services: []                           # [booking_api, booking_data]
requirements_count: 0                  # Number of FR-* requirements

# Pipelines
pipelines:
  business: true                       # Has business pipeline
  data: true                           # Has data pipeline
  integration: true                    # Has integrations
  modified: []                         # [pipeline1, pipeline2] — for FEATURE
---

# PRD: {Project/Feature Name}

**Feature ID**: {FID}
**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Author**: AI Agent (Analyst)
**Status**: Draft | Review | Approved

---

## 1. Overview

### 1.1 Problem

{Description of the problem the project/feature solves}

- What pain does the user experience?
- Why is the current solution unsatisfactory?
- What are the consequences of an unsolved problem?

### 1.2 Solution

{Brief description of the proposed solution}

- How does the solution address the problem?
- Key components of the solution
- Expected outcome

### 1.3 Target Audience

| Segment | Description | Needs |
|---------|-------------|-------|
| {Segment 1} | {Description} | {What they need} |
| {Segment 2} | {Description} | {What they need} |

### 1.4 Value Proposition

{Why the user will choose this solution}

---

## 2. Functional Requirements

### 2.1 Core Features (Must Have)

| ID | Name | Description | Acceptance Criteria |
|----|------|-------------|---------------------|
| FR-001 | {Name} | {Detailed function description} | {How to verify it is implemented} |
| FR-002 | {Name} | {Detailed function description} | {How to verify it is implemented} |
| FR-003 | {Name} | {Detailed function description} | {How to verify it is implemented} |

### 2.2 Important Features (Should Have)

| ID | Name | Description | Acceptance Criteria |
|----|------|-------------|---------------------|
| FR-010 | {Name} | {Detailed function description} | {How to verify it is implemented} |
| FR-011 | {Name} | {Detailed function description} | {How to verify it is implemented} |

### 2.3 Nice to Have (Could Have)

| ID | Name | Description | Acceptance Criteria |
|----|------|-------------|---------------------|
| FR-020 | {Name} | {Detailed function description} | {How to verify it is implemented} |

---

## 3. User Stories

### US-001: {Story Name}

**As a** {user role}
**I want to** {action}
**So that** {goal/benefit}

**Acceptance criteria:**
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] {Criterion 3}

**Related requirements:** FR-001, FR-002

---

### US-002: {Story Name}

**As a** {user role}
**I want to** {action}
**So that** {goal/benefit}

**Acceptance criteria:**
- [ ] {Criterion 1}
- [ ] {Criterion 2}

**Related requirements:** FR-003

---

## 4. Pipelines

### 4.0 Change Type

| Parameter | Value |
|-----------|-------|
| Mode | CREATE (new) / FEATURE (modification) |
| Affected pipelines | {list or "all new"} |

### 4.1 Business Pipeline

> Sequence of business operations and entity states

**Main flow:**

```
[Event] → [Validation] → [Processing] → [Result] → [Notification]
```

| # | Stage | Description | Transition Conditions | Result |
|---|-------|-------------|----------------------|--------|
| 1 | {Stage} | {What happens} | {When to transition} | {What we get} |

**Entity states:**

| Entity | States | Transitions |
|--------|--------|-------------|
| {Entity} | draft → pending → confirmed → completed | {Transition rules} |

### 4.2 Data Pipeline

> Data flow between system components

**Data flow diagram:**

```
┌─────────┐     HTTP      ┌─────────────┐     HTTP     ┌──────────┐
│ Client  │ ────────────▶ │ Business API│ ───────────▶ │ Data API │
└─────────┘               └─────────────┘              └──────────┘
                                │                            │
                                │ async                      │ SQL
                                ▼                            ▼
                          ┌──────────┐               ┌────────────┐
                          │  Queue   │               │ PostgreSQL │
                          └──────────┘               └────────────┘
                                │
                                ▼
                          ┌──────────┐
                          │  Worker  │
                          └──────────┘
```

| # | Source | Destination | Data | Format | Synchronicity |
|---|--------|-------------|------|--------|---------------|
| 1 | {From} | {To} | {What is transferred} | JSON/Protobuf | sync/async |

**Data transformations:**

| # | Point | Input Data | Transformation | Output Data |
|---|-------|------------|----------------|-------------|
| 1 | {Where} | {Input DTO} | {What is done} | {Output DTO} |

### 4.3 Integration Pipeline

> Interaction between services and external systems

**Service map:**

```
┌─────────────────────────────────────────────────────────────┐
│                          SYSTEM                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐       ┌──────────────┐                    │
│  │ Business API │◄─────►│   Data API   │                    │
│  └──────┬───────┘       └──────────────┘                    │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐       ┌──────────────┐                    │
│  │ Telegram Bot │       │    Worker    │                    │
│  └──────────────┘       └──────────────┘                    │
└─────────────────────────────────────────────────────────────┘
          │                       │
          ▼                       ▼
    ┌───────────┐          ┌────────────┐
    │ Telegram  │          │ External   │
    │    API    │          │  Service   │
    └───────────┘          └────────────┘
```

**Integration points:**

| ID | From | To | Protocol | Endpoint | Description |
|----|------|----|----------|----------|-------------|
| INT-001 | Business API | Data API | HTTP/REST | /api/v1/* | CRUD operations |
| INT-002 | Bot | Business API | HTTP/REST | /api/v1/* | Bot commands |
| INT-003 | Worker | External | HTTP/REST | {URL} | {Description} |

**API contracts:**

| Integration | Request | Response | Errors |
|-------------|---------|----------|--------|
| INT-001 | {Schema} | {Schema} | 4xx, 5xx |

### 4.4 Impact on Existing Pipelines

> Filled in ALWAYS. For CREATE: "New system". For FEATURE: change table.

**Mode:** CREATE / FEATURE

**For CREATE:**
```
New system — no existing pipelines.
All pipelines are created from scratch per sections 4.1-4.3.
```

**For FEATURE:**

| Pipeline | Change Type | Affected Stages | Backward Compatibility |
|----------|-------------|-----------------|------------------------|
| {Name} | add/modify/remove | {Stages} | Yes/No (reason) |

**Breaking changes:**
- [ ] No breaking changes
- [ ] {Breaking change description and migration plan}

---

## 5. UI/UX Requirements

### 5.1 Screens and Interfaces

| ID | Screen | Description | Priority |
|----|--------|-------------|----------|
| UI-001 | {Screen name} | {Description of purpose and key elements} | Must |
| UI-002 | {Screen name} | {Description of purpose and key elements} | Should |

### 5.2 User Flows

**Flow 1: {Name}**

```
[Start] → [Step 1] → [Step 2] → [Decision?]
                                    ↓ Yes
                              [Step 3] → [End]
                                    ↓ No
                              [Alternative]
```

### 5.3 Accessibility Requirements

- [ ] Keyboard navigation support
- [ ] Text contrast >= 4.5:1
- [ ] Alt text for images
- [ ] Screen reader support

---

## 6. Non-Functional Requirements

### 6.1 Performance

| ID | Metric | Requirement | Measurement |
|----|--------|-------------|-------------|
| NF-001 | API response time | < 200ms (p95) | Prometheus metrics |
| NF-002 | Page load time | < 3s | Lighthouse |
| NF-003 | Throughput | > 100 RPS | Load testing |

### 6.2 Scalability

| ID | Requirement | Description |
|----|-------------|-------------|
| NF-010 | Horizontal scaling | {Description} |
| NF-011 | Expected load | {X users, Y requests} |

### 6.3 Security

| ID | Requirement | Description |
|----|-------------|-------------|
| NF-020 | Authentication | {JWT/OAuth2/etc} |
| NF-021 | Authorization | {RBAC/ABAC/etc} |
| NF-022 | Encryption | {TLS 1.3, data at rest} |
| NF-023 | Logging | {Action audit} |

### 6.4 Reliability

| ID | Metric | Requirement |
|----|--------|-------------|
| NF-030 | Uptime | >= 99.9% |
| NF-031 | RTO | < 1 hour |
| NF-032 | RPO | < 15 minutes |

### 6.5 Testing Requirements

#### Smoke Tests (MANDATORY)
- [ ] 100% of public endpoints have a happy-path test
- [ ] All containers start without errors
- [ ] Health checks respond 200
- [ ] Databases are accessible and responding

#### Unit Tests
- **Required**: {Yes/No}
- **Coverage threshold**: {>=75%/other}
- **Critical modules**: {list}

#### Integration Tests
- **Required**: {Yes/No}
- **Critical pipelines**: {list}
- **Test DBs**: testcontainers for {DB from PRD} (e.g. PostgreSQL)

#### E2E Tests
- **Required**: {Yes/No}
- **Cross-service flow scenarios**: {list}

#### Summary Table

| ID | Type | Requirement | Mandatory |
|----|------|-------------|-----------|
| TRQ-001 | Smoke | 100% endpoints happy-path | ✅ Yes |
| TRQ-002 | Smoke | Containers start | ✅ Yes |
| TRQ-003 | Smoke | Health checks respond 200 | ✅ Yes |
| TRQ-004 | Smoke | Databases accessible | ✅ Yes |
| TRQ-005 | Unit | Coverage >= {threshold} | {Yes/No} |
| TRQ-006 | Integration | Critical pipelines | {Yes/No} |
| TRQ-007 | E2E | End-to-end scenarios | {Yes/No} |

---

## 7. Technical Constraints

### 7.1 Required Technologies

- **Backend**: Python 3.11+, FastAPI
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Container**: Docker, Docker Compose
- **CI/CD**: {tool or "none"}

### 7.2 Integrations

| System | Integration Type | Description |
|--------|-----------------|-------------|
| {System 1} | REST API | {Description} |
| {System 2} | Webhook | {Description} |

### 7.3 Constraints

- {Constraint 1: description and reason}
- {Constraint 2: description and reason}

---

## 8. Assumptions and Risks

### 8.1 Assumptions

| # | Assumption | Impact if Wrong |
|---|-----------|-----------------|
| 1 | {Assumption} | {Consequences} |
| 2 | {Assumption} | {Consequences} |

### 8.2 Risks

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| 1 | {Risk} | High/Med/Low | High/Med/Low | {How to mitigate} |
| 2 | {Risk} | High/Med/Low | High/Med/Low | {How to mitigate} |

---

## 9. Open Questions

| # | Question | Status | Responsible | Resolution |
|---|----------|--------|-------------|------------|
| 1 | {Question} | Open | {Name} | — |
| 2 | {Question} | Resolved | {Name} | {Resolution} |

---

## 10. Glossary

| Term | Definition |
|------|------------|
| {Term 1} | {Definition} |
| {Term 2} | {Definition} |

---

## 11. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | AI Analyst | Initial version |

---

## Quality Gates

### PRD_READY Checklist

- [ ] All sections filled in
- [ ] Requirements have unique IDs (FR-*, NF-*, UI-*, INT-*)
- [ ] Acceptance criteria defined for each requirement
- [ ] User stories linked to requirements
- [ ] Business pipeline described (main flow, entity states)
- [ ] Data Pipeline described (flow diagram, data transformations)
- [ ] Integration pipeline described (service map, integration points, contracts)
- [ ] "Impact on existing pipelines" section filled in
- [ ] No blocking open questions
- [ ] Risks identified and have mitigation plans
- [ ] Document agreed upon with stakeholders
