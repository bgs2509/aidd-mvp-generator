# Парсер вопросов easyoffer.ru для Python Developer

Парсер для извлечения вопросов с собеседований Python Developer с сайта [easyoffer.ru](https://easyoffer.ru/python-developer/questions).

## Возможности

- Извлечение вопросов через официальный API
- Получение процента вероятности ("шанс") для каждого вопроса
- Авторизация через Telegram для доступа к данным
- Автоматическое сохранение в JSON формат
- Промежуточное сохранение результатов каждые 10 страниц
- Статистика по спарсенным вопросам
- Автоматическое определение доступного количества страниц

## Требования

- Python 3.8+
- Аккаунт Telegram для авторизации на сайте

## ⚠️ ВАЖНОЕ ОГРАНИЧЕНИЕ API

**Бесплатный доступ ограничен 20 вопросами!**

После тестирования обнаружено, что API easyoffer.ru имеет жёсткие ограничения для бесплатных аккаунтов:

- **user_limit: 20** — доступны только первые 20 вопросов
- **total_pages: 1** — доступна только страница 1
- Попытки получить page=2 возвращают **404 Not Found**
- Параметр `page_size` не влияет на лимит (проверено со значениями 50, 100)

**Для доступа ко всем 7959 вопросам требуется платная подписка на сайте easyoffer.ru.**

Парсер корректно работает в рамках этого ограничения и успешно извлекает все доступные 20 вопросов.

## Установка

1. Перейдите в директорию парсера:
```bash
cd easyoffer-parser
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите браузеры для Playwright (если планируете использовать автоматическое получение cookies):
```bash
playwright install chromium
```

## Быстрый старт

### Шаг 1: Получение cookies

**Вариант А: Автоматически через Playwright (Рекомендуется)**

```bash
python get_cookies.py
```

Откроется браузер. Выполните следующие действия:
1. Нажмите "Войти через Telegram"
2. Авторизуйтесь
3. Вернитесь в терминал и нажмите Enter

Cookies автоматически сохранятся в `cookies.json`.

**Вариант Б: Вручную**

1. Откройте https://easyoffer.ru в браузере
2. Откройте DevTools (F12)
3. Авторизуйтесь через Telegram
4. Перейдите в DevTools: `Application → Cookies → https://easyoffer.ru`
5. Скопируйте cookies в формате JSON
6. Сохраните в файл `cookies.json`

Пример структуры `cookies.json`:
```json
[
  {
    "name": "sessionid",
    "value": "ваш_токен_сессии",
    "domain": ".easyoffer.ru",
    "path": "/",
    "expires": 1234567890,
    "httpOnly": true,
    "secure": true,
    "sameSite": "Lax"
  }
]
```

### Шаг 2: Запуск парсера

```bash
python parser.py
```

Парсер автоматически:
- Проверит доступность API и количество страниц
- Спарсит все доступные вопросы
- Сохранит результаты в `python_questions.json`
- Выведет статистику

## Структура выходных данных

Результаты сохраняются в `python_questions.json`:

```json
[
  {
    "id": 123,
    "question": "Расскажи о себе",
    "chance_percent": 99.0,
    "slug": "rasskazhi-o-sebe",
    "page": 1
  },
  {
    "id": 124,
    "question": "Что такое декоратор в Python",
    "chance_percent": 35.0,
    "slug": "chto-takoe-dekorator-v-python",
    "page": 1
  }
]
```

Вопросы отсортированы по убыванию процента вероятности (chance_percent).

## Описание файлов

| Файл | Описание |
|------|----------|
| `parser.py` | Основной скрипт парсера |
| `get_cookies.py` | Утилита для получения cookies |
| `requirements.txt` | Зависимости проекта |
| `cookies.json` | Файл с cookies (создаётся пользователем) |
| `python_questions.json` | Результаты парсинга |
| `backup_page_*.json` | Промежуточные сохранения (каждые 10 страниц) |

## Использование в коде

```python
from parser import EasyOfferParser

# Создать экземпляр парсера
parser = EasyOfferParser(cookies_file="cookies.json")

# Проверить доступ
access_info = parser.verify_access()
print(f"Доступно страниц: {access_info['total_pages']}")
print(f"Лимит пользователя: {access_info['user_limit']}")

# Спарсить все доступные страницы (автоопределение)
# Парсер сам определит реальное количество доступных страниц
parser.parse_all_pages(start_page=1, end_page=160)

# Или явно указать только доступные страницы
# parser.parse_all_pages(start_page=1, end_page=access_info['total_pages'])

# Сохранить результаты
parser.save_to_json("output.json")

# Получить статистику
stats = parser.get_statistics()
print(f"Всего вопросов: {stats['total']}")
print(f"Средний шанс: {stats['avg_chance']}%")
```

## Ограничения и особенности

### Лимиты API
**Бесплатные аккаунты:**
- Доступны только первые **20 вопросов** (из 7959)
- Доступна только **страница 1**
- Авторизация через Telegram **не снимает** это ограничение

**Платные аккаунты:**
- Для доступа ко всем вопросам требуется оплаченная подписка на easyoffer.ru
- После оплаты предположительно станут доступны все 160 страниц (7959 вопросов)

### Количество страниц
Парсер автоматически определяет реальное количество доступных страниц через API (`total_pages`).

Для бесплатных аккаунтов вы увидите:
```
✓ Доступно страниц: 1
⚠️ Доступно только 1 страниц, а не 160
```

### Rate Limiting
Парсер автоматически добавляет задержку 1 секунда между запросами, чтобы не перегружать сервер.

### Промежуточные сохранения
Каждые 10 страниц результаты автоматически сохраняются в `backup_page_N.json`. Это защищает от потери данных при прерывании парсинга.

## Примеры использования результатов

### Фильтрация по шансу
```python
import json

# Загрузить данные
with open('python_questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Только вопросы с шансом > 20%
popular = [q for q in questions if q['chance_percent'] > 20]
print(f"Популярных вопросов: {len(popular)}")

# Топ-10 самых вероятных
top_10 = questions[:10]
for q in top_10:
    print(f"{q['chance_percent']}% - {q['question']}")
```

### Конвертация в CSV
```python
import pandas as pd
import json

with open('python_questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

df = pd.DataFrame(questions)
df.to_csv('python_questions.csv', index=False, encoding='utf-8-sig')
```

## Решение проблем

### Ошибка 401 (Unauthorized)
**Проблема:** Cookies устарели или неверны

**Решение:**
1. Удалите старый `cookies.json`
2. Повторно запустите `python get_cookies.py`
3. Пройдите авторизацию заново

### Доступно меньше страниц, чем ожидалось
**Проблема:** API возвращает `total_pages: 1` вместо 160

**Причина:**
- **Бесплатные аккаунты** ограничены 20 вопросами на странице 1
- Даже после авторизации через Telegram лимит сохраняется (`user_limit: 20`)

**Решение:**
Для доступа ко всем 7959 вопросам необходима **платная подписка** на easyoffer.ru.

Парсер автоматически определит доступное количество страниц и выведет:
```
✓ Доступно страниц: 1
✓ Лимит пользователя: 20
⚠️ Доступно только 1 страниц, а не 160
```

Парсер успешно извлечёт все 20 доступных вопросов.

### Playwright не установлен
**Ошибка:** `ImportError: No module named 'playwright'`

**Решение:**
```bash
pip install playwright
playwright install chromium
```

### Файл cookies.json не найден
**Ошибка:** `FileNotFoundError: cookies.json`

**Решение:**
Сначала получите cookies:
```bash
python get_cookies.py
```

## API Endpoint

Парсер использует официальный API:
```
GET https://easyoffer.ru/api/v1/professions/python-developer/questions/?page={N}
```

**Ответ для бесплатного аккаунта (авторизованного через Telegram):**
```json
{
  "count": 7959,
  "total_pages": 1,
  "current_page": 1,
  "user_limit": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 123,
      "title": "Расскажи о себе",
      "frequency": 0.99,
      "slug": "rasskazhi-o-sebe",
      "anki_progress_lvl": 0
    },
    ...20 вопросов всего...
  ]
}
```

**Ключевые поля:**
- `count`: 7959 — всего вопросов в базе данных
- `total_pages`: 1 — доступно страниц для бесплатного аккаунта
- `user_limit`: 20 — лимит вопросов для пользователя
- `results`: массив из 20 вопросов

**Примечание:** Для платных аккаунтов `total_pages` предположительно будет 160, а `user_limit` отсутствовать или быть больше.

## Лицензия

MIT

## Автор

Создано для парсинга вопросов с easyoffer.ru

## Примечания

- Используйте парсер ответственно
- Соблюдайте Terms of Service сайта easyoffer.ru
- Не перегружайте сервер частыми запросами
- Уважайте авторские права на контент
