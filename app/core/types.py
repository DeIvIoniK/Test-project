from dataclasses import dataclass


@dataclass(frozen=True)
class Button:
    text: str
    callback_data: str | None = None


@dataclass(frozen=True)
class BotReply:
    text: str
    buttons: list[list[Button]]
