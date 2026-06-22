import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import BotCommand, CallbackQuery, FSInputFile, Message

from app.bot.keyboards import inline_keyboard, main_reply_keyboard
from app.bot.session import cleanup_chat_context, prune_chat_history, remember_bot_message
from app.bot.state import is_support_dialogue_mode, is_talk_mode, set_chat_mode
from app.core.crisis import crisis_reply, is_crisis_text
from app.core.onboarding import onboarding_buttons, onboarding_start_text, rules_text
from app.services.literature import literature_reply
from app.services.llm import LLMReplyError, generate_support_reply, llm_is_configured
from app.services.voice import text_to_speech_ogg, transcribe_telegram_voice


async def send_clean_text(message: Message, text: str, **kwargs) -> Message:
    sent = await message.answer(text, **kwargs)
    remember_bot_message(sent)
    await prune_chat_history(sent)
    return sent


async def send_text_and_voice(message: Message, text: str, **kwargs) -> Message:
    sent = await send_clean_text(message, text, **kwargs)
    voice_path: Path | None = None
    try:
        voice_path = await text_to_speech_ogg(text)
        voice_message = await message.answer_voice(FSInputFile(voice_path))
        remember_bot_message(voice_message)
        await prune_chat_history(voice_message)
    except Exception:
        pass
    finally:
        if voice_path:
            with contextlib.suppress(Exception):
                voice_path.unlink(missing_ok=True)
    return sent


async def generate_live_support_reply(message: Message, text: str, lang: str = "ru") -> str | None:
    if not llm_is_configured():
        await send_clean_text(message, "LLM API не настроен. Добавь OPENROUTER_API_KEY/LLM_API_KEY в .env.")
        return None
    try:
        return await generate_support_reply(text, lang)
    except LLMReplyError:
        await send_clean_text(message, "LLM API сейчас не ответил. Попробуй ещё раз через минуту.")
        return None


