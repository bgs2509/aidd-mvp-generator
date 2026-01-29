#!/usr/bin/env python3
"""
Тестирование различных API endpoints для поиска правильного
"""

import requests
import json
from typing import Dict, Optional


def load_cookies(cookies_file: str = "cookies.json") -> requests.Session:
    """Загрузить cookies в сессию"""
    session = requests.Session()

    with open(cookies_file, 'r', encoding='utf-8') as f:
        cookies = json.load(f)

    for cookie in cookies:
        session.cookies.set(
            name=cookie['name'],
            value=cookie['value'],
            domain=cookie.get('domain', '.easyoffer.ru')
        )

    return session


def test_endpoint(session: requests.Session, url: str, name: str) -> Optional[Dict]:
    """Тестировать один endpoint"""
    print(f"\n{'='*70}")
    print(f"ТЕСТ: {name}")
    print(f"URL: {url}")
    print('='*70)

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://easyoffer.ru/python-developer/questions',
        'Origin': 'https://easyoffer.ru',
    }

    try:
        response = session.get(url, headers=headers, timeout=10)
        print(f"Статус: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ УСПЕХ! Получен JSON ответ")
                print(f"  • total_pages: {data.get('total_pages', 'N/A')}")
                print(f"  • user_limit: {data.get('user_limit', 'N/A')}")
                print(f"  • count: {data.get('count', 'N/A')}")
                print(f"  • current_page: {data.get('current_page', 'N/A')}")
                print(f"  • results length: {len(data.get('results', []))}")

                if data.get('results'):
                    print(f"  • Первый вопрос: {data['results'][0].get('title', 'N/A')[:50]}...")

                return data

            except json.JSONDecodeError:
                print(f"⚠️ Ответ не является JSON")
                print(f"Первые 200 символов: {response.text[:200]}")
                return None
        else:
            print(f"❌ HTTP {response.status_code}")
            return None

    except requests.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return None


def main():
    """Основная функция тестирования"""
    print("="*70)
    print("ПОИСК ПРАВИЛЬНОГО API ENDPOINT")
    print("="*70)

    # Загрузить cookies
    print("\n📁 Загрузка cookies...")
    session = load_cookies("cookies.json")
    print(f"✓ Загружено {len(session.cookies)} cookies")

    # Список гипотез для тестирования
    endpoints = [
        # Гипотеза 1: Тот же endpoint но с interviewType
        {
            "name": "API v1 + interviewType (page=2)",
            "url": "https://easyoffer.ru/api/v1/professions/python-developer/questions/?page=2&interviewType=tehnicheskoe"
        },

        # Гипотеза 2: API v2
        {
            "name": "API v2 (page=2)",
            "url": "https://easyoffer.ru/api/v2/professions/python-developer/questions/?page=2"
        },

        # Гипотеза 3: API v2 + interviewType
        {
            "name": "API v2 + interviewType (page=2)",
            "url": "https://easyoffer.ru/api/v2/professions/python-developer/questions/?page=2&interviewType=tehnicheskoe"
        },

        # Гипотеза 4: Premium endpoint
        {
            "name": "Premium API (page=2)",
            "url": "https://easyoffer.ru/api/v1/premium/questions/?page=2&profession=python-developer"
        },

        # Гипотеза 5: Оригинальный endpoint (для сравнения)
        {
            "name": "API v1 оригинальный (page=1)",
            "url": "https://easyoffer.ru/api/v1/professions/python-developer/questions/?page=1"
        },

        # Гипотеза 6: Оригинальный endpoint (page=2 для проверки)
        {
            "name": "API v1 оригинальный (page=2)",
            "url": "https://easyoffer.ru/api/v1/professions/python-developer/questions/?page=2"
        },
    ]

    results = {}

    # Тестировать каждый endpoint
    for endpoint in endpoints:
        data = test_endpoint(session, endpoint["url"], endpoint["name"])
        results[endpoint["name"]] = {
            "success": data is not None,
            "data": data
        }

    # Итоговый отчет
    print("\n" + "="*70)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("="*70)

    successful = [name for name, result in results.items() if result["success"]]

    if successful:
        print(f"\n✅ Успешные endpoints ({len(successful)}):")
        for name in successful:
            data = results[name]["data"]
            print(f"\n  • {name}")
            print(f"    total_pages: {data.get('total_pages')}, user_limit: {data.get('user_limit')}, results: {len(data.get('results', []))}")
    else:
        print("\n❌ Ни один endpoint не вернул данные")

    # Поиск endpoint с доступом к странице 2
    page2_access = [
        name for name, result in results.items()
        if result["success"] and result["data"].get("current_page") == 2
    ]

    if page2_access:
        print(f"\n🎯 НАЙДЕН ENDPOINT С ДОСТУПОМ К СТРАНИЦЕ 2:")
        for name in page2_access:
            print(f"  • {name}")
            data = results[name]["data"]
            print(f"    URL для адаптации парсера:")
            for endpoint in endpoints:
                if endpoint["name"] == name:
                    print(f"    {endpoint['url'].replace('page=2', 'page={{N}}')}")


if __name__ == "__main__":
    main()
