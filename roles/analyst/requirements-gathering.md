# Function: Requirements Gathering

> **Purpose**: Formalizing requirements from the user's idea.

---

## Goal

Transform a verified idea into a structured set of
functional, non-functional, and UI/UX requirements.

---

## Types of Requirements

### Functional Requirements (FR-*)

**What the system should do.**

```
FR-{NNN}: {Short name}
Description: {Detailed function description}
Priority: Must | Should | Could
Acceptance criteria: {How to verify the requirement is met}
```

**Examples**:
```
FR-001: Restaurant search
Description: User can search restaurants by name, cuisine type, and location
Priority: Must
Acceptance criteria: Search returns relevant results in <2 seconds
```

### Non-Functional Requirements (NF-*)

**How the system should work.**

```
NF-{NNN}: {Short name}
Description: {Quality/performance requirement}
Metric: {Measurable indicator}
```

**Examples**:
```
NF-001: API response time
Description: API should respond quickly
Metric: 95th percentile < 500ms
```

### UI/UX Requirements (UI-*)

**Interface requirements.**

```
UI-{NNN}: {Short name}
Description: {Interface requirement}
Priority: Must | Should | Could
```

**Examples**:
```
UI-001: Restaurant list display
Description: Search results displayed as cards with photo, name, rating
Priority: Must
```

### Integration Points (INT-*)

**Where the system interacts with other components.**

```
INT-{NNN}: {Short name}
From: {Source service}
To: {Target service/system}
Protocol: HTTP/REST | Webhook | gRPC | Event Bus
Description: {Contract, data, error handling}
```

**Examples**:
```
INT-001: Business API → Data API
From: booking_api
To: booking_data
Protocol: HTTP/REST
Description: CRUD operations with bookings, JSON, retry on 5xx

INT-002: Bot → Business API
From: booking_bot
To: booking_api
Protocol: HTTP/REST
Description: Bot commands, JSON, timeout 30s

INT-003: Worker → External Service
From: notification_worker
To: Telegram API
Protocol: HTTP/REST
Description: Sending notifications, exponential backoff on errors
```

---

## Prioritization (MoSCoW)

| Priority | Description | For MVP |
|----------|-------------|---------|
| **Must** | Mandatory for MVP | Yes |
| **Should** | Important but not critical | Partially |
| **Could** | Desirable if time allows | No |
| **Won't** | Not in this release | No |

For **Level 2 (MVP)** we include:
- All **Must** requirements
- Core **Should** requirements

---

## Gathering Process

### Step 1: Extracting Functions

```
From the idea description, extract:
1. Main user actions
2. Data objects
3. Interactions between objects
```

### Step 2: Formulating FR

```
For each action:
- Formulate FR-{NNN}
- Determine priority
- Describe acceptance criteria
```

### Step 3: Defining NF

```
Standard NF for MVP:
- NF-001: API response time (<500ms)
- NF-002: Availability (99%)
- NF-003: Test coverage (≥75%)
```

### Step 4: Defining UI

```
For each screen/command:
- Formulate UI-{NNN}
- Determine priority
```

---

## Requirements Table Template

### Functional Requirements

| ID | Name | Description | Priority | Acceptance Criteria |
|----|------|-------------|----------|---------------------|
| FR-001 | | | Must/Should/Could | |
| FR-002 | | | | |

### Non-Functional Requirements

| ID | Name | Description | Metric |
|----|------|-------------|--------|
| NF-001 | Response time | API responds quickly | 95p < 500ms |
| NF-002 | Availability | System is available | 99% uptime |
| NF-003 | Test coverage | Code is covered by tests | ≥75% |

### UI/UX Requirements

| ID | Name | Description | Priority |
|----|------|-------------|----------|
| UI-001 | | | Must/Should/Could |

---

## Requirements Gathering Checklist

- [ ] All main functions described (FR-*)
- [ ] Each FR has acceptance criteria
- [ ] Priorities are set
- [ ] NF requirements defined
- [ ] UI requirements defined (if applicable)
- [ ] No duplicate requirements
- [ ] Requirements are atomic (one requirement = one function)

---

## Sources

| Document | Description |
|----------|-------------|
| `.ai-framework/docs/guides/prompt-templates.md` | Prompt templates |
| `.ai-framework/docs/templates/requirements-intake-template.md` | Requirements template |
