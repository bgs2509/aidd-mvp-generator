# Шаблон комплексного аудита документации AIDD-MVP Generator

## Назначение

Этот шаблон помогает AI-агентам проводить комплексный аудит документации фреймворка AIDD-MVP Generator для выявления и исправления структурных, консистентных и контентных проблем.

> **Философия**: VERIFY BEFORE ACT — Проверяй перед действием.
>
> **Ключевой принцип**: Аудит должен быть исчерпывающим, а не выборочным.

---

## 🔴 ПРОТОКОЛ ВЫПОЛНЕНИЯ (ОБЯЗАТЕЛЬНО)

**ПРОЧИТАЙТЕ ЭТОТ РАЗДЕЛ ПЕРВЫМ ПЕРЕД НАЧАЛОМ ЛЮБОЙ РАБОТЫ ПО АУДИТУ**

### Критические правила выполнения

1. **НЕ ДЕЛЕГИРОВАТЬ** аудит Task-агенту или другим агентам
   - Вы ОБЯЗАНЫ выполнять ВСЕ команды валидации самостоятельно через Bash tool
   - Task-агенты могут интерпретировать "комплексный" как "выборочная проверка"
   - Только прямое выполнение гарантирует исчерпывающую валидацию (проверка ВСЕХ файлов, не только выборки)

2. **ПРОЧИТАТЬ ВЕСЬ ШАБЛОН** перед началом
   - Не пропускайте сразу к OBJECTIVES
   - Прочитайте разделы Smoke Tests, Validation Commands, Verification Protocol
   - Поймите полный scope: 12 smoke tests, 16 objectives

3. **ВЫПОЛНИТЬ SMOKE TESTS СНАЧАЛА** (30 секунд) перед глубоким аудитом
   - Понять scope документации
   - Выявить критические проблемы быстро
   - См. раздел "Smoke Tests" ниже

4. **ВЫПОЛНИТЬ validation commands** последовательно для каждой цели
   - Не просто ЧИТАТЬ objectives — ЗАПУСКАТЬ bash-команды
   - Каждая цель имеет раздел "КОМАНДЫ ВАЛИДАЦИИ" с точными командами
   - Записывать вывод и анализировать результаты

5. **ВЕРИФИЦИРОВАТЬ результаты аудита** spot-checks
   - Выбрать 3 случайные проблемы из находок
   - Вручную проверить каждую (не false positive)
   - Включить результаты верификации в отчёт

### ⚠️ Антипаттерны (чего ИЗБЕГАТЬ)

| ❌ НЕ ДЕЛАТЬ | ✅ ДЕЛАТЬ ВМЕСТО |
|--------------|------------------|
| Делегировать весь аудит Task-агенту | Выполнять validation commands самостоятельно через Bash |
| Проверить 10 файлов и экстраполировать | Использовать `grep -r` и `find` для ВСЕХ файлов |
| Пропустить проверку ролей/команд | Явно проверить все 7 ролей и 10 команд |
| Доверять "Stage 0 работает → всё работает" | Запустить исчерпывающую валидацию |
| Пропустить Smoke Tests | Выполнить все 12 smoke tests перед полным аудитом |
| Оценивать health score без расчёта | Показать формулу: `100 - (CRITICAL×4) - (HIGH×2) - (MEDIUM×0.5)` |
| Говорить "несколько файлов имеют проблемы" | Указать точные `file:line` для КАЖДОЙ проблемы |
| Проверять только docs/ | Проверять и корневые файлы (CLAUDE.md, workflow.md, conventions.md) |
| Доверять что "шаблон существует = работает" | Проверять README, именование, соответствие документации |

---

## 🧪 Smoke Tests (Выполнить первыми — 60 секунд)

**Цель**: Быстрая оценка здоровья документации для выявления критических проблем перед полным аудитом.

### Smoke Test 1: Подсчёт markdown файлов

```bash
echo "=== SMOKE TEST 1: Всего Markdown файлов ==="
find . -name "*.md" -not -path "./.git/*" 2>/dev/null | wc -l
# Ожидание: ~300-400 файлов
# Если < 100 или > 600 → исследовать scope
```

### Smoke Test 2: Подсчёт ссылок

```bash
echo "=== SMOKE TEST 2: Всего Markdown ссылок ==="
grep -rho '\[.*\](.*\.md' . --include="*.md" 2>/dev/null | wc -l
# Ожидание: ~1000-2000 ссылок
# Это даёт scope задачи валидации ссылок
```

### Smoke Test 3: 🚨 CRITICAL — Legacy/Deprecated ссылки

```bash
echo "=== SMOKE TEST 3: Legacy/Deprecated ссылки (ДОЛЖНО БЫТЬ 0) ==="
grep -rn "legacy\|deprecated\|old-docs\|DEPRECATED" . --include="*.md" 2>/dev/null | wc -l
# Ожидание: 0
# Если > 0 → КРИТИЧЕСКАЯ ПРОБЛЕМА (блокирует пользователей/AI-агентов)
```

### Smoke Test 4: Выборочная проверка битых ссылок

```bash
echo "=== SMOKE TEST 4: Битые ссылки (первые 10 файлов) ==="
find . -name "*.md" -not -path "./.git/*" | head -10 | while read f; do
  grep -oP '\[.*?\]\(\K[^)]+\.md' "$f" 2>/dev/null | while read link; do
    # Убираем якоря
    target="${link%%#*}"
    dir=$(dirname "$f")
    # Проверяем относительный путь
    if [ ! -f "$dir/$target" ] && [ ! -f "$target" ]; then
      echo "BROKEN: $f → $target"
    fi
  done
done | head -5
# Ожидание: 0 битых ссылок
# Если > 0 → указывает на системные проблемы с ссылками
```

### Smoke Test 5: 🚨 CRITICAL — Stage 0 файлы

```bash
echo "=== SMOKE TEST 5: Stage 0 документы (Критические для AI) ==="
for doc in CLAUDE.md workflow.md conventions.md; do
  if [ -f "$doc" ]; then
    echo "✅ $doc ($(wc -l < "$doc") строк)"
  else
    echo "🚨 CRITICAL MISSING: $doc"
  fi
done
# Ожидание: Все 3 файла существуют
# Если любой отсутствует → КРИТИЧЕСКАЯ ПРОБЛЕМА (AI не может работать)
```

### Smoke Test 6: 🚨 CRITICAL — 7 ролей AI-агентов

```bash
echo "=== SMOKE TEST 6: 7 ролей AI-агентов ==="
ROLES=(analyst researcher architect implementer reviewer qa validator)
missing=0
for role in "${ROLES[@]}"; do
  if [ -f ".claude/agents/$role.md" ]; then
    echo "✅ $role.md"
  else
    echo "🚨 MISSING: $role.md"
    missing=$((missing + 1))
  fi
done
echo "Итого: $((7 - missing))/7 ролей"
# Ожидание: 7/7
# Если < 7 → КРИТИЧЕСКАЯ ПРОБЛЕМА (пайплайн неполный)
```

### Smoke Test 7: 🚨 CRITICAL — 10 slash-команд

