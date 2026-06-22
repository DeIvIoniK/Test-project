from app.core.types import BotReply, Button

_CRISIS_MARKERS = (
    "хочу умереть", "убить себя", "суицид", "передоз", "передозировка",
    "ломка", "абстинен", "насили", "угроза жизни", "не хочу жить",
)


def is_crisis_text(text: str) -> bool:
    normalized = text.lower().replace("ё", "е")
    return any(marker in normalized for marker in _CRISIS_MARKERS)


def crisis_reply(lang: str = "ru") -> BotReply:
    if lang != "ru":
        return BotReply(
            text=(
                "I’m here. I can’t keep you safe on my own. "
                "If there is immediate danger, call emergency services or ask someone nearby to stay with you. "
                "Are you in immediate danger right now?"
            ),
            buttons=[[Button("Contact a person", "contact")]],
        )
    return BotReply(
        text=(
            "Я рядом. Я не могу обеспечить твою безопасность один. "
            "Если есть непосредственная опасность — позвони в экстренную службу или попроси человека рядом побыть с тобой. "
            "Ты сейчас в непосредственной опасности?"
        ),
        buttons=[[Button("Связаться с человеком", "contact")]],
    )
