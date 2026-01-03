# Security Checklist для AI-агентов

> **Назначение**: Чек-лист проверки безопасности секретных данных в целевом проекте.
> **Когда проверять**: На этапах REVIEW (5), VALIDATE (7), перед DEPLOY (8).

---

## Автоматическая проверка AI-агентом

AI-агент ОБЯЗАН выполнить следующие проверки перед прохождением качественных ворот.

---

## 1. Проверка .gitignore

### Команды проверки

```bash
# Проверить наличие .gitignore
test -f .gitignore && echo "OK" || echo "FAIL: .gitignore не найден"

# Проверить что .env игнорируется
grep -q "^\.env$" .gitignore && echo "OK" || echo "FAIL: .env не в .gitignore"

# Проверить ключевые паттерны
for pattern in ".env" ".env.local" "*.pem" "*.key" "credentials.json"; do
  grep -q "$pattern" .gitignore && echo "OK: $pattern" || echo "WARN: $pattern не в .gitignore"
done
```

### Критерии

| Проверка | Обязательно | Критичность |
|----------|-------------|-------------|
| `.gitignore` существует | Да | Blocker |
| `.env` в .gitignore | Да | Blocker |
| `*.pem`, `*.key` в .gitignore | Да | Critical |
| `credentials.json` в .gitignore | Да | Critical |

---

## 2. Проверка отсутствия секретов в коде

### Команды проверки

```bash
# Поиск hardcoded паролей
grep -rn "password\s*=\s*['\"][^'\"]*['\"]" services/ --include="*.py" | \
  grep -v "test_\|_test\.py\|example\|template" || echo "OK: Нет hardcoded паролей"

# Поиск hardcoded токенов
grep -rn "token\s*=\s*['\"][^'\"]*['\"]" services/ --include="*.py" | \
  grep -v "test_\|_test\.py\|example\|template" || echo "OK: Нет hardcoded токенов"

# Поиск подозрительных строк
grep -rn "secret\s*=\s*['\"]" services/ --include="*.py" | \
  grep -v "test_\|_test\.py" || echo "OK"
```

### Паттерны для поиска

```
ЗАПРЕЩЁННЫЕ паттерны в Python коде:
- password = "..."
- PASSWORD = "..."
- token = "..."
- api_key = "..."
- secret = "..."
- POSTGRES_PASSWORD = "..."
```

### Критерии

| Проверка | Критичность |
|----------|-------------|
| Нет hardcoded passwords | Blocker |
| Нет hardcoded tokens | Blocker |
| Нет hardcoded API keys | Blocker |

---

## 3. Проверка .env.example

### Команды проверки

```bash
# Проверить наличие .env.example
test -f .env.example && echo "OK" || echo "WARN: .env.example не найден"

# Проверить что нет реальных секретов (placeholder'ы)
if [ -f .env.example ]; then
  # Должны быть CHANGE_ME или подобные маркеры
  grep -q "CHANGE_ME" .env.example && echo "OK: Есть placeholder'ы" || \
    echo "WARN: Нет CHANGE_ME placeholder'ов"

  # Не должно быть реальных паролей
  grep -vE "^#|CHANGE_ME|your_|example|placeholder" .env.example | \
    grep -E "PASSWORD=.+" && echo "WARN: Возможно реальный пароль" || echo "OK"
fi
```

### Критерии

| Проверка | Обязательно | Критичность |
|----------|-------------|-------------|
| `.env.example` существует | Рекомендуется | Warning |
| Содержит CHANGE_ME placeholder'ы | Да | Warning |
| Нет реальных паролей | Да | Critical |

---

## 4. Проверка docker-compose

### Команды проверки

```bash
# Проверить что нет hardcoded секретов
grep -n "PASSWORD.*:.*-" docker-compose*.yml | \
  grep -v ":?" && echo "WARN: Найден default пароль" || echo "OK"

# Проверить использование обязательных переменных
grep -q ":?.*required\|:?.*Required" docker-compose*.yml && \
  echo "OK: Есть обязательные переменные" || \
  echo "WARN: Нет обязательных переменных для секретов"

# Проверить что порт БД закрыт в prod
grep -A5 "postgres:" docker-compose.prod.yml | grep "ports: \[\]" && \
  echo "OK: Порт БД закрыт в prod" || echo "WARN: Порт БД может быть открыт"
```

### Критерии

| Проверка | Критичность |
|----------|-------------|
| Нет `:-secret` default значений | Critical |
| Используется `:?` для обязательных | Warning |
| Порты БД закрыты в prod compose | Warning |

---

## 5. Проверка логирования

### Команды проверки