```bash
echo "=== SMOKE TEST 7: 10 Slash-команд ==="
COMMANDS=(init idea research plan feature-plan generate review test validate deploy)
missing=0
for cmd in "${COMMANDS[@]}"; do
  if [ -f ".claude/commands/$cmd.md" ]; then
    echo "✅ /$cmd"
  else
    echo "🚨 MISSING: /$cmd"
    missing=$((missing + 1))
  fi
done
echo "Итого: $((10 - missing))/10 команд"
# Ожидание: 10/10
# Если < 10 → КРИТИЧЕСКАЯ ПРОБЛЕМА (пайплайн неполный)
```

### Smoke Test 8: 🚨 CRITICAL — 5 шаблонов сервисов

```bash
echo "=== SMOKE TEST 8: 5 шаблонов сервисов ==="
SERVICES=(fastapi_business_api postgres_data_api mongo_data_api aiogram_bot asyncio_worker)
missing=0
for svc in "${SERVICES[@]}"; do
  if [ -d "templates/services/$svc" ]; then
    readme_status="(без README)"
    [ -f "templates/services/$svc/README.md" ] && readme_status="(README ✓)"
    echo "✅ $svc $readme_status"
  else
    echo "🚨 MISSING: $svc"
    missing=$((missing + 1))
  fi
done
echo "Итого: $((5 - missing))/5 шаблонов"
# Ожидание: 5/5 с README
```

### Smoke Test 9: Шаблоны документов

```bash
echo "=== SMOKE TEST 9: Шаблоны документов ==="
TEMPLATES=(prd-template.md architecture-template.md feature-plan-template.md \
           implementation-plan-template.md review-report-template.md \
           qa-report-template.md validation-report-template.md rtm-template.md)
count=0
for tpl in "${TEMPLATES[@]}"; do
  if [ -f "templates/documents/$tpl" ]; then
    echo "✅ $tpl"
    count=$((count + 1))
  else
    echo "❌ MISSING: $tpl"
  fi
done
echo "Итого: $count/${#TEMPLATES[@]} шаблонов"
# Ожидание: 8/8 (минимум)
```

### Smoke Test 10: 🚨 CRITICAL — Консистентность ворот (Gates)

```bash
echo "=== SMOKE TEST 10: Консистентность ворот ==="
echo "Ворота в CLAUDE.md:"
grep -o "[A-Z_]*_READY\|[A-Z_]*_DONE\|[A-Z_]*_APPROVED\|[A-Z_]*_OK\|[A-Z_]*_PASSED\|DEPLOYED" CLAUDE.md 2>/dev/null | sort -u

echo ""
echo "Ворота в workflow.md:"
grep -o "[A-Z_]*_READY\|[A-Z_]*_DONE\|[A-Z_]*_APPROVED\|[A-Z_]*_OK\|[A-Z_]*_PASSED\|DEPLOYED" workflow.md 2>/dev/null | sort -u

echo ""
echo "Ворота в docs/NAVIGATION.md:"
grep -o "[A-Z_]*_READY\|[A-Z_]*_DONE\|[A-Z_]*_APPROVED\|[A-Z_]*_OK\|[A-Z_]*_PASSED\|DEPLOYED" docs/NAVIGATION.md 2>/dev/null | sort -u
# Ожидание: Все 9 ворот совпадают во всех файлах
# BOOTSTRAP_READY, PRD_READY, RESEARCH_DONE, PLAN_APPROVED,
# IMPLEMENT_OK, REVIEW_OK, QA_PASSED, ALL_GATES_PASSED, DEPLOYED
```

### Smoke Test 11: Режимы CREATE/FEATURE

```bash
echo "=== SMOKE TEST 11: Режимы CREATE/FEATURE ==="
echo "CREATE упоминания:"
grep -c "CREATE" CLAUDE.md workflow.md docs/NAVIGATION.md 2>/dev/null | paste -sd+ | bc

echo "FEATURE упоминания:"
grep -c "FEATURE" CLAUDE.md workflow.md docs/NAVIGATION.md 2>/dev/null | paste -sd+ | bc

# Проверка /aidd-plan vs /feature-plan
[ -f ".claude/commands/plan.md" ] && echo "✅ /aidd-plan (CREATE mode)" || echo "❌ /plan"
[ -f ".claude/commands/feature-plan.md" ] && echo "✅ /aidd-feature-plan (FEATURE mode)" || echo "❌ /feature-plan"
# Ожидание: Оба режима описаны, обе команды существуют
```

### Smoke Test 12: База знаний (knowledge/)

```bash
echo "=== SMOKE TEST 12: База знаний ==="
find knowledge/ -name "*.md" 2>/dev/null | wc -l
# Ожидание: 40+ файлов

echo ""
echo "Категории:"
ls -d knowledge/*/ 2>/dev/null | xargs -I{} basename {}
# Ожидание: architecture, services, quality, infrastructure, integrations
```

### Таблица решений на основе Smoke Tests

| Smoke Test | Результат | Действие |
|------------|-----------|----------|
| Test 3 (Legacy) | > 0 | **СТОП. КРИТИЧЕСКАЯ ПРОБЛЕМА.** Сообщить немедленно. |
| Test 4 (Битые ссылки) | > 0 | **HIGH PRIORITY.** Отметить, продолжить с полной валидацией. |
| Test 5 (Stage 0) | Любой missing | **CRITICAL.** AI-агенты не могут работать. |
| Test 6 (Роли) | < 7 | **CRITICAL.** Пайплайн неполный. |
| Test 7 (Команды) | < 10 | **CRITICAL.** Пайплайн неполный. |
| Test 8 (Сервисы) | < 5 | **CRITICAL.** Шаблоны неполные. |
| Test 10 (Ворота) | Несовпадение | **CRITICAL.** Консистентность нарушена. |
| Все тесты | ✅ | Продолжить с полным 16-objective аудитом. |

---

## OBJECTIVES (16 целей аудита)

### Категория A: Структура (Objectives 1-5)

---

### Objective 1: Понимание назначения проекта

**Цель**: Понять основное назначение фреймворка и его целевую аудиторию.

**Действия**:
- Прочитать CLAUDE.md, README.md
- Идентифицировать главные цели проекта
- Понять архитектуру и технологический стек

**Ключевые характеристики AIDD-MVP Generator**:

| Параметр | Значение |
|----------|----------|
| Уровень зрелости | Level 2 (MVP) — всегда |
| Покрытие тестами | ≥75% |
| Архитектура | DDD/Hexagonal, HTTP-only доступ к данным |
| Пайплайн | 9 этапов (0-8), 9 ворот |
| Типы сервисов | Business API, Data API, Bot, Worker |

---

### Objective 2: Валидация ссылок ⚡ ОБЯЗАТЕЛЬНЫЕ КОМАНДЫ

**Цель**: Найти ВСЕ битые markdown ссылки, включая legacy/deprecated ссылки.

**КОМАНДЫ ВАЛИДАЦИИ** (выполнять по порядку):

