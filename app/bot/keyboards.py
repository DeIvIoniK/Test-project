from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from app.core.types import Button


MAIN_REPLY_ROWS = [
    ["Просто выговориться", "Мне плохо / хочу сорваться"],
    ["Связаться с человеком", "Я новичок"],
    ["Литература", "Меню"],
]


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
        keyboard=[[KeyboardButton(text=label) for label in row] for row in MAIN_REPLY_ROWS],
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False,
    )
