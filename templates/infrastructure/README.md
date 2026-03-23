# {project_name} MVP Infrastructure

Infrastructure templates for deploying an MVP project.

## Structure

```
infrastructure/
├── docker-compose/
│   ├── docker-compose.yml        # Base configuration
│   ├── docker-compose.dev.yml    # Development overrides
│   ├── docker-compose.prod.yml   # Production overrides
│   └── .env.example              # Environment variables template
├── nginx/
│   ├── nginx.conf                # Nginx configuration
│   └── Dockerfile                # Dockerfile for Nginx
├── Makefile                      # Management commands
└── README.md                     # This file
```

## Quick Start

### 1. Prepare the Environment

```bash
# Copy environment variables
cp docker-compose/.env.example .env

# Edit .env
nano .env
```

### 2. Start in Development Mode

```bash
# Start all services
make dev

# Or directly via docker compose
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 3. Verify

```bash
# Container status
make ps

# Logs
make logs

# Health check
curl http://localhost:8000/health
```

## Environments

### Development

```bash
make dev                # Start with hot reload
make dev-tools          # + pgAdmin, Redis Commander
make logs               # View logs
```

**Features:**
- Hot reload via volume mounts
- Debug mode enabled
- All ports exposed
- Dev tools available

### Production

```bash
make prod               # Start production
make prod-build         # Rebuild and start
```

**Features:**
- Nginx reverse proxy with SSL
- Resource limits (CPU, memory)
- Rate limiting
- Security headers
- Internal ports closed

## Services

| Service | Dev Port | Prod Port | Description |
|---------|----------|-----------|-------------|
| API | 8000 | 443 (nginx) | Business API |
| Data API | 8001 | internal | Data API |
| PostgreSQL | 5432 | internal | Database |
| Redis | 6379 | internal | Cache/queues |
| pgAdmin | 5050 | — | Dev tool |

## Makefile Commands

```bash
# Help
make help

# Development
make dev            # Start dev
make dev-build      # Rebuild dev
make logs           # Logs

# Testing
make test           # All tests
make test-unit      # Unit tests
make test-cov       # With coverage

# Linting
make lint           # Check
make lint-fix       # Auto-fix
make format         # Format

# Database
make db-migrate     # Apply migrations
make db-shell       # PostgreSQL CLI
make db-backup      # Backup

# Cleanup
make clean          # Temporary files
make clean-docker   # Docker resources
```

## CI/CD

CI/CD is not created automatically in templates. Configure it for your tool as needed.

### CI (recommended set)

1. **Lint** — ruff, mypy
2. **Unit Tests** — pytest with coverage
3. **Integration Tests** — with PostgreSQL, Redis
4. **Security Scan** — bandit, safety
5. **Build** — Docker images

### CD (optional)

1. **Build & Push** — registry
2. **Deploy Staging** — automatically (if available)
3. **Deploy Production** — after approval
4. **Smoke Tests** — health check
5. **Rollback** — rollback scenario

### CI/CD Secrets (example)

```
STAGING_HOST
STAGING_USER
STAGING_SSH_KEY

PRODUCTION_HOST
PRODUCTION_USER
PRODUCTION_SSH_KEY

CODECOV_TOKEN         # Codecov token (optional)
```

## Nginx

### SSL Certificates

**Development:**
- Self-signed certificate is generated automatically

**Production:**
```bash
# Let's Encrypt with certbot
certbot certonly --webroot -w /var/www/html -d your-domain.com

# Copy certificates
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

### Rate Limiting

- API: 10 req/s (burst 20)
- Auth: 5 req/min (burst 5)

## Monitoring

### Health Checks

All services have a `/health` endpoint:

```bash
curl http://localhost:8000/health
# {"status": "healthy", "timestamp": "..."}
```

### Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f {context}-api

# Nginx access logs
docker compose exec nginx tail -f /var/log/nginx/access.log
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs {service_name}

# Check status
docker compose ps

# Restart
docker compose restart {service_name}
```

### Database Unavailable

```bash
# Check PostgreSQL
docker compose exec postgres pg_isready

# Check connection
make db-shell
```

### Port Already in Use

```bash
# Find the process
lsof -i :8000

# Change port in .env
API_PORT=8080
```

## Environment Variables

See `.env.example` for the full list.

**Required for production:**
- `POSTGRES_PASSWORD` — DB password
- `JWT_SECRET_KEY` — JWT secret (min 32 chars)
- `TELEGRAM_BOT_TOKEN` — bot token (if used)