```bash
# ========================================
# ШАГ 1: Проверка legacy/deprecated (CRITICAL)
# ========================================
echo "Шаг 1: Поиск legacy/deprecated ссылок..."
grep -rn "legacy\|deprecated\|old-\|DEPRECATED" . --include="*.md" 2>/dev/null > /tmp/legacy_refs.txt

LEGACY_COUNT=$(wc -l < /tmp/legacy_refs.txt)
echo "Найдено $LEGACY_COUNT legacy ссылок"

if [ "$LEGACY_COUNT" -gt 0 ]; then
  echo "🚨 CRITICAL: Найдены legacy ссылки!"
  head -20 /tmp/legacy_refs.txt
fi

# ========================================
# ШАГ 2: Извлечение ВСЕХ markdown ссылок
# ========================================
echo "Шаг 2: Извлечение всех markdown ссылок..."
grep -rno '\[.*\](.*\.md' . --include="*.md" 2>/dev/null > /tmp/all_links.txt

TOTAL_LINKS=$(wc -l < /tmp/all_links.txt)
echo "Найдено $TOTAL_LINKS markdown ссылок"

# ========================================
# ШАГ 3: Проверка каждой ссылки
# ========================================
echo "Шаг 3: Валидация целей ссылок..."
> /tmp/broken_links.txt  # Очистка файла

# Извлекаем уникальные пути ссылок
grep -rho '\[.*\](.*\.md' . --include="*.md" 2>/dev/null | \
  sed 's/.*(\([^)]*\.md\).*/\1/' | sort -u > /tmp/unique_refs.txt

UNIQUE_REFS=$(wc -l < /tmp/unique_refs.txt)
echo "Уникальных ссылок: $UNIQUE_REFS"

# Проверяем каждую уникальную ссылку
while read -r ref; do
  # Пробуем разные варианты путей
  if [ ! -f "$ref" ] && [ ! -f "docs/$ref" ] && [ ! -f "./$ref" ]; then
    # Находим файлы, ссылающиеся на эту битую ссылку
    grep -l "$ref" . -r --include="*.md" 2>/dev/null | head -3 | while read -r file; do
      line=$(grep -n "$ref" "$file" | head -1 | cut -d: -f1)
      echo "BROKEN: $file:$line → $ref" >> /tmp/broken_links.txt
    done
  fi
done < /tmp/unique_refs.txt

BROKEN_COUNT=$(wc -l < /tmp/broken_links.txt)
echo "Найдено $BROKEN_COUNT битых ссылок"

if [ "$BROKEN_COUNT" -gt 0 ]; then
  echo "⚠️ HIGH PRIORITY: Битые ссылки!"
  head -30 /tmp/broken_links.txt
fi

# ========================================
# ИТОГ
# ========================================
echo ""
echo "=== ИТОГ ВАЛИДАЦИИ ССЫЛОК ==="
echo "Всего ссылок: $TOTAL_LINKS"
echo "Legacy ссылок: $LEGACY_COUNT (ДОЛЖНО БЫТЬ 0)"
echo "Битых ссылок: $BROKEN_COUNT (ДОЛЖНО БЫТЬ 0)"
```

**Ожидаемые результаты**:
- Legacy ссылки: **0** (если >0 → CRITICAL)
- Битые ссылки: **0** (если >0 → HIGH)

**Приоритизация**:
- Legacy ссылки: **CRITICAL** (блокирует AI-агентов, путает пользователей)
- Битые ссылки: **HIGH** (404 ошибки, навигация ломается)
- Битые якоря: **MEDIUM** (UX деградация)

---

### Objective 3: Полнота файлов

**Цель**: Убедиться, что все ссылающиеся файлы существуют.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка Stage 0 документов
# ========================================
echo "=== Проверка Stage 0 документов ==="
STAGE0_DOCS=(
  "CLAUDE.md"
  "workflow.md"
  "conventions.md"
  "docs/INDEX.md"
  "docs/NAVIGATION.md"
  "docs/initialization.md"
)

for doc in "${STAGE0_DOCS[@]}"; do
  if [ -f "$doc" ]; then
    lines=$(wc -l < "$doc")
    echo "✅ $doc ($lines строк)"
  else
    echo "❌ CRITICAL MISSING: $doc"
  fi
done

# ========================================
# Проверка всех документов из INDEX.md
# ========================================
echo ""
echo "=== Проверка документов из INDEX.md ==="
grep -oP '\[.*?\]\(\K[^)]+\.md' docs/INDEX.md 2>/dev/null | while read -r ref; do
  if [ -f "$ref" ] || [ -f "docs/$ref" ]; then
    echo "✅ $ref"
  else
    echo "❌ BROKEN: $ref (referenced in INDEX.md)"
  fi
done | grep "❌" | head -20

# ========================================
# Проверка документов из NAVIGATION.md
# ========================================
echo ""
echo "=== Проверка документов из NAVIGATION.md ==="
grep -oP '\[.*?\]\(\K[^)]+\.md' docs/NAVIGATION.md 2>/dev/null | while read -r ref; do
  if [ -f "$ref" ] || [ -f "docs/$ref" ]; then
    echo "✅ $ref"
  else
    echo "❌ BROKEN: $ref (referenced in NAVIGATION.md)"
  fi
done | grep "❌" | head -20
```

---

### Objective 4: Структурная консистентность

**Цель**: Убедиться, что структура директорий соответствует документации.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка структуры .claude/
# ========================================
echo "=== Структура .claude/ ==="
echo "agents/:"
ls -1 .claude/agents/*.md 2>/dev/null | wc -l
echo "commands/:"
ls -1 .claude/commands/*.md 2>/dev/null | wc -l

# ========================================
# Проверка структуры templates/
# ========================================
echo ""
echo "=== Структура templates/ ==="
echo "services/:"
ls -d templates/services/*/ 2>/dev/null | xargs -I{} basename {}
echo ""
echo "documents/:"
ls templates/documents/*.md 2>/dev/null | wc -l

# ========================================
# Проверка структуры knowledge/
# ========================================
echo ""
echo "=== Структура knowledge/ ==="
for dir in architecture services quality infrastructure integrations; do
  if [ -d "knowledge/$dir" ]; then
    count=$(find "knowledge/$dir" -name "*.md" | wc -l)
    echo "✅ $dir/ ($count файлов)"
  else
    echo "❌ MISSING: knowledge/$dir/"
  fi
done

# ========================================
# Проверка структуры roles/
# ========================================
echo ""
echo "=== Структура roles/ ==="
for role in analyst researcher architect implementer reviewer qa validator; do
  if [ -d "roles/$role" ]; then
    count=$(find "roles/$role" -name "*.md" | wc -l)
    echo "✅ $role/ ($count файлов)"
  else
    echo "⚠️ MISSING: roles/$role/"
  fi
done
```

---

### Objective 5: Качество контента

