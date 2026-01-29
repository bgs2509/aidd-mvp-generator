# Комплексный аудит AIDD-MVP Generator — Codex (2025-01-13)

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


## 1. Executive Summary
### Назначение проекта
AIDD-MVP Generator — эталонный репозиторий методологии AI-Driven Development. Он определяет 9-этапный пайплайн, 7 ролей агентов, шаблоны сервисов (FastAPI, Aiogram, async workers) и документацию для быстрой сборки production-ready MVP за ~10 минут. Репозиторий служит «фабрикой инструкций» — `/aidd-*` команды и документация копируются в целевой проект и управляют качеством на каждом этапе.

Аудит подтвердил, что Stage 0 документы, сервисные и документ-шаблоны сохранены. **Ревизия аудита**: Проблема с Smoke Test 7 (slash-команды) отклонена — команды `aidd-*.md` корректны по дизайну. Остаётся **1 CRITICAL**: в шаблонах state-машины присутствуют DEPRECATED поля `current_feature`/`current_stage`. Также 20 битых ссылок (HIGH) и deprecated-упоминания в документах.

### Health Score
```
Health Score = 100 - (CRITICAL×4) - (HIGH×2) - (MEDIUM×0.5) - (LOW×0.1)
Базовый: 100
CRITICAL (1):  1 × 4   =  -4    ← Проблема 1 отклонена (ошибка теста)
HIGH (5):      5 × 2   = -10
MEDIUM (3):    3 × 0.5 = -1.5
LOW (1):       1 × 0.1 = -0.1
---------------------------------
ИТОГО: 100 - 15.6 = 84.4 / 100   ← УЛУЧШЕНО после ревизии
```

### Всего найдено проблем
| Приоритет | Кол-во | Топ-3 примера (file:line) | Влияние |
|-----------|--------|---------------------------|---------|
| **CRITICAL** | 1 | `templates/documents/pipeline-state-template.json:64` (deprecated fields) | State-машина содержит DEPRECATED поля `current_feature`/`current_stage` |
| ~~CRITICAL~~ | ~~1~~ | ~~`.claude/commands/plan.md`~~ | ~~ОТКЛОНЕНО: ошибка теста, команды `aidd-*.md` корректны~~ |
| **HIGH** | 5 | `docs/LINKS_REFERENCE.md:46`, `docs/audit/templates/comprehensive-audit.md:1540`, `templates/documents/template-map.md:184` | Пользователи и аудиторы переходят по 404, ссылки на Stage 0 и target-structure неверные |
| **MEDIUM** | 3 | `.claude/agents/analyst.md:11`, `docs/history/2025-12-19-aidd-mvp-implementation-todo.md:1`, `workflow.md:33` | Автоматические проверки ролей, placeholder и визуализация ворот дают шум |
| **LOW** | 1 | `docs/audit/templates/comprehensive-audit.md:94` | Smoke Test 4 из шаблона всегда печатает `Broken pipe`, мешая чтению лога |
| **ИТОГО** | 10 | (было 11, 1 отклонена) |  |

## 2. Smoke Tests
Результаты получены запуском `/tmp/run_smoke_tests.sh` (см. `/tmp/smoke_tests.log`).

| Тест | Команда | Результат |
|------|---------|-----------|
| 1. Markdown-файлы | `find . -name "*.md" -not -path "./.git/*"` | **157** (ниже ожидаемых 300-400, подтверждает урезанный scope) |
| 2. Markdown-ссылки | `grep -rho '\[.*\](.*\.md' . --include="*.md"` | **251**, резкое отклонение от 1000-2000 → внутренняя навигация ограничена |
| 3. Legacy ссылки | `grep -rn "legacy\|deprecated\|old-docs\|DEPRECATED" . --include="*.md"` | **20** (CRITICAL) |
| 4. Битые ссылки (10 файлов) | См. шаблон (Test 4) | Команда выводит `find: 'standard output': Broken pipe`; отдельная полная проверка показала **20** битых ссылок (`/tmp/broken_links_precise.txt`) |
| 5. Stage 0 | `for doc in CLAUDE.md workflow.md conventions.md` | Все три файла присутствуют (584/1264/599 строк) |
| 6. 7 ролей | Проверка `.claude/agents/*.md` | 7/7 файлов, но скрипт не видит «Этап N» (см. MEDIUM) |
| 7. Slash-команды | `ls .claude/commands/aidd-*.md` | **10/10** — все команды имеют префикс `aidd-` (это корректно по дизайну) |
| 8. Шаблоны сервисов | `ls templates/services/*/` | 5/5, все с README, src, tests, Dockerfile |
| 9. Шаблоны документов | 10/10 (`prd`, `architecture`, `qa`, `validation`, `tasklist`, `pipeline-state`, …) |
| 10. Gates | `grep -o "[A-Z_]*_READY\|…"` | CLAUDE/NAVIGATION = 9/9; workflow.md содержит лишние `_DONE/_OK` токены |
| 11. CREATE/FEATURE | `grep -c "CREATE"` и проверка файлов | CREATE=21, FEATURE=37, но `/plan`/`/feature-plan` отсутствуют |
| 12. Knowledge base | `find knowledge/ -name "*.md"` | 53 файлов, категории: architecture, infrastructure, integrations, pipeline, quality, security, services |

