from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from app.core.types import Button


def inline_keyboard(buttons: list[list[Button]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=button.text,
                    callback_data=button.callback_data or button.text,
                )
                for button in row
            ]
            for row in buttons
        ]
    )


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Меню")]],
        resize_keyboard=True,
        is_persistent=True,
    )