**Цель**: Проверить качество контента: TODO, примеры кода, язык.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Поиск TODO/FIXME/WIP маркеров
# ========================================
echo "=== TODO/FIXME/WIP маркеры ==="
grep -rn "TODO\|FIXME\|XXX\|HACK\|WIP" . --include="*.md" 2>/dev/null > /tmp/todos.txt
TODO_COUNT=$(wc -l < /tmp/todos.txt)
echo "Найдено TODO маркеров: $TODO_COUNT"
if [ "$TODO_COUNT" -gt 0 ]; then
  echo "⚠️ Незавершённая документация:"
  head -10 /tmp/todos.txt
fi

# ========================================
# Проверка Python code blocks
# ========================================
echo ""
echo "=== Валидация Python блоков ==="
grep -l '```python' . -r --include="*.md" 2>/dev/null | head -5 | while read -r file; do
  echo "Проверка: $file"
done

# ========================================
# Проверка на нерусский контент (английский OK)
# ========================================
echo ""
echo "=== Проверка языка (русский/английский) ==="
# Документация должна быть на русском или английском
# Предупреждение только для других языков
```

---

### Категория B: Пайплайн (Objectives 6-10)

---

### Objective 6: Консистентность 9 этапов (0-8) ⚡ ОБЯЗАТЕЛЬНЫЕ КОМАНДЫ

**Цель**: Убедиться, что все 9 этапов пайплайна описаны консистентно.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка описания этапов в CLAUDE.md
# ========================================
echo "=== Этапы в CLAUDE.md ==="
for stage in 0 1 2 3 4 5 6 7 8; do
  if grep -q "Этап $stage\|Stage $stage\|этап $stage" CLAUDE.md 2>/dev/null; then
    echo "✅ Этап $stage"
  else
    echo "❌ Этап $stage не найден"
  fi
done

# ========================================
# Проверка описания этапов в workflow.md
# ========================================
echo ""
echo "=== Этапы в workflow.md ==="
for stage in 0 1 2 3 4 5 6 7 8; do
  if grep -q "Этап $stage\|Stage $stage\|этап $stage" workflow.md 2>/dev/null; then
    echo "✅ Этап $stage"
  else
    echo "❌ Этап $stage не найден"
  fi
done

# ========================================
# Проверка описания этапов в NAVIGATION.md
# ========================================
echo ""
echo "=== Этапы в NAVIGATION.md ==="
for stage in 0 1 2 3 4 5 6 7 8; do
  if grep -q "Этап $stage\|Stage $stage\|этап $stage" docs/NAVIGATION.md 2>/dev/null; then
    echo "✅ Этап $stage"
  else
    echo "❌ Этап $stage не найден"
  fi
done
```

**Ожидаемые результаты**:
- Все 9 этапов (0-8) описаны во всех трёх файлах
- Номера этапов совпадают с командами

| Этап | Команда | Агент | Ворота |
|------|---------|-------|--------|
| 0 | /aidd-init | — | BOOTSTRAP_READY |
| 1 | /aidd-idea | analyst | PRD_READY |
| 2 | /aidd-research | researcher | RESEARCH_DONE |
| 3 | /aidd-plan или /aidd-feature-plan | architect | PLAN_APPROVED |
| 4 | /aidd-generate | implementer | IMPLEMENT_OK |
| 5 | /aidd-review | reviewer | REVIEW_OK |
| 6 | /aidd-test | qa | QA_PASSED |
| 7 | /aidd-validate | validator | ALL_GATES_PASSED |
| 8 | /aidd-deploy | validator | DEPLOYED |

---

### Objective 7: Консистентность 7 ролей и 10 команд ⚡ ОБЯЗАТЕЛЬНЫЕ КОМАНДЫ

**Цель**: Убедиться, что все роли и команды согласованы.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка соответствия ролей и этапов
# ========================================
echo "=== Соответствие ролей этапам ==="

declare -A ROLE_STAGES=(
  ["analyst"]="1"
  ["researcher"]="2"
  ["architect"]="3"
  ["implementer"]="4"
  ["reviewer"]="5"
  ["qa"]="6"
  ["validator"]="7,8"
)

for role in "${!ROLE_STAGES[@]}"; do
  stages="${ROLE_STAGES[$role]}"
  if [ -f ".claude/agents/$role.md" ]; then
    echo "✅ $role → Этап(ы) $stages"
    # Проверяем, упоминается ли этап в файле роли
    for stage in $(echo "$stages" | tr ',' ' '); do
      if grep -qi "этап $stage\|stage $stage" ".claude/agents/$role.md" 2>/dev/null; then
        echo "   ✅ Упоминает Этап $stage"
      else
        echo "   ⚠️ Не упоминает Этап $stage"
      fi
    done
  else
    echo "❌ $role.md не найден"
  fi
done

# ========================================
# Проверка соответствия команд и этапов
# ========================================
echo ""
echo "=== Соответствие команд этапам ==="

declare -A CMD_STAGES=(
  ["init"]="0"
  ["idea"]="1"
  ["research"]="2"
  ["plan"]="3"
  ["feature-plan"]="3"
  ["generate"]="4"
  ["review"]="5"
  ["test"]="6"
  ["validate"]="7"
  ["deploy"]="8"
)

for cmd in "${!CMD_STAGES[@]}"; do
  stage="${CMD_STAGES[$cmd]}"
  if [ -f ".claude/commands/$cmd.md" ]; then
    echo "✅ /$cmd → Этап $stage"
  else
    echo "❌ /$cmd не найден"
  fi
done

# ========================================
# Перекрёстная проверка: команда ссылается на роль
# ========================================
echo ""
echo "=== Перекрёстные ссылки команда→роль ==="
for cmd in idea research plan feature-plan generate review test validate deploy; do
  if [ -f ".claude/commands/$cmd.md" ]; then
    if grep -q "agents/" ".claude/commands/$cmd.md" 2>/dev/null; then
      echo "✅ /$cmd ссылается на роль"
    else
      echo "⚠️ /$cmd не ссылается на роль"
    fi
  fi
done
```

---

### Objective 8: Консистентность 9 ворот (Gates) ⚡ ОБЯЗАТЕЛЬНЫЕ КОМАНДЫ

**Цель**: Убедиться, что все 9 ворот описаны консистентно во всех файлах.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Определение ожидаемых ворот
# ========================================
EXPECTED_GATES=(
  "BOOTSTRAP_READY"
  "PRD_READY"
  "RESEARCH_DONE"
  "PLAN_APPROVED"
  "IMPLEMENT_OK"
  "REVIEW_OK"
  "QA_PASSED"
  "ALL_GATES_PASSED"
  "DEPLOYED"
)

echo "=== Проверка 9 ворот ==="
echo ""

# ========================================
# Проверка каждых ворот в ключевых файлах
# ========================================
for gate in "${EXPECTED_GATES[@]}"; do
  echo "--- $gate ---"

  # CLAUDE.md
  if grep -q "$gate" CLAUDE.md 2>/dev/null; then
    echo "  ✅ CLAUDE.md"
  else
    echo "  ❌ CLAUDE.md"
  fi

  # workflow.md
  if grep -q "$gate" workflow.md 2>/dev/null; then
    echo "  ✅ workflow.md"
  else
    echo "  ❌ workflow.md"
  fi

  # NAVIGATION.md
  if grep -q "$gate" docs/NAVIGATION.md 2>/dev/null; then
    echo "  ✅ NAVIGATION.md"
  else
    echo "  ❌ NAVIGATION.md"
  fi
done

# ========================================
# Сводка
# ========================================
echo ""
echo "=== СВОДКА ВОРОТ ==="
for file in CLAUDE.md workflow.md docs/NAVIGATION.md; do
  count=$(grep -o "BOOTSTRAP_READY\|PRD_READY\|RESEARCH_DONE\|PLAN_APPROVED\|IMPLEMENT_OK\|REVIEW_OK\|QA_PASSED\|ALL_GATES_PASSED\|DEPLOYED" "$file" 2>/dev/null | sort -u | wc -l)
  echo "$file: $count/9 ворот"
done
```

---

### Objective 9: Консистентность режимов CREATE/FEATURE

**Цель**: Убедиться, что оба режима работы описаны полностью.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка описания режимов
# ========================================
echo "=== Режим CREATE ==="
echo "Упоминания в CLAUDE.md: $(grep -c "CREATE" CLAUDE.md 2>/dev/null)"
echo "Упоминания в workflow.md: $(grep -c "CREATE" workflow.md 2>/dev/null)"

echo ""
echo "=== Режим FEATURE ==="
echo "Упоминания в CLAUDE.md: $(grep -c "FEATURE" CLAUDE.md 2>/dev/null)"
echo "Упоминания в workflow.md: $(grep -c "FEATURE" workflow.md 2>/dev/null)"

# ========================================
# Проверка отличий команд для режимов
# ========================================
echo ""
echo "=== Команды для режимов ==="
if [ -f ".claude/commands/plan.md" ]; then
  echo "✅ /aidd-plan (CREATE mode)"
  if grep -qi "CREATE\|полный\|новый проект" ".claude/commands/plan.md" 2>/dev/null; then
    echo "   ✅ Описывает CREATE mode"
  else
    echo "   ⚠️ Не описывает CREATE mode явно"
  fi
fi

if [ -f ".claude/commands/feature-plan.md" ]; then
  echo "✅ /aidd-feature-plan (FEATURE mode)"
  if grep -qi "FEATURE\|добавление\|существующий" ".claude/commands/feature-plan.md" 2>/dev/null; then
    echo "   ✅ Описывает FEATURE mode"
  else
    echo "   ⚠️ Не описывает FEATURE mode явно"
  fi
fi

# ========================================
# Проверка алгоритма detect_mode
# ========================================
echo ""
echo "=== Алгоритм detect_mode ==="
if grep -q "detect_mode\|определение режима" workflow.md 2>/dev/null; then
  echo "✅ Алгоритм detect_mode описан в workflow.md"
else
  echo "⚠️ Алгоритм detect_mode не найден"
fi
```

---

### Objective 10: Валидация алгоритмов

**Цель**: Убедиться, что ключевые алгоритмы описаны и корректны.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка наличия алгоритмов в workflow.md
# ========================================
echo "=== Алгоритмы в workflow.md ==="

ALGORITHMS=(
  "detect_mode"
  "check_preconditions\|check_gate"
  "handle_gate_failure\|gate.*failure"
  "version_artifact\|версионирование"
  "find_artifact\|поиск.*артефакт"
)

for algo in "${ALGORITHMS[@]}"; do
  if grep -Eqi "$algo" workflow.md 2>/dev/null; then
    echo "✅ $algo найден"
  else
    echo "❌ $algo не найден"
  fi
done

# ========================================
# Проверка паттернов glob для артефактов
# ========================================
echo ""
echo "=== Паттерны поиска артефактов ==="
grep -o "\*\*\/\*.*\|glob.*pattern\|ai-docs" workflow.md 2>/dev/null | head -10
```

---

### Категория C: Шаблоны и знания (Objectives 11-14)

---

### Objective 11: Целостность шаблонов сервисов ⚡ ОБЯЗАТЕЛЬНЫЕ КОМАНДЫ

**Цель**: Убедиться, что все 5 шаблонов сервисов полные и документированы.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка каждого шаблона сервиса
# ========================================
echo "=== Проверка шаблонов сервисов ==="

SERVICES=(
  "fastapi_business_api:Business API:8000-8099"
  "postgres_data_api:Data API PostgreSQL:8001"
  "mongo_data_api:Data API MongoDB:8002"
  "aiogram_bot:Telegram Bot:—"
  "asyncio_worker:Background Worker:—"
)

for svc_spec in "${SERVICES[@]}"; do
  IFS=':' read -r svc_name svc_type svc_port <<< "$svc_spec"
  svc_dir="templates/services/$svc_name"

  echo ""
  echo "=== $svc_name ($svc_type) ==="

  if [ ! -d "$svc_dir" ]; then
    echo "❌ CRITICAL: Директория не существует"
    continue
  fi

  echo "✅ Директория существует"

  # README
  if [ -f "$svc_dir/README.md" ]; then
    lines=$(wc -l < "$svc_dir/README.md")
    echo "✅ README.md ($lines строк)"
  else
    echo "❌ README.md отсутствует"
  fi

  # Структура src/ или аналог
  if [ -d "$svc_dir/src" ]; then
    echo "✅ src/ директория"
  elif [ -d "$svc_dir/app" ]; then
    echo "✅ app/ директория"
  else
    echo "⚠️ Нет src/ или app/"
  fi

  # tests/
  if [ -d "$svc_dir/tests" ]; then
    echo "✅ tests/ директория"
  else
    echo "⚠️ tests/ отсутствует"
  fi

  # Dockerfile
  if [ -f "$svc_dir/Dockerfile" ]; then
    echo "✅ Dockerfile"
  else
    echo "⚠️ Dockerfile отсутствует"
  fi

  # pyproject.toml или requirements.txt
  if [ -f "$svc_dir/pyproject.toml" ]; then
    echo "✅ pyproject.toml"
  elif [ -f "$svc_dir/requirements.txt" ]; then
    echo "✅ requirements.txt"
  else
    echo "⚠️ Нет pyproject.toml или requirements.txt"
  fi
done
```

---

### Objective 12: Целостность шаблонов документов

**Цель**: Убедиться, что все шаблоны документов существуют и полные.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка шаблонов документов
# ========================================
echo "=== Шаблоны документов ==="

TEMPLATES=(
  "prd-template.md:PRD:Этап 1"
  "architecture-template.md:Архитектура:Этап 3"
  "feature-plan-template.md:План фичи:Этап 3 FEATURE"
  "implementation-plan-template.md:План реализации:Этап 3"
  "review-report-template.md:Отчёт ревью:Этап 5"
  "qa-report-template.md:Отчёт QA:Этап 6"
  "validation-report-template.md:Отчёт валидации:Этап 7"
  "rtm-template.md:RTM:Все этапы"
  "tasklist-template.md:Список задач:Опционально"
  "pipeline-state-template.json:Состояние пайплайна:Этап 0"
)

for tpl_spec in "${TEMPLATES[@]}"; do
  IFS=':' read -r tpl_file tpl_name tpl_stage <<< "$tpl_spec"
  tpl_path="templates/documents/$tpl_file"

  if [ -f "$tpl_path" ]; then
    lines=$(wc -l < "$tpl_path" 2>/dev/null || echo "0")
    echo "✅ $tpl_file ($tpl_name, $tpl_stage) — $lines строк"
  else
    echo "❌ MISSING: $tpl_file ($tpl_name, $tpl_stage)"
  fi
done

# ========================================
# Проверка README и template-map
# ========================================
echo ""
echo "=== Метаинформация ==="
[ -f "templates/documents/README.md" ] && echo "✅ README.md" || echo "❌ README.md"
[ -f "templates/documents/template-map.md" ] && echo "✅ template-map.md" || echo "❌ template-map.md"
```

