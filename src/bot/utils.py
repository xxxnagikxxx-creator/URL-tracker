from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from src.live_checker.schemas import LinkCheckResponse, ShortLinkResponse
from src.telegram_auth.schemas import UserCreate
from src.telegram_auth.services import create_user


def main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить ссылку", callback_data="add")],
            [InlineKeyboardButton(text="📋 Посмотреть ссылки", callback_data="view")],
            [InlineKeyboardButton(text="📊 Последняя информация", callback_data="info")],
            [InlineKeyboardButton(text="❌ Удалить ссылку", callback_data="delete")],
        ]
    )


def links_kb(links: list[ShortLinkResponse], action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{index}. {link.url}", callback_data=f"{action}:{link.id}")]
            for index, link in enumerate(links, start=1)
        ]
    )


def format_links(links: list[ShortLinkResponse]) -> str:
    return "\n".join(f"{index}. {link.url}" for index, link in enumerate(links, start=1))


def format_latest_check(check: LinkCheckResponse | None) -> str:
    if check is None:
        return "Проверок для этой ссылки пока нет."

    return (
        "Последняя проверка:\n"
        f"Статус: {check.status_code}\n"
        f"Время ответа: {check.response_time:.3f} сек.\n"
        f"Дата: {check.created_at:%Y-%m-%d %H:%M:%S}"
    )


def is_valid_url(url: str) -> bool:
    return url.startswith(("http://", "https://"))


async def ensure_user(session: AsyncSession, telegram_user) -> None:
    await create_user(
        session,
        UserCreate(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name or "",
            last_name=telegram_user.last_name,
            photo_url=None,
        ),
    )
