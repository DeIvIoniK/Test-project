from collections import defaultdict
from contextlib import suppress

from aiogram.types import Message

_KEEP_LAST_MESSAGES = 2
_MAX_AGGRESSIVE_DELETE_RANGE = 200
_CHAT_MESSAGES: dict[int, set[int]] = defaultdict(set)


def _remember(chat_id: int, message_id: int) -> None:
    _CHAT_MESSAGES[chat_id].add(message_id)


def remember_message(message: Message | None) -> Message | None:
    if message:
        _remember(message.chat.id, message.message_id)
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


async def cleanup_chat_context(message: Message | None) -> None:
    """Remember current incoming/bot message and keep only last two known messages.

    Telegram may refuse to delete some service messages; we still try to delete
    the whole old message_id range so system/user messages disappear when allowed.
    """
    remember_message(message)
    await prune_chat_history(message)