---

### Objective 13: Целостность базы знаний (knowledge/)

**Цель**: Убедиться, что база знаний полная и хорошо структурирована.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка категорий knowledge/
# ========================================
echo "=== Категории базы знаний ==="

CATEGORIES=(
  "architecture:Архитектура и паттерны"
  "services:Шаблоны сервисов (FastAPI, Aiogram, etc.)"
  "quality:Тестирование и качество"
  "infrastructure:Docker, CI/CD, Nginx"
  "integrations:HTTP, Redis, etc."
)

total_files=0
for cat_spec in "${CATEGORIES[@]}"; do
  IFS=':' read -r cat_name cat_desc <<< "$cat_spec"
  cat_dir="knowledge/$cat_name"

  if [ -d "$cat_dir" ]; then
    count=$(find "$cat_dir" -name "*.md" 2>/dev/null | wc -l)
    total_files=$((total_files + count))
    echo "✅ $cat_name/ — $count файлов ($cat_desc)"
  else
    echo "❌ MISSING: $cat_name/"
  fi
done

echo ""
echo "Всего файлов в knowledge/: $total_files"
# Ожидание: 40+ файлов

# ========================================
# Проверка README
# ========================================
echo ""
if [ -f "knowledge/README.md" ]; then
  echo "✅ knowledge/README.md (индекс базы знаний)"
else
  echo "❌ knowledge/README.md отсутствует"
fi
```

---

### Objective 14: HTTP-only архитектура

**Цель**: Убедиться, что HTTP-only принцип описан чётко.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка упоминания HTTP-only
# ========================================
echo "=== HTTP-only архитектура ==="

FILES=(CLAUDE.md workflow.md conventions.md)
for file in "${FILES[@]}"; do
  if grep -qi "HTTP-only\|http only\|через HTTP\|via HTTP" "$file" 2>/dev/null; then
    echo "✅ $file упоминает HTTP-only"
  else
    echo "⚠️ $file не упоминает HTTP-only явно"
  fi
done

# ========================================
# Проверка в базе знаний
# ========================================
echo ""
echo "=== HTTP-only в knowledge/ ==="
grep -rl "HTTP-only\|http only\|через HTTP" knowledge/ 2>/dev/null | head -5

# ========================================
# Проверка что бизнес не обращается к БД напрямую
# ========================================
echo ""
echo "=== Разделение Business/Data ==="
if grep -qi "бизнес.*не.*БД\|business.*database.*never\|Data API" knowledge/ -r 2>/dev/null; then
  echo "✅ Принцип разделения описан"
else
  echo "⚠️ Принцип разделения не найден явно"
fi
```

---

### Категория D: Качество (Objectives 15-16)

---

### Objective 15: DDD/Hexagonal структура

**Цель**: Убедиться, что DDD/Hexagonal архитектура описана.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Проверка упоминания DDD/Hexagonal
# ========================================
echo "=== DDD/Hexagonal архитектура ==="

# В conventions.md
if grep -qi "DDD\|Hexagonal\|Clean Architecture\|domain" conventions.md 2>/dev/null; then
  echo "✅ conventions.md описывает DDD/Hexagonal"
else
  echo "⚠️ conventions.md не описывает DDD/Hexagonal"
fi

# В knowledge/
echo ""
echo "Файлы о DDD/Hexagonal в knowledge/:"
find knowledge/ -name "*.md" -exec grep -l "DDD\|Hexagonal\|domain\|infrastructure" {} \; 2>/dev/null | head -5

# ========================================
# Проверка 6 слоёв в conventions.md
# ========================================
echo ""
echo "=== 6 слоёв DDD ==="
LAYERS=(api application domain infrastructure schemas core)
for layer in "${LAYERS[@]}"; do
  if grep -qi "$layer" conventions.md 2>/dev/null; then
    echo "✅ $layer/"
  else
    echo "⚠️ $layer/ не описан"
  fi
done
```

---

### Objective 16: Устаревшие файлы и очистка

**Цель**: Найти файлы, которые следует удалить или архивировать.

**КОМАНДЫ ВАЛИДАЦИИ**:

```bash
# ========================================
# Поиск backup файлов
# ========================================
echo "=== Backup файлы ==="
find . -name "*.bak" -o -name "*.backup" -o -name "*_backup.*" 2>/dev/null | head -10

# ========================================
# Поиск old версий
# ========================================
echo ""
echo "=== Old версии ==="
find . -name "*.old" -o -name "*_old.*" -o -name "*_v1.*" 2>/dev/null | head -10

# ========================================
# Поиск временных файлов
# ========================================
echo ""
echo "=== Временные файлы ==="
find . -name "*.tmp" -o -name "*~" -o -name "*.swp" -o -name ".DS_Store" 2>/dev/null | head -10

# ========================================
# Поиск пустых директорий
# ========================================
echo ""
echo "=== Пустые директории ==="
find . -type d -empty 2>/dev/null | head -10

# ========================================
# Проверка .gitignore
# ========================================
echo ""
echo "=== .gitignore ==="
if [ -f ".gitignore" ]; then
  echo "✅ .gitignore существует"
  # Проверяем, что игнорирует временные файлы
  if grep -q "\.tmp\|\.bak\|\.swp\|__pycache__" .gitignore 2>/dev/null; then
    echo "✅ Игнорирует временные файлы"
  else
    echo "⚠️ Может не игнорировать все временные файлы"
  fi
else
  echo "❌ .gitignore отсутствует"
