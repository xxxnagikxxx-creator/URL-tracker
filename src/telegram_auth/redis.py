from redis.asyncio import Redis
from src.config import settings

redis = Redis(
    host=settings.redis_settings.redis_host, 
    port=settings.redis_settings.redis_port, 
    password=settings.redis_settings.redis_password,
    decode_responses=True
)

async def set_refresh_token(refresh_token: str, telegram_id: int) -> None:
    ttl = settings.jwt_settings.refresh_token_expire_days * 24 * 60 * 60
    await redis.set(telegram_id, refresh_token, ex=ttl)

async def get_refresh_token(telegram_id: int) -> str | None:
    return await redis.get(telegram_id)

async def delete_refresh_token(telegram_id: int) -> None:
    await redis.delete(telegram_id)