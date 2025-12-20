# Паттерны CI/CD

> **Назначение**: Настройка GitHub Actions для CI/CD.

---

## CI Pipeline

```yaml
# .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install ruff mypy

      - name: Ruff check
        run: ruff check services/

      - name: Ruff format check
        run: ruff format --check services/

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r services/{context}_api/requirements.txt
          pip install -r services/{context}_api/requirements-dev.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          pytest services/{context}_api/tests \
            --cov=services/{context}_api/src \
            --cov-report=xml \
            --cov-fail-under=75

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: test

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build API image
        uses: docker/build-push-action@v5
        with:
          context: ./services/{context}_api
          push: false
          tags: {context}-api:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build Data image
        uses: docker/build-push-action@v5
        with:
          context: ./services/{context}_data
          push: false
          tags: {context}-data:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## CD Pipeline

```yaml
# .github/workflows/cd.yml

name: CD

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    name: Build and Push
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha

      - name: Build and push API
        uses: docker/build-push-action@v5
        with:
          context: ./services/{context}_api
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-api:${{ steps.meta.outputs.version }}
          labels: ${{ steps.meta.outputs.labels }}

      - name: Build and push Data
        uses: docker/build-push-action@v5
        with:
          context: ./services/{context}_data
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-data:${{ steps.meta.outputs.version }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /opt/{context}
            docker compose pull
            docker compose up -d
            docker system prune -f
```

---

## PR Preview

```yaml
# .github/workflows/preview.yml

name: PR Preview

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  preview:
    name: Deploy Preview
    runs-on: ubuntu-latest
    environment:
      name: preview
      url: ${{ steps.deploy.outputs.url }}

    steps:
      - uses: actions/checkout@v4

      - name: Build and deploy preview
        id: deploy
        run: |
          # Логика деплоя preview окружения
          echo "url=https://pr-${{ github.event.pull_request.number }}.preview.example.com" >> $GITHUB_OUTPUT

      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 Preview deployed: ${{ steps.deploy.outputs.url }}'
            })
```

---

## Секреты и переменные

```yaml
# Требуемые секреты в GitHub:

# Для CI:
# - CODECOV_TOKEN (для отчётов о покрытии)

# Для CD:
# - DEPLOY_HOST (IP или домен сервера)
# - DEPLOY_USER (SSH пользователь)
# - DEPLOY_KEY (SSH приватный ключ)

# Для Docker Registry:
# - GITHUB_TOKEN (автоматически)
# или
# - DOCKER_USERNAME
# - DOCKER_PASSWORD
```

---

## Миграции в CI/CD

```yaml
# В deploy job

- name: Run migrations
  uses: appleboy/ssh-action@v1.0.0
  with:
    host: ${{ secrets.DEPLOY_HOST }}
    username: ${{ secrets.DEPLOY_USER }}
    key: ${{ secrets.DEPLOY_KEY }}
    script: |
      cd /opt/{context}
      docker compose exec -T {context}-data alembic upgrade head
```

---

## Rollback

```yaml
# .github/workflows/rollback.yml

name: Rollback

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to rollback to'
        required: true

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Rollback deployment
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /opt/{context}
            docker compose pull {context}-api:${{ github.event.inputs.version }}
            docker compose pull {context}-data:${{ github.event.inputs.version }}
            docker compose up -d
```

---

## Чек-лист

- [ ] CI: lint, test, build
- [ ] CD: push images, deploy
- [ ] Coverage ≥75%
- [ ] Секреты настроены
- [ ] Миграции в деплое
- [ ] Rollback workflow
