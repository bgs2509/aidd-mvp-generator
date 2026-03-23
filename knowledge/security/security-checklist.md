# Security Checklist for AI Agents

> **Purpose**: Security verification checklist for secret data in the Target Project.
> **When to check**: At REVIEW (5), VALIDATE (7) stages, before DEPLOY (8).

---

## Automatic AI Agent Verification

The AI agent MUST perform the following checks before passing Quality Gates.

---

## 1. .gitignore Verification

### Check Commands

```bash
# Check .gitignore exists
test -f .gitignore && echo "OK" || echo "FAIL: .gitignore not found"

# Check that .env is ignored
grep -q "^\.env$" .gitignore && echo "OK" || echo "FAIL: .env not in .gitignore"

# Check key patterns
for pattern in ".env" ".env.local" "*.pem" "*.key" "credentials.json"; do
  grep -q "$pattern" .gitignore && echo "OK: $pattern" || echo "WARN: $pattern not in .gitignore"
done
```

### Criteria

| Check | Required | Severity |
|----------|-------------|-------------|
| `.gitignore` exists | Yes | Blocker |
| `.env` in .gitignore | Yes | Blocker |
| `*.pem`, `*.key` in .gitignore | Yes | Critical |
| `credentials.json` in .gitignore | Yes | Critical |

---

## 2. No Secrets in Code Verification

### Check Commands

```bash
# Search for hardcoded passwords
grep -rn "password\s*=\s*['\"][^'\"]*['\"]" services/ --include="*.py" | \
  grep -v "test_\|_test\.py\|example\|template" || echo "OK: No hardcoded passwords"

# Search for hardcoded tokens
grep -rn "token\s*=\s*['\"][^'\"]*['\"]" services/ --include="*.py" | \
  grep -v "test_\|_test\.py\|example\|template" || echo "OK: No hardcoded tokens"

# Search for suspicious strings
grep -rn "secret\s*=\s*['\"]" services/ --include="*.py" | \
  grep -v "test_\|_test\.py" || echo "OK"
```

### Patterns to Search For

```
PROHIBITED patterns in Python code:
- password = "..."
- PASSWORD = "..."
- token = "..."
- api_key = "..."
- secret = "..."
- POSTGRES_PASSWORD = "..."
```

### Criteria

| Check | Severity |
|----------|-------------|
| No hardcoded passwords | Blocker |
| No hardcoded tokens | Blocker |
| No hardcoded API keys | Blocker |

---

## 3. .env.example Verification

### Check Commands

```bash
# Check .env.example exists
test -f .env.example && echo "OK" || echo "WARN: .env.example not found"

# Check for no real secrets (placeholders)
if [ -f .env.example ]; then
  # Should have CHANGE_ME or similar markers
  grep -q "CHANGE_ME" .env.example && echo "OK: Has placeholders" || \
    echo "WARN: No CHANGE_ME placeholders"

  # Should not have real passwords
  grep -vE "^#|CHANGE_ME|your_|example|placeholder" .env.example | \
    grep -E "PASSWORD=.+" && echo "WARN: Possible real password" || echo "OK"
fi
```

### Criteria

| Check | Required | Severity |
|----------|-------------|-------------|
| `.env.example` exists | Recommended | Warning |
| Contains CHANGE_ME placeholders | Yes | Warning |
| No real passwords | Yes | Critical |

---

## 4. docker-compose Verification

### Check Commands

```bash
# Check for no hardcoded secrets
grep -n "PASSWORD.*:.*-" docker-compose*.yml | \
  grep -v ":?" && echo "WARN: Default password found" || echo "OK"

# Check for required variable usage
grep -q ":?.*required\|:?.*Required" docker-compose*.yml && \
  echo "OK: Has required variables" || \
  echo "WARN: No required variables for secrets"

# Check that DB port is closed in prod
grep -A5 "postgres:" docker-compose.prod.yml | grep "ports: \[\]" && \
  echo "OK: DB port closed in prod" || echo "WARN: DB port may be open"
```

### Criteria

| Check | Severity |
|----------|-------------|
| No `:-secret` default values | Critical |
| Uses `:?` for required vars | Warning |
| DB ports closed in prod compose | Warning |

---

## 5. Logging Verification

### Check Commands

