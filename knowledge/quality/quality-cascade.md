# Quality Cascade v2

> **Principle**: Quality errors should be detected at an EARLY stage, not only at Review.
> **Philosophy**: Each role checks ALL applicable principles. All checks are MANDATORY.

---

## 1. The Problem (before Quality Cascade)

```
/aidd-analyze -> /aidd-research -> /aidd-plan -> /aidd-code -> /aidd-validate
     ❌              ❌              ❌           ❌             ✅

Quality principles were checked ONLY at the Validate stage.
DRY/KISS/YAGNI errors passed through the entire pipeline.
```

**Example**: At the `/aidd-research` stage, a 5-file structure with DRY violations is proposed.
The error is discovered only at Validate -- after code generation.

---

## 2. Solution: Quality Cascade v2

```
Error -> [Research]  -> [Architect]  -> [Implement]  -> [Review]
          7 checks      16 checks      17 checks      17 checks
          MANDATORY     MANDATORY      MANDATORY      MANDATORY
```

Each role performs ALL applicable checks at its stage.

---

## 3. Principle Applicability Matrix

| # | Principle | Research | Architect | Implement | Review |
|---|---------|:--------:|:---------:|:---------:|:------:|
| 1 | DRY | ✓ | ✓ | ✓ | ✓ |
| 2 | KISS | ✓ | ✓ | ✓ | ✓ |
| 3 | YAGNI | ✓ | ✓ | ✓ | ✓ |
| 4 | SRP | - | ✓ | ✓ | ✓ |
| 5 | OCP | - | ✓ | ✓ | ✓ |
| 6 | LSP | - | - | ✓ | ✓ |
| 7 | ISP | - | ✓ | ✓ | ✓ |
| 8 | DIP | - | ✓ | ✓ | ✓ |
| 9 | SoC | ✓ | ✓ | ✓ | ✓ |
| 10 | SSoT | ✓ | ✓ | ✓ | ✓ |
| 11 | LoD | - | ✓ | ✓ | ✓ |
| 12 | CoC | ✓ | ✓ | ✓ | ✓ |
| 13 | Fail Fast | - | ✓ | ✓ | ✓ |
| 14 | Explicit | - | ✓ | ✓ | ✓ |
| 15 | Composition | - | ✓ | ✓ | ✓ |
| 16 | Testability | - | ✓ | ✓ | ✓ |
| 17 | Security | ✓ | ✓ | ✓ | ✓ |
| | **Total** | **7** | **16** | **17** | **17** |

**Legend**:
- ✓ = MANDATORY check
- `-` = Not applicable (no artifact to check)

---

## 4. Brief Principle Descriptions

### Basic (applied everywhere)

| Principle | Essence |
|---------|------|
| **DRY** | Don't Repeat Yourself -- no code duplication |
| **KISS** | Keep It Simple -- simple solutions without over-engineering |
| **YAGNI** | You Aren't Gonna Need It -- only what is necessary |
| **SoC** | Separation of Concerns -- separating responsibilities |
| **SSoT** | Single Source of Truth -- one data source |
| **CoC** | Convention over Configuration -- following conventions |
| **Security** | Security at all levels |

### SOLID (from the Architect stage)

| Principle | Essence |
|---------|------|
| **SRP** | Single Responsibility -- one responsibility |
| **OCP** | Open/Closed -- open for extension, closed for modification |
| **LSP** | Liskov Substitution -- subtypes replace parents |
| **ISP** | Interface Segregation -- small interfaces |
| **DIP** | Dependency Inversion -- depend on abstractions |

### Additional

| Principle | Essence |
|---------|------|
| **LoD** | Law of Demeter -- minimal coupling |
| **Fail Fast** | Validate early, fail explicitly |
| **Explicit > Implicit** | Explicit code without magic |
| **Composition > Inheritance** | Composition over inheritance |
| **Testability** | Code can be tested |

---

## 5. Checks by Role

### 5.1 Researcher (7 checks)

**Artifact**: Research Report

| # | Principle | Check Purpose |
|---|---------|---------------|
| 1 | DRY | Find existing code for reuse |
| 2 | KISS | Assess complexity of PRD proposals |
| 3 | YAGNI | Filter out "for the future" components |
| 4 | SoC | Analyze separation of concerns |
| 5 | SSoT | Identify data sources |
| 6 | CoC | Identify project conventions |
| 7 | Security | Analyze security practices |

**Mandatory report section**: `Quality Cascade Checklist (7/7)`

### 5.2 Architect (16 checks)

**Artifact**: Architecture Plan

All 7 Researcher checks + 9 additional:
- SRP, OCP, ISP, DIP -- SOLID principles
- LoD -- module coupling
- Fail Fast -- error handling strategy
- Explicit -- explicit contracts
- Composition -- reuse patterns
- Testability -- architecture testability

**Mandatory plan section**: `Quality Cascade Checklist (16/16)`

### 5.3 Implementer (17 checks)

**Artifact**: Code

All 16 Architect checks + LSP (Liskov Substitution).

**Mandatory self-review**: `Quality Cascade Self-Check (17/17)`

### 5.4 Reviewer (17 checks)

**Artifact**: Review Report

Final verification of all 17 principles.

**Mandatory report section**: `Quality Cascade Verification (17/17)`

---

## 6. Report Format

```markdown
## Quality Cascade Checklist (N/N)

### QC-1: DRY ✅
- [x] Check item 1
- [x] Check item 2
-> Result/Recommendation

### QC-2: KISS ✅
- [x] Check item 1
...

### QC-N: Security ✅
- [x] Check item 1
...

**Total**: N/N checks passed
```

---

## 7. Integration with Quality Gates

| Stage | Gate | Requirement |
|------|--------|------------|
| Research | `RESEARCH_DONE` | Quality Cascade Checklist (7/7) included |
| Architect | `PLAN_APPROVED` | Quality Cascade Checklist (16/16) included |
| Implement | `IMPLEMENT_OK` | Quality Cascade Self-Check (17/17) completed |
| Review | `REVIEW_OK` | Quality Cascade Verification (17/17) completed |

**If checks fail** -> Gate does NOT open -> Transition is blocked.

---

## 8. Example: F005-C with Quality Cascade

### Research Report (excerpt)

```markdown
## Quality Cascade Checklist (7/7)

### DRY ✅
- [x] Found settings.py for configuration
- [x] Found convert.py for extension
-> Recommendation: DO NOT create config.py

### YAGNI ✅
- [x] PRD proposes 5 files
- [x] prompts.py contains 1 constant -> redundant
-> Recommendation: exclude prompts.py
```

### Architecture Plan (excerpt)

```markdown
## Quality Cascade Checklist (16/16)

### KISS ✅
- [x] Minimized to 1 file
-> Justification: llm_client.py is sufficient

### SRP ✅
- [x] llm_client.py: only LLM integration
- [x] convert.py: only conversion (extended)
```

---

## 9. References

| Document | Description |
|----------|----------|
| `.claude/agents/researcher.md` | 7 checks for Researcher |
| `.claude/agents/planner.md` | 16 checks for Architect |
| `.claude/agents/coder.md` | 17 checks for Implementer |
| `.claude/agents/code-review-library.md` | 17 checks for Code Review (used by Validator) |
| `knowledge/quality/dry-kiss-yagni.md` | DRY/KISS/YAGNI details |
| `contributors/2026-01-13-aidd-enhancement-quality-cascade.md` | Original proposal |

---

**Version**: 2.0
**Implementation date**: 2026-01-13
**Status**: Implemented
