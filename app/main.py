import asyncio

from app.config import settings


async def main() -> None:
    if not settings.bot_token:
        print("BOT_TOKEN is not set. Fill .env before starting Telegram polling.")
        return
    from app.bot.runner import run_bot

    await run_bot(settings.bot_token)


if __name__ == "__main__":
    asyncio.run(main())
