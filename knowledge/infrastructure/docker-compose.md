# Настройка Docker Compose

> **Назначение**: Конфигурация Docker Compose для микросервисов.

---

## Базовая структура

```yaml
# docker-compose.yml

services:
  # Business API
  {context}-api:
    build:
      context: ./services/{context}_api
      dockerfile: Dockerfile
    container_name: {context}-api
    ports:
      - "8000:8000"
    environment:
      - DATA_API_URL=http://{context}-data:8001
      - REDIS_URL=redis://{context}-redis:6379/0
      - LOG_LEVEL=INFO
    depends_on:
      {context}-data:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Data API
  {context}-data:
    build:
      context: ./services/{context}_data
      dockerfile: Dockerfile
    container_name: {context}-data
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@{context}-postgres:5432/{context}
      - LOG_LEVEL=INFO
    depends_on:
      {context}-postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL
  {context}-postgres:
    image: postgres:15-alpine
    container_name: {context}-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB={context}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  {context}-redis:
    image: redis:7-alpine
    container_name: {context}-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: {context}-network
```

---

## Dev overrides

```yaml
# docker-compose.dev.yml

services:
  {context}-api:
    build:
      target: development
    volumes:
      - ./services/{context}_api/src:/app/src:ro
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    command: uvicorn src.{context}_api.main:app --host 0.0.0.0 --port 8000 --reload

  {context}-data:
    build:
      target: development
    volumes:
      - ./services/{context}_data/src:/app/src:ro
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    command: uvicorn src.{context}_data.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## Production конфигурация

```yaml
# docker-compose.prod.yml

services:
  {context}-api:
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO

  {context}-data:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO

  {context}-postgres:
    restart: always

  {context}-redis:
    restart: always
```

---

## С Telegram ботом

```yaml
# Добавить в docker-compose.yml

services:
  {context}-bot:
    build:
      context: ./services/{context}_bot
      dockerfile: Dockerfile
    container_name: {context}-bot
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - BUSINESS_API_URL=http://{context}-api:8000
      - LOG_LEVEL=INFO
    depends_on:
      {context}-api:
        condition: service_healthy
    restart: unless-stopped
```

---

## С Background Worker

```yaml
# Добавить в docker-compose.yml

services:
  {context}-worker:
    build:
      context: ./services/{context}_worker
      dockerfile: Dockerfile
    container_name: {context}-worker
    environment:
      - BUSINESS_API_URL=http://{context}-api:8000
      - DATA_API_URL=http://{context}-data:8001
      - REDIS_URL=redis://{context}-redis:6379/0
      - LOG_LEVEL=INFO
    depends_on:
      {context}-api:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## С Nginx (Level 3+)

```yaml
# Добавить в docker-compose.prod.yml

services:
  {context}-nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    container_name: {context}-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - {context}-api
    restart: always
```

---

## Команды

```bash
# Запуск для разработки
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Запуск для production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Просмотр логов
docker compose logs -f {context}-api

# Перезапуск сервиса
docker compose restart {context}-api

# Остановка
docker compose down

# Остановка с удалением volumes
docker compose down -v
```

---

## Makefile

```makefile
.PHONY: dev prod down logs

# Разработка
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production
prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Остановка
down:
	docker compose down

# Логи
logs:
	docker compose logs -f

# Миграции
migrate:
	docker compose exec {context}-data alembic upgrade head

# Тесты
test:
	docker compose exec {context}-api pytest
```

---

## Чек-лист

- [ ] Все сервисы определены
- [ ] Healthcheck настроен
- [ ] depends_on с condition
- [ ] Volumes для персистентности
- [ ] Dev и prod overrides созданы
- [ ] Сеть именована
