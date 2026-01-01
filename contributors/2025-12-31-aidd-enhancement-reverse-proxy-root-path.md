# Enhancement: Reverse Proxy + root_path Best Practice

> **Дата**: 2025-12-31
> **Автор**: bgs (с помощью Claude Code)
> **Контекст**: Проблема 404 для StaticFiles при работе за nginx с rewrite
> **Тип**: Enhancement (улучшение)
> **Затрагивает**: Все сервисы за reverse proxy с путевым префиксом

---

## Проблема

При развёртывании нескольких сервисов на одном IP с разными путевыми префиксами
(например, `/service-a/`, `/service-b/`) возникает конфликт конфигураций.

### Сценарий

```
95.142.37.184/free-ai-selector/...  → Business API
95.142.37.184/smi-convert/...       → SMI Convert
```

### Текущий (неправильный) подход

**nginx** с rewrite:
```nginx
location /free-ai-selector/ {
    rewrite ^/free-ai-selector/(.*) /$1 break;  # убирает префикс
    proxy_pass http://backend:8000;
}
```

**FastAPI** с root_path:
```python
app = FastAPI(root_path="/free-ai-selector")
```

### Симптомы

| Компонент | Результат |
|-----------|-----------|
| API routes (`/health`, `/api/v1/*`) | ✅ Работает |
| StaticFiles mounts (`/static/*`) | ❌ 404 Not Found |
| OpenAPI docs (`/docs`) | ⚠️ Может работать/не работать |

### Причина

`root_path` влияет по-разному на routes и mounts:

- **APIRoute**: маршрутизация по `scope["path"]`, root_path НЕ влияет
- **Mount (StaticFiles)**: маршрутизация учитывает root_path

Когда nginx убирает префикс, но FastAPI ожидает его для mounts — конфликт.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Путь в браузере: /free-ai-selector/static/index.html                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  nginx с rewrite:                                                        │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ rewrite ^/free-ai-selector/(.*) /$1 break;                         │ │
│  │ → FastAPI получает: /static/index.html                             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  FastAPI с root_path="/free-ai-selector":                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Mount("/static") ищет: /free-ai-selector/static/index.html         │ │
│  │ Получил:              /static/index.html                           │ │
│  │ → НЕ СОВПАДАЕТ → 404 Not Found                                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  APIRoute("/health") работает потому что:                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Маршрутизация по scope["path"], root_path игнорируется             │ │
│  │ Получил: /health → Совпадает с @app.get("/health") → 200 OK        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Решение: Best Practice

### Принцип

> **nginx НЕ делает rewrite** + **FastAPI использует root_path**

FastAPI/Starlette сами обрабатывают root_path:
1. Получают полный путь `/free-ai-selector/static/index.html`
2. Убирают root_path для маршрутизации → `/static/index.html`
3. Добавляют root_path для генерации URL → `/free-ai-selector/static/...`

### Конфигурация

**nginx** (БЕЗ rewrite):
```nginx
location /free-ai-selector/ {
    # ВАЖНО: БЕЗ rewrite!
    # FastAPI с root_path сам обработает префикс

    proxy_pass http://backend:8000;  # без trailing slash
    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /free-ai-selector;
}
```

**FastAPI** (с root_path из env):
```python
ROOT_PATH = os.getenv("ROOT_PATH", "")

app = FastAPI(
    title="My Service",
    root_path=ROOT_PATH,
)

# Routes объявляем БЕЗ префикса
@app.get("/health")
async def health():
    return {"status": "ok"}

# Mounts работают автоматически
app.mount("/static", StaticFiles(directory="static"))
```

**.env** на VPS:
```bash
ROOT_PATH=/free-ai-selector
```

### Как работает правильная конфигурация

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Путь в браузере: /free-ai-selector/static/index.html                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  nginx БЕЗ rewrite:                                                      │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ proxy_pass http://backend:8000;                                    │ │
│  │ → FastAPI получает: /free-ai-selector/static/index.html            │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  FastAPI с root_path="/free-ai-selector":                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Starlette автоматически:                                           │ │
│  │ 1. Видит root_path="/free-ai-selector"                             │ │
│  │ 2. Убирает из path: /free-ai-selector/static/... → /static/...     │ │
│  │ 3. Mount("/static") получает: /static/index.html                   │ │
│  │ → СОВПАДАЕТ → 200 OK                                               │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Изменения в фреймворке AIDD

### 1. Шаблон nginx (templates/infrastructure/nginx/)

**Создать файл**: `conf.d/service-location.conf.template`

```nginx
# Шаблон location для сервиса за reverse proxy
#
# Переменные:
#   {service_path} - путевой префикс (например, /my-service)
#   {upstream_name} - имя upstream (например, my_service_api)

location {service_path}/ {
    # ВАЖНО: НЕ используем rewrite!
    # FastAPI с root_path сам обработает префикс

    proxy_pass http://{upstream_name};
    proxy_http_version 1.1;

    # Стандартные заголовки
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix {service_path};
    proxy_set_header X-Request-ID $request_id;
    proxy_set_header Connection "";

    # Таймауты
    proxy_connect_timeout 30s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

### 2. Шаблон FastAPI main.py (templates/services/fastapi_business_api/)

**Изменить**: `src/main.py`

```diff
+ import os
+
+ # Reverse Proxy Support
+ # При работе за nginx с путевым префиксом
+ ROOT_PATH = os.getenv("ROOT_PATH", "")

  def create_app() -> FastAPI:
      app = FastAPI(
          title=settings.app_name,
          version="1.0.0",
+         root_path=ROOT_PATH,
          # OpenAPI URL генерируется автоматически с учётом root_path
      )
```

### 3. Шаблон .env.example (templates/project/)

**Добавить**:

```bash
# =============================================================================
# Reverse Proxy Configuration
# =============================================================================
# При работе за nginx с путевым префиксом (например, /my-service/)
# установите ROOT_PATH равным этому префиксу.
#
# Локальная разработка: ROOT_PATH= (пустое)
# Production за proxy: ROOT_PATH=/my-service
#
# ВАЖНО: nginx НЕ должен делать rewrite, FastAPI сам обработает root_path
ROOT_PATH=
```

### 4. Knowledge база (knowledge/infrastructure/nginx.md)

**Добавить секцию**:

```markdown
## Работа с путевыми префиксами (Multi-Service на одном IP)

### Проблема

При размещении нескольких сервисов по разным путям:
- `/service-a/` → Service A
- `/service-b/` → Service B

### Best Practice

| Компонент | Настройка |
|-----------|-----------|
| nginx | БЕЗ rewrite, передаёт полный путь |
| FastAPI | root_path из env переменной |
| .env | ROOT_PATH=/service-name |

### Почему НЕ использовать rewrite

rewrite ломает:
- StaticFiles mounts
- WebSocket endpoints
- Sub-applications
- Некоторые redirect сценарии

### Пример

nginx:
```nginx
location /my-service/ {
    proxy_pass http://my-service:8000;  # без trailing slash, без rewrite
}
```

FastAPI:
```python
app = FastAPI(root_path=os.getenv("ROOT_PATH", ""))
```

.env:
```
ROOT_PATH=/my-service
```
```

### 5. Conventions (conventions.md)

**Добавить в секцию 9. Конфигурация**:

```markdown
### 9.3 Reverse Proxy (root_path)

При работе за nginx с путевым префиксом:

```python
# src/core/config.py

class Settings(BaseSettings):
    # ... другие настройки

    # Reverse proxy
    root_path: str = ""  # Путевой префикс (например, "/my-service")

# src/main.py

app = FastAPI(
    title=settings.app_name,
    root_path=settings.root_path,
)
```

**Правила**:
- nginx НЕ делает rewrite
- FastAPI использует root_path из env
- Routes объявляются БЕЗ префикса
- Mounts работают автоматически
```

---

## Миграция существующих сервисов

### Шаг 1: nginx-proxy-vps

```diff
  location /free-ai-selector/ {
-     rewrite ^/free-ai-selector/(.*) /$1 break;
      proxy_pass http://free-ai-selector-business-api:8000;
  }
```

### Шаг 2: Каждый сервис

1. Убедиться, что ROOT_PATH установлен в .env
2. Убедиться, что root_path используется в FastAPI app
3. Перезапустить контейнер

### Шаг 3: Тестирование

```bash
# API
curl http://IP/service-name/health
curl http://IP/service-name/api/v1/...

# Static files
curl http://IP/service-name/static/index.html

# OpenAPI docs
curl http://IP/service-name/docs
curl http://IP/service-name/openapi.json
```

---

## Затрагиваемые файлы фреймворка

| # | Файл | Изменение | Статус |
|---|------|-----------|--------|
| 1 | `templates/infrastructure/nginx/conf.d/service-location.conf.template` | Добавить шаблон без rewrite | ✅ Done |
| 2 | `templates/services/fastapi_business_api/src/main.py` | Добавить root_path | ✅ Done |
| 3 | `templates/services/fastapi_business_api/src/core/config.py` | Добавить root_path | ✅ Done |
| 4 | `templates/services/postgres_data_api/src/main.py` | Добавить root_path | ✅ Done |
| 5 | `templates/services/postgres_data_api/src/core/config.py` | Добавить root_path | ✅ Done |
| 6 | `templates/services/mongo_data_api/src/main.py` | Добавить root_path | ✅ Done |
| 7 | `templates/services/mongo_data_api/src/core/config.py` | Добавить root_path | ✅ Done |
| 8 | `templates/project/.env.example.template` | Добавить ROOT_PATH | ✅ Done |
| 9 | `knowledge/infrastructure/nginx.md` | Документация multi-service | ✅ Done |
| 10 | `conventions.md` | Секция 9.3 Reverse Proxy | ✅ Done |

---

## Приоритет

**Высокий** — влияет на все проекты с multi-service deployment.

---

## Статус

| Этап | Статус |
|------|--------|
| Проектирование | ✅ Завершено (этот документ) |
| Реализация в фреймворке | ✅ Завершено (2026-01-01) |
| Миграция free-ai-selector | ⏳ Ожидает |
| Миграция других сервисов | ⏳ Ожидает |

---

*Создано: 2025-12-31*
*Автор: bgs (с помощью Claude Code)*
*Причина: Анализ и исправление проблемы 404 для StaticFiles в free-ai-selector*
