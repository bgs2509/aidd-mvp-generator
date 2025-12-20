# Конфигурация SSL

> **Назначение**: Настройка SSL/TLS для production.

---

## Let's Encrypt с Certbot

```bash
# Установка Certbot
apt-get install certbot python3-certbot-nginx

# Получение сертификата
certbot --nginx -d example.com -d www.example.com

# Автоматическое обновление
certbot renew --dry-run

# Cron для обновления
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## Docker с Certbot

```yaml
# docker-compose.prod.yml

services:
  {context}-nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - certbot_certs:/etc/letsencrypt:ro
      - certbot_www:/var/www/certbot:ro

  certbot:
    image: certbot/certbot
    volumes:
      - certbot_certs:/etc/letsencrypt
      - certbot_www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  certbot_certs:
  certbot_www:
```

---

## Nginx с Let's Encrypt

```nginx
# nginx.conf для Let's Encrypt

server {
    listen 80;
    server_name example.com;

    # Для проверки Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Редирект на HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name example.com;

    # Сертификаты Let's Encrypt
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Рекомендуемые настройки от Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location /api/ {
        proxy_pass http://{context}_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Самоподписанный сертификат (dev)

```bash
# Генерация самоподписанного сертификата
mkdir -p nginx/ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/privkey.pem \
    -out nginx/ssl/fullchain.pem \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=Dev/CN=localhost"
```

---

## SSL настройки (production)

```nginx
# Современные SSL настройки

ssl_protocols TLSv1.2 TLSv1.3;

# Шифры для TLS 1.2
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

# Приоритет серверных шифров
ssl_prefer_server_ciphers off;

# Сессии
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Diffie-Hellman
ssl_dhparam /etc/nginx/ssl/dhparam.pem;
```

---

## Генерация DH параметров

```bash
# Генерация dhparam (может занять несколько минут)
openssl dhparam -out nginx/ssl/dhparam.pem 2048
```

---

## Security Headers

```nginx
# Заголовки безопасности

server {
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Защита от clickjacking
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Защита от XSS
    add_header X-XSS-Protection "1; mode=block" always;

    # Защита от MIME sniffing
    add_header X-Content-Type-Options "nosniff" always;

    # Referrer Policy
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Content Security Policy (настроить под проект)
    # add_header Content-Security-Policy "default-src 'self'" always;
}
```

---

## Проверка SSL

```bash
# Проверка конфигурации
nginx -t

# Проверка сертификата
openssl s_client -connect example.com:443 -servername example.com

# Проверка даты истечения
openssl x509 -enddate -noout -in /etc/letsencrypt/live/example.com/fullchain.pem

# Тестирование через SSL Labs
# https://www.ssllabs.com/ssltest/
```

---

## Скрипт инициализации

```bash
#!/bin/bash
# init-letsencrypt.sh

domains=(example.com www.example.com)
email="admin@example.com"
staging=0  # 1 для тестирования

# Остановить nginx если запущен
docker compose stop nginx

# Получить сертификат
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $email \
    --agree-tos \
    --no-eff-email \
    $(if [ $staging -eq 1 ]; then echo "--staging"; fi) \
    -d ${domains[0]} \
    -d ${domains[1]}

# Запустить nginx
docker compose up -d nginx
```

---

## Чек-лист

- [ ] SSL сертификат получен
- [ ] Автообновление настроено
- [ ] TLS 1.2+ только
- [ ] HSTS включен
- [ ] Security headers добавлены
- [ ] SSL Labs оценка A+
