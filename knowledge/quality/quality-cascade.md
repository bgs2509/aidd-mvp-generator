# Quality Cascade v2

> **Принцип**: Ошибки качества должны выявляться на РАННЕМ этапе, а не только на Review.
> **Философия**: Каждая роль проверяет ВСЕ применимые принципы. Все проверки ОБЯЗАТЕЛЬНЫ.

---

## 1. Проблема (до Quality Cascade)

```
/idea → /research → /plan → /generate → /review
  ❌       ❌         ❌        ❌          ✅

Принципы качества проверялись ТОЛЬКО на этапе Review.
Ошибки DRY/KISS/YAGNI проходили через весь пайплайн.
```

**Пример**: На этапе `/research` предлагается структура из 5 файлов с нарушениями DRY.
Ошибка обнаруживается только на Review — после генерации кода.

---

## 2. Решение: Quality Cascade v2

```
Ошибка → [Research]  → [Architect]  → [Implement]  → [Review]
          7 проверок   16 проверок   17 проверок   17 проверок
          ОБЯЗАТЕЛЬНО  ОБЯЗАТЕЛЬНО   ОБЯЗАТЕЛЬНО   ОБЯЗАТЕЛЬНО
```

Каждая роль выполняет ВСЕ применимые проверки на своём этапе.

---

## 3. Матрица применимости принципов

| # | Принцип | Research | Architect | Implement | Review |
|---|---------|:--------:|:---------:|:---------:|:------:|
| 1 | DRY | ✓ | ✓ | ✓ | ✓ |
| 2 | KISS | ✓ | ✓ | ✓ | ✓ |
| 3 | YAGNI | ✓ | ✓ | ✓ | ✓ |
| 4 | SRP | - | ✓ | ✓ | ✓ |
| 5 | OCP | - | ✓ | ✓ | ✓ |
| 6 | LSP | - | - | ✓ | ✓ |
| 7 | ISP | - | ✓ | ✓ | ✓ |
| 8 | DIP | - | ✓ | ✓ | ✓ |
| 9 | SoC | ✓ | ✓ | ✓ | ✓ |
| 10 | SSoT | ✓ | ✓ | ✓ | ✓ |
| 11 | LoD | - | ✓ | ✓ | ✓ |
| 12 | CoC | ✓ | ✓ | ✓ | ✓ |
| 13 | Fail Fast | - | ✓ | ✓ | ✓ |
| 14 | Explicit | - | ✓ | ✓ | ✓ |
| 15 | Composition | - | ✓ | ✓ | ✓ |
| 16 | Testability | - | ✓ | ✓ | ✓ |
| 17 | Security | ✓ | ✓ | ✓ | ✓ |
| | **Итого** | **7** | **16** | **17** | **17** |

**Легенда**:
- ✓ = ОБЯЗАТЕЛЬНАЯ проверка
- `-` = Неприменимо (нет артефакта для проверки)

---

## 4. Краткое описание принципов

### Базовые (применяются везде)

| Принцип | Суть |
|---------|------|
| **DRY** | Don't Repeat Yourself — нет дублирования кода |
| **KISS** | Keep It Simple — простые решения без over-engineering |
| **YAGNI** | You Aren't Gonna Need It — только необходимое |
| **SoC** | Separation of Concerns — разделение ответственностей |
| **SSoT** | Single Source of Truth — один источник данных |
| **CoC** | Convention over Configuration — следование конвенциям |
| **Security** | Безопасность на всех уровнях |

### SOLID (с этапа Architect)

| Принцип | Суть |
|---------|------|
| **SRP** | Single Responsibility — одна ответственность |
| **OCP** | Open/Closed — открыт для расширения, закрыт для модификации |
| **LSP** | Liskov Substitution — подтипы заменяют родителей |
| **ISP** | Interface Segregation — маленькие интерфейсы |
| **DIP** | Dependency Inversion — зависимость от абстракций |

### Дополнительные

| Принцип | Суть |
|---------|------|
| **LoD** | Law of Demeter — минимальная связанность |
| **Fail Fast** | Валидация рано, падение явно |
| **Explicit > Implicit** | Явный код без магии |
| **Composition > Inheritance** | Композиция вместо наследования |
| **Testability** | Код можно тестировать |

