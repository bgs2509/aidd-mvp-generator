# VPS Security Mode

> **Purpose**: Read-only mode for AI agents when working on production VPS.

---

## What Is VPS Mode

VPS Mode is a special AI agent operation mode where:
- Any file modifications are **prohibited**
- Dangerous commands (rm, systemctl, docker exec) are **prohibited**
- Only reading and analysis are **allowed**

---

## When to Use

| Situation | Mode |
|----------|-------|
| Local development | Standard mode |
| CI/CD pipeline | Standard mode |
| **Production VPS** | **VPS Mode** |
| **Staging VPS** | **VPS Mode** |
| Debugging on server | **VPS Mode** |

---

## SSH Auto-detection

The AI agent automatically detects SSH sessions via environment variables:

```bash
# SSH session indicators (any of):
SSH_CONNECTION    # Client and server IP
SSH_CLIENT        # Client IP and port
SSH_TTY           # Session TTY

# Check:
if [ -n "$SSH_CONNECTION" ] || [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "VPS Mode recommended!"
fi
```

---

## How to Activate

### Method 1: Use settings.vps.json

```bash
# Copy template
cp .aidd/templates/project/.claude/settings.vps.json.example .claude/settings.json

# Restart Claude Code
claude
```

### Method 2: During initialization

The `/aidd-init` command automatically:
1. Checks for SSH session
2. Displays a warning
3. Suggests activating VPS Mode

---

## Allowed Operations in VPS Mode

### Reading

```json
{
  "allow": [
    "Read(**)",
    "Glob(**)",
    "Grep(**)"
  ]
}
```

### Git (read-only)

```json
{
  "allow": [
    "Bash(git status)",
    "Bash(git log :*)",
    "Bash(git diff :*)",
    "Bash(git show :*)"
  ]
}
```

### Docker (logs and status only)

```json
{
  "allow": [
    "Bash(docker logs :*)",
    "Bash(docker ps :*)",
    "Bash(docker inspect :*)"
  ]
}
```

### System (read-only)

```json
{
  "allow": [
    "Bash(ls :*)",
    "Bash(tail :*)",
    "Bash(journalctl :*)",
    "Bash(systemctl status :*)"
  ]
}
```

---

## Prohibited Operations in VPS Mode

### File Modification

```json
{
  "deny": [
    "Edit(**)",
    "Write(**)"
  ]
}
```

### Dangerous Commands

```json
{
  "deny": [
    "Bash(rm :*)",
    "Bash(rmdir :*)",
    "Bash(mv :*)",
    "Bash(cp :*)",
    "Bash(chmod :*)",
    "Bash(chown :*)"
  ]
}
```

### Git (modification)

```json
{
  "deny": [
    "Bash(git commit :*)",
    "Bash(git push :*)",
    "Bash(git checkout :*)",
    "Bash(git reset :*)"
  ]
}
```

### Docker (modification)

```json
{
  "deny": [
    "Bash(docker exec :*)",
    "Bash(docker run :*)",
    "Bash(docker stop :*)",
    "Bash(docker restart :*)",
    "Bash(docker rm :*)"
  ]
}
```

### System (modification)

```json
{
  "deny": [
    "Bash(systemctl start :*)",
    "Bash(systemctl stop :*)",
    "Bash(systemctl restart :*)",
    "Bash(sudo :*)"
  ]
}
```

---

## Usage Scenarios

### Log Analysis

```
User: Analyze logs for the last hour

AI agent:
1. docker logs --since 1h {service}
2. Analyzes error patterns
3. Provides a report with recommendations
```

### Problem Diagnostics

```
User: Why is the service not responding?

AI agent:
1. docker ps -- checks container status
2. docker logs -- looks at errors
3. systemctl status -- checks system services
4. Provides diagnosis and action plan (for the human)
```

### Code Review on Server

```
User: Check the nginx configuration

AI agent:
1. Read nginx.conf
2. Analyzes settings
3. Provides comments and recommendations
```

---

## Important

```
┌─────────────────────────────────────────────────────────────────┐
│  VPS Mode = ANALYSIS ONLY                                       │
├─────────────────────────────────────────────────────────────────┤
│  • AI reads, analyzes, recommends                               │
│  • Human makes decisions and performs actions                    │
│  • This protects against accidental production modifications    │
└─────────────────────────────────────────────────────────────────┘
```

---

## References

| Document | Description |
|----------|----------|
| `templates/project/.claude/settings.vps.json.example` | VPS settings template |
| `knowledge/security/secrets-management.md` | Secrets management |
| `knowledge/security/security-checklist.md` | Security checklist |