```bash
# Проверить что используется sanitize_sensitive_data
grep -rn "sanitize_sensitive_data" services/ --include="*.py" || \
  echo "INFO: sanitize_sensitive_data не найден в services/"

# Проверить что не логируются секреты напрямую
grep -rn "logger.*password\|logger.*token\|logger.*secret" services/ --include="*.py" | \
  grep -v "REDACTED\|sanitize" && echo "WARN: Возможно логирование секретов" || echo "OK"

# Проверить setup_logging в main.py
for service in services/*/; do
  grep -q "setup_logging" "${service}src/main.py" 2>/dev/null && \
    echo "OK: setup_logging в $service" || echo "WARN: Нет setup_logging в $service"
done
```

### Критерии

| Проверка | Критичность |
|----------|-------------|
| Используется structlog с sanitization | Warning |
| Нет прямого логирования секретов | Critical |

---

## 6. Проверка CI/CD

### Команды проверки

```bash
# Проверить что секреты используются через secrets
if [ -d ".github/workflows" ]; then
  # Хорошо: ${{ secrets.* }}
  grep -rn '\${{ secrets\.' .github/workflows/ && echo "OK: Используются GitHub secrets"

  # Плохо: hardcoded значения
  grep -rn "PASSWORD=\|TOKEN=" .github/workflows/ | \
    grep -v "secrets\." && echo "WARN: Возможно hardcoded секреты в CI" || echo "OK"
fi
```

### Критерии

| Проверка | Критичность |
|----------|-------------|
| Secrets через ${{ secrets.* }} | Warning |
| Нет hardcoded в workflows | Critical |

---

## 7. Проверка pre-commit hooks

### Команды проверки

```bash
# Проверить наличие .pre-commit-config.yaml
test -f .pre-commit-config.yaml && echo "OK" || echo "WARN: pre-commit не настроен"

# Проверить что gitleaks включён
grep -q "gitleaks" .pre-commit-config.yaml 2>/dev/null && \
  echo "OK: gitleaks настроен" || echo "WARN: gitleaks не настроен"

# Проверить что detect-secrets включён
grep -q "detect-secrets" .pre-commit-config.yaml 2>/dev/null && \
  echo "OK: detect-secrets настроен" || echo "INFO: detect-secrets не настроен"
```

### Критерии

| Проверка | Критичность |
|----------|-------------|
| `.pre-commit-config.yaml` существует | Рекомендуется |
| gitleaks hook настроен | Рекомендуется |

---

## 8. Проверка Settings (Pydantic)

### Что проверять в коде

```python
# ХОРОШО: Обязательные поля без default
class Settings(BaseSettings):
    database_url: str  # Обязательно
    secret_key: str = Field(..., min_length=32)  # С валидацией

# ПЛОХО: Default значения для секретов
class Settings(BaseSettings):
    password: str = "default123"  # НИКОГДА так не делать!
```

### Команды проверки

```bash
# Найти Settings классы с default паролями
grep -A10 "class Settings" services/*/src/core/config.py | \
  grep -E "(password|secret|token).*=.*['\"]" && \
  echo "WARN: Default значения для секретов" || echo "OK"
```

---

## 9. Сводная таблица для Review Report

```markdown
## Security Checklist

| # | Проверка | Статус | Комментарий |
|---|----------|--------|-------------|
| 1 | .gitignore содержит .env | ✅/❌ | |
| 2 | .gitignore содержит *.pem, *.key | ✅/❌ | |
| 3 | Нет hardcoded паролей в коде | ✅/❌ | |
| 4 | Нет hardcoded токенов в коде | ✅/❌ | |
| 5 | .env.example без реальных секретов | ✅/❌ | |
| 6 | docker-compose без default паролей | ✅/❌ | |
| 7 | Логирование с sanitization | ✅/❌ | |
| 8 | CI/CD использует secrets | ✅/❌ | |
| 9 | Pre-commit hooks настроены | ✅/⚠️ | |
| 10 | Settings без default секретов | ✅/❌ | |
```

---

## 10. Блокирующие критерии

### BLOCKER (блокирует REVIEW_OK)

- [ ] Hardcoded пароли в коде
- [ ] Hardcoded токены в коде
- [ ] .env не в .gitignore
- [ ] Реальные секреты в .env.example

### CRITICAL (требует исправления)

- [ ] Default пароли в docker-compose
- [ ] Прямое логирование секретов
- [ ] Секреты в CI/CD без ${{ secrets }}
- [ ] *.pem, *.key не в .gitignore

### WARNING (рекомендуется исправить)

- [ ] Нет .pre-commit-config.yaml
- [ ] Нет gitleaks hook
- [ ] Нет CHANGE_ME в .env.example

---

## 11. Интеграция в качественные ворота

### REVIEW (Этап 5)

AI-ревьюер ОБЯЗАН:
1. Выполнить проверки 1-8 из этого чек-листа
2. Включить результаты в секцию "Безопасность" Review Report
3. Заблокировать REVIEW_OK при наличии BLOCKER issues

### VALIDATE (Этап 7)

AI-валидатор ОБЯЗАН:
1. Подтвердить что все BLOCKER и CRITICAL исправлены
2. Задокументировать WARNING как "известные ограничения"
3. Включить Security Summary в Validation Report

### DEPLOY (Этап 8)

AI-валидатор ОБЯЗАН:
1. Подтвердить что .env.example актуален
2. Проверить что production compose не содержит debug режимов
3. Убедиться что HTTPS настроен (для production)

---

## 12. Docker Security

> **Подробнее**: `knowledge/security/docker-security.md`

### Dockerfile проверки

```bash
# Проверить non-root user
for dockerfile in services/*/Dockerfile; do
  grep -q "USER appuser\|USER 1000" "$dockerfile" && \
    echo "OK: Non-root user в $dockerfile" || \
    echo "WARN: Нет non-root user в $dockerfile"
done

# Проверить ENTRYPOINT + CMD паттерн
for dockerfile in services/*/Dockerfile; do
  grep -q "ENTRYPOINT" "$dockerfile" && \
    echo "OK: ENTRYPOINT в $dockerfile" || \
    echo "INFO: Нет ENTRYPOINT в $dockerfile"
done
```

### Docker Compose проверки

```bash
# Проверить security_opt
grep -q "no-new-privileges" docker-compose.yml && \
  echo "OK: security_opt настроен" || echo "WARN: security_opt не настроен"

# Проверить cap_drop в prod
grep -q "cap_drop" docker-compose.prod.yml && \
  echo "OK: cap_drop настроен в prod" || echo "WARN: cap_drop не настроен в prod"

# Проверить read_only в prod
grep -q "read_only: true" docker-compose.prod.yml && \
  echo "OK: read_only в prod" || echo "INFO: read_only не настроен в prod"
```

### Критерии

| Проверка | Критичность |
|----------|-------------|
| Non-root user в Dockerfile | Warning |
| security_opt: no-new-privileges | Warning |
| cap_drop: ALL для stateless | Warning |
| read_only + tmpfs в prod | Info |
| Resource limits в prod | Warning |

---

## 13. VPS Security Mode

> **Подробнее**: `knowledge/security/vps-mode.md`

### Проверка SSH-сессии

```bash
# Определить VPS/production среду
if [ -n "$SSH_CONNECTION" ] || [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "⚠️  ОБНАРУЖЕНА SSH-СЕССИЯ"
    echo ""
    echo "Рекомендуется VPS Mode (только чтение):"
    echo "  cp .aidd/templates/project/.claude/settings.vps.json.example \\"
    echo "     .claude/settings.json"
fi
```

### Проверка VPS settings

```bash
# Проверить что Edit и Write запрещены
if [ -f ".claude/settings.json" ]; then
  grep -q '"Edit(\*\*)"' .claude/settings.json && \
    echo "VPS Mode: Edit запрещён" || echo "WARN: Edit может быть разрешён"

  grep -q '"Write(\*\*)"' .claude/settings.json && \
    echo "VPS Mode: Write запрещён" || echo "WARN: Write может быть разрешён"
fi
```

### Критерии для production

| Проверка | Критичность |
|----------|-------------|
| VPS Mode активирован на production | Рекомендуется |
| Edit/Write запрещены | Рекомендуется |
| docker exec запрещён | Рекомендуется |
| systemctl start/stop/restart запрещены | Рекомендуется |

---

## 14. Сводная таблица (расширенная)

```markdown
## Security Checklist

| # | Проверка | Статус | Комментарий |
|---|----------|--------|-------------|
| 1 | .gitignore содержит .env | ✅/❌ | |
| 2 | .gitignore содержит *.pem, *.key | ✅/❌ | |
| 3 | Нет hardcoded паролей в коде | ✅/❌ | |
| 4 | Нет hardcoded токенов в коде | ✅/❌ | |
| 5 | .env.example без реальных секретов | ✅/❌ | |
| 6 | docker-compose без default паролей | ✅/❌ | |
| 7 | Логирование с sanitization | ✅/❌ | |
| 8 | CI/CD использует secrets | ✅/❌ | |
| 9 | Pre-commit hooks настроены | ✅/⚠️ | |
| 10 | Settings без default секретов | ✅/❌ | |
| 11 | Non-root user в Dockerfile | ✅/⚠️ | |
| 12 | security_opt настроен | ✅/⚠️ | |
| 13 | cap_drop для stateless | ✅/⚠️ | |
| 14 | VPS Mode на production | ✅/ℹ️ | |
```

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| `knowledge/security/secrets-management.md` | Управление секретами |
| `knowledge/security/docker-security.md` | Docker best practices |
| `knowledge/security/vps-mode.md` | VPS режим для production |
| `templates/documents/review-report-template.md` | Шаблон ревью |
| `templates/documents/validation-report-template.md` | Шаблон валидации |
| `.claude/settings.json` | Ограничения для AI |
| `templates/project/.claude/settings.vps.json.example` | Шаблон VPS settings |

---

**Версия документа**: 1.1
**Обновлён**: 2026-01-03
