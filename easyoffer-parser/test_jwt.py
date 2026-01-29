#!/usr/bin/env python3
"""
Быстрый тест доступа к странице 2 с JWT токеном
"""

from parser import EasyOfferParser
import os

# Загрузить JWT
if not os.path.exists("jwt_token.txt"):
    print("❌ jwt_token.txt не найден!")
    exit(1)

with open("jwt_token.txt", 'r') as f:
    jwt_token = f.read().strip()

parser = EasyOfferParser(
    cookies_file="cookies.json",
    jwt_token=jwt_token
)

# Проверка страницы 1
print("\n=== ТЕСТ: Страница 1 (контроль) ===")
data1 = parser.fetch_page(1)
if data1 and 'results' in data1:
    print(f"✅ Страница 1: {len(data1['results'])} вопросов")
    print(f"  • total_pages: {data1.get('total_pages')}")
    print(f"  • user_limit: {data1.get('user_limit')}")
else:
    print("❌ ОШИБКА: Страница 1 недоступна")

# Проверка страницы 2
print("\n=== ТЕСТ: Страница 2 (ГЛАВНЫЙ ТЕСТ) ===")
data2 = parser.fetch_page(2)

if data2 and 'results' in data2:
    print(f"✅ УСПЕХ! Страница 2 доступна!")
    print(f"  • current_page: {data2.get('current_page')}")
    print(f"  • total_pages: {data2.get('total_pages')}")
    print(f"  • user_limit: {data2.get('user_limit')}")
    print(f"  • Вопросов на странице: {len(data2['results'])}")

    if data2['results']:
        first_q = data2['results'][0]
        print(f"  • Первый вопрос: {first_q.get('title', 'N/A')[:60]}...")
        print(f"  • Шанс: {round(first_q.get('frequency', 0) * 100, 2)}%")
else:
    print("❌ ОШИБКА: Страница 2 недоступна")

print("\n" + "="*70)
if data2 and data2.get('total_pages', 0) > 1:
    print("🎉 JWT ТОКЕН РАБОТАЕТ! Можно запускать полный парсинг.")
    print(f"Доступно страниц: {data2.get('total_pages')}")
else:
    print("⚠️ Проблема сохраняется. Нужна дополнительная диагностика.")