## 3. Категории проблем
### Проблемы пайплайна и ссылок
#### ~~Проблема 1~~: ОТКЛОНЕНО — Ошибка методологии теста
- **Статус**: NOT A BUG
- **Причина**: Smoke Test 7 искал файлы без префикса (`plan.md`), но по дизайну все команды имеют префикс `aidd-` для namespace isolation.
- **Факт**: Все 10 команд присутствуют: `aidd-init.md`, `aidd-idea.md`, `aidd-research.md`, `aidd-plan.md`, `aidd-feature-plan.md`, `aidd-generate.md`, `aidd-review.md`, `aidd-test.md`, `aidd-validate.md`, `aidd-deploy.md`
- **Исправление**: Обновлён Smoke Test 7 для корректного поиска `aidd-*.md`
- **Верификация**
  ```bash
  ls .claude/commands/aidd-*.md | wc -l  # → 10
  ```

#### Проблема 2 (CRITICAL): Legacy `current_feature` в шаблонах state-машины
- **Расположение**: `templates/documents/pipeline-state-template.json:64-71`, `contributors/2025-01-13-detailed-fix-recommendations.md:96-110`
- **Влияние**: `/aidd-init` продолжает генерировать `current_feature`/`current_stage`, что противоречит v2 (`active_pipelines`). Агенты получают конфликтующие инструкции, smoke test 3 всегда видит 20 legacy ссылок.
- **Как обнаружено**
  ```bash
  rg -n "current_feature" templates/documents/pipeline-state-template.json
  rg -n "current_feature" contributors/2025-01-13-detailed-fix-recommendations.md
  ```
- **Команда исправления**
  ```bash
  apply_patch <<'PATCH'
  *** Begin Patch
  *** Update File: templates/documents/pipeline-state-template.json
  @@
  -  "current_feature": {
  -    "$comment": "DEPRECATED в v2. Используется для backward compatibility. В новых проектах = null.",
  -    "$deprecated": true
  -  },
  -
  -  "current_stage": {
  -    "$comment": "DEPRECATED в v2. Этап теперь хранится в active_pipelines[FID].stage.",
  -    "$deprecated": true
  -  },
  *** End Patch
  PATCH
  sed -i '/current_feature/,+10d' contributors/2025-01-13-detailed-fix-recommendations.md
  ```
- **Верификация**
  ```bash
  rg -n "current_feature" templates/documents/pipeline-state-template.json
  grep -rn "legacy\|deprecated" . --include="*.md"
  ```

#### Проблема 3 (HIGH): Навигация (`docs/LINKS_REFERENCE.md`, `docs/PIPELINE-TREE.md`, contributor-репорты) ссылается на несуществующие `.claude/commands/<cmd>.md`
- **Расположение**: `docs/LINKS_REFERENCE.md:46-54`, `docs/PIPELINE-TREE.md:151-188`, `contributors/2025-01-13-comprehensive-audit-report.md:83`
- **Влияние**: Любая документация, которая использует таблицу ссылок, открывает 404 вместо инструкций по командам. Даже после добавления алиасов нужно актуализировать ссылки на реальные пути `aidd-*.md`.
- **Как обнаружено**
  ```bash
  sed -n '46,54p' docs/LINKS_REFERENCE.md
  rg -n '\.claude/commands/idea.md' docs/PIPELINE-TREE.md contributors/2025-01-13-comprehensive-audit-report.md
  ```
- **Команда исправления**
  ```bash
  rg -l '\.claude/commands/[a-z-]*\.md' docs/LINKS_REFERENCE.md docs/PIPELINE-TREE.md contributors/2025-01-13-comprehensive-audit-report.md \
    | xargs perl -0pi -e 's#\.claude/commands/([a-z-]+)\.md#\.claude/commands/aidd-\1.md#g'
  ```
- **Верификация**
  ```bash
  rg -n '\.claude/commands/' docs/LINKS_REFERENCE.md | head
  ```