import contextlib


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(message: Message) -> None:
        await cleanup_chat_context(message)
        set_chat_mode(message.chat.id, "menu")
        await send_clean_text(
            message,
            onboarding_start_text("ru"),
            reply_markup=inline_keyboard(onboarding_buttons("ru")),
        )
        await send_clean_text(message, rules_text("ru"), reply_markup=main_reply_keyboard())

    @dp.message(Command("menu"))
    @dp.message(F.text.casefold().in_({"меню", "/menu", "menu"}))
    async def menu(message: Message) -> None:
        await cleanup_chat_context(message)
        set_chat_mode(message.chat.id, "menu")
        await send_clean_text(
            message,
            "Выбери, что сейчас ближе:",
            reply_markup=main_reply_keyboard(),
        )

    @dp.message(Command("sos"))
    @dp.message(F.text.casefold() == "мне плохо / хочу сорваться")
    async def sos(message: Message) -> None:
        await cleanup_chat_context(message)
        await enter_sos_dialogue(message)

    @dp.callback_query(F.data == "accept_rules")
    async def accept_rules(callback: CallbackQuery) -> None:
        await callback.answer("Принято")
        await cleanup_chat_context(callback.message)
        if callback.message:
            set_chat_mode(callback.message.chat.id, "menu")
            await send_clean_text(
                callback.message,
                "Хорошо. Я рядом. Можешь просто написать, что сейчас происходит, или открыть меню.",
                reply_markup=main_reply_keyboard(),
            )

    @dp.callback_query(F.data == "sos")
    async def sos_callback(callback: CallbackQuery) -> None:
        await callback.answer()
        await cleanup_chat_context(callback.message)
        reply = crisis_reply("ru")
        if callback.message:
            await enter_sos_dialogue(callback.message)

    async def enter_sos_dialogue(message: Message) -> None:
        set_chat_mode(message.chat.id, "sos")
        opening = await generate_live_support_reply(
            message,
            "Пользователь нажал «Мне плохо / хочу сорваться». Ответь как живой бережный помощник: коротко, спокойно, без диагноза и давления. Спроси один ближайший вопрос и предложи голосом или текстом сказать, что происходит прямо сейчас. Если есть непосредственная опасность — мягко направь к экстренной/живой помощи.",
        )
        if opening:
            await send_text_and_voice(message, opening, reply_markup=main_reply_keyboard())
        else:
            reply = crisis_reply("ru")
            await send_text_and_voice(message, reply.text, reply_markup=main_reply_keyboard())

    @dp.callback_query(F.data == "talk")
    async def talk_callback(callback: CallbackQuery) -> None:
        await callback.answer()
        await cleanup_chat_context(callback.message)
        if callback.message:
            await enter_talk_mode(callback.message)

    @dp.message(F.text.casefold() == "просто выговориться")
    async def talk_message_button(message: Message) -> None:
        await cleanup_chat_context(message)
        await enter_talk_mode(message)

    async def enter_talk_mode(message: Message) -> None:
        set_chat_mode(message.chat.id, "talk")
        opening = await generate_live_support_reply(
            message,
            "Пользователь открыл раздел «Просто выговориться». Мягко пригласи его написать или сказать голосом, что сейчас тяжелее всего.",
        )
        if opening:
            await send_text_and_voice(message, opening, reply_markup=main_reply_keyboard())

    @dp.callback_query(F.data == "contact")
    async def contact_callback(callback: CallbackQuery) -> None:
        await callback.answer()
        await cleanup_chat_context(callback.message)
        if callback.message:
            await enter_contact_mode(callback.message)

    @dp.message(F.text.casefold() == "связаться с человеком")
    async def contact_message_button(message: Message) -> None:
        await cleanup_chat_context(message)
        await enter_contact_mode(message)

    async def enter_contact_mode(message: Message) -> None:
        set_chat_mode(message.chat.id, "contact")
        await send_clean_text(
            message,
            "Пока живые помощники ещё не подключены. Сейчас я могу остаться рядом и помочь тебе сделать ближайший безопасный шаг.",
            reply_markup=main_reply_keyboard(),
        )

    @dp.callback_query(F.data == "newcomer")
    async def newcomer_callback(callback: CallbackQuery) -> None:
        await callback.answer()
        await cleanup_chat_context(callback.message)
        if callback.message:
            await enter_newcomer_mode(callback.message)

    @dp.message(F.text.casefold() == "я новичок")
    async def newcomer_message_button(message: Message) -> None:
        await cleanup_chat_context(message)
        await enter_newcomer_mode(message)

    async def enter_newcomer_mode(message: Message) -> None:
        set_chat_mode(message.chat.id, "newcomer")
        await send_clean_text(
            message,
            "Если ты новичок: можно просто прийти на группу, слушать и не говорить, если не хочется. Спонсор — это человек с опытом выздоровления, который помогает идти по шагам.",
            reply_markup=main_reply_keyboard(),
        )

    @dp.callback_query(F.data == "literature")
    async def literature_callback(callback: CallbackQuery) -> None:
        await callback.answer()
        await cleanup_chat_context(callback.message)
        if callback.message:
            set_chat_mode(callback.message.chat.id, "literature")
            await send_clean_text(
                callback.message,
                "Можешь спросить про шаг, традицию, тягу, спонсора или группу — я найду опору в литературе АА.",
            )

    @dp.message(Command("literature"))
    @dp.message(F.text.casefold() == "литература")
    async def literature_command(message: Message) -> None:
        await cleanup_chat_context(message)
        text = message.text or ""
        query = text.replace("/literature", "", 1).strip() if text.startswith("/literature") else ""
        if not query:
            await send_clean_text(
                message,
                "Можешь спросить про шаг, традицию, тягу, спонсора или группу — я найду опору в литературе АА.",
                reply_markup=main_reply_keyboard(),
            )
            set_chat_mode(message.chat.id, "literature")
            return
        await send_clean_text(message, literature_reply(query, "ru"), parse_mode="Markdown", reply_markup=main_reply_keyboard())

    @dp.callback_query()
    async def any_callback(callback: CallbackQuery) -> None:
        await callback.answer()
        await cleanup_chat_context(callback.message)
        if callback.message:
            set_chat_mode(callback.message.chat.id, "menu")
            await send_clean_text(callback.message, "Этот раздел скоро добавим поэтапно. Пока можешь написать мне обычным сообщением.")

    @dp.message(F.voice)
    async def voice_message(message: Message) -> None:
        await cleanup_chat_context(message)
        if not is_support_dialogue_mode(message.chat.id):
            await send_clean_text(message, "Голосом можно ответить в разделах «Просто выговориться» и «Мне плохо / хочу сорваться». Нажми нужную кнопку в меню.", reply_markup=main_reply_keyboard())
            return
        text = await transcribe_telegram_voice(message.bot, message.voice)
        if not text:
            await send_clean_text(message, "Не получилось распознать голос. Повтори, пожалуйста, коротко.")
            return
        if is_crisis_text(text):
            reply = crisis_reply("ru")
            await send_text_and_voice(message, reply.text, reply_markup=main_reply_keyboard())
            return
        answer = await generate_live_support_reply(message, text, "ru")
        if answer:
            await send_text_and_voice(message, answer)

    @dp.message()
    async def any_message(message: Message) -> None:
        await cleanup_chat_context(message)
        text = message.text or ""
        if is_crisis_text(text):
            reply = crisis_reply("ru")
            if is_talk_mode(message.chat.id):
                await send_text_and_voice(message, reply.text, reply_markup=main_reply_keyboard())
            else:
                await send_clean_text(message, reply.text, reply_markup=main_reply_keyboard())
            return
        if is_support_dialogue_mode(message.chat.id):
            answer = await generate_live_support_reply(message, text, "ru")
            if answer:
                if is_talk_mode(message.chat.id) or message.text is not None:
                    await send_text_and_voice(message, answer, reply_markup=main_reply_keyboard())
                else:
                    await send_clean_text(message, answer, reply_markup=main_reply_keyboard())
            return
        await send_clean_text(message, "Открой /menu и выбери нужный раздел. Для живого голосового общения выбери «Просто выговориться».", reply_markup=main_reply_keyboard())

    return dp


async def run_bot(token: str) -> None:
    bot = Bot(token=token)
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="menu", description="Открыть меню"),
        BotCommand(command="sos", description="Мне плохо / хочу сорваться"),
        BotCommand(command="literature", description="Поиск по литературе"),
    ])
    dp = create_dispatcher()
    await dp.start_polling(bot)
