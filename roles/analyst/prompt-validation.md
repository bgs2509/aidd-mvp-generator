# Function: Prompt Validation

> **Purpose**: Verifying and refining the user's idea before forming the PRD.

---

## Goal

Ensure that the user's idea is specific and complete enough
to create a quality PRD document.

---

## Quality Prompt Criteria

### Required Elements

| Element | Question | Example |
|---------|----------|---------|
| **What** | What should the system do? | "Restaurant table booking service" |
| **Who** | Who is the target audience? | "Restaurant visitors" |
| **Why** | What problem does it solve? | "Simplify booking" |

### Desirable Elements

| Element | Question | Example |
|---------|----------|---------|
| **How** | What are the main scenarios? | "Search, browse, book" |
| **Where** | What channels/interfaces? | "API + Telegram bot" |
| **Constraints** | What is NOT in scope? | "No online payment" |

---

## Validation Process

### Step 1: Completeness Analysis

```
Read the user's idea.

Check for:
[ ] Functionality description (WHAT)
[ ] Target audience (WHO)
[ ] Value/problem (WHY)
```

### Step 2: Identifying Gaps

```
If something is missing:
→ Formulate clarifying questions
→ Ask the user

DO NOT make assumptions about critical details for the user!
```

### Step 3: Confirming Understanding

```
Briefly state your understanding of the idea:
"I understood your idea as follows: [description]. Is this correct?"

Wait for confirmation.
```

---

## Clarifying Questions

### If the functionality is unclear

```
- What main actions should the user perform?
- What data should the system store?
- Is integration with external services needed?
```

### If the audience is unclear

```
- Who will use the system?
- Are there different types of users (roles)?
- What is the users' technical proficiency level?
```

### If constraints are unclear

```
- What should definitely NOT be included in the MVP?
- Are there technical constraints?
- Are there time constraints?
```

---

## Examples

### Good prompt (no clarification needed)

```
"Create a restaurant table booking service.
Users can search restaurants by cuisine and location,
view available tables and book for a desired time.
Restaurants receive booking notifications via Telegram.
MVP without online payment."
```

### Prompt requiring clarification

```
"Need a service for restaurants"

Clarifying questions:
1. What exactly should the service do? (booking, menu, delivery?)
2. Who are the users? (visitors, restaurants, both?)
3. Is a web interface or Telegram bot needed?
```

---

## Validation Checklist

- [ ] Functionality is clear
- [ ] Target audience is defined
- [ ] Main scenarios are clear
- [ ] Scope constraints are agreed upon
- [ ] Understanding is confirmed by the user

---

## Sources

| Document | Description |
|----------|-------------|
| `.ai-framework/docs/guides/prompt-validation-guide.md` | Validation guide |
| `.ai-framework/docs/reference/maturity-levels.md` | Maturity levels |
