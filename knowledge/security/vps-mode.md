# VPS Security Mode

> **Назначение**: Режим "только чтение" для AI агентов при работе на production VPS.

---

## Что такое VPS Mode

VPS Mode — специальный режим работы AI агента, при котором:
- **Запрещены** любые модификации файлов
- **Запрещены** опасные команды (rm, systemctl, docker exec)
- **Разрешено** только чтение и анализ

---

## Когда использовать

| Ситуация | Режим |
|----------|-------|
| Локальная разработка | Стандартный режим |
| CI/CD pipeline | Стандартный режим |
| **Production VPS** | **VPS Mode** |
| **Staging VPS** | **VPS Mode** |
| Debugging на сервере | **VPS Mode** |

---

## Автоопределение SSH

AI агент автоматически определяет SSH-сессию по переменным окружения:

```bash
# Признаки SSH-сессии (любой из):
SSH_CONNECTION    # IP клиента и сервера
SSH_CLIENT        # IP и порт клиента
SSH_TTY           # TTY сессии

# Проверка:
if [ -n "$SSH_CONNECTION" ] || [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "VPS Mode рекомендуется!"
fi
```

---

## Как активировать

### Способ 1: Использовать settings.vps.json

```bash
# Скопировать шаблон
cp .aidd/templates/project/.claude/settings.vps.json.example .claude/settings.json

# Перезапустить Claude Code
claude
```

### Способ 2: При инициализации

Команда `/aidd-init` автоматически:
1. Проверяет SSH-сессию
2. Выводит предупреждение
3. Предлагает активировать VPS Mode

---

## Разрешённые операции в VPS Mode

### Чтение

```json
{
  "allow": [
    "Read(**)",
    "Glob(**)",
    "Grep(**)"
  ]
}
```

### Git (только чтение)

```json
{
  "allow": [
    "Bash(git status)",
    "Bash(git log :*)",
    "Bash(git diff :*)",
    "Bash(git show :*)"
  ]
}
```

### Docker (только логи и статус)

```json
{
  "allow": [
    "Bash(docker logs :*)",
    "Bash(docker ps :*)",
    "Bash(docker inspect :*)"
  ]
}
```

### Системные (только чтение)

```json
{
  "allow": [
    "Bash(ls :*)",
    "Bash(tail :*)",
    "Bash(journalctl :*)",
    "Bash(systemctl status :*)"
  ]
}
```

---

## Запрещённые операции в VPS Mode

### Модификация файлов

```json
{
  "deny": [
    "Edit(**)",
    "Write(**)"
  ]
}
```

### Опасные команды

```json
{
  "deny": [
    "Bash(rm :*)",
    "Bash(rmdir :*)",
    "Bash(mv :*)",
    "Bash(cp :*)",
    "Bash(chmod :*)",
    "Bash(chown :*)"
  ]
}
```

### Git (модификация)

```json
{
  "deny": [
    "Bash(git commit :*)",
    "Bash(git push :*)",
    "Bash(git checkout :*)",
    "Bash(git reset :*)"
  ]
}
```

### Docker (модификация)

```json
{
  "deny": [
    "Bash(docker exec :*)",
    "Bash(docker run :*)",
    "Bash(docker stop :*)",
    "Bash(docker restart :*)",
    "Bash(docker rm :*)"
  ]
}
```

### Системные (модификация)

```json
{
  "deny": [
    "Bash(systemctl start :*)",
    "Bash(systemctl stop :*)",
    "Bash(systemctl restart :*)",
    "Bash(sudo :*)"
  ]
}
```

---

## Сценарии использования

### Анализ логов

```
Пользователь: Проанализируй логи за последний час

AI агент:
1. docker logs --since 1h {service}
2. Анализирует паттерны ошибок
3. Выдаёт отчёт с рекомендациями
```

### Диагностика проблем

```
Пользователь: Почему сервис не отвечает?

AI агент:
1. docker ps — проверяет статус контейнеров
2. docker logs — смотрит ошибки
3. systemctl status — проверяет системные сервисы
4. Выдаёт диагноз и план действий (для человека)
```

### Code review на сервере

```
Пользователь: Проверь конфигурацию nginx

AI агент:
1. Read nginx.conf
2. Анализирует настройки
3. Выдаёт замечания и рекомендации
```

---

## Важно

```
┌─────────────────────────────────────────────────────────────────┐
│  VPS Mode = ТОЛЬКО АНАЛИЗ                                       │
├─────────────────────────────────────────────────────────────────┤
│  • AI читает, анализирует, рекомендует                          │
│  • Человек принимает решения и выполняет действия               │
│  • Это защита от случайных модификаций production               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Ссылки

| Документ | Описание |
|----------|----------|
| `templates/project/.claude/settings.vps.json.example` | Шаблон VPS settings |
| `knowledge/security/secrets-management.md` | Управление секретами |
| `knowledge/security/security-checklist.md` | Чек-лист безопасности |
