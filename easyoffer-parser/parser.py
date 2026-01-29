"""
Парсер вопросов с сайта easyoffer.ru для Python Developer
Требует авторизацию через Telegram для доступа ко всем вопросам
"""

import requests
import json
import time
import os
from typing import List, Dict, Optional


class EasyOfferParser:
    """Парсер для извлечения вопросов с easyoffer.ru через API"""

    def __init__(self, cookies_file: str = "cookies.json", jwt_token: str = None):
        """
        Инициализация парсера

        Args:
            cookies_file: Путь к файлу с cookies после авторизации
            jwt_token: JWT токен для доступа к premium контенту
        """
        self.base_url = "https://easyoffer.ru/api/v1/professions/python-developer/questions/"
        self.session = requests.Session()
        self.questions: List[Dict] = []

        # Загрузить cookies из файла
        self.load_cookies(cookies_file)

        # Добавить JWT токен для premium доступа
        if jwt_token:
            self.session.headers.update({
                'Authorization': f'Bearer {jwt_token}'
            })

        # Добавить стандартные заголовки
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://easyoffer.ru/python-developer/questions',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
        })

    def load_cookies(self, cookies_file: str) -> None:
        """
        Загрузка cookies из файла

        Args:
            cookies_file: Путь к JSON файлу с cookies
        """
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)

            for cookie in cookies:
                self.session.cookies.set(
                    name=cookie['name'],
                    value=cookie['value'],
                    domain=cookie.get('domain', '.easyoffer.ru')
                )

            print(f"✓ Загружено {len(cookies)} cookies из {cookies_file}")

        except FileNotFoundError:
            print(f"⚠️ Файл {cookies_file} не найден!")
            print("Используйте get_cookies.py для получения cookies или создайте файл вручную")
            raise
        except json.JSONDecodeError:
            print(f"⚠️ Ошибка парсинга {cookies_file}. Проверьте формат JSON")
            raise

    def fetch_page(self, page_num: int) -> Optional[Dict]:
        """
        Получить данные одной страницы через API

        Args:
            page_num: Номер страницы (начиная с 1)

        Returns:
            Словарь с данными страницы или None при ошибке
        """
        url = f"{self.base_url}?page={page_num}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            if response.status_code == 404:
                print(f"⚠️ Страница {page_num} не найдена (404)")
            elif response.status_code == 401:
                print(f"⚠️ Требуется авторизация (401). Проверьте cookies!")
            else:
                print(f"⚠️ HTTP ошибка {response.status_code}: {e}")
            return None

        except requests.RequestException as e:
            print(f"⚠️ Ошибка при запросе страницы {page_num}: {e}")
            return None

    def verify_access(self) -> Dict:
        """
        Проверить доступ и получить информацию о доступных страницах

        Returns:
            Словарь с информацией: total_pages, count, user_limit
        """
        print("\n=== Проверка доступа ===")
        data = self.fetch_page(1)

        if not data:
            print("❌ Не удалось получить данные. Проверьте авторизацию!")
            return {}

        info = {
            'total_pages': data.get('total_pages', 0),
            'total_count': data.get('count', 0),
            'user_limit': data.get('user_limit', 0),
            'page_size': len(data.get('results', []))
        }

        print(f"✓ Всего вопросов в базе: {info['total_count']}")
        print(f"✓ Доступно страниц: {info['total_pages']}")
        print(f"✓ Лимит пользователя: {info['user_limit']}")
        print(f"✓ Вопросов на странице: {info['page_size']}")

        return info

    def parse_all_pages(self, start_page: int = 1, end_page: int = 160) -> None:
        """
        Парсинг всех доступных страниц

        Args:
            start_page: Начальная страница
            end_page: Конечная страница (будет скорректирована по факту)
        """
        print(f"\n=== Начало парсинга ===")
        print(f"Целевой диапазон: страницы {start_page}-{end_page}")

        # Проверить доступ и скорректировать end_page
        access_info = self.verify_access()
        if not access_info:
            return

        actual_pages = access_info.get('total_pages', 0)
        if actual_pages > 0 and actual_pages < end_page:
            print(f"⚠️ Доступно только {actual_pages} страниц, а не {end_page}")
            print(f"Парсинг будет выполнен для {actual_pages} страниц")
            end_page = actual_pages

        # Парсинг страниц
        for page_num in range(start_page, end_page + 1):
            print(f"\n[{page_num}/{end_page}] Парсинг страницы {page_num}...")

            data = self.fetch_page(page_num)

            if not data or 'results' not in data:
                print(f"❌ Страница {page_num} пуста или недоступна. Остановка.")
                break

            results = data['results']
            questions_found = len(results)
            print(f"  ✓ Найдено вопросов: {questions_found}")

            # Извлечение вопросов
            for item in results:
                question = {
                    'id': item.get('id'),
                    'question': item.get('title'),
                    'chance_percent': round(item.get('frequency', 0) * 100, 2),
                    'slug': item.get('slug'),
                    'page': page_num
                }
                self.questions.append(question)

            # Rate limiting — задержка 1 секунда между запросами
            if page_num < end_page:
                time.sleep(1)

            # Сохранение промежуточных результатов каждые 10 страниц
            if page_num % 10 == 0:
                self.save_to_json(f"backup_page_{page_num}.json")
                print(f"  ✓ Промежуточное сохранение: backup_page_{page_num}.json")

        print(f"\n=== Парсинг завершён ===")
        print(f"Всего спарсено вопросов: {len(self.questions)}")

    def save_to_json(self, filename: str = "python_questions.json") -> None:
        """
        Сохранение результатов в JSON с сортировкой по шансу

        Args:
            filename: Имя выходного файла
        """
        # Сортировка по убыванию шанса
        sorted_questions = sorted(
            self.questions,
            key=lambda x: x['chance_percent'],
            reverse=True
        )

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sorted_questions, f, ensure_ascii=False, indent=2)

        print(f"\n=== Результаты сохранены ===")
        print(f"✓ Файл: {filename}")
        print(f"✓ Всего вопросов: {len(sorted_questions)}")

        if sorted_questions:
            print(f"✓ Максимальный шанс: {sorted_questions[0]['chance_percent']}%")
            print(f"  → \"{sorted_questions[0]['question']}\"")
            print(f"✓ Минимальный шанс: {sorted_questions[-1]['chance_percent']}%")
            print(f"  → \"{sorted_questions[-1]['question']}\"")

    def get_statistics(self) -> Dict:
        """
        Получить статистику по спарсенным вопросам

        Returns:
            Словарь со статистикой
        """
        if not self.questions:
            return {}

        chances = [q['chance_percent'] for q in self.questions]

        return {
            'total': len(self.questions),
            'max_chance': max(chances),
            'min_chance': min(chances),
            'avg_chance': round(sum(chances) / len(chances), 2),
            'unique_ids': len(set(q['id'] for q in self.questions))
        }