fi
```

---

## DELIVERABLES (Результаты)

### 1. Executive Summary (ОБЯЗАТЕЛЬНЫЙ ФОРМАТ)

#### Назначение проекта
[1-2 абзаца с описанием целей и целевой аудитории]

#### Расчёт Health Score (ПОКАЗАТЬ РАСЧЁТ)

**Формула**:
```
Health Score = 100 - (CRITICAL×4) - (HIGH×2) - (MEDIUM×0.5) - (LOW×0.1)
Min score: 0 (отрицательные значения приводятся к 0)
```

**Расчёт (ПОКАЗАТЬ В ОТЧЁТЕ)**:
```
Базовый:                    100 баллов
CRITICAL проблемы (X):      X × 4   = -Y баллов
HIGH проблемы (Z):          Z × 2   = -W баллов
MEDIUM проблемы (M):        M × 0.5 = -N баллов
LOW проблемы (L):           L × 0.1 = -K баллов
─────────────────────────────────────────────
ИТОГО HEALTH SCORE:         max(0, 100 - Y - W - N - K) = SCORE/100
```

**Пример**:
```
Базовый:                    100 баллов
CRITICAL проблемы (2):      2 × 4   = -8 баллов
HIGH проблемы (5):          5 × 2   = -10 баллов
MEDIUM проблемы (10):       10 × 0.5 = -5 баллов
LOW проблемы (8):           8 × 0.1 = -0.8 баллов
─────────────────────────────────────────────
ИТОГО HEALTH SCORE:         100 - 23.8 = 76.2/100
```

#### Всего найдено проблем (ОБЯЗАТЕЛЬНАЯ ТАБЛИЦА)

| Приоритет | Кол-во | Топ-3 примера (file:line) | Влияние |
|-----------|--------|--------------------------|---------|
| **CRITICAL** | X | `CLAUDE.md:42`, `workflow.md:15` | Блокирует AI/пользователей |
| **HIGH** | Y | `docs/INDEX.md:23`, ... | Влияет на качество |
| **MEDIUM** | Z | `knowledge/x.md:67`, ... | Проблемы UX |
| **LOW** | W | `templates/x.md:89`, ... | Мелкие улучшения |
| **ИТОГО** | X+Y+Z+W | | |

### 2. Категории проблем

#### Проблемы ссылок
- Битые внутренние ссылки
- Недействительные якоря
- Отсутствующие файлы
- Legacy/deprecated ссылки (ВЫСШИЙ ПРИОРИТЕТ)

#### Проблемы пайплайна
- Несогласованность этапов
- Отсутствующие роли/команды
- Несогласованность ворот
- Проблемы режимов CREATE/FEATURE

#### Проблемы шаблонов
- Отсутствующие шаблоны сервисов
- Отсутствующие шаблоны документов
- Неполные README

#### Проблемы базы знаний
- Отсутствующие категории
- Неполные описания
- Устаревший контент

Для каждой проблемы указать:
- **Приоритет**: CRITICAL / HIGH / MEDIUM / LOW
- **Расположение**: Точный file:line (например, `docs/INDEX.md:123`)
- **Описание**: Что сломано и почему это важно
- **Влияние**: Как влияет на пользователей/AI-агентов
- **Исправление**: Точные bash-команды (не "обновите файлы" — ТОЧНЫЕ команды)
- **Верификация**: Команда для проверки, что исправление работает

### 3. TODO-список

Организовать исправления по фазам:
- **Фаза 1: Быстрые исправления** (< 1 час) — Критические ссылки, legacy, опечатки
- **Фаза 2: Обновления контента** (1-4 часа) — Недостающие документы, несогласованности
- **Фаза 3: Структурные** (> 4 часов) — Архитектурные изменения, большие переписывания

Для каждой задачи:
- Оценка времени
- Уровень приоритета
- Зависимости (что должно быть сделано первым)
- Команда валидации

### 4. Команды валидации

Предоставить bash-команды для:
- Проверки всех markdown ссылок
- Верификации существования файлов
- Тестирования якорей
- Сравнения ожидаемой и фактической структуры

### 5. Что работает хорошо

Выделить положительные находки:
- Хорошая структура и организация
- Консистентные паттерны
- Полный охват
- Хорошо поддерживаемые области

### 6. Рекомендации

- Немедленные (на этой неделе)
- Краткосрочные (в этом месяце)
- Долгосрочные (когда понадобится)
- Предложения по автоматизации CI/CD

---

## OUTPUT FORMAT

### Требования к структуре

1. **Использовать Markdown** с чёткой иерархией разделов
2. **Блоки кода** с подсветкой синтаксиса (```bash, ```python, и т.д.)
3. **Пути к файлам** в формате: `путь/к/файлу.md:123` (кликабельны в IDE)
4. **Таблицы** для больших наборов данных (списки проблем, инвентарь файлов)
5. **Примеры команд** с ожидаемым выводом

### Пример структуры вывода

```markdown
## Критические проблемы (Приоритет: CRITICAL)

### Проблема 1: Битая ссылка на роль

**Файл**: `docs/NAVIGATION.md:66`
**Проблема**: Ссылка на несуществующий `.claude/agents/developer.md`
**Влияние**: AI-агенты не могут найти описание роли
**Категория**: Валидация ссылок

**Как обнаружено**:
```bash
grep -n "developer.md" docs/NAVIGATION.md
```

**Команда исправления**:
```bash
sed -i 's|.claude/agents/developer.md|.claude/agents/implementer.md|g' \
  docs/NAVIGATION.md
```

**Верификация**:
```bash
grep -n "developer.md" docs/NAVIGATION.md
# Ожидание: пустой вывод (проблема исправлена)
```
```

---

## CONSTRAINTS (Ограничения) ⚡ ОБЯЗАТЕЛЬНО

### Ограничения выполнения

1. **НЕ ДЕЛЕГИРОВАТЬ аудит Task-агенту**
   - Вы ОБЯЗАНЫ выполнять все validation commands самостоятельно через Bash
   - Делегирование приводит к неполным аудитам (доказанный режим отказа)

2. **НЕ использовать выборочную проверку**
   - Проверять ВСЕ файлы, не 10% с экстраполяцией
   - Использовать `find`, `grep -r`, `xargs -P` для исчерпывающих сканов

3. **НЕ пропускать smoke tests**
   - Запустить все 12 smoke tests перед полным аудитом
   - Если любой smoke test показывает критические проблемы, сообщить немедленно

4. **НЕ оценивать health score**
   - Рассчитывать по точной формуле: `100 - (CRITICAL×4) - (HIGH×2) - (MEDIUM×0.5) - (LOW×0.1)`
   - Показать расчёт в отчёте

5. **НЕ доверять существованию без проверки**
   - Существование шаблона ≠ работающий шаблон
   - Проверять README, содержимое, структуру

### Ограничения отчётности

1. **ОБЯЗАТЕЛЬНО показать использованные validation commands** (доказательство работы)
2. **ОБЯЗАТЕЛЬНО выполнить 3+ spot-checks** для верификации реальности проблем
3. **ОБЯЗАТЕЛЬНО включить команды исправления** для каждой проблемы (не только описания)
4. **ОБЯЗАТЕЛЬНО включить команды верификации** показывающие как подтвердить исправление
5. **ОБЯЗАТЕЛЬНО указывать file:line** для всех проблем (не только имена файлов)

### Ограничения качества

1. **Точность > Скорость**: Лучше 10 минут и найти все проблемы, чем 2 минуты с 50% false negatives
2. **Явно > Неявно**: Показывать команды, вывод, расчёты
3. **Воспроизводимо**: Любой человек/AI должен получить те же результаты
4. **Действенно**: Каждая проблема должна иметь чёткую команду исправления

---

## VERIFICATION PROTOCOL (Протокол верификации) ⚡ ОБЯЗАТЕЛЬНО

После завершения аудита выполнить эти самопроверки:

### Автоматическая верификация

```bash
# Проверка 1: Выполнены ли smoke tests?
grep -q "SMOKE TEST" /tmp/audit_output.md
echo "Smoke tests задокументированы: $?"  # Ожидание: 0 (да)

