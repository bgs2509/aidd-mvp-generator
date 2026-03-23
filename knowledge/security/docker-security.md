# Docker Security Best Practices

> **Purpose**: Docker security rules for AIDD-MVP projects.

---

## Dockerfile Security

### 1. Pinned SHA for Images

> **Problem**: Tags like `python:3.11-slim` can point to different images over time.
> This breaks reproducibility and can introduce vulnerabilities.

#### Recommendation

```dockerfile
# Development: use tag for convenience
FROM python:3.11-slim

# Production: use pinned SHA for reproducible builds
# docker pull python:3.11-slim && docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
FROM python:3.11-slim@sha256:abc123def456...
```

#### Getting SHA

```bash
# Get SHA for an image
docker pull python:3.11-slim
docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
# Output: python@sha256:abc123def456...
```

---

### 2. ENTRYPOINT + CMD Pattern

> **Problem**: Using only CMD allows completely overriding the startup command,
> which can be insecure.

#### Recommendation

```dockerfile
# Before: CMD only (everything can be overridden)
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# After: ENTRYPOINT + CMD (only arguments can be overridden)
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Advantages

| Aspect | CMD Only | ENTRYPOINT + CMD |
|--------|-----------|------------------|
| Override | Full | Arguments only |
| Security | Any command can be run | Fixed entry point |
| Flexibility | Maximum | Controlled |

---

### 3. Non-root User

> **Problem**: Running as root inside the container creates privilege escalation risks.

#### Recommendation

```dockerfile
# Create non-privileged user
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

# Copy files with correct ownership
COPY --chown=appuser:appgroup src/ ./src/

# Switch to non-privileged user
USER appuser
```

---

### 4. Multi-stage Builds

> **Problem**: Build dependencies (compilers, dev libraries) increase
> the attack surface and image size.

#### Recommendation

```dockerfile
# === Build stage ===
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Build wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# === Final image ===
FROM python:3.11-slim

WORKDIR /app

# Only runtime dependencies, no build tools
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

COPY --chown=appuser:appgroup src/ ./src/

USER appuser
```

---

## Docker Compose Security

### 1. security_opt: no-new-privileges

> **Purpose**: Prevents processes inside the container from gaining new privileges.

```yaml
services:
  api:
    security_opt:
      - no-new-privileges:true
```

**What this prevents**:
- Use of setuid/setgid binaries
- Privilege escalation through vulnerabilities

---

### 2. cap_drop: ALL

> **Purpose**: Removes all default Linux capabilities.

```yaml
services:
  api:
    cap_drop:
      - ALL
```

**Removed capabilities**:
- `NET_RAW` (raw sockets, ARP spoofing)
- `SYS_ADMIN` (mount, namespace manipulation)
- `CHOWN`, `DAC_OVERRIDE` (file permission bypass)

**Exceptions**:
- PostgreSQL requires some capabilities, so `cap_drop` is not applied to it
- Nginx requires `NET_BIND_SERVICE` for ports 80/443

---

### 3. cap_add: Minimal Privileges

> **Purpose**: Adds only necessary capabilities after `cap_drop: ALL`.

```yaml
services:
  nginx:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # For binding to ports < 1024
```

---

### 4. read_only: true

> **Purpose**: Mounts the container's root filesystem as read-only.

```yaml
services:
  api:
    read_only: true
    tmpfs:
      - /tmp:size=64M,mode=1777
```

**What this prevents**:
- System file modification by an attacker
- Writing malicious code to disk
- Persistence after compromise

**Requires tmpfs for**:
- `/tmp` -- temporary files
- `/var/cache/nginx` -- Nginx cache
- `/run` -- PID files and sockets

---

### 5. tmpfs: In-memory Directory

> **Purpose**: Mounts a directory in memory (RAM).

```yaml
services:
  nginx:
    read_only: true
    tmpfs:
      - /tmp:size=64M,mode=1777
      - /var/cache/nginx:size=128M
      - /run:size=16M
```

**Parameters**:
- `size` -- maximum size in memory
- `mode=1777` -- sticky bit for /tmp (everyone can write, but only delete their own files)

---

### 6. Environment Variables with Required Values

> **Purpose**: Container will not start without critical variables.

```yaml
services:
  postgres:
    environment:
      # Container will NOT start without these variables
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?POSTGRES_PASSWORD required}
      - POSTGRES_USER=${POSTGRES_USER:?POSTGRES_USER required}
```

**Syntax**:
- `${VAR:?message}` -- error if VAR is not set or empty
- `${VAR:-default}` -- default if VAR is not set (DO NOT use for secrets!)

---

### 7. Closing Ports in Production

> **Purpose**: Services are accessible only through reverse proxy.

```yaml
# docker-compose.prod.yml
services:
  postgres:
    ports: []  # Close external access

  redis:
    ports: []  # Close external access
```

---

## Resource Limits

### Production Configuration

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 256M
```

**What this prevents**:
- DoS through resource exhaustion
- One container affecting others
- Host OOM kill

---

## Full Example

### docker-compose.yml (development)

```yaml
services:
  api:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL

  postgres:
    security_opt:
      - no-new-privileges:true
    # No cap_drop -- PostgreSQL requires capabilities
```

### docker-compose.prod.yml (production)

```yaml
services:
  nginx:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp:size=64M,mode=1777
      - /var/cache/nginx:size=128M
      - /run:size=16M
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 128M

  api:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: true
    tmpfs:
      - /tmp:size=64M,mode=1777
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
      replicas: 2

  postgres:
    # No read_only -- requires write to /var/lib/postgresql/data
    ports: []  # External access closed
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
```

---

## Checklist

### Dockerfile

- [ ] Pinned SHA for production images
- [ ] ENTRYPOINT + CMD pattern
- [ ] Non-root user (USER appuser)
- [ ] Multi-stage builds
- [ ] Minimal final image (no build tools)

### Docker Compose

- [ ] `security_opt: - no-new-privileges:true` for all services
- [ ] `cap_drop: - ALL` for stateless services
- [ ] `read_only: true` + `tmpfs` for stateless services
- [ ] `${VAR:?required}` for required variables
- [ ] `ports: []` for databases in production
- [ ] Resource limits in production

---

## References

| Document | Description |
|----------|----------|
| `knowledge/security/security-checklist.md` | Full security checklist |
| `knowledge/security/vps-mode.md` | VPS mode for production |
| `templates/infrastructure/docker-compose/` | Docker Compose templates |
| `templates/services/*/Dockerfile` | Dockerfile templates |
