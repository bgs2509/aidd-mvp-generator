# Aiogram State Management

> **Purpose**: FSM (Finite State Machine) for dialogs.

---

## Defining States

```python
"""States for order placement."""

from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """Order process states."""

    # Restaurant selection
    waiting_for_restaurant = State()

    # Dish selection
    waiting_for_dishes = State()

    # Comment input
    waiting_for_comment = State()

    # Confirmation
    waiting_for_confirmation = State()


class RegistrationStates(StatesGroup):
    """Registration states."""

    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
```

---

## Handlers with States

```python
"""Handlers with FSM."""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from {context}_bot.states.order import OrderStates
from {context}_bot.keyboards.order import (
    get_restaurants_keyboard,
    get_dishes_keyboard,
    get_confirmation_keyboard,
)

router = Router()


@router.message(Command("order"))
async def start_order(message: Message, state: FSMContext) -> None:
    """
    Start order placement.

    Args:
        message: Incoming message.
        state: FSM context.
    """
    # Set state
    await state.set_state(OrderStates.waiting_for_restaurant)

    # Clear previous data
    await state.clear()

    await message.answer(
        "Select a restaurant:",
        reply_markup=get_restaurants_keyboard(),
    )


@router.callback_query(
    OrderStates.waiting_for_restaurant,
    F.data.startswith("restaurant:"),
)
async def select_restaurant(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """
    Select a restaurant.

    Args:
        callback: Callback query.
        state: FSM context.
    """
    restaurant_id = callback.data.split(":")[1]

    # Save data
    await state.update_data(restaurant_id=restaurant_id)

    # Transition to next state
    await state.set_state(OrderStates.waiting_for_dishes)

    await callback.answer()
    await callback.message.edit_text(
        "Select dishes:",
        reply_markup=get_dishes_keyboard(restaurant_id),
    )


@router.callback_query(
    OrderStates.waiting_for_dishes,
    F.data.startswith("dish:"),
)
async def select_dish(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """
    Select a dish.

    Args:
        callback: Callback query.
        state: FSM context.
    """
    dish_id = callback.data.split(":")[1]

    # Get current data
    data = await state.get_data()
    dishes = data.get("dishes", [])
    dishes.append(dish_id)

    # Update data
    await state.update_data(dishes=dishes)

    await callback.answer(f"Dish added! Total: {len(dishes)}")


@router.callback_query(
    OrderStates.waiting_for_dishes,
    F.data == "dishes:done",
)
async def finish_dishes(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """
    Finish dish selection.

    Args:
        callback: Callback query.
        state: FSM context.
    """
    await state.set_state(OrderStates.waiting_for_comment)

    await callback.answer()
    await callback.message.edit_text(
        "Enter a comment for the order (or send /skip):"
    )


@router.message(OrderStates.waiting_for_comment)
async def receive_comment(message: Message, state: FSMContext) -> None:
    """
    Receive comment.

    Args:
        message: Incoming message.
        state: FSM context.
    """
    comment = message.text if message.text != "/skip" else None

    await state.update_data(comment=comment)
    await state.set_state(OrderStates.waiting_for_confirmation)

    # Get all data
    data = await state.get_data()

    await message.answer(
        f"Confirm your order:\n"
        f"Restaurant: {data['restaurant_id']}\n"
        f"Dishes: {len(data['dishes'])} items\n"
        f"Comment: {comment or 'none'}",
        reply_markup=get_confirmation_keyboard(),
    )


@router.callback_query(
    OrderStates.waiting_for_confirmation,
    F.data == "order:confirm",
)
async def confirm_order(
    callback: CallbackQuery,
    state: FSMContext,
    api_client: BusinessApiClient,
) -> None:
    """
    Confirm the order.

    Args:
        callback: Callback query.
        state: FSM context.
        api_client: HTTP client.
    """
    # Get data
    data = await state.get_data()

    # Create order via API
    order = await api_client.create_order(
        user_id=callback.from_user.id,
        restaurant_id=data["restaurant_id"],
        dishes=data["dishes"],
        comment=data.get("comment"),
    )

    # Clear state
    await state.clear()

    await callback.answer("Order created!")
    await callback.message.edit_text(
        f"Order #{order['id']} successfully created!"
    )


@router.callback_query(
    OrderStates.waiting_for_confirmation,
    F.data == "order:cancel",
)
async def cancel_order(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """
    Cancel the order.

    Args:
        callback: Callback query.
        state: FSM context.
    """
    await state.clear()

    await callback.answer("Order cancelled")
    await callback.message.edit_text("Order cancelled.")
```

---

## State Storage

```python
"""State storage configuration."""

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage


# For development — in-memory
storage = MemoryStorage()

# For production — Redis
# storage = RedisStorage.from_url("redis://localhost:6379/0")

dp = Dispatcher(storage=storage)
```

---

## Cancel at Any Time

```python
"""Global cancellation."""

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()


@router.message(Command("cancel"), StateFilter("*"))
@router.message(F.text.casefold() == "cancel", StateFilter("*"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Cancel current action.

    Args:
        message: Incoming message.
        state: FSM context.
    """
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Nothing to cancel.")
        return

    await state.clear()
    await message.answer(
        "Action cancelled. Choose a command from the menu.",
        reply_markup=get_main_keyboard(),
    )
```

---

## State Diagram

```
[*] --> waiting_for_restaurant: /order

waiting_for_restaurant --> waiting_for_dishes: restaurant:{id}

waiting_for_dishes --> waiting_for_dishes: dish:{id}
waiting_for_dishes --> waiting_for_comment: dishes:done

waiting_for_comment --> waiting_for_confirmation: (text)

waiting_for_confirmation --> [*]: order:confirm
waiting_for_confirmation --> [*]: order:cancel

* --> [*]: /cancel
```

---

## Checklist

- [ ] States defined in StatesGroup
- [ ] Data saved via state.update_data()
- [ ] Transitions via state.set_state()
- [ ] Global cancellation configured
- [ ] Storage selected (Memory/Redis)
