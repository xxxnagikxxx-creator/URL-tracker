from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.live_checker.models import Link, LinkCheck
from src.live_checker.schemas import LinkCreate, LinkResponse, ShortLinkResponse, LinksResponse
from src.live_checker.exceptions import LinkNotFoundException
from src.live_checker.utils import check_link

async def create_link(session: AsyncSession, telegram_id: int, link_data: LinkCreate) -> LinkResponse:
    link = Link(
        url=link_data.url,
        telegram_id=telegram_id
    )
    session.add(link)
    await session.commit()
    await session.refresh(link)
    return LinkResponse.model_validate(link.to_dict())

async def get_links_by_telegram_id(session: AsyncSession, telegram_id: int) -> LinksResponse:
    result = await session.execute(select(Link).where(Link.telegram_id == telegram_id))
    links = result.scalars().all()
    return LinksResponse.model_validate({"links": [link.to_dict() for link in links]})

async def get_link_by_id(session: AsyncSession, link_id: int, telegram_id: int) -> LinkResponse:
    result = await session.execute(
        select(Link)
        .options(selectinload(Link.checks))
        .where(Link.id == link_id, Link.telegram_id == telegram_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise LinkNotFoundException()
    return LinkResponse.model_validate(link.to_dict())

async def delete_link(session: AsyncSession, link_id: int, telegram_id: int) -> None:
    result = await session.execute(select(Link).where(Link.id == link_id, Link.telegram_id == telegram_id))
    link = result.scalar_one_or_none()
    if not link:
        raise LinkNotFoundException()
    await session.delete(link)
    await session.commit()
    return None

async def check_link(session: AsyncSession, link_id: int, status_code: int, response_time: float) -> None:
    link_check = LinkCheck(
        link_id=link_id,
        status_code=status_code,
        response_time=response_time
    )
    session.add(link_check)
    await session.commit()
    await session.refresh(link_check)
    return None

