from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from app.core.menu import main_menu_buttons
from app.core.types import Button


def _main_reply_rows(lang: str = "ru", is_admin: bool = False) -> list[list[str]]:
    rows = [[button.text for button in row] for row in main_menu_buttons(lang=lang, is_admin=is_admin)]
    rows.append(["Меню"])
    return rows


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
        keyboard=[[KeyboardButton(text=label) for label in row] for row in _main_reply_rows()],
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False,
    )
