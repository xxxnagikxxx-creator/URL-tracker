from fastapi import APIRouter, Depends, Response, Request
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.telegram_auth.services import (
    create_user,
    get_full_user,
    get_short_user,
    update_user,
    delete_user,
    get_all_users,
)
from src.telegram_auth.schemas import ShortUserResponse, FullUserResponse, UserUpdate, TelegramAuthData
from src.telegram_auth.dependencies import get_current_user
from src.telegram_auth.token import set_tokens, refresh_access_token, delete_tokens
from src.telegram_auth.utils import verify_telegram_auth_data
from src.database import get_db

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/telegram", response_model=FullUserResponse)
async def telegram_auth_endpoint(
    auth_data: TelegramAuthData,
    response: Response,
    session: AsyncSession = Depends(get_db)
) -> FullUserResponse:
    user_data = verify_telegram_auth_data(auth_data)
    user = await create_user(session, user_data)
    await set_tokens(user.telegram_id, response)
    return user

@auth_router.get("/get_full_user", response_model=FullUserResponse)
async def get_full_user_endpoint(
    telegram_id: int = Depends(get_current_user), 
    session: AsyncSession = Depends(get_db)
) -> FullUserResponse:
    user = await get_full_user(session, telegram_id)
    return user

@auth_router.get("/get_short_user", response_model=ShortUserResponse)
async def get_short_user_endpoint(
    telegram_id: int = Depends(get_current_user), 
    session: AsyncSession = Depends(get_db)
) -> ShortUserResponse:
    user = await get_short_user(session, telegram_id)
    return user

@auth_router.get("/get_all_users", response_model=List[ShortUserResponse])
async def get_all_users_endpoint(
    telegram_id: int = Depends(get_current_user), 
    session: AsyncSession = Depends(get_db)
) -> List[ShortUserResponse]:
    users = await get_all_users(session)
    return users

@auth_router.put("/update_user", response_model=FullUserResponse)
async def update_user_endpoint(
    user_data: UserUpdate, 
    telegram_id: int = Depends(get_current_user), 
    session: AsyncSession = Depends(get_db)
) -> FullUserResponse:
    user = await update_user(session, telegram_id, user_data)
    return user

@auth_router.delete("/delete_user")
async def delete_user_endpoint(
    request: Request,
    response: Response,
    telegram_id: int = Depends(get_current_user), 
    session: AsyncSession = Depends(get_db)
) -> dict:
    await delete_user(session, telegram_id)
    await delete_tokens(request, response)
    return {"status": "success", "message": "User deleted successfully"}

@auth_router.post("/refresh")
async def refresh_token_endpoint(request: Request, response: Response) -> dict:
    await refresh_access_token(request, response)
    return {"status": "success", "message": "Token refreshed successfully"}

@auth_router.post("/logout")
async def logout_endpoint(request: Request, response: Response) -> dict:
    await delete_tokens(request, response)
    return {"status": "success", "message": "Logged out successfully"}
