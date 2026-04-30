from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    name = State()
    notifications = State()
    change_name = State()
    change_notifications = State()
