import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.utils import (
    ensure_user,
    format_latest_check,
    format_links,
    is_valid_url,
    links_kb,
    main_kb,
)
from src.config import settings
from src.database import Session
from src.live_checker.exceptions import LinkNotFoundException
from src.live_checker.schemas import LinkCreate
from src.live_checker.services import (
    create_link,
    delete_link as delete_link_by_id,
    get_link_by_id,
    get_links_by_telegram_id,
)



bot = Bot(token=settings.telegram_settings.telegram_bot_token)
dp = Dispatcher(storage=MemoryStorage())



class LinkState(StatesGroup):
    waiting_for_link = State()


@dp.message(CommandStart())
async def start(message: Message):
    async with Session() as session:
        await ensure_user(session, message.from_user)

    await message.answer("Выберите действие:", reply_markup=main_kb())



@dp.callback_query(F.data == "add")
async def add_link(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LinkState.waiting_for_link)
    await callback.message.answer("Отправь ссылку:")
    await callback.answer()


@dp.message(LinkState.waiting_for_link)
async def save_link(message: Message, state: FSMContext):
    user_id = message.from_user.id
    url = (message.text or "").strip()

    if not is_valid_url(url):
        await message.answer("Отправь ссылку, которая начинается с http:// или https://")
        return

    async with Session() as session:
        await ensure_user(session, message.from_user)
        await create_link(session, user_id, LinkCreate(url=url))

    await message.answer("✅ Ссылка сохранена!", reply_markup=main_kb())
    await state.clear()


@dp.callback_query(F.data == "view")
async def view_links(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with Session() as session:
        await ensure_user(session, callback.from_user)
        response = await get_links_by_telegram_id(session, user_id)
        links = response.links

    if not links:
        text = "У тебя пока нет ссылок"
    else:
        text = format_links(links)

    await callback.message.answer(text, reply_markup=main_kb())
    await callback.answer()


@dp.callback_query(F.data == "delete")
async def delete_link(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with Session() as session:
        await ensure_user(session, callback.from_user)
        response = await get_links_by_telegram_id(session, user_id)
        links = response.links

    if not links:
        await callback.message.answer("Нет ссылок для удаления")
        await callback.answer()
        return

    await callback.message.answer("Какую ссылку удалить?", reply_markup=links_kb(links, "delete_link"))
    await callback.answer()


@dp.callback_query(F.data.startswith("delete_link:"))
async def confirm_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    link_id = int(callback.data.split(":", maxsplit=1)[1])

    try:
        async with Session() as session:
            await delete_link_by_id(session, link_id, user_id)
    except LinkNotFoundException:
        await callback.message.answer("Ссылка не найдена или уже удалена", reply_markup=main_kb())
    else:
        await callback.message.answer("❌ Ссылка удалена", reply_markup=main_kb())

    await callback.answer()


@dp.callback_query(F.data == "info")
async def choose_link_for_info(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with Session() as session:
        await ensure_user(session, callback.from_user)
        response = await get_links_by_telegram_id(session, user_id)
        links = response.links

    if not links:
        await callback.message.answer("У тебя пока нет ссылок")
        await callback.answer()
        return

    await callback.message.answer("По какой ссылке показать информацию?", reply_markup=links_kb(links, "info_link"))
    await callback.answer()


@dp.callback_query(F.data.startswith("info_link:"))
async def show_latest_info(callback: CallbackQuery):
    user_id = callback.from_user.id
    link_id = int(callback.data.split(":", maxsplit=1)[1])

    try:
        async with Session() as session:
            link = await get_link_by_id(session, link_id, user_id)
    except LinkNotFoundException:
        await callback.message.answer("Ссылка не найдена или уже удалена", reply_markup=main_kb())
        await callback.answer()
        return

    latest_check = max(link.checks, key=lambda check: check.created_at, default=None)
    text = f"{link.url}\n\n{format_latest_check(latest_check)}"

    await callback.message.answer(text, reply_markup=main_kb())
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())