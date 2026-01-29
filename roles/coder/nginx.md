# Функция: Nginx (Level ≥ 3)

> **Назначение**: Настройка Nginx как reverse proxy.

---

## Уровень применения

```
Level 2 (MVP): НЕ ТРЕБУЕТСЯ
Level 3+:      ОБЯЗАТЕЛЬНО
```

---

## Цель

Настроить Nginx как reverse proxy и API gateway
для production окружения.

---

## Когда применяется

```
if MATURITY_LEVEL >= 3:
    → Добавить Nginx
    → Настроить SSL
    → Настроить rate limiting
else:
    → Пропустить (прямой доступ к API)
```

---

## Компоненты

### 1. nginx.conf (базовая конфигурация)

```nginx
# nginx.conf
# Конфигурация Nginx для {context}

worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Логирование
    log_format json escape=json '{'
        '"time": "$time_iso8601",'
        '"remote_addr": "$remote_addr",'
        '"request_id": "$request_id",'
        '"request_method": "$request_method",'
        '"request_uri": "$request_uri",'
        '"status": $status,'
        '"body_bytes_sent": $body_bytes_sent,'
        '"request_time": $request_time,'
        '"upstream_response_time": "$upstream_response_time",'
        '"http_referer": "$http_referer",'
        '"http_user_agent": "$http_user_agent"'
    '}';

    access_log /var/log/nginx/access.log json;

    # Оптимизации
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    # Upstream сервисы
    upstream business_api {
        server {context}-api:8000;
        keepalive 32;
    }

    upstream data_api {
        server {context}-data:8001;
        keepalive 32;
    }

    # Основной сервер
    server {
        listen 80;
        server_name _;

        # Редирект на HTTPS (для production)
        # return 301 https://$host$request_uri;

        # Или прямой proxy (для development)
        include /etc/nginx/conf.d/locations.conf;
    }

    # HTTPS сервер (для production)
    # server {
    #     listen 443 ssl http2;
    #     server_name example.com;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    #     ssl_prefer_server_ciphers off;
    #
    #     include /etc/nginx/conf.d/locations.conf;
    # }
}
```

### 2. locations.conf (маршруты)

```nginx
# /etc/nginx/conf.d/locations.conf
# Маршруты API

# Генерация Request ID
set $request_id $request_id;
if ($http_x_request_id) {
    set $request_id $http_x_request_id;
}

# Health check
location /health {
    access_log off;
    return 200 '{"status": "ok"}';
    add_header Content-Type application/json;
}

# Business API
location /api/v1/ {
    # Rate limiting
    limit_req zone=api_limit burst=20 nodelay;
    limit_conn conn_limit 10;

    # Proxy headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Request-ID $request_id;

    # Proxy настройки
    proxy_connect_timeout 30s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;

    # Upstream
    proxy_pass http://business_api;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
}

# Data API (только внутренний доступ)
location /internal/data/ {
    # Запретить внешний доступ
    allow 10.0.0.0/8;
    allow 172.16.0.0/12;
    allow 192.168.0.0/16;
    deny all;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Request-ID $request_id;

    proxy_pass http://data_api/api/v1/;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
}

# Документация API (OpenAPI)
location /docs {
    proxy_pass http://business_api/docs;
    proxy_set_header Host $host;
}

location /openapi.json {
    proxy_pass http://business_api/openapi.json;
    proxy_set_header Host $host;
}

# Статика (если есть)
location /static/ {
    alias /var/www/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Обработка ошибок
error_page 500 502 503 504 /50x.html;
location = /50x.html {
    root /usr/share/nginx/html;
    internal;
}
```

### 3. Dockerfile для Nginx

```dockerfile
# nginx/Dockerfile
FROM nginx:1.25-alpine

# Копирование конфигурации
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# SSL сертификаты (для production)
# COPY ssl/ /etc/nginx/ssl/

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

EXPOSE 80 443
```

### 4. docker-compose сервис

```yaml
# docker-compose.yml (добавить к существующему)

services:
  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - {context}-api
    networks:
      - {context}-network
    restart: unless-stopped
    volumes:
      # Для development - live reload конфигурации
      # - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      # - ./nginx/conf.d:/etc/nginx/conf.d:ro
      # SSL сертификаты
      # - ./nginx/ssl:/etc/nginx/ssl:ro
      # Статические файлы
      # - ./static:/var/www/static:ro
      pass
```

### 5. SSL конфигурация (Level 3+)

```nginx
# /etc/nginx/conf.d/ssl.conf
# SSL настройки

# SSL сессии
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# Современные протоколы
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

# HSTS (раскомментировать для production)
# add_header Strict-Transport-Security "max-age=63072000" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

---

## Структура директорий

```
nginx/
├── Dockerfile
├── nginx.conf
├── conf.d/
│   ├── locations.conf
│   └── ssl.conf
└── ssl/
    ├── cert.pem
    └── key.pem
```

---

## Rate Limiting

### Настройка зон

```nginx
# В http блоке
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;
```

### Применение к locations

```nginx
# Общий API - 10 запросов в секунду
location /api/v1/ {
    limit_req zone=api_limit burst=20 nodelay;
    ...
}

# Авторизация - 5 запросов в секунду
location /api/v1/auth/ {
    limit_req zone=auth_limit burst=10 nodelay;
    ...
}
```

---

## Security Headers

```nginx
# В server или location блоке
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Для API (убрать для статики)
add_header Content-Security-Policy "default-src 'none'" always;
```

---

## Мониторинг

### Status endpoint

```nginx
# Добавить в server блок
location /nginx_status {
    stub_status;
    allow 127.0.0.1;
    allow 10.0.0.0/8;
    deny all;
}
```

---

## Качественные ворота

### NGINX_READY (Level 3+)

- [ ] nginx.conf создан и валиден
- [ ] Locations настроены для всех сервисов
- [ ] Rate limiting настроен
- [ ] SSL настроен (если production)
- [ ] Security headers добавлены
- [ ] `docker-compose up nginx` запускается
- [ ] Health check проходит
- [ ] API доступен через Nginx

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/infrastructure/nginx.md` | Настройка Nginx |
| `knowledge/infrastructure/ssl.md` | SSL конфигурация |
| `templates/infrastructure/nginx/` | Шаблоны |
