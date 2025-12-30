# Управление секретными данными

> **Назначение**: Правила работы с секретами в проектах AIDD-MVP.
> **Критичность**: Высокая — нарушение ведёт к компрометации системы.

---

## 1. Классификация секретов

### 1.1 Типы секретных данных

| Категория | Примеры | Уровень риска |
|-----------|---------|---------------|
| **Аутентификация** | Пароли БД, JWT секреты, API ключи | Критический |
| **Токены сервисов** | Telegram Bot Token, OAuth tokens | Критический |
| **Строки подключения** | DATABASE_URL, REDIS_URL | Высокий |
| **Криптографические ключи** | SSL/TLS сертификаты, SSH ключи | Критический |
| **Платёжные данные** | Ключи платёжных систем | Критический |

### 1.2 Файлы содержащие секреты

```
ЗАПРЕЩЕНО коммитить:
├── .env                    # Переменные окружения
├── .env.local              # Локальные переменные
├── .env.*.local            # Любые локальные .env
├── *.pem                   # SSL/TLS сертификаты
├── *.key                   # Приватные ключи
├── credentials.json        # Учётные данные
├── secrets.json            # Секреты
├── service-account.json    # Service account ключи
└── .secrets.baseline       # Baseline detect-secrets
```

---

## 2. Защитные меры

### 2.1 Git защита

#### .gitignore (обязательно)

```gitignore
# Environment
.env
.env.local
.env.*.local
*.env

# Secrets
*.pem
*.key
credentials.json
secrets.json
service-account.json

# Claude Code local settings
.claude/settings.local.json
```

#### Pre-commit hooks (рекомендуется)

```bash
# Установка
pip install pre-commit
pre-commit install

# Запуск вручную
pre-commit run --all-files
```

Шаблон: `templates/project/.pre-commit-config.yaml.template`

### 2.2 Claude Code защита

В `.claude/settings.json` настроены запреты:

```json
{
  "permissions": {
    "deny": [
      "Read(**/.env)",
      "Read(**/.env.*)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Read(**/credentials.json)",
      "Read(**/secrets.json)",
      "Edit(**/.env)",
      "Write(**/.env)",
      "Bash(cat **/.env*)",
      "Bash(echo *PASSWORD*)"
    ]
  }
}
```

### 2.3 Защита в логах

Structlog автоматически маскирует секреты:

```python
from shared.utils.logger import get_logger

logger = get_logger()

# Автоматически замаскируется
logger.info("User login", password="secret123", token="abc")
# Output: {"password": "***REDACTED***", "token": "***REDACTED***"}
```

Маскируемые поля:
- `password`, `passwd`, `pwd`, `secret`, `token`
- `api_key`, `apikey`, `api_secret`, `jwt`
- `database_url`, `connection_string`
- `private_key`, `public_key`
- И другие (см. `shared/utils/logger.py`)

### 2.4 Защита в Docker

```yaml
# docker-compose.yml
environment:
  # ОБЯЗАТЕЛЬНЫЕ переменные (без default)
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?Required}

  # Не передавать секреты через ARG
  # ARG опасны - сохраняются в истории образа
```

### 2.5 Защита в CI/CD

```yaml
# GitHub Actions
env:
  # Используйте секреты репозитория
  DATABASE_URL: ${{ secrets.DATABASE_URL }}

  # НЕ логируйте секреты
  # Плохо: echo $DATABASE_URL
```

---

## 3. Правила для разработчиков

### 3.1 НИКОГДА не делать

| Запрещено | Пример | Почему |
|-----------|--------|--------|
| Hardcode секретов | `password = "secret123"` | Попадёт в git history |
| Default пароли | `:-secret` в docker-compose | Используются в production |
| Секреты в URL | `?api_key=xxx` | Логируется в access logs |
| Секреты в логах | `logger.info(password)` | Утечка через логи |
| Print debug | `print(f"Token: {token}")` | Вывод в консоль |

