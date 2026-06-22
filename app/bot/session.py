import asyncio
from collections import defaultdict
from contextlib import suppress

from aiogram.types import Message

_KEEP_LAST_MESSAGES = 2
_MAX_AGGRESSIVE_DELETE_RANGE = 200
AUTO_DELETE_AFTER_SECONDS = 30 * 60
_CHAT_MESSAGES: dict[int, set[int]] = defaultdict(set)
_AUTO_DELETE_TASKS: dict[tuple[int, int], asyncio.Task] = {}


def _message_key(chat_id: int, message_id: int) -> tuple[int, int]:
    return chat_id, message_id


async def _auto_delete_later(bot, chat_id: int, message_id: int) -> None:
    try:
        await asyncio.sleep(AUTO_DELETE_AFTER_SECONDS)
        with suppress(Exception):
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        _CHAT_MESSAGES[chat_id].discard(message_id)
    finally:
        _AUTO_DELETE_TASKS.pop(_message_key(chat_id, message_id), None)


def _schedule_auto_delete(message: Message) -> None:
    key = _message_key(message.chat.id, message.message_id)
    existing = _AUTO_DELETE_TASKS.pop(key, None)
    if existing:
        existing.cancel()
    _AUTO_DELETE_TASKS[key] = asyncio.create_task(_auto_delete_later(message.bot, message.chat.id, message.message_id))


def _cancel_auto_delete(chat_id: int, message_id: int) -> None:
    task = _AUTO_DELETE_TASKS.pop(_message_key(chat_id, message_id), None)
    if task:
        task.cancel()


def _remember(chat_id: int, message_id: int) -> None:
    _CHAT_MESSAGES[chat_id].add(message_id)


def remember_message(message: Message | None) -> Message | None:
    if message:
        _remember(message.chat.id, message.message_id)
        _schedule_auto_delete(message)
    return message


def remember_bot_message(message: Message) -> Message:
    remember_message(message)
    return message


def _message_ids_to_delete(known_ids: set[int], keep_last: int) -> tuple[list[int], set[int]]:
    if len(known_ids) <= keep_last:
        return [], known_ids

    sorted_known = sorted(known_ids)
    keep_ids = set(sorted_known[-keep_last:])
    first = sorted_known[0]
    last_delete_candidate = sorted_known[-keep_last] - 1

    if last_delete_candidate < first:
        return [], keep_ids

    # Aggressive mode: try deleting every Telegram message_id in the old range.
    # This catches service/system messages and user messages if Telegram permits deletion.
    # Keep a safety cap so a long-id jump cannot trigger thousands of API calls.
    if last_delete_candidate - first + 1 <= _MAX_AGGRESSIVE_DELETE_RANGE:
        to_delete = [mid for mid in range(first, last_delete_candidate + 1) if mid not in keep_ids]
    else:
        to_delete = [mid for mid in sorted_known[:-keep_last] if mid not in keep_ids]

    return to_delete, keep_ids


async def prune_chat_history(message: Message | None, keep_last: int = _KEEP_LAST_MESSAGES) -> None:
    if not message:
        return
    chat_id = message.chat.id
    to_delete, keep_ids = _message_ids_to_delete(_CHAT_MESSAGES[chat_id], keep_last)
    _CHAT_MESSAGES[chat_id] = keep_ids

    for message_id in to_delete:
        with suppress(Exception):
            await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
        _cancel_auto_delete(chat_id, message_id)


async def cleanup_chat_context(message: Message | None) -> None:
    """Remember current incoming/bot message and keep only last two known messages.

    Telegram may refuse to delete some service messages; we still try to delete
    the whole old message_id range so system/user messages disappear when allowed.
    Every remembered message also gets a delayed auto-delete task so inactive
    chats are cleaned after the privacy window.
    """
    remember_message(message)
    await prune_chat_history(message)


async def wait_for_auto_cleanup_tasks() -> None:
    """Test helper: wait until currently scheduled immediate cleanup tasks finish."""
    tasks = list(_AUTO_DELETE_TASKS.values())
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
