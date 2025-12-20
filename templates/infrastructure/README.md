# Инфраструктура {project_name} MVP

Шаблоны инфраструктуры для развёртывания MVP проекта.

## Структура

```
infrastructure/
├── docker-compose/
│   ├── docker-compose.yml        # Базовая конфигурация
│   ├── docker-compose.dev.yml    # Development overrides
│   ├── docker-compose.prod.yml   # Production overrides
│   └── .env.example              # Шаблон переменных окружения
├── nginx/
│   ├── nginx.conf                # Конфигурация Nginx
│   └── Dockerfile                # Dockerfile для Nginx
├── github-actions/
│   └── .github/
│       └── workflows/
│           ├── ci.yml            # CI pipeline
│           └── cd.yml            # CD pipeline
├── Makefile                      # Команды управления
└── README.md                     # Этот файл
```

## Быстрый старт

### 1. Подготовка окружения

```bash
# Копируем переменные окружения
cp docker-compose/.env.example .env

# Редактируем .env
nano .env
```

### 2. Запуск в development режиме

```bash
# Запуск всех сервисов
make dev

# Или напрямую через docker compose
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 3. Проверка

```bash
# Статус контейнеров
make ps

# Логи
make logs

# Health check
curl http://localhost:8000/health
```

## Окружения

### Development

```bash
make dev                # Запуск с hot reload
make dev-tools          # + pgAdmin, Redis Commander
make logs               # Просмотр логов
```

**Особенности:**
- Hot reload через volume mounts
- Debug режим включён
- Все порты открыты
- Доступны dev-инструменты

### Production

```bash
make prod               # Запуск production
make prod-build         # Пересборка и запуск
```

**Особенности:**
- Nginx reverse proxy с SSL
- Ограничения ресурсов (CPU, память)
- Rate limiting
- Security headers
- Закрытые внутренние порты

## Сервисы

| Сервис | Dev Port | Prod Port | Описание |
|--------|----------|-----------|----------|
| API | 8000 | 443 (nginx) | Business API |
| Data API | 8001 | internal | Data API |
| PostgreSQL | 5432 | internal | База данных |
| Redis | 6379 | internal | Кэш/очереди |
| pgAdmin | 5050 | — | Dev tool |

## Команды Makefile

```bash
# Справка
make help

# Development
make dev            # Запуск dev
make dev-build      # Пересборка dev
make logs           # Логи

# Тестирование
make test           # Все тесты
make test-unit      # Unit тесты
make test-cov       # С coverage

# Линтинг
make lint           # Проверка
make lint-fix       # Автоисправление
make format         # Форматирование

# База данных
make db-migrate     # Применить миграции
make db-shell       # PostgreSQL CLI
make db-backup      # Бэкап

# Очистка
make clean          # Временные файлы
make clean-docker   # Docker ресурсы
```

## CI/CD

### CI Pipeline (ci.yml)

Запускается при push/PR:

1. **Lint** — Ruff, MyPy
2. **Unit Tests** — pytest с coverage
3. **Integration Tests** — с PostgreSQL, Redis
4. **Security Scan** — Bandit, Safety
5. **Build** — Docker images

### CD Pipeline (cd.yml)

Запускается при создании тега `v*.*.*`:

1. **Build & Push** — GitHub Container Registry
2. **Deploy Staging** — автоматически
3. **Deploy Production** — после approval

### Secrets для GitHub Actions

```
STAGING_HOST          # IP staging сервера
STAGING_USER          # SSH пользователь
STAGING_SSH_KEY       # SSH приватный ключ

PRODUCTION_HOST       # IP production сервера
PRODUCTION_USER       # SSH пользователь
PRODUCTION_SSH_KEY    # SSH приватный ключ

CODECOV_TOKEN         # Токен Codecov (опционально)
```

## Nginx

### SSL сертификаты

**Development:**
- Самоподписанный сертификат генерируется автоматически

**Production:**
```bash
# Let's Encrypt с certbot
certbot certonly --webroot -w /var/www/html -d your-domain.com

# Копируем сертификаты
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

### Rate Limiting

- API: 10 req/s (burst 20)
- Auth: 5 req/min (burst 5)

## Мониторинг

### Health Checks

Все сервисы имеют `/health` endpoint:

```bash
curl http://localhost:8000/health
# {"status": "healthy", "timestamp": "..."}
```

### Логи

```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f {context}-api

# Nginx access logs
docker compose exec nginx tail -f /var/log/nginx/access.log
```

## Troubleshooting

### Контейнер не запускается

```bash
# Проверить логи
docker compose logs {service_name}

# Проверить статус
docker compose ps

# Перезапустить
docker compose restart {service_name}
```

### База данных недоступна

```bash
# Проверить PostgreSQL
docker compose exec postgres pg_isready

# Проверить подключение
make db-shell
```

### Порт занят

```bash
# Найти процесс
lsof -i :8000

# Изменить порт в .env
API_PORT=8080
```

## Переменные окружения

Смотрите `.env.example` для полного списка.

**Обязательные для production:**
- `POSTGRES_PASSWORD` — пароль БД
- `JWT_SECRET_KEY` — секрет JWT (min 32 chars)
- `TELEGRAM_BOT_TOKEN` — токен бота (если используется)