---

## 5. Проверки по ролям

### 5.1 Researcher (7 проверок)

**Артефакт**: Research Report

| # | Принцип | Цель проверки |
|---|---------|---------------|
| 1 | DRY | Найти существующий код для переиспользования |
| 2 | KISS | Оценить сложность предложений в PRD |
| 3 | YAGNI | Отфильтровать компоненты "на будущее" |
| 4 | SoC | Проанализировать разделение ответственностей |
| 5 | SSoT | Определить источники данных |
| 6 | CoC | Выявить конвенции проекта |
| 7 | Security | Проанализировать security-практики |

**Обязательная секция в отчёте**: `Quality Cascade Checklist (7/7)`

### 5.2 Architect (16 проверок)

**Артефакт**: Architecture Plan

Все 7 проверок Researcher + 9 дополнительных:
- SRP, OCP, ISP, DIP — SOLID принципы
- LoD — связанность модулей
- Fail Fast — стратегия обработки ошибок
- Explicit — явные контракты
- Composition — паттерны переиспользования
- Testability — тестируемость архитектуры

**Обязательная секция в плане**: `Quality Cascade Checklist (16/16)`

### 5.3 Implementer (17 проверок)

**Артефакт**: Код

Все 16 проверок Architect + LSP (Liskov Substitution).

**Обязательный self-review**: `Quality Cascade Self-Check (17/17)`

### 5.4 Reviewer (17 проверок)

**Артефакт**: Review Report

Финальная верификация всех 17 принципов.

**Обязательная секция в отчёте**: `Quality Cascade Verification (17/17)`

---

## 6. Формат отчёта

```markdown
## Quality Cascade Checklist (N/N)

### QC-1: DRY ✅
- [x] Пункт проверки 1
- [x] Пункт проверки 2
→ Результат/Рекомендация

### QC-2: KISS ✅
- [x] Пункт проверки 1
...

### QC-N: Security ✅
- [x] Пункт проверки 1
...

**Итого**: N/N проверок пройдено
```

---

## 7. Интеграция в качественные ворота

| Этап | Ворота | Требование |
|------|--------|------------|
| Research | `RESEARCH_DONE` | Quality Cascade Checklist (7/7) включён |
| Architect | `PLAN_APPROVED` | Quality Cascade Checklist (16/16) включён |
| Implement | `IMPLEMENT_OK` | Quality Cascade Self-Check (17/17) выполнен |
| Review | `REVIEW_OK` | Quality Cascade Verification (17/17) выполнена |

**Если проверки не пройдены** → Ворота НЕ открываются → Переход блокирован.

---

## 8. Пример: F005-C с Quality Cascade

### Research Report (фрагмент)

```markdown
## Quality Cascade Checklist (7/7)

### DRY ✅
- [x] Найден settings.py для конфигурации
- [x] Найден convert.py для расширения
→ Рекомендация: НЕ создавать config.py

### YAGNI ✅
- [x] PRD предлагает 5 файлов
- [x] prompts.py содержит 1 константу → избыточен
→ Рекомендация: исключить prompts.py
```

### Architecture Plan (фрагмент)

```markdown
## Quality Cascade Checklist (16/16)

### KISS ✅
- [x] Минимизировано до 1 файла
→ Обоснование: llm_client.py достаточен

### SRP ✅
- [x] llm_client.py: только LLM-интеграция
- [x] convert.py: только конвертация (расширяется)
```

---

## 9. Ссылки

| Документ | Описание |
|----------|----------|
| `.claude/agents/researcher.md` | 7 проверок для Researcher |
| `.claude/agents/architect.md` | 16 проверок для Architect |
| `.claude/agents/implementer.md` | 17 проверок для Implementer |
| `.claude/agents/reviewer.md` | 17 проверок для Reviewer |
| `knowledge/quality/dry-kiss-yagni.md` | Детали DRY/KISS/YAGNI |
| `contributors/2026-01-13-aidd-enhancement-quality-cascade.md` | Исходное предложение |

---

**Версия**: 2.0
**Дата внедрения**: 2026-01-13
**Статус**: Внедрено
