from app.core.types import Button


def onboarding_start_text(lang: str = "ru") -> str:
    if lang != "ru":
        return (
            "Hi. I can listen and help you take the next safe step.\n\n"
            "If you need support right now, press the button below."
        )
    return (
        "Привет. Я могу выслушать и помочь сделать ближайший безопасный шаг.\n\n"
        "Если тебе плохо прямо сейчас — нажми кнопку ниже."
    )


def rules_text(lang: str = "ru") -> str:
    if lang != "ru":
        return (
            "Short rules: I am not a doctor, therapist, emergency service, or official AA representative. "
            "I do not give medical instructions. Dialogues are not stored longer than 30 minutes."
        )
    return (
        "Короткие правила: я не врач, не психолог, не экстренная служба и не официальный представитель АА. "
        "Я не даю медицинских назначений. Диалоги не хранятся дольше 30 минут."
    )


def onboarding_buttons(lang: str = "ru") -> list[list[Button]]:
    if lang != "ru":
        return [
            [Button("I need urgent support", "sos")],
            [Button("I understand and accept", "accept_rules")],
        ]
    return [
        [Button("Мне срочно нужна поддержка", "sos")],
        [Button("Понимаю и принимаю", "accept_rules")],
    ]
