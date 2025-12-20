# Паттерны обработчиков Aiogram

> **Назначение**: Организация обработчиков сообщений.

---

## Базовый роутер

```python
"""Обработчики команд."""

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Обработать /start."""
    await message.answer("Привет! Я бот для бронирования.")


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Обработать /help."""
    await message.answer(
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Помощь\n"
        "/menu - Главное меню"
    )
```

---

## Фильтры сообщений

```python
"""Различные фильтры сообщений."""

from aiogram import Router, F
from aiogram.types import Message

router = Router()


# Текстовые сообщения
@router.message(F.text == "Меню")
async def menu_text_handler(message: Message) -> None:
    """Обработать текст 'Меню'."""
    await message.answer("Открываю меню...")


# Содержит текст
@router.message(F.text.contains("привет"))
async def hello_handler(message: Message) -> None:
    """Обработать сообщение с 'привет'."""
    await message.answer("Привет!")


# Регулярное выражение
@router.message(F.text.regexp(r"^\d{4}$"))
async def code_handler(message: Message) -> None:
    """Обработать 4-значный код."""
    code = message.text
    await message.answer(f"Получен код: {code}")


# Фото
@router.message(F.photo)
async def photo_handler(message: Message) -> None:
    """Обработать фото."""
    await message.answer("Фото получено!")


# Документ
@router.message(F.document)
async def document_handler(message: Message) -> None:
    """Обработать документ."""
    await message.answer(f"Документ: {message.document.file_name}")
```

---

## Callback обработчики

```python
"""Обработчики callback query."""

from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


# Точное совпадение
@router.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery) -> None:
    """Обработать нажатие кнопки 'menu'."""
    await callback.answer()
    await callback.message.edit_text("Главное меню")


# Префикс
@router.callback_query(F.data.startswith("order:"))
async def order_callback(callback: CallbackQuery) -> None:
    """Обработать callback заказа."""
    order_id = callback.data.split(":")[1]
    await callback.answer()
    await callback.message.edit_text(f"Заказ: {order_id}")


# Кастомный фильтр
class OrderCallbackData:
    """Фильтр для callback заказов."""

    def __init__(self, action: str):
        self.action = action

    def __call__(self, callback: CallbackQuery) -> bool:
        if not callback.data:
            return False
        parts = callback.data.split(":")
        return len(parts) >= 2 and parts[0] == "order" and parts[1] == self.action


@router.callback_query(OrderCallbackData("confirm"))
async def confirm_order(callback: CallbackQuery) -> None:
    """Подтвердить заказ."""
    await callback.answer("Заказ подтверждён!")
```

---

## Callback Data Factory

```python
"""Использование CallbackData."""

from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


class OrderAction(CallbackData, prefix="order"):
    """Callback data для действий с заказом."""

    action: str
    order_id: int


router = Router()


def get_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру заказа.

    Args:
        order_id: ID заказа.

    Returns:
        Inline клавиатура.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=OrderAction(
                        action="confirm",
                        order_id=order_id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data=OrderAction(
                        action="cancel",
                        order_id=order_id,
                    ).pack(),
                ),
            ],
        ],
    )


@router.callback_query(OrderAction.filter(F.action == "confirm"))
async def confirm_order(
    callback: CallbackQuery,
    callback_data: OrderAction,
) -> None:
    """
    Подтвердить заказ.

    Args:
        callback: Callback query.
        callback_data: Распарсенные данные.
    """
    await callback.answer("Подтверждаю...")
    await callback.message.edit_text(
        f"Заказ #{callback_data.order_id} подтверждён!"
    )


@router.callback_query(OrderAction.filter(F.action == "cancel"))
async def cancel_order(
    callback: CallbackQuery,
    callback_data: OrderAction,
) -> None:
    """
    Отменить заказ.

    Args:
        callback: Callback query.
        callback_data: Распарсенные данные.
    """
    await callback.answer("Отменяю...")
    await callback.message.edit_text(
        f"Заказ #{callback_data.order_id} отменён!"
    )
```

---

## Доступ к зависимостям

```python
"""Доступ к зависимостям через workflow_data."""

from aiogram import Router
from aiogram.types import Message

from {context}_bot.infrastructure.http.business_api_client import BusinessApiClient

router = Router()


@router.message(Command("orders"))
async def list_orders(
    message: Message,
    api_client: BusinessApiClient,  # Инъекция из workflow_data
) -> None:
    """
    Показать список заказов.

    Args:
        message: Входящее сообщение.
        api_client: HTTP клиент.
    """
    user_id = message.from_user.id
    orders = await api_client.get_user_orders(user_id)

    if not orders:
        await message.answer("У вас нет заказов.")
        return

    text = "Ваши заказы:\n\n"
    for order in orders:
        text += f"• #{order['id']} - {order['status']}\n"

    await message.answer(text)
```

---

## Организация роутеров

```python
"""Организация роутеров по модулям."""

# handlers/__init__.py
from aiogram import Router

from . import start, menu, orders, profile

# Главный роутер
main_router = Router()

# Подключение модулей
main_router.include_router(start.router)
main_router.include_router(menu.router)
main_router.include_router(orders.router)
main_router.include_router(profile.router)


# main.py
from handlers import main_router

dp = Dispatcher()
dp.include_router(main_router)
```

---

## Правила

| Элемент | Файл | Пример |
|---------|------|--------|
| Команды | `start.py` | /start, /help |
| Меню | `menu.py` | Главное меню |
| Фича | `{feature}_handlers.py` | orders_handlers.py |
| Callback | В том же файле | order:confirm |
