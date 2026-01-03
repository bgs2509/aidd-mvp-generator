# Dockerfile для Nginx
# {project_name} MVP — Reverse Proxy

# SECURITY: В production используйте pinned SHA для reproducible builds
# docker pull nginx:alpine && docker inspect --format='{{index .RepoDigests 0}}' nginx:alpine
# Пример: FROM nginx:alpine@sha256:abc123...
FROM nginx:alpine

# Метаданные
LABEL maintainer="{maintainer}"
LABEL description="Nginx reverse proxy для {project_name}"

# Удаляем дефолтную конфигурацию
RUN rm /etc/nginx/conf.d/default.conf

# Копируем конфигурацию
COPY nginx.conf /etc/nginx/nginx.conf

# Создаём директории
RUN mkdir -p /etc/nginx/ssl \
    && mkdir -p /var/log/nginx \
    && mkdir -p /app/static

# Генерируем самоподписанный сертификат для development
# В production используйте настоящие сертификаты!
RUN apk add --no-cache openssl \
    && openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout /etc/nginx/ssl/key.pem \
       -out /etc/nginx/ssl/cert.pem \
       -subj "/C=RU/ST=Moscow/L=Moscow/O=Development/CN=localhost" \
    && apk del openssl

# Права доступа
RUN chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /app/static

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/nginx-health || exit 1

# Порты
EXPOSE 80 443

# Запуск
# ENTRYPOINT + CMD паттерн позволяет переопределять аргументы при запуске
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
