from types import SimpleNamespace

import pytest

from app.bot.session import cleanup_chat_context, prune_chat_history, remember_bot_message, remember_message


class FakeBot:
    def __init__(self):
        self.deleted = []

    async def delete_message(self, chat_id: int, message_id: int) -> None:
        self.deleted.append((chat_id, message_id))


def fake_message(chat_id: int, message_id: int, is_bot: bool = True, bot: FakeBot | None = None):
    return SimpleNamespace(
        chat=SimpleNamespace(id=chat_id),
        message_id=message_id,
        from_user=SimpleNamespace(is_bot=is_bot),
        bot=bot or FakeBot(),
    )


@pytest.mark.asyncio
async def test_prune_chat_history_keeps_only_two_latest_known_messages():
    bot = FakeBot()
    for message_id in [10, 11, 12, 13, 14]:
        remember_message(fake_message(300, message_id, bot=bot))

    await prune_chat_history(fake_message(300, 14, bot=bot))

    assert bot.deleted == [(300, 10), (300, 11), (300, 12)]


@pytest.mark.asyncio
async def test_cleanup_remembers_current_message_before_pruning():
    bot = FakeBot()
    remember_bot_message(fake_message(301, 20, bot=bot))
    remember_bot_message(fake_message(301, 21, bot=bot))

    await cleanup_chat_context(fake_message(301, 22, is_bot=False, bot=bot))

    assert bot.deleted == [(301, 20)]


@pytest.mark.asyncio
async def test_prune_tries_to_delete_unknown_system_messages_between_known_messages():
    bot = FakeBot()
    for message_id in [30, 35, 36]:
        remember_message(fake_message(302, message_id, bot=bot))

    await prune_chat_history(fake_message(302, 36, bot=bot))

    assert bot.deleted == [(302, 30), (302, 31), (302, 32), (302, 33), (302, 34)]
