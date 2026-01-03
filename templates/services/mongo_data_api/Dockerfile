# Dockerfile для {context}_data
# MongoDB Data API сервис

# === Этап сборки ===
# SECURITY: В production используйте pinned SHA для reproducible builds
# docker pull python:3.11-slim && docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
# Пример: FROM python:3.11-slim@sha256:abc123...
FROM python:3.11-slim as builder

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# === Финальный образ ===
# SECURITY: В production используйте тот же pinned SHA что и в builder
FROM python:3.11-slim

WORKDIR /app

# Создание непривилегированного пользователя
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

# Копирование wheels из этапа сборки
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Копирование кода приложения
COPY --chown=appuser:appgroup src/ ./src/

# Переключение на непривилегированного пользователя
USER appuser

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Порт приложения
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8001/health')" || exit 1

# Запуск приложения
# ENTRYPOINT + CMD паттерн позволяет переопределять аргументы при запуске
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["src.main:app", "--host", "0.0.0.0", "--port", "8001"]
