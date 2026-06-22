import os

import httpx

from app.core.prompts import build_support_system_prompt
from app.services.literature import format_literature_context, search_literature


class LLMReplyError(RuntimeError):
    """Raised when the support reply cannot be generated through the LLM API."""


def _api_key() -> str:
    return os.getenv("OPENROUTER_API_KEY") or os.getenv("LLM_API_KEY") or ""


def llm_is_configured() -> bool:
    return bool(_api_key())


def build_rag_messages(user_text: str, lang: str = "ru") -> list[dict[str, str]]:
    hits = search_literature(user_text, limit=4)
    literature_context = format_literature_context(hits, max_chars=2400)
    system_prompt = (
        build_support_system_prompt(lang)
        + " Ты отвечаешь только через LLM, без заготовленных поддерживающих шаблонов. "
        + "Каждый ответ должен быть живым и конкретным к сообщению пользователя: 1-3 коротких предложения. "
        + "Обязательно учитывай локальную базу литературы АА ниже, если найденный контекст релевантен. "
        + "Не цитируй длинно, не выдумывай источники, не давай медицинских советов. "
        + "Если уместно, кратко упомяни источник вроде: «В литературе АА есть такая опора…». "
        + "Если контекст не подходит, скажи человечески и поддерживающе, не имитируя цитату."
    )
    user_content = user_text[:2000]
    if literature_context:
        user_content = (
            "Контекст из локальной базы литературы АА:\n"
            f"{literature_context}\n\n"
            "Сообщение пользователя:\n"
            f"{user_text[:2000]}"
        )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]


async def generate_support_reply(user_text: str, lang: str = "ru") -> str:
    api_key = _api_key()
    if not api_key:
        raise LLMReplyError("LLM API key is not configured")

    model = os.getenv("LLM_MODEL", "openai/gpt-4.1-mini")
    base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    payload = {
        "model": model,
        "messages": build_rag_messages(user_text, lang),
        "temperature": 0.65,
        "max_tokens": 220,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        text = data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise LLMReplyError("LLM API request failed") from exc

    if not text:
        raise LLMReplyError("LLM API returned an empty reply")
    return text