### 3.2 ВСЕГДА делать

| Требование | Пример |
|------------|--------|
| Использовать env vars | `os.getenv("PASSWORD")` |
| Требовать обязательно | `${VAR:?Required}` |
| Валидировать при старте | Pydantic Settings |
| Маскировать в логах | sanitize_sensitive_data() |
| Использовать pre-commit | gitleaks, detect-secrets |

---

## 4. Генерация секретов

### 4.1 Команды для генерации

```bash
# Пароли и ключи (32 символа hex)
openssl rand -hex 32

# Пароли для БД (base64, без спецсимволов)
openssl rand -base64 24

# UUID-based
python -c "import uuid; print(uuid.uuid4())"

# JWT секрет (минимум 32 символа)
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4.2 Требования к паролям

| Тип | Минимум | Рекомендация |
|-----|---------|--------------|
| JWT Secret | 32 символа | 64 символа |
| Database | 16 символов | 24 символа |
| API Key | 32 символа | 64 символа |
| Webhook Secret | 32 символа | 64 символа |

---

## 5. Ротация секретов

### 5.1 Периодичность

| Секрет | Рекомендуемый период |
|--------|---------------------|
| JWT Secret | 90 дней |
| Database password | 90 дней |
| API Keys | 30-90 дней |
| SSL сертификаты | До истечения |

### 5.2 Процедура ротации

```
1. Сгенерировать новый секрет
2. Добавить в secrets manager / .env
3. Перезапустить сервисы
4. Проверить работоспособность
5. Отозвать старый секрет (если применимо)
6. Задокументировать в changelog
```

---

## 6. Инциденты

### 6.1 При утечке секрета

```
НЕМЕДЛЕННО:
1. Отозвать/сменить скомпрометированный секрет
2. Проверить логи на несанкционированный доступ
3. Сообщить team lead / security

ПОСЛЕ:
4. Провести анализ причины утечки
5. Добавить превентивные меры
6. Обновить документацию
```

### 6.2 Проверка утечек в git history

```bash
# Поиск секретов в истории
gitleaks detect --source . --verbose

# Если найдены секреты в истории:
# 1. Сменить все скомпрометированные секреты
# 2. Рассмотреть git filter-branch (сложно!)
# 3. Или принять риск и защитить новые коммиты
```

---

## 7. Чек-лист для ревью

### Security Review Checklist

- [ ] Нет hardcoded секретов в коде
- [ ] .env файлы в .gitignore
- [ ] Секретные поля маскируются в логах
- [ ] Нет секретов в Dockerfile ARG
- [ ] Нет default паролей в docker-compose
- [ ] CI/CD использует secrets, не plain text
- [ ] Pre-commit hooks настроены (gitleaks)
- [ ] Валидация секретов при старте приложения

---

## 8. Интеграция с секрет-менеджерами (опционально)

### 8.1 HashiCorp Vault

```python
import hvac

client = hvac.Client(url='http://vault:8200')
client.token = os.getenv('VAULT_TOKEN')

secret = client.secrets.kv.v2.read_secret_version(
    path='myapp/database'
)
password = secret['data']['data']['password']
```

### 8.2 AWS Secrets Manager

```python
import boto3

client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='myapp/database')
secret = json.loads(response['SecretString'])
```

### 8.3 Docker Secrets

```yaml
# docker-compose.yml
secrets:
  db_password:
    file: ./secrets/db_password.txt

services:
  api:
    secrets:
      - db_password
```

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| `knowledge/quality/production-requirements.md` | Production чек-лист |
| `templates/project/.pre-commit-config.yaml.template` | Pre-commit hooks |
| `templates/shared/utils/logger.py` | Фильтрация секретов в логах |
| `.claude/settings.json` | Ограничения для AI |

---

**Версия документа**: 1.0
**Создан**: 2025-12-30
