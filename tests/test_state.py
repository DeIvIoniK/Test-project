from app.bot.state import get_chat_mode, is_support_dialogue_mode, is_talk_mode, set_chat_mode


def test_chat_mode_defaults_to_menu_and_can_switch_to_talk():
    chat_id = 123456

    assert get_chat_mode(chat_id) == "menu"
    assert is_talk_mode(chat_id) is False

    set_chat_mode(chat_id, "talk")

    assert get_chat_mode(chat_id) == "talk"
    assert is_talk_mode(chat_id) is True
    assert is_support_dialogue_mode(chat_id) is True


def test_sos_mode_accepts_voice_dialogue_like_talk_mode():
    chat_id = 123457

    set_chat_mode(chat_id, "sos")

    assert get_chat_mode(chat_id) == "sos"
    assert is_talk_mode(chat_id) is False
    assert is_support_dialogue_mode(chat_id) is True
