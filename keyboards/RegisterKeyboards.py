from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_skip_notifications_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Настроить позже", callback_data="get_profile", style="primary")
    )
    return builder
