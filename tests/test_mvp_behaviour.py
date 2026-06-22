from datetime import datetime, timedelta, timezone

from app.core.crisis import is_crisis_text, crisis_reply
from app.core.onboarding import onboarding_buttons, onboarding_start_text, rules_text
from app.core.menu import main_menu_buttons
from app.core.privacy import should_delete_dialogue
from app.core.prompts import build_support_system_prompt


def test_main_menu_contains_required_mvp_buttons():
    buttons = main_menu_buttons(lang="ru", is_admin=False)
    labels = [button.text for row in buttons for button in row]

    assert "Просто выговориться" in labels
    assert "Мне плохо / хочу сорваться" in labels
    assert "Связаться с человеком" in labels
    assert "Я новичок" in labels
    assert "Настройки" in labels


def test_admin_button_visible_only_for_admin():
    user_labels = [button.text for row in main_menu_buttons(lang="ru", is_admin=False) for button in row]
    admin_labels = [button.text for row in main_menu_buttons(lang="ru", is_admin=True) for button in row]

    assert "Админ" not in user_labels
    assert "Админ" in admin_labels


def test_onboarding_has_urgent_support_and_acceptance():
    text = onboarding_start_text(lang="ru") + "\n" + rules_text(lang="ru")
    labels = [button.text for row in onboarding_buttons(lang="ru") for button in row]

    assert "Мне срочно нужна поддержка" in labels
    assert "Понимаю и принимаю" in labels
    assert "Кнопка:" not in text
    assert "не врач" in text.lower()
    assert "не экстренная служба" in text.lower()
    assert "30 минут" in text


def test_crisis_detection_catches_high_risk_phrases():
    assert is_crisis_text("я хочу умереть") is True
    assert is_crisis_text("кажется передозировка") is True
    assert is_crisis_text("очень сильная ломка и страшно") is True
    assert is_crisis_text("мне стыдно и хочется выговориться") is False


def test_crisis_reply_is_short_one_question_and_has_human_contact_button():
    reply = crisis_reply(lang="ru")

    assert len(reply.text) < 420
    assert reply.text.count("?") == 1
    assert "Я не могу обеспечить твою безопасность один" in reply.text
    labels = [button.text for row in reply.buttons for button in row]
    assert "Связаться с человеком" in labels


def test_dialogue_context_expires_after_30_minutes_inactivity():
    now = datetime(2026, 1, 1, 12, 31, tzinfo=timezone.utc)
    old = now - timedelta(minutes=31)
    fresh = now - timedelta(minutes=10)

    assert should_delete_dialogue(old, now=now) is True
    assert should_delete_dialogue(fresh, now=now) is False


def test_support_prompt_contains_safety_boundaries():
    prompt = build_support_system_prompt(lang="ru")

    assert "не врач" in prompt.lower()
    assert "не психолог" in prompt.lower()
    assert "не давай медицинских назначений" in prompt.lower()
    assert "не спорь" in prompt.lower()
    assert "один вопрос за раз" in prompt.lower()
