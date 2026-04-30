from aiogram.fsm.state import StatesGroup, State


class TaskStates(StatesGroup):
    voice_message = State()