```bash
# Check that sanitize_sensitive_data is used
grep -rn "sanitize_sensitive_data" services/ --include="*.py" || \
  echo "INFO: sanitize_sensitive_data not found in services/"

# Check that secrets are not logged directly
grep -rn "logger.*password\|logger.*token\|logger.*secret" services/ --include="*.py" | \
  grep -v "REDACTED\|sanitize" && echo "WARN: Possible secret logging" || echo "OK"

# Check setup_logging in main.py
for service in services/*/; do
  grep -q "setup_logging" "${service}src/main.py" 2>/dev/null && \
    echo "OK: setup_logging in $service" || echo "WARN: No setup_logging in $service"
done
```

### Criteria

| Check | Severity |
|----------|-------------|
| Uses structlog with sanitization | Warning |
| No direct secret logging | Critical |

---

## 6. CI/CD Verification

### Recommendations

- Ensure there are no hardcoded secrets in CI/CD configurations.
- Use your CI system's secrets mechanism and environment variables.

### Criteria

| Check | Severity |
|----------|-------------|
| No hardcoded secrets in CI/CD configs | Critical |
| Secrets passed through CI/CD mechanism | Warning |

---

## 7. Pre-commit Hooks Verification

### Check Commands

```bash
# Check .pre-commit-config.yaml exists
test -f .pre-commit-config.yaml && echo "OK" || echo "WARN: pre-commit not configured"

# Check that gitleaks is enabled
grep -q "gitleaks" .pre-commit-config.yaml 2>/dev/null && \
  echo "OK: gitleaks configured" || echo "WARN: gitleaks not configured"

# Check that detect-secrets is enabled
grep -q "detect-secrets" .pre-commit-config.yaml 2>/dev/null && \
  echo "OK: detect-secrets configured" || echo "INFO: detect-secrets not configured"
```

### Criteria

| Check | Severity |
|----------|-------------|
| `.pre-commit-config.yaml` exists | Recommended |
| gitleaks hook configured | Recommended |

---

## 8. Settings (Pydantic) Verification

### What to Check in Code

```python
# GOOD: Required fields without default
class Settings(BaseSettings):
    database_url: str  # Required
    secret_key: str = Field(..., min_length=32)  # With validation

# BAD: Default values for secrets
class Settings(BaseSettings):
    password: str = "default123"  # NEVER do this!
```

### Check Commands

```bash
# Find Settings classes with default passwords
grep -A10 "class Settings" services/*/src/core/config.py | \
  grep -E "(password|secret|token).*=.*['\"]" && \
  echo "WARN: Default values for secrets" || echo "OK"
```

---

## 9. Summary Table for Review Report

```markdown
## Security Checklist

| # | Check | Status | Comment |
|---|----------|--------|-------------|
| 1 | .gitignore contains .env | ✅/❌ | |
| 2 | .gitignore contains *.pem, *.key | ✅/❌ | |
| 3 | No hardcoded passwords in code | ✅/❌ | |
| 4 | No hardcoded tokens in code | ✅/❌ | |
| 5 | .env.example without real secrets | ✅/❌ | |
| 6 | docker-compose without default passwords | ✅/❌ | |
| 7 | Logging with sanitization | ✅/❌ | |
| 8 | CI/CD uses secrets | ✅/❌ | |
| 9 | Pre-commit hooks configured | ✅/⚠️ | |
| 10 | Settings without default secrets | ✅/❌ | |
```

---

## 10. Blocking Criteria

### BLOCKER (blocks REVIEW_OK)

- [ ] Hardcoded passwords in code
- [ ] Hardcoded tokens in code
- [ ] .env not in .gitignore
- [ ] Real secrets in .env.example

### CRITICAL (requires fixing)

- [ ] Default passwords in docker-compose
- [ ] Direct secret logging
- [ ] Secrets in CI/CD without ${{ secrets }}
- [ ] *.pem, *.key not in .gitignore

### WARNING (recommended to fix)

- [ ] No .pre-commit-config.yaml
- [ ] No gitleaks hook
- [ ] No CHANGE_ME in .env.example

---

## 11. Integration with Quality Gates

### REVIEW (Stage 5)

AI reviewer MUST:
1. Perform checks 1-8 from this checklist
2. Include results in the "Security" section of the Review Report
3. Block REVIEW_OK if BLOCKER issues exist

### VALIDATE (Stage 7)

AI validator MUST:
1. Confirm all BLOCKER and CRITICAL issues are fixed
2. Document WARNINGs as "known limitations"
3. Include Security Summary in the Validation Report

### DEPLOY (Stage 8)