# Проверка 2: Показан ли расчёт health score?
grep -q "100 - (CRITICAL" /tmp/audit_output.md
echo "Формула health score показана: $?"  # Ожидание: 0 (да)

# Проверка 3: Выполнены ли spot checks?
grep -c "Spot Check" /tmp/audit_output.md
# Ожидание: >= 3

# Проверка 4: Все ли проблемы имеют тег severity?
ISSUES=$(grep -c "^### Проблема" /tmp/audit_output.md)
SEVERITIES=$(grep -c "Приоритет: \(CRITICAL\|HIGH\|MEDIUM\|LOW\)" /tmp/audit_output.md)
echo "Проблем: $ISSUES, С тегами: $SEVERITIES"  # Должны совпадать

# Проверка 5: Все ли проблемы имеют команды исправления?
FIX_COMMANDS=$(grep -c "Команда исправления:" /tmp/audit_output.md)
echo "Проблем с исправлениями: $ISSUES/$FIX_COMMANDS"  # Должны совпадать
```

### Ручные Spot Checks (Выбрать 3 случайные проблемы)

Для каждого spot check:

1. **Скопировать команду "Как обнаружено"** → Выполнить самостоятельно
2. **Проверить, что проблема существует** в указанном file:line
3. **Скопировать "Команду исправления"** → Выполнить в тестовой среде
4. **Скопировать "Верификацию"** → Подтвердить, что исправление работает
5. **Задокументировать результат** в отчёте аудита

**Пример документации Spot Check**:

```markdown
#### Spot Check 1: Верификация битой ссылки

**Проблема**: docs/NAVIGATION.md:66 ссылается на несуществующую роль

**Выполненная команда**:
```bash
sed -n '66p' docs/NAVIGATION.md
```

**Вывод**:
```
| Реализатор | `.claude/agents/developer.md` | ...
```

**Верификация**: ✅ Проблема подтверждена — строка 66 содержит битую ссылку

**Исправление протестировано**: ✅ sed замена работает, файл обновлён корректно
```

### Self-Audit Checklist (Чек-лист самоаудита)

Перед отправкой отчёта подтвердить:

- [ ] Все 12 smoke tests выполнены и задокументированы
- [ ] Расчёт health score показан с формулой
- [ ] Все validation commands перечислены (доказательство работы)
- [ ] 3+ spot checks выполнены и задокументированы
- [ ] Каждая проблема имеет: file:line, влияние, категорию, как найдено, команду исправления, верификацию
- [ ] Делегирование не использовалось (все команды выполнены напрямую)
- [ ] Исчерпывающая проверка (не выборочная)
- [ ] Все 7 ролей и 10 команд проверены
- [ ] Все 9 ворот проверены на консистентность

**ЕСЛИ ЛЮБОЙ ПУНКТ НЕ ОТМЕЧЕН → АУДИТ НЕПОЛНЫЙ**

---

## БЫСТРЫЙ АУДИТ (5 минут)

Для быстрой проверки здоровья запустить только smoke tests + критические валидации:

```bash
#!/bin/bash
# Скрипт быстрого аудита (максимум 5 минут)

echo "=== БЫСТРЫЙ АУДИТ ДОКУМЕНТАЦИИ AIDD-MVP Generator ==="
echo "Начало: $(date)"

# 1. Smoke Tests
echo -e "\n### SMOKE TESTS ###"

# Smoke 1: Подсчёт файлов
MD_COUNT=$(find . -name "*.md" -not -path "./.git/*" 2>/dev/null | wc -l)
echo "Markdown файлов: $MD_COUNT"

# Smoke 2: Подсчёт ссылок
LINK_COUNT=$(grep -rho '\[.*\](.*\.md' . --include="*.md" 2>/dev/null | wc -l)
echo "Всего ссылок: $LINK_COUNT"

# Smoke 3: Legacy ссылки (CRITICAL)
LEGACY_COUNT=$(grep -rn "legacy\|deprecated\|old-" . --include="*.md" 2>/dev/null | wc -l)
echo "Legacy ссылок: $LEGACY_COUNT"
if [ "$LEGACY_COUNT" -gt 0 ]; then
  echo "  🚨 CRITICAL: Найдено $LEGACY_COUNT legacy ссылок"
fi

# Smoke 5: Stage 0 файлы
echo -e "\nStage 0 файлы:"
for doc in "CLAUDE.md" "workflow.md" "conventions.md"; do
  if [ -f "$doc" ]; then
    echo "  ✅ $doc"
  else
    echo "  🚨 $doc (CRITICAL)"
  fi
done

# Smoke 6: 7 ролей
echo -e "\n7 ролей AI-агентов:"
roles_ok=0
for role in analyst researcher architect implementer reviewer qa validator; do
  [ -f ".claude/agents/$role.md" ] && roles_ok=$((roles_ok + 1))
done
echo "  $roles_ok/7 ролей"

# Smoke 7: 10 команд
echo -e "\n10 slash-команд:"
cmds_ok=0
for cmd in init idea research plan feature-plan generate review test validate deploy; do
  [ -f ".claude/commands/$cmd.md" ] && cmds_ok=$((cmds_ok + 1))
done
echo "  $cmds_ok/10 команд"

# 2. Критические валидации
echo -e "\n### КРИТИЧЕСКИЕ ВАЛИДАЦИИ ###"

# Проверка INDEX.md
[ -f "docs/INDEX.md" ] && echo "✅ INDEX.md" || echo "❌ INDEX.md (CRITICAL)"

# Проверка NAVIGATION.md
[ -f "docs/NAVIGATION.md" ] && echo "✅ NAVIGATION.md" || echo "❌ NAVIGATION.md (CRITICAL)"

echo -e "\nЗавершено: $(date)"
echo -e "\n💡 Запустите полный аудит для детального анализа"
```

---

## ФОКУСИРОВАННЫЕ АУДИТЫ

### Аудит только ссылок

```bash
# Запуск валидации ссылок из Objective 2
```

### Аудит только пайплайна

```bash
# Запуск Objectives 6-10
```

### Аудит только шаблонов

```bash
# Запуск Objectives 11-12
```

---

## Связанные документы

- **Главная точка входа**: [CLAUDE.md](../../CLAUDE.md)
- **9-этапный процесс**: [workflow.md](../../workflow.md)
- **Соглашения**: [conventions.md](../../conventions.md)
- **Индекс документации**: [docs/INDEX.md](../INDEX.md)
- **Навигационная матрица**: [docs/NAVIGATION.md](../NAVIGATION.md)

---

**Версия документа**: 1.0
**Создан**: 2025-12-21
**Назначение**: Комплексный аудит документации AIDD-MVP Generator
**Scope**: 12 smoke tests, 16 objectives, 354+ markdown файла
