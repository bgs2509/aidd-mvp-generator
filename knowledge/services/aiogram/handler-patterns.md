# Aiogram Handler Patterns

> **Purpose**: Organizing message handlers.

---

## Basic Router

```python
"""Command handlers."""

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Handle /start."""
    await message.answer("Hello! I'm a booking bot.")


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Handle /help."""
    await message.answer(
        "Available commands:\n"
        "/start - Get started\n"
        "/help - Help\n"
        "/menu - Main menu"
    )
```

---

## Message Filters

```python
"""Various message filters."""

from aiogram import Router, F
from aiogram.types import Message

router = Router()


# Text messages
@router.message(F.text == "Menu")
async def menu_text_handler(message: Message) -> None:
    """Handle text 'Menu'."""
    await message.answer("Opening menu...")


# Contains text
@router.message(F.text.contains("hello"))
async def hello_handler(message: Message) -> None:
    """Handle message containing 'hello'."""
    await message.answer("Hello!")


# Regular expression
@router.message(F.text.regexp(r"^\d{4}$"))
async def code_handler(message: Message) -> None:
    """Handle 4-digit code."""
    code = message.text
    await message.answer(f"Code received: {code}")


# Photo
@router.message(F.photo)
async def photo_handler(message: Message) -> None:
    """Handle photo."""
    await message.answer("Photo received!")


# Document
@router.message(F.document)
async def document_handler(message: Message) -> None:
    """Handle document."""
    await message.answer(f"Document: {message.document.file_name}")
```

---

## Callback Handlers

```python
"""Callback query handlers."""

from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


# Exact match
@router.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery) -> None:
    """Handle 'menu' button press."""
    await callback.answer()
    await callback.message.edit_text("Main menu")


# Prefix
@router.callback_query(F.data.startswith("order:"))
async def order_callback(callback: CallbackQuery) -> None:
    """Handle order callback."""
    order_id = callback.data.split(":")[1]
    await callback.answer()
    await callback.message.edit_text(f"Order: {order_id}")


# Custom filter
class OrderCallbackData:
    """Filter for order callbacks."""

    def __init__(self, action: str):
        self.action = action

    def __call__(self, callback: CallbackQuery) -> bool:
        if not callback.data:
            return False
        parts = callback.data.split(":")
        return len(parts) >= 2 and parts[0] == "order" and parts[1] == self.action


@router.callback_query(OrderCallbackData("confirm"))
async def confirm_order(callback: CallbackQuery) -> None:
    """Confirm order."""
    await callback.answer("Order confirmed!")
```

---

## Callback Data Factory

```python
"""Using CallbackData."""

from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


class OrderAction(CallbackData, prefix="order"):
    """Callback data for order actions."""

    action: str
    order_id: int


router = Router()


def get_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """
    Create order keyboard.

    Args:
        order_id: Order ID.

    Returns:
        Inline keyboard.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Confirm",
                    callback_data=OrderAction(
                        action="confirm",
                        order_id=order_id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="Cancel",
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
    Confirm order.

    Args:
        callback: Callback query.
        callback_data: Parsed data.
    """
    await callback.answer("Confirming...")
    await callback.message.edit_text(
        f"Order #{callback_data.order_id} confirmed!"
    )


@router.callback_query(OrderAction.filter(F.action == "cancel"))
async def cancel_order(
    callback: CallbackQuery,
    callback_data: OrderAction,
) -> None:
    """
    Cancel order.

    Args:
        callback: Callback query.
        callback_data: Parsed data.
    """
    await callback.answer("Cancelling...")
    await callback.message.edit_text(
        f"Order #{callback_data.order_id} cancelled!"
    )
```

---

## Accessing Dependencies

```python
"""Accessing dependencies via workflow_data."""

from aiogram import Router
from aiogram.types import Message

from {context}_bot.infrastructure.http.business_api_client import BusinessApiClient

router = Router()


@router.message(Command("orders"))
async def list_orders(
    message: Message,
    api_client: BusinessApiClient,  # Injected from workflow_data
) -> None:
    """
    Show order list.

    Args:
        message: Incoming message.
        api_client: HTTP client.
    """
    user_id = message.from_user.id
    orders = await api_client.get_user_orders(user_id)

    if not orders:
        await message.answer("You have no orders.")
        return

    text = "Your orders:\n\n"
    for order in orders:
        text += f"- #{order['id']} - {order['status']}\n"

    await message.answer(text)
```

---

## Router Organization

```python
"""Organizing routers by module."""

# handlers/__init__.py
from aiogram import Router

from . import start, menu, orders, profile

# Main router
main_router = Router()

# Include modules
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

## Rules

| Element | File | Example |
|---------|------|---------|
| Commands | `start.py` | /start, /help |
| Menu | `menu.py` | Main menu |
| Feature | `{feature}_handlers.py` | orders_handlers.py |
| Callback | Same file | order:confirm |