#### Проблема 4 (HIGH): Аудиторский шаблон ссылается на `docs/CLAUDE.md`
- **Расположение**: `docs/audit/templates/comprehensive-audit.md:1540-1544`
- **Влияние**: Любой агент, копирующий ссылки из шаблона, попадает в `docs/CLAUDE.md` (файла нет) или в `docs/NAVIGATION.md` внутри `docs/audit/`, и тратит время на поиски Stage 0.
- **Как обнаружено**
  ```bash
  sed -n '1538,1544p' docs/audit/templates/comprehensive-audit.md
  ls docs/CLAUDE.md  # → нет файла
  ```
- **Команда исправления**
  ```bash
  sed -i '1540,1542s|../../|../../../|' docs/audit/templates/comprehensive-audit.md
  sed -i '1543,1544s|../|../../|' docs/audit/templates/comprehensive-audit.md
  ```
- **Верификация**
  ```bash
  sed -n '1538,1544p' docs/audit/templates/comprehensive-audit.md
  ls ../../../CLAUDE.md
  ```

#### Проблема 5 (HIGH): Template-map и исторические документы ведут на несуществующие файлы
- **Расположение**: `templates/documents/template-map.md:184`, `docs/history/2025-12-20-pipeline-integration-problem.md:1617-1715`
- **Влияние**: Матрица шаблонов отправляет пользователя в `templates/target-project-structure.md` (файла нет), а история пайплайна ссылается на `../CLAUDE.md` и `.ai-framework/AGENTS.md`, которых нет в репозитории → невозможно подтвердить решения, описанные в истории.
- **Как обнаружено**
  ```bash
  sed -n '178,186p' templates/documents/template-map.md
  sed -n '1612,1716p' docs/history/2025-12-20-pipeline-integration-problem.md
  ```
- **Команда исправления**
  ```bash
  sed -i '184s|../target-project-structure.md|../../docs/target-project-structure.md|' templates/documents/template-map.md
  sed -i '1617,1619s|../|../../|g' docs/history/2025-12-20-pipeline-integration-problem.md
  sed -i '1715s|\.ai-framework/AGENTS.md|roles/analyst/initialization.md|' docs/history/2025-12-20-pipeline-integration-problem.md
  ```
- **Верификация**
  ```bash
  sed -n '178,186p' templates/documents/template-map.md
  sed -n '1612,1716p' docs/history/2025-12-20-pipeline-integration-problem.md
  ```

#### Проблема 6 (HIGH): Примеры артефактов ведут на файлы, которые создаются только в целевых проектах
- **Расположение**: `docs/artifact-naming.md:222`, `.claude/commands/aidd-analyze.md:383`
- **Влияние**: Кликабельные ссылки `[PRD](prd/...)` открывают 404 внутри генератора. AI-агенту приходится гадать где искать пример, а линк-валидаторы считают это ошибкой.
- **Как обнаружено**
  ```bash
  sed -n '218,224p' docs/artifact-naming.md
  sed -n '380,384p' .claude/commands/aidd-analyze.md
  ```
- **Команда исправления**
  ```bash
  perl -0pi -e 's|\[PRD\]\((prd/[A-Za-z0-9_-]+-prd\.md)\)|`PRD`: \1|g' docs/artifact-naming.md .claude/commands/aidd-analyze.md
  ```
- **Верификация**
  ```bash
  rg -n '\[PRD\]' docs/artifact-naming.md .claude/commands/aidd-analyze.md
  ```

### Проблемы качества и структуры
#### Проблема 7 (MEDIUM): Ролевые инструкции не содержат явных токенов `Этап N`
- **Расположение**: `.claude/agents/analyst.md:11`, `.claude/agents/reviewer.md:11`, `.claude/agents/qa.md:11`, `.claude/agents/validator.md:11`
- **Влияние**: Objective 7 (`grep -qi "этап $stage"`) считает, что роли не привязаны к стадиям. Это создаёт ложные срабатывания в smoke tests и не позволяет автоматически проверять покрытие ролей.
- **Как обнаружено**
  ```bash
  python - <<'PY'
  from pathlib import Path
  for role in ['analyst','researcher','architect','reviewer','qa','validator']:
      text = Path(f'.claude/agents/{role}.md').read_text()
      if "Этап" not in text:
          print(role)
  PY
  ```
  или `roles vs stages` скрипт из Objective 7 (см. `/tmp/smoke_tests.log`).
