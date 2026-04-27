from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from src.telegram_auth.models import User
from src.telegram_auth.schemas import UserCreate, ShortUserResponse, FullUserResponse, UserUpdate
from src.telegram_auth.exceptions import UserNotFoundException


async def create_user(session: AsyncSession, user_data: UserCreate) -> FullUserResponse:
    result = await session.execute(select(User).where(User.telegram_id == user_data.telegram_id))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        update_data = UserUpdate(
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            photo_url=user_data.photo_url,
        )
        return await update_user(session, user_data.telegram_id, update_data)

    user = User(
        telegram_id=user_data.telegram_id,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        photo_url=user_data.photo_url
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return FullUserResponse.model_validate(user.to_dict())

async def get_full_user(session: AsyncSession, telegram_id: int) -> FullUserResponse:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFoundException()
    return FullUserResponse.model_validate(user.to_dict())

async def get_short_user(session: AsyncSession, telegram_id: int) -> ShortUserResponse:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFoundException()
    return ShortUserResponse.model_validate(user.to_dict())

async def get_all_users(session: AsyncSession) -> List[ShortUserResponse]:
    result = await session.execute(select(User))
    users = result.scalars().all()
    return [ShortUserResponse.model_validate(user.to_dict()) for user in users]

async def update_user(session: AsyncSession, telegram_id: int, user_data: UserUpdate) -> FullUserResponse:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFoundException()
    user.username = user_data.username
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    user.photo_url = user_data.photo_url
    await session.commit()
    await session.refresh(user)
    return FullUserResponse.model_validate(user.to_dict())

async def delete_user(session: AsyncSession, telegram_id: int) -> None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFoundException()
    await session.delete(user)
    await session.commit()
    return None
