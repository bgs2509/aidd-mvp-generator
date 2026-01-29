# Паттерны CI/CD

> **Назначение**: Рекомендации по построению CI/CD без привязки к платформе.

---

## CI Pipeline

### Когда запускать
- push в основные ветки
- pull/merge request
- по расписанию (опционально)

### Что проверять
1. Lint и форматирование (ruff)
2. Type check (mypy)
3. Unit/Integration tests (pytest)
4. Coverage ≥75%
5. Security scan (bandit/safety)
6. Build Docker images

### Пример команд

```bash
pip install ruff mypy pytest pytest-cov bandit safety
ruff check .
ruff format --check .
mypy .
pytest services/{context}_api/tests     --cov=services/{context}_api/src     --cov-report=xml     --cov-fail-under=75
bandit -r . -c pyproject.toml || true
safety check --full-report || true

docker build -t {context}-api:local services/{context}_api
docker build -t {context}-data:local services/{context}_data
```

### Зависимости в CI
- PostgreSQL, Redis (если нужны интеграционные тесты)
- переменные окружения (DATABASE_URL, REDIS_URL)

---

## CD Pipeline

### Когда запускать
- тег релиза (например, v1.2.3)
- вручную (manual)
- по расписанию (опционально)

### Шаги
1. Build & Push images в registry
2. Deploy на staging (если есть)
3. Smoke tests
4. Approval и deploy на production
5. Rollback сценарий (на случай ошибки)

---

## PR Preview (опционально)

- Поднять временное окружение для MR/PR
- Вернуть URL превью в комментарии/статусе проверки

---

## Секреты и переменные

Пример необходимых секретов:
- REGISTRY_USER / REGISTRY_PASSWORD (если нужен приватный реестр)
- DEPLOY_HOST / DEPLOY_USER / DEPLOY_KEY
- CODECOV_TOKEN (опционально)

---

## Миграции в CI/CD

```bash
# Пример в деплой-скрипте
cd /opt/{context}
docker compose exec -T {context}-data alembic upgrade head
```

---

## Rollback

```bash
# Пример ручного отката
cd /opt/{context}
docker compose pull {context}-api:{version}
docker compose pull {context}-data:{version}
docker compose up -d
```

---

## Чек-лист

- [ ] CI: lint, test, build
- [ ] Coverage ≥75%
- [ ] CD: push images, deploy (если нужно)
- [ ] Секреты настроены
- [ ] Миграции и rollback описаны