- **Команда исправления**
  ```bash
  perl -0pi -e 's/> Это первый этап/> Этап 1 — первый этап/' .claude/agents/analyst.md
  perl -0pi -e 's/> Пятый этап/> Этап 5 — пятый этап/' .claude/agents/reviewer.md
  perl -0pi -e 's/> Шестой этап/> Этап 6 — шестой этап/' .claude/agents/qa.md
  perl -0pi -e 's/> Валидатор отвечает/> Этапы 7-8 — валидатор отвечает/' .claude/agents/validator.md
  ```
- **Верификация**
  ```bash
  rg -n 'Этап [0-9]' .claude/agents/*.md
  /tmp/run_smoke_tests.sh  # тест 7 должен видеть этапы
  ```

#### Проблема 8 (MEDIUM): 25 открытых placeholder/FIXME маркеров в опубликованных документах
- **Расположение**: `docs/history/2025-12-19-aidd-mvp-implementation-todo.md:1`, `docs/history/2025-12-19-problems-solutions-todo.md:1`, `templates/documents/*-report-template.md` (FR-XXX заглушки)
- **Влияние**: Публикация placeholder внутри эталонных документов затрудняет автоматический аудит (любая проверка воспринимает placeholder как блокер) и вводит пользователей в заблуждение (неясно, реализована ли задача).
- **Как обнаружено**
  ```bash
  grep -rn 'placeholder\|FIXME\|XXX' . --include='*.md' > /tmp/todo_hits.txt
  wc -l /tmp/todo_hits.txt  # → 25
  ```
- **Команда исправления**
  ```bash
  # Исторические файлы: заменить "# placeholder" на фактическое название и добавить статус
  sed -i '1s/# placeholder:/# История:/' docs/history/2025-12-19-aidd-mvp-implementation-todo.md
  # В шаблонах отчётов: пояснить placeholder
  perl -0pi -e 's/\{FR-XXX\}/\[Укажите ID требования\]/g' templates/documents/*report-template.md
  ```
- **Верификация**
  ```bash
  rg -n 'placeholder\|FR-XXX' docs/history templates/documents
  ```

#### Проблема 9 (MEDIUM): workflow-диаграмма генерирует ложные ворота `_DONE` и `_OK`
- **Расположение**: `workflow.md:31-36`
- **Влияние**: Команда из Objective 10 (`grep -o "[A-Z_]*_READY\|…"`) выводит `_DONE` и `_OK`, из-за чего Smoke Test 10 показывает «лишние» ворота и требует ручной фильтрации.
- **Как обнаружено**
  ```bash
  grep -o "[A-Z_]*_READY\|[A-Z_]*_DONE\|[A-Z_]*_APPROVED\|[A-Z_]*_OK" workflow.md | sort -u
  ```
- **Команда исправления**
  ```bash
  sed -i '34s/RESEARCH \|  _DONE/RESEARCH_DONE/' workflow.md
  sed -i '34s/IMPLEMENT\|   _OK/IMPLEMENT_OK/' workflow.md
  ```
- **Верификация**
  ```bash
  grep -o "_DONE\|_OK" workflow.md
  ```

### Проблемы UX (Low)
#### Проблема 10 (LOW): Smoke Test 4 из шаблона всегда печатает `Broken pipe`
- **Расположение**: `docs/audit/templates/comprehensive-audit.md:94-105`
- **Влияние**: При дословном запуске команда производит `find: 'standard output': Broken pipe`, что путает аудиторов и маскирует реальный вывод.
- **Как обнаружено**
  ```bash
  /tmp/run_smoke_tests.sh  # журнал /tmp/smoke_tests.log содержит сообщения find: Broken pipe
  ```
- **Команда исправления**
  ```bash
  apply_patch <<'PATCH'
  *** Begin Patch
  *** Update File: docs/audit/templates/comprehensive-audit.md
  @@
  -find . -name "*.md" -not -path "./.git/*" | head -10 | while read f; do
  +mapfile -t files < <(find . -name "*.md" -not -path "./.git/*" | head -10)
  +for f in "${files[@]}"; do
        ...
  -done | head -5
  +done | head -5
  *** End Patch
  PATCH
  ```
- **Верификация**
  ```bash
  bash <(sed -n '94,105p' docs/audit/templates/comprehensive-audit.md)
  ```

