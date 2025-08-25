from aiogram.fsm.state import State, StatesGroup


class AddCoin(StatesGroup):
    """Состояния для добавления монеты"""
    waiting_for_symbol = State()
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_quantity = State()
    waiting_for_confirmation = State() 