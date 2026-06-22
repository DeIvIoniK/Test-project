import pytest

from app.services.llm import LLMReplyError, build_rag_messages, generate_support_reply, llm_is_configured


@pytest.mark.asyncio
async def test_generate_support_reply_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    with pytest.raises(LLMReplyError, match="API key"):
        await generate_support_reply("мне тяжело", "ru")


def test_llm_is_configured_when_api_key_exists(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    assert llm_is_configured() is True


def test_build_rag_messages_includes_literature_context_for_relevant_query():
    messages = build_rag_messages("первый шаг бессилие перед алкоголем", "ru")
    system_message = messages[0]["content"]
    user_message = messages[1]["content"]

    assert "без заготовленных поддерживающих шаблонов" in system_message
    assert "Контекст из локальной базы литературы АА" in user_message
    assert "Источник:" in user_message
    assert "Сообщение пользователя" in user_message
