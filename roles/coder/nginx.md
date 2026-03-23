# Function: Nginx (Level >= 3)

> **Purpose**: Setting up Nginx as a reverse proxy.

---

## Applicability Level

```
Level 2 (MVP): NOT REQUIRED
Level 3+:      MANDATORY
```

---

## Goal

Set up Nginx as a reverse proxy and API gateway
for the production environment.

---

## When to Apply

```
if MATURITY_LEVEL >= 3:
    → Add Nginx
    → Configure SSL
    → Configure rate limiting
else:
    → Skip (direct API access)
```

---

## Components

### 1. nginx.conf (base configuration)

```nginx
# nginx.conf
# Nginx configuration for {context}

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

    # Logging
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

    # Optimizations
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

    # Upstream services
    upstream business_api {
        server {context}-api:8000;
        keepalive 32;
    }

    upstream data_api {
        server {context}-data:8001;
        keepalive 32;
    }

    # Main server
    server {
        listen 80;
        server_name _;

        # Redirect to HTTPS (for production)
        # return 301 https://$host$request_uri;

        # Or direct proxy (for development)
        include /etc/nginx/conf.d/locations.conf;
    }

    # HTTPS server (for production)
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

### 2. locations.conf (routes)

```nginx
# /etc/nginx/conf.d/locations.conf
# API routes

# Request ID generation
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

    # Proxy settings
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

# Data API (internal access only)
location /internal/data/ {
    # Deny external access
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

# API documentation (OpenAPI)
location /docs {
    proxy_pass http://business_api/docs;
    proxy_set_header Host $host;
}

location /openapi.json {
    proxy_pass http://business_api/openapi.json;
    proxy_set_header Host $host;
}

# Static files (if any)
location /static/ {
    alias /var/www/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Error handling
error_page 500 502 503 504 /50x.html;
location = /50x.html {
    root /usr/share/nginx/html;
    internal;
}
```

### 3. Dockerfile for Nginx

```dockerfile
# nginx/Dockerfile
FROM nginx:1.25-alpine

# Copy configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# SSL certificates (for production)
# COPY ssl/ /etc/nginx/ssl/

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

EXPOSE 80 443
```

### 4. docker-compose Service

```yaml
# docker-compose.yml (add to existing)

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
      # For development - live reload configuration
      # - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      # - ./nginx/conf.d:/etc/nginx/conf.d:ro
      # SSL certificates
      # - ./nginx/ssl:/etc/nginx/ssl:ro
      # Static files
      # - ./static:/var/www/static:ro
      pass
```

### 5. SSL Configuration (Level 3+)

```nginx
# /etc/nginx/conf.d/ssl.conf
# SSL settings

# SSL sessions
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# Modern protocols
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

# HSTS (uncomment for production)
# add_header Strict-Transport-Security "max-age=63072000" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

---

## Directory Structure

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

### Zone Configuration

```nginx
# In http block
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;
```

### Applying to Locations

```nginx
# General API - 10 requests per second
location /api/v1/ {
    limit_req zone=api_limit burst=20 nodelay;
    ...
}

# Authorization - 5 requests per second
location /api/v1/auth/ {
    limit_req zone=auth_limit burst=10 nodelay;
    ...
}
```

---

## Security Headers

```nginx
# In server or location block
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# For API (remove for static files)
add_header Content-Security-Policy "default-src 'none'" always;
```

---

## Monitoring

### Status Endpoint

```nginx
# Add to server block
location /nginx_status {
    stub_status;
    allow 127.0.0.1;
    allow 10.0.0.0/8;
    deny all;
}
```

---

## Quality Gates

### NGINX_READY (Level 3+)

- [ ] nginx.conf created and valid
- [ ] Locations configured for all services
- [ ] Rate limiting configured
- [ ] SSL configured (if production)
- [ ] Security headers added
- [ ] `docker-compose up nginx` starts successfully
- [ ] Health check passes
- [ ] API is accessible through Nginx

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/infrastructure/nginx.md` | Nginx setup |
| `knowledge/infrastructure/ssl.md` | SSL configuration |
| `templates/infrastructure/nginx/` | Templates |