def main():
    """Основная функция для запуска парсера"""
    print("=" * 60)
    print("EASYOFFER.RU PARSER — Вопросы Python Developer")
    print("=" * 60)

    try:
        # Загрузить JWT токен
        jwt_token = None
        if os.path.exists("jwt_token.txt"):
            with open("jwt_token.txt", 'r') as f:
                jwt_token = f.read().strip()
            print("✓ Загружен JWT токен")
        else:
            print("⚠️ jwt_token.txt не найден - используем только cookies")

        # Инициализация парсера
        parser = EasyOfferParser(
            cookies_file="cookies.json",
            jwt_token=jwt_token
        )

        # Парсинг всех страниц (автоматически определит реальное количество)
        parser.parse_all_pages(start_page=1, end_page=160)

        # Сохранение результатов
        parser.save_to_json("python_questions.json")

        # Вывод статистики
        stats = parser.get_statistics()
        if stats:
            print(f"\n=== Статистика ===")
            print(f"Средний шанс: {stats['avg_chance']}%")
            print(f"Уникальных ID: {stats['unique_ids']}")

    except FileNotFoundError:
        print("\n❌ Ошибка: Файл cookies.json не найден!")
        print("\nДля получения cookies:")
        print("1. Запустите: python get_cookies.py")
        print("2. Или создайте cookies.json вручную (см. README.md)")

    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
