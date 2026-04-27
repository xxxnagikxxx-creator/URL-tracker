import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.live_checker.exceptions import LinkNotFoundException
from src.live_checker.models import Link
from src.live_checker.schemas import LinkCreate
from src.live_checker.services import create_link, delete_link, get_link_by_id, get_links_by_telegram_id
from src.telegram_auth.exceptions import UserNotFoundException
from src.telegram_auth.models import User
from src.telegram_auth.schemas import UserCreate
from src.telegram_auth.services import create_user, delete_user, get_full_user


@pytest.mark.asyncio
async def test_create_user_creates_new_user(session: AsyncSession) -> None:
    user = await create_user(
        session,
        UserCreate(
            telegram_id=1,
            username="first",
            first_name="First",
            last_name="User",
            photo_url=None,
        ),
    )

    assert user.telegram_id == 1
    assert user.username == "first"


@pytest.mark.asyncio
async def test_create_user_updates_existing_user(session: AsyncSession) -> None:
    await create_user(
        session,
        UserCreate(
            telegram_id=1,
            username="old",
            first_name="Old",
            last_name="Name",
            photo_url=None,
        ),
    )

    updated_user = await create_user(
        session,
        UserCreate(
            telegram_id=1,
            username="new",
            first_name="New",
            last_name="Name",
            photo_url="https://example.com/new.jpg",
        ),
    )

    result = await session.execute(select(User).where(User.telegram_id == 1))
    users = result.scalars().all()

    assert len(users) == 1
    assert updated_user.username == "new"
    assert updated_user.first_name == "New"
    assert updated_user.photo_url == "https://example.com/new.jpg"


@pytest.mark.asyncio
async def test_get_full_user_raises_for_missing_user(session: AsyncSession) -> None:
    with pytest.raises(UserNotFoundException):
        await get_full_user(session, telegram_id=404)


@pytest.mark.asyncio
async def test_delete_user_removes_user(session: AsyncSession) -> None:
    await create_user(
        session,
        UserCreate(
            telegram_id=1,
            username="user",
            first_name="Test",
            last_name=None,
            photo_url=None,
        ),
    )

    await delete_user(session, telegram_id=1)

    with pytest.raises(UserNotFoundException):
        await get_full_user(session, telegram_id=1)


@pytest.mark.asyncio
async def test_get_links_returns_only_current_user_links(session: AsyncSession) -> None:
    await create_user(session, UserCreate(telegram_id=1, username=None, first_name="One"))
    await create_user(session, UserCreate(telegram_id=2, username=None, first_name="Two"))
    await create_link(session, 1, LinkCreate(url="https://one.example.com"))
    await create_link(session, 2, LinkCreate(url="https://two.example.com"))

    response = await get_links_by_telegram_id(session, telegram_id=1)

    assert [link.url for link in response.links] == ["https://one.example.com"]


@pytest.mark.asyncio
async def test_get_link_by_id_does_not_return_other_user_link(session: AsyncSession) -> None:
    await create_user(session, UserCreate(telegram_id=1, username=None, first_name="One"))
    await create_user(session, UserCreate(telegram_id=2, username=None, first_name="Two"))
    link = await create_link(session, 2, LinkCreate(url="https://two.example.com"))

    with pytest.raises(LinkNotFoundException):
        await get_link_by_id(session, link_id=link.id, telegram_id=1)


@pytest.mark.asyncio
async def test_delete_link_does_not_delete_other_user_link(session: AsyncSession) -> None:
    await create_user(session, UserCreate(telegram_id=1, username=None, first_name="One"))
    await create_user(session, UserCreate(telegram_id=2, username=None, first_name="Two"))
    link = await create_link(session, 2, LinkCreate(url="https://two.example.com"))

    with pytest.raises(LinkNotFoundException):
        await delete_link(session, link_id=link.id, telegram_id=1)

    result = await session.execute(select(Link).where(Link.id == link.id))
    assert result.scalar_one_or_none() is not None
