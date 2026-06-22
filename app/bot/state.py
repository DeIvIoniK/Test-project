from collections import defaultdict

_CHAT_MODES: dict[int, str] = defaultdict(lambda: "menu")
_SUPPORT_DIALOGUE_MODES = {"talk", "sos"}


def set_chat_mode(chat_id: int, mode: str) -> None:
    _CHAT_MODES[chat_id] = mode


def get_chat_mode(chat_id: int) -> str:
    return _CHAT_MODES[chat_id]


def is_talk_mode(chat_id: int) -> bool:
    return get_chat_mode(chat_id) == "talk"


def is_support_dialogue_mode(chat_id: int) -> bool:
    return get_chat_mode(chat_id) in _SUPPORT_DIALOGUE_MODES
