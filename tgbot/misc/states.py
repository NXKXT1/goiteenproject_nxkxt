from aiogram.dispatcher.filters.state import StatesGroup, State


class MyForm(StatesGroup):
    reminder_datetime = State()
    translator = State()
    reminder_on = State()

