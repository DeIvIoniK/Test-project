from app.core.types import Button


def main_menu_buttons(lang: str = "ru", is_admin: bool = False) -> list[list[Button]]:
    if lang != "ru":
        buttons = [
            [Button("Just talk", "talk"), Button("I feel bad / craving", "sos")],
            [Button("Contact a person", "contact"), Button("I'm new", "newcomer")],
            [Button("Find a group", "groups"), Button("Literature", "literature")],
            [Button("Speaker talks / audio", "audio"), Button("Sobriety days", "sobriety")],
            [Button("Help another", "helper"), Button("Support the project", "donate")],
            [Button("About", "about"), Button("Settings", "settings")],
        ]
        if is_admin:
            buttons.append([Button("Admin", "admin")])
        return buttons

    buttons = [
        [Button("Просто выговориться", "talk"), Button("Мне плохо / хочу сорваться", "sos")],
        [Button("Связаться с человеком", "contact"), Button("Я новичок", "newcomer")],
        [Button("Найти группу", "groups"), Button("Литература", "literature")],
        [Button("Спикерские / аудио", "audio"), Button("Дни трезвости", "sobriety")],
        [Button("Помочь другому", "helper"), Button("Поддержать проект", "donate")],
        [Button("О проекте", "about"), Button("Настройки", "settings")],
    ]
    if is_admin:
        buttons.append([Button("Админ", "admin")])
    return buttons