## 4. placeholder-список
| Фаза | Задача | Приоритет | Команда проверки |
|------|--------|-----------|------------------|
| **Фаза 1 — быстрые** | ~~Добавить алиасы `.claude/commands/<cmd>.md`~~ ОТКЛОНЕНО — команды `aidd-*.md` корректны | ~~CRITICAL~~ | — |
| | Удалить `current_feature/current_stage` из шаблонов и документов | CRITICAL | `rg -n 'current_feature' templates/documents` |
| | Исправить относительные пути в `docs/audit/templates` | HIGH | Ручная верификация ссылок |
| **Фаза 2 — контент** | Вставить явные `Этап N` токены в `.claude/agents/*.md` | MEDIUM | `grep -n 'Этап [0-9]' .claude/agents/*.md` |
| | Обновить примеры артефактов на текстовые пояснения | HIGH | `rg -n '\[PRD\]' docs .claude/commands` |
| **Фаза 3 — структурные** | Переписать проблемные разделы исторических документов | MEDIUM | Повторный аудит ссылок |

## 5. Команды валидации
Ниже главные команды, использованные в ходе аудита (см. упомянутые логи):
```bash
/tmp/run_smoke_tests.sh                         # все 12 smoke tests
/tmp/run_objective2.sh                          # Objective 2 (legacy + ссылки)
find . -name "*.md" -not -path "./.git/*"      # Smoke Test 1
grep -rho '\[.*\](.*\.md' . --include="*.md"  # Smoke Test 2
rg -rn "legacy\|deprecated" . --include="*.md" # Smoke Test 3
ls .claude/commands                              # Smoke Tests 6-7
find knowledge/ -name "*.md"                     # Smoke Test 12
rg -n '\.claude/commands/' docs/                # Навигация
sed -n '1538,1544p' docs/audit/templates/...    # Stage 0 ссылки
sed -n '178,186p' templates/documents/template-map.md
wc -l /tmp/todo_hits.txt                         # placeholder inventory
grep -o "[A-Z_]*_READY\|..." workflow.md        # Gates
```

## 6. Spot Checks
### Spot Check 1 — Slash-команды (РЕВИЗИЯ)
```
$ ls .claude/commands/aidd-*.md
# → aidd-deploy.md aidd-feature-plan.md aidd-generate.md aidd-idea.md aidd-init.md
#   aidd-plan.md aidd-research.md aidd-review.md aidd-test.md aidd-validate.md
```
✅ **РЕВИЗИЯ**: Все 10 команд присутствуют с префиксом `aidd-`. Это корректно по дизайну — namespace isolation.

### Spot Check 2 — Аудиторский шаблон
```
$ sed -n '1538,1544p' docs/audit/templates/comprehensive-audit.md
- **Главная точка входа**: 
$ ls docs/CLAUDE.md
ls: cannot access 'docs/CLAUDE.md': No such file or directory
```
✅ Подтверждено: ссылка ведет на `docs/CLAUDE.md`, которого нет.

### Spot Check 3 — Template-map → target structure
```
$ sed -n '178,184p' templates/documents/template-map.md
|  |
$ ls templates/target-project-structure.md
ls: cannot access 'templates/target-project-structure.md'
$ ls docs/target-project-structure.md
# файл существует
```
✅ Подтверждено: относительный путь должен вести в `../../docs/`.

## 7. Что работает хорошо
- Stage 0 документы (`CLAUDE.md`, `workflow.md`, `conventions.md`, `docs/initialization.md`) присутствуют и подробны.
- Все пять шаблонов сервисов содержат README, `src`, `tests`, Dockerfile и requirements — готовы к копированию.
- Каталог `templates/documents/` полон (10+ файлов), включает `tasklist` и `pipeline-state` для целевых проектов.
- База знаний (`knowledge/…`) содержит 53 файла в 7 категориях, есть индекс `knowledge/README.md`.
- HTTP-only и DDD/Hexagonal принципы явно описаны в `CLAUDE.md`, `workflow.md`, `conventions.md` и в knowledge-базе (`knowledge/architecture/*`).

## 8. Рекомендации
1. **Немедленно (неделя)**: добавить алиасы `.claude/commands/<cmd>.md`, удалить `current_feature`, исправить все битые ссылки (см. `/tmp/broken_links_precise.txt`). После этого повторно запустить `run_smoke_tests.sh` и Objective 2 для подтверждения.
2. **Краткосрочно (месяц)**: обновить инструкции ролей и шаблоны (FR-XXX/placeholder), чтобы автоматизированные проверки проходили без ложных тревог. Одновременно исправить визуальные ворота в `workflow.md` и пересобрать документацию (`docs/history/*`) с корректными ссылками.
3. **Долгосрочно**: добавить CI-задачу (например, CI/CD) с Python-линкчекером из Objective 2 и smoke-скриптом. Автоматизировать генерацию таблиц ссылок (docs/LINKS_REFERENCE.md) напрямую из содержимого `.claude/commands/`.