AI validator MUST:
1. Confirm .env.example is up to date
2. Verify production compose does not contain debug modes
3. Ensure HTTPS is configured (for production)

---

## 12. Docker Security

> **Details**: `knowledge/security/docker-security.md`

### Dockerfile Checks

```bash
# Check non-root user
for dockerfile in services/*/Dockerfile; do
  grep -q "USER appuser\|USER 1000" "$dockerfile" && \
    echo "OK: Non-root user in $dockerfile" || \
    echo "WARN: No non-root user in $dockerfile"
done

# Check ENTRYPOINT + CMD pattern
for dockerfile in services/*/Dockerfile; do
  grep -q "ENTRYPOINT" "$dockerfile" && \
    echo "OK: ENTRYPOINT in $dockerfile" || \
    echo "INFO: No ENTRYPOINT in $dockerfile"
done
```

### Docker Compose Checks

```bash
# Check security_opt
grep -q "no-new-privileges" docker-compose.yml && \
  echo "OK: security_opt configured" || echo "WARN: security_opt not configured"

# Check cap_drop in prod
grep -q "cap_drop" docker-compose.prod.yml && \
  echo "OK: cap_drop configured in prod" || echo "WARN: cap_drop not configured in prod"

# Check read_only in prod
grep -q "read_only: true" docker-compose.prod.yml && \
  echo "OK: read_only in prod" || echo "INFO: read_only not configured in prod"
```

### Criteria

| Check | Severity |
|----------|-------------|
| Non-root user in Dockerfile | Warning |
| security_opt: no-new-privileges | Warning |
| cap_drop: ALL for stateless | Warning |
| read_only + tmpfs in prod | Info |
| Resource limits in prod | Warning |

---

## 13. VPS Security Mode

> **Details**: `knowledge/security/vps-mode.md`

### SSH Session Check

```bash
# Detect VPS/production environment
if [ -n "$SSH_CONNECTION" ] || [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "WARNING: SSH SESSION DETECTED"
    echo ""
    echo "VPS Mode (read-only) recommended:"
    echo "  cp .aidd/templates/project/.claude/settings.vps.json.example \\"
    echo "     .claude/settings.json"
fi
```

### VPS Settings Check

```bash
# Check that Edit and Write are denied
if [ -f ".claude/settings.json" ]; then
  grep -q '"Edit(\*\*)"' .claude/settings.json && \
    echo "VPS Mode: Edit denied" || echo "WARN: Edit may be allowed"

  grep -q '"Write(\*\*)"' .claude/settings.json && \
    echo "VPS Mode: Write denied" || echo "WARN: Write may be allowed"
fi
```

### Production Criteria

| Check | Severity |
|----------|-------------|
| VPS Mode activated on production | Recommended |
| Edit/Write denied | Recommended |
| docker exec denied | Recommended |
| systemctl start/stop/restart denied | Recommended |

---

## 14. Extended Summary Table

```markdown
## Security Checklist

| # | Check | Status | Comment |
|---|----------|--------|-------------|
| 1 | .gitignore contains .env | ✅/❌ | |
| 2 | .gitignore contains *.pem, *.key | ✅/❌ | |
| 3 | No hardcoded passwords in code | ✅/❌ | |
| 4 | No hardcoded tokens in code | ✅/❌ | |
| 5 | .env.example without real secrets | ✅/❌ | |
| 6 | docker-compose without default passwords | ✅/❌ | |
| 7 | Logging with sanitization | ✅/❌ | |
| 8 | CI/CD uses secrets | ✅/❌ | |
| 9 | Pre-commit hooks configured | ✅/⚠️ | |
| 10 | Settings without default secrets | ✅/❌ | |
| 11 | Non-root user in Dockerfile | ✅/⚠️ | |
| 12 | security_opt configured | ✅/⚠️ | |
| 13 | cap_drop for stateless | ✅/⚠️ | |
| 14 | VPS Mode on production | ✅/ℹ️ | |
```

---

## Related Documents

| Document | Description |
|----------|----------|
| `knowledge/security/secrets-management.md` | Secrets management |
| `knowledge/security/docker-security.md` | Docker best practices |
| `knowledge/security/vps-mode.md` | VPS mode for production |
| `templates/documents/review-report-template.md` | Review template |
| `templates/documents/validation-report-template.md` | Validation template |
| `.claude/settings.json` | AI restrictions |
| `templates/project/.claude/settings.vps.json.example` | VPS settings template |

---

**Document version**: 1.1
**Updated**: 2026-01-03
