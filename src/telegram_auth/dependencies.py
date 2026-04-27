from fastapi import Depends, Request
from src.telegram_auth.token import verify_access_token
from src.telegram_auth.exceptions import InvalidCredentialsException

async def get_current_user(request: Request) -> int:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise InvalidCredentialsException()
    telegram_id = verify_access_token(access_token)
    return telegram_id
