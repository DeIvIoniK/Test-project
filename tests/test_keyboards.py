from app.bot.keyboards import inline_keyboard, main_reply_keyboard
from app.core.types import Button


def test_inline_keyboard_uses_real_telegram_buttons():
    markup = inline_keyboard([[Button("Понимаю и принимаю", "accept_rules")]])

    assert markup.inline_keyboard[0][0].text == "Понимаю и принимаю"
    assert markup.inline_keyboard[0][0].callback_data == "accept_rules"


def test_main_reply_keyboard_contains_persistent_menu_button():
    markup = main_reply_keyboard()

    assert markup.keyboard[0][0].text == "Меню"
    assert markup.resize_keyboard is True
    assert markup.is_persistent is True
