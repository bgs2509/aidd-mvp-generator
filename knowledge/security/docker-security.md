# Docker Security Best Practices

> **Назначение**: Правила безопасности Docker для проектов AIDD-MVP.

---

## Dockerfile Security

### 1. Pinned SHA для образов

> **Проблема**: Теги вроде `python:3.11-slim` могут указывать на разные образы со временем.
> Это нарушает reproducibility и может привнести уязвимости.

#### Рекомендация

```dockerfile
# Development: используйте тег для удобства
FROM python:3.11-slim

# Production: используйте pinned SHA для reproducible builds
# docker pull python:3.11-slim && docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
FROM python:3.11-slim@sha256:abc123def456...
```

#### Получение SHA

```bash
# Получить SHA для образа
docker pull python:3.11-slim
docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
# Вывод: python@sha256:abc123def456...
```

---

### 2. ENTRYPOINT + CMD паттерн

> **Проблема**: Только CMD позволяет полностью переопределить команду запуска,
> что может быть небезопасно.

#### Рекомендация

```dockerfile
# Было: только CMD (можно переопределить всё)
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Стало: ENTRYPOINT + CMD (можно переопределить только аргументы)
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Преимущества

| Аспект | Только CMD | ENTRYPOINT + CMD |
|--------|-----------|------------------|
| Переопределение | Полное | Только аргументы |
| Безопасность | Можно запустить любую команду | Фиксированная точка входа |
| Гибкость | Максимальная | Контролируемая |

---

### 3. Non-root пользователь

> **Проблема**: Запуск от root внутри контейнера создаёт риски эскалации привилегий.

#### Рекомендация

```dockerfile
# Создание непривилегированного пользователя
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

# Копирование файлов с правильным владельцем
COPY --chown=appuser:appgroup src/ ./src/

# Переключение на непривилегированного пользователя
USER appuser
```

---

### 4. Multi-stage builds

> **Проблема**: Build-зависимости (компиляторы, dev-библиотеки) увеличивают
> поверхность атаки и размер образа.

#### Рекомендация

```dockerfile
# === Этап сборки ===
FROM python:3.11-slim as builder

WORKDIR /app

# Установка build-зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Сборка wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# === Финальный образ ===
FROM python:3.11-slim

WORKDIR /app

# Только runtime-зависимости, никаких build tools
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

COPY --chown=appuser:appgroup src/ ./src/

USER appuser
```

---

## Docker Compose Security

### 1. security_opt: no-new-privileges

> **Назначение**: Запрещает процессам внутри контейнера получать новые привилегии.

```yaml
services:
  api:
    security_opt:
      - no-new-privileges:true
```

**Что это предотвращает**:
- Использование setuid/setgid бинарников
- Эскалацию привилегий через уязвимости

---

### 2. cap_drop: ALL

> **Назначение**: Удаляет все Linux capabilities по умолчанию.

```yaml
services:
  api:
    cap_drop:
      - ALL
```

**Удаляемые capabilities**:
- `NET_RAW` (raw сокеты, ARP spoofing)
- `SYS_ADMIN` (mount, namespace манипуляции)
- `CHOWN`, `DAC_OVERRIDE` (обход файловых прав)

**Исключения**:
- PostgreSQL требует некоторые capabilities, поэтому для него `cap_drop` не применяется
- Nginx требует `NET_BIND_SERVICE` для портов 80/443

---

### 3. cap_add: минимальные привилегии

> **Назначение**: Добавляет только необходимые capabilities после `cap_drop: ALL`.

```yaml
services:
  nginx:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Для привязки к портам < 1024
```

---

### 4. read_only: true

> **Назначение**: Монтирует корневую файловую систему контейнера только для чтения.

```yaml
services:
  api:
    read_only: true
    tmpfs:
      - /tmp:size=64M,mode=1777
```

**Что это предотвращает**:
- Модификацию системных файлов атакующим
- Запись вредоносного кода на диск
- Persistence после компрометации

**Требует tmpfs для**:
- `/tmp` — временные файлы
- `/var/cache/nginx` — кэш Nginx
- `/run` — PID файлы и сокеты

---

### 5. tmpfs: временная память

> **Назначение**: Монтирует директорию в памяти (RAM).

```yaml
services:
  nginx:
    read_only: true
    tmpfs:
      - /tmp:size=64M,mode=1777
      - /var/cache/nginx:size=128M
      - /run:size=16M
```

**Параметры**:
- `size` — максимальный размер в памяти
- `mode=1777` — sticky bit для /tmp (все могут писать, но удалять только свои файлы)

---

### 6. Переменные окружения с обязательными значениями

> **Назначение**: Контейнер не запустится без критических переменных.

```yaml
services:
  postgres:
    environment:
      # Контейнер НЕ запустится без этих переменных
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?POSTGRES_PASSWORD required}
      - POSTGRES_USER=${POSTGRES_USER:?POSTGRES_USER required}
```

**Синтаксис**:
- `${VAR:?message}` — ошибка если VAR не задана или пустая
- `${VAR:-default}` — default если VAR не задана (НЕ использовать для секретов!)

---

### 7. Закрытие портов в production

> **Назначение**: Сервисы доступны только через reverse proxy.

```yaml
# docker-compose.prod.yml
services:
  postgres:
    ports: []  # Закрываем внешний доступ

  redis:
    ports: []  # Закрываем внешний доступ
```

---

## Resource Limits

### Production конфигурация

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

**Что это предотвращает**:
- DoS через исчерпание ресурсов
- Влияние одного контейнера на другие
- OOM kill хоста

---

## Полный пример

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
    # Без cap_drop — PostgreSQL требует capabilities
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
    # Без read_only — требует запись в /var/lib/postgresql/data
    ports: []  # Закрыт внешний доступ
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
```

---

## Чек-лист

### Dockerfile

- [ ] Pinned SHA для production образов
- [ ] ENTRYPOINT + CMD паттерн
- [ ] Non-root пользователь (USER appuser)
- [ ] Multi-stage builds
- [ ] Минимальный финальный образ (без build tools)

### Docker Compose

- [ ] `security_opt: - no-new-privileges:true` для всех сервисов
- [ ] `cap_drop: - ALL` для stateless сервисов
- [ ] `read_only: true` + `tmpfs` для stateless сервисов
- [ ] `${VAR:?required}` для обязательных переменных
- [ ] `ports: []` для БД в production
- [ ] Resource limits в production

---

## Ссылки

| Документ | Описание |
|----------|----------|
| `knowledge/security/security-checklist.md` | Полный чек-лист безопасности |
| `knowledge/security/vps-mode.md` | VPS режим для production |
| `templates/infrastructure/docker-compose/` | Шаблоны Docker Compose |
| `templates/services/*/Dockerfile` | Шаблоны Dockerfile |
