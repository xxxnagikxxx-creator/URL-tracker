from aiogram import Bot
from src.config import settings


def build_bad_status_message(url: str, status_code: int, response_time: float) -> str:
    return (
        "⚠️ Проблема с ссылкой\n\n"
        f"URL: {url}\n"
        f"Статус: {status_code}\n"
        f"Время ответа: {response_time:.3f} сек."
    )


async def notify_bad_status(
    ctx: dict,
    telegram_id: int,
    url: str,
    status_code: int,
    response_time: float,
) -> None:
    bot: Bot = ctx["bot"]
    await bot.send_message(
        chat_id=telegram_id,
        text=build_bad_status_message(url, status_code, response_time),
    )


async def startup_bot(ctx: dict) -> None:
    ctx["bot"] = Bot(token=settings.telegram_settings.telegram_bot_token)


async def shutdown_bot(ctx: dict) -> None:
    bot: Bot | None = ctx.get("bot")
    if bot is not None:
        await bot.session.close()
