# Паттерны Dockerfile

> **Назначение**: Шаблоны Dockerfile для Python сервисов.

---

## Multi-stage Dockerfile

```dockerfile
# Dockerfile

# === Build stage ===
FROM python:3.11-slim as builder

WORKDIR /build

# Установка зависимостей для сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt


# === Development stage ===
FROM python:3.11-slim as development

WORKDIR /app

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование wheels из builder
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Установка dev зависимостей
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Копирование исходников
COPY src/ ./src/

# Точка входа для разработки
CMD ["uvicorn", "src.{context}_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# === Production stage ===
FROM python:3.11-slim as production

WORKDIR /app

# Создание непривилегированного пользователя
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование wheels из builder
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Копирование исходников
COPY --chown=appuser:appgroup src/ ./src/

# Переключение на непривилегированного пользователя
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Точка входа
CMD ["uvicorn", "src.{context}_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Data API Dockerfile

```dockerfile
# Dockerfile для Data API с миграциями

FROM python:3.11-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt


FROM python:3.11-slim as production

WORKDIR /app

RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Копирование миграций и конфигурации
COPY --chown=appuser:appgroup alembic.ini .
COPY --chown=appuser:appgroup migrations/ ./migrations/
COPY --chown=appuser:appgroup src/ ./src/

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Запуск с миграциями
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.{context}_data.main:app --host 0.0.0.0 --port 8001"]
```

---

## Telegram Bot Dockerfile

```dockerfile
# Dockerfile для Telegram бота

FROM python:3.11-slim as builder

WORKDIR /build

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt


FROM python:3.11-slim as production

WORKDIR /app

RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY --chown=appuser:appgroup src/ ./src/

USER appuser

# Бот не требует health check через HTTP
CMD ["python", "-m", "src.{context}_bot.main"]
```

---

## Worker Dockerfile

```dockerfile
# Dockerfile для Background Worker

FROM python:3.11-slim as builder

WORKDIR /build

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt


FROM python:3.11-slim as production

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY --chown=appuser:appgroup src/ ./src/

USER appuser

# Health check через HTTP endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "src.{context}_worker.main"]
```

---

## .dockerignore

```
# .dockerignore

# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
.venv
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp

# Tests
.pytest_cache
.coverage
htmlcov/
.tox

# Docs
docs/
*.md
!README.md

# Docker
Dockerfile*
docker-compose*

# Local
.env
.env.local
*.log
```

---

## Оптимизации

```dockerfile
# Оптимизированный Dockerfile

FROM python:3.11-slim as production

WORKDIR /app

# Одна команда RUN для минимизации слоёв
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

# Копирование requirements отдельно для кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY --chown=appuser:appgroup src/ ./src/

USER appuser

CMD ["uvicorn", "src.{context}_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Чек-лист

- [ ] Multi-stage сборка
- [ ] Непривилегированный пользователь
- [ ] .dockerignore настроен
- [ ] Health check добавлен
- [ ] Минимальный размер образа
- [ ] Кэширование слоёв оптимизировано
