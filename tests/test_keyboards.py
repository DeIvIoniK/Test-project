from app.bot.keyboards import inline_keyboard, main_reply_keyboard
from app.core.types import Button


def test_inline_keyboard_uses_real_telegram_buttons():
    markup = inline_keyboard([[Button("Понимаю и принимаю", "accept_rules")]])

    assert markup.inline_keyboard[0][0].text == "Понимаю и принимаю"
    assert markup.inline_keyboard[0][0].callback_data == "accept_rules"


def test_main_reply_keyboard_contains_persistent_main_actions():
    markup = main_reply_keyboard()
    labels = [button.text for row in markup.keyboard for button in row]

    assert "Просто выговориться" in labels
    assert "Мне плохо / хочу сорваться" in labels
    assert "Связаться с человеком" in labels
    assert "Я новичок" in labels
    assert "Литература" in labels
    assert "Меню" in labels
    assert markup.resize_keyboard is True
    assert markup.is_persistent is True
    assert markup.one_time_keyboard is False
