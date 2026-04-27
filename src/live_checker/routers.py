from fastapi import APIRouter, Depends, Response, Request
from src.live_checker.services import create_link, get_links_by_telegram_id, get_link_by_id, delete_link
from src.live_checker.schemas import LinkCreate, LinkResponse, ShortLinkResponse, LinksResponse
from src.telegram_auth.dependencies import get_current_user
from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

live_checker_router = APIRouter(prefix="/live_checker", tags=["live_checker"])

@live_checker_router.post("/create_link")
async def create_link_endpoint(
    link_data: LinkCreate,
    telegram_id: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> LinkResponse:
    link = await create_link(session, telegram_id, link_data)
    return link

@live_checker_router.get("/get_links")
async def get_links_endpoint(
    telegram_id: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> LinksResponse:
    links = await get_links_by_telegram_id(session, telegram_id)
    return links

@live_checker_router.get("/get_link/{link_id}")
async def get_link_endpoint(
    link_id: int,
    telegram_id: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> LinkResponse:
    link = await get_link_by_id(session, link_id, telegram_id)
    return link

@live_checker_router.delete("/delete_link/{link_id}")
async def delete_link_endpoint(
    link_id: int,
    telegram_id: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> dict:
    await delete_link(session, link_id, telegram_id)
    return {"status": "success", "message": "Link deleted successfully"}
