# Настройка Nginx

> **Назначение**: Nginx как reverse proxy (Level 3+).

---

## Базовая конфигурация

```nginx
# nginx.conf

user nginx;
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
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

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
    gzip_types text/plain text/css text/xml application/json application/javascript;

    # Upstream для Business API
    upstream {context}_api {
        server {context}-api:8000;
        keepalive 32;
    }

    # Upstream для Data API (внутренний)
    upstream {context}_data {
        server {context}-data:8001;
        keepalive 32;
    }

    server {
        listen 80;
        server_name localhost;

        # Health check
        location /health {
            access_log off;
            return 200 "OK";
            add_header Content-Type text/plain;
        }

        # API
        location /api/ {
            proxy_pass http://{context}_api;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";

            # Таймауты
            proxy_connect_timeout 30s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;

            # Буферизация
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # Документация API (только dev)
        location /docs {
            proxy_pass http://{context}_api;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
        }

        location /redoc {
            proxy_pass http://{context}_api;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
        }
    }
}
```

---

## SSL конфигурация

```nginx
# nginx-ssl.conf

server {
    listen 80;
    server_name example.com;

    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    # SSL сертификаты
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # SSL настройки
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Протоколы и шифры
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # API
    location /api/ {
        proxy_pass http://{context}_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
    }
}
```

---

## Rate Limiting

```nginx
# В секции http
http {
    # Зона для rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    server {
        # Общий лимит для API
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://{context}_api;
        }

        # Строгий лимит для аутентификации
        location /api/v1/auth/ {
            limit_req zone=auth_limit burst=5 nodelay;
            proxy_pass http://{context}_api;
        }
    }
}
```

---

## Load Balancing

```nginx
# Балансировка нескольких инстансов

upstream {context}_api {
    least_conn;  # или ip_hash для sticky sessions

    server {context}-api-1:8000 weight=3;
    server {context}-api-2:8000 weight=2;
    server {context}-api-3:8000 backup;

    keepalive 32;
}
```

---

## Dockerfile для Nginx

```dockerfile
# nginx/Dockerfile

FROM nginx:1.25-alpine

# Удаление дефолтной конфигурации
RUN rm /etc/nginx/conf.d/default.conf

# Копирование кастомной конфигурации
COPY nginx.conf /etc/nginx/nginx.conf

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
```

---

## Docker Compose

```yaml
# В docker-compose.prod.yml

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
      - nginx_logs:/var/log/nginx
    depends_on:
      - {context}-api
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  nginx_logs:
```

---

## Чек-лист

- [ ] Reverse proxy настроен
- [ ] Заголовки X-Real-IP, X-Forwarded-For
- [ ] Gzip включен
- [ ] SSL настроен (production)
- [ ] Rate limiting добавлен
- [ ] Health check endpoint
