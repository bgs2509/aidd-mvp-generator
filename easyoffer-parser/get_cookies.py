"""
Утилита для автоматического получения cookies с easyoffer.ru
Использует Playwright для открытия браузера и авторизации через Telegram
"""

import json
from playwright.sync_api import sync_playwright


def get_cookies_interactive():
    """
    Интерактивное получение cookies через Playwright

    Пользователь вручную авторизуется через Telegram,
    затем cookies автоматически сохраняются в cookies.json
    """
    print("=" * 60)
    print("ПОЛУЧЕНИЕ COOKIES С EASYOFFER.RU")
    print("=" * 60)
    print("\nСейчас откроется браузер. Выполните следующие шаги:")
    print("1. Нажмите кнопку 'Войти через Telegram'")
    print("2. Авторизуйтесь в Telegram")
    print("3. Дождитесь полной загрузки страницы после авторизации")
    print("4. Вернитесь в терминал и нажмите Enter\n")

    with sync_playwright() as p:
        # Запустить браузер (headless=False для визуального контроля)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Перейти на сайт
        print("▶ Открываем https://easyoffer.ru...")
        page.goto("https://easyoffer.ru")

        # Ждать пока пользователь авторизуется
        input("\n✋ Выполните авторизацию в открытом браузере, затем нажмите Enter...")

        # Получить все cookies
        cookies = context.cookies()

        # Закрыть браузер
        browser.close()

        # Проверка, что есть cookies
        if not cookies:
            print("❌ Cookies не найдены! Возможно, авторизация не была выполнена.")
            return False

        # Сохранить cookies в JSON
        output_file = "cookies.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Успешно сохранено {len(cookies)} cookies в {output_file}")
        print("\nТеперь вы можете запустить парсер:")
        print("  python parser.py")

        return True


def get_cookies_manual_instructions():
    """Вывести инструкции для ручного получения cookies"""
    print("\n" + "=" * 60)
    print("ИНСТРУКЦИЯ ДЛЯ РУЧНОГО ПОЛУЧЕНИЯ COOKIES")
    print("=" * 60)
    print("""
1. Откройте браузер (Chrome/Firefox) и перейдите на:
   https://easyoffer.ru

2. Откройте DevTools (F12 или Ctrl+Shift+I)

3. Авторизуйтесь через Telegram:
   - Нажмите кнопку "Войти через Telegram"
   - Подтвердите авторизацию

4. В DevTools перейдите на вкладку:
   Application → Cookies → https://easyoffer.ru

5. Скопируйте все cookies в формате JSON:

   Пример структуры:
   [
     {
       "name": "sessionid",
       "value": "YOUR_SESSION_ID",
       "domain": ".easyoffer.ru",
       "path": "/",
       "expires": 1234567890,
       "httpOnly": true,
       "secure": true,
       "sameSite": "Lax"
     }
   ]

6. Сохраните в файл cookies.json в директории проекта

7. Запустите парсер:
   python parser.py
""")


def verify_cookies():
    """Проверить существующий файл cookies.json"""
    import os

    if not os.path.exists("cookies.json"):
        print("❌ Файл cookies.json не найден!")
        return False

    try:
        with open("cookies.json", 'r', encoding='utf-8') as f:
            cookies = json.load(f)

        print(f"✓ Файл cookies.json найден ({len(cookies)} cookies)")

        # Показать ключевые cookies
        important_cookies = ['sessionid', 'csrftoken', '_ga']
        found_important = []

        for cookie in cookies:
            if cookie.get('name') in important_cookies:
                found_important.append(cookie['name'])

        if found_important:
            print(f"✓ Найдены важные cookies: {', '.join(found_important)}")
        else:
            print("⚠️ Не найдены стандартные cookies (sessionid, csrftoken)")
            print("   Возможно, требуется повторная авторизация")

        return True

    except json.JSONDecodeError:
        print("❌ Ошибка чтения cookies.json — неверный формат JSON")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке cookies: {e}")
        return False


def main():
    """Основная функция с интерактивным меню"""
    print("\n" + "=" * 60)
    print("УТИЛИТА ПОЛУЧЕНИЯ COOKIES — EASYOFFER.RU")
    print("=" * 60)

    # Проверить, существует ли уже файл cookies.json
    if verify_cookies():
        print("\n⚠️ Файл cookies.json уже существует!")
        choice = input("Перезаписать? (y/N): ").lower()
        if choice != 'y':
            print("Операция отменена")
            return

    print("\nВыберите способ получения cookies:")
    print("1. Автоматически через браузер (Playwright) [Рекомендуется]")
    print("2. Показать инструкцию для ручного получения")
    print("3. Выход")

    choice = input("\nВаш выбор (1-3): ").strip()

    if choice == '1':
        try:
            success = get_cookies_interactive()
            if not success:
                print("\n⚠️ Попробуйте ещё раз или используйте ручной способ (опция 2)")
        except ImportError:
            print("\n❌ Ошибка: Playwright не установлен!")
            print("\nУстановите с помощью:")
            print("  pip install playwright")
            print("  playwright install chromium")
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()

    elif choice == '2':
        get_cookies_manual_instructions()

    elif choice == '3':
        print("Выход")

    else:
        print("❌ Неверный выбор")


if __name__ == "__main__":
    main()
