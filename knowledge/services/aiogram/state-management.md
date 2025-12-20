# Управление состоянием Aiogram

> **Назначение**: FSM (Finite State Machine) для диалогов.

---

## Определение состояний

```python
"""Состояния для оформления заказа."""

from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """Состояния процесса заказа."""

    # Выбор ресторана
    waiting_for_restaurant = State()

    # Выбор блюд
    waiting_for_dishes = State()

    # Ввод комментария
    waiting_for_comment = State()

    # Подтверждение
    waiting_for_confirmation = State()


class RegistrationStates(StatesGroup):
    """Состояния регистрации."""

    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
```

---

## Обработчики с состояниями

```python
"""Обработчики с FSM."""

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
    Начать оформление заказа.

    Args:
        message: Входящее сообщение.
        state: Контекст FSM.
    """
    # Установить состояние
    await state.set_state(OrderStates.waiting_for_restaurant)

    # Очистить предыдущие данные
    await state.clear()

    await message.answer(
        "Выберите ресторан:",
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
    Выбрать ресторан.

    Args:
        callback: Callback query.
        state: Контекст FSM.
    """
    restaurant_id = callback.data.split(":")[1]

    # Сохранить данные
    await state.update_data(restaurant_id=restaurant_id)

    # Перейти к следующему состоянию
    await state.set_state(OrderStates.waiting_for_dishes)

    await callback.answer()
    await callback.message.edit_text(
        "Выберите блюда:",
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
    Выбрать блюдо.

    Args:
        callback: Callback query.
        state: Контекст FSM.
    """
    dish_id = callback.data.split(":")[1]

    # Получить текущие данные
    data = await state.get_data()
    dishes = data.get("dishes", [])
    dishes.append(dish_id)

    # Обновить данные
    await state.update_data(dishes=dishes)

    await callback.answer(f"Блюдо добавлено! Всего: {len(dishes)}")


@router.callback_query(
    OrderStates.waiting_for_dishes,
    F.data == "dishes:done",
)
async def finish_dishes(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """
    Завершить выбор блюд.

    Args:
        callback: Callback query.
        state: Контекст FSM.
    """
    await state.set_state(OrderStates.waiting_for_comment)

    await callback.answer()
    await callback.message.edit_text(
        "Введите комментарий к заказу (или отправьте /skip):"
    )


@router.message(OrderStates.waiting_for_comment)
async def receive_comment(message: Message, state: FSMContext) -> None:
    """
    Получить комментарий.

    Args:
        message: Входящее сообщение.
        state: Контекст FSM.
    """
    comment = message.text if message.text != "/skip" else None

    await state.update_data(comment=comment)
    await state.set_state(OrderStates.waiting_for_confirmation)

    # Получить все данные
    data = await state.get_data()

    await message.answer(
        f"Подтвердите заказ:\n"
        f"Ресторан: {data['restaurant_id']}\n"
        f"Блюда: {len(data['dishes'])} шт.\n"
        f"Комментарий: {comment or 'нет'}",
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
    Подтвердить заказ.

    Args:
        callback: Callback query.
        state: Контекст FSM.
        api_client: HTTP клиент.
    """
    # Получить данные
    data = await state.get_data()

    # Создать заказ через API
    order = await api_client.create_order(
        user_id=callback.from_user.id,
        restaurant_id=data["restaurant_id"],
        dishes=data["dishes"],
        comment=data.get("comment"),
    )

    # Очистить состояние
    await state.clear()

    await callback.answer("Заказ создан!")
    await callback.message.edit_text(
        f"✅ Заказ #{order['id']} успешно создан!"
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
    Отменить заказ.

    Args:
        callback: Callback query.
        state: Контекст FSM.
    """
    await state.clear()

    await callback.answer("Заказ отменён")
    await callback.message.edit_text("❌ Заказ отменён.")
```

---

## Хранилище состояний

```python
"""Настройка хранилища состояний."""

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage


# Для разработки — в памяти
storage = MemoryStorage()

# Для production — Redis
# storage = RedisStorage.from_url("redis://localhost:6379/0")

dp = Dispatcher(storage=storage)
```

---

## Отмена в любой момент

```python
"""Глобальная отмена."""

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()


@router.message(Command("cancel"), StateFilter("*"))
@router.message(F.text.casefold() == "отмена", StateFilter("*"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Отменить текущее действие.

    Args:
        message: Входящее сообщение.
        state: Контекст FSM.
    """
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Нечего отменять.")
        return

    await state.clear()
    await message.answer(
        "Действие отменено. Выберите команду из меню.",
        reply_markup=get_main_keyboard(),
    )
```

---

## Диаграмма состояний

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

## Чек-лист

- [ ] Состояния определены в StatesGroup
- [ ] Данные сохраняются через state.update_data()
- [ ] Переходы через state.set_state()
- [ ] Глобальная отмена настроена
- [ ] Хранилище выбрано (Memory/Redis)
