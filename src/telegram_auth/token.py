from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status, Response, Request
from src.config import settings
from src.telegram_auth.redis import set_refresh_token, get_refresh_token, delete_refresh_token
from src.telegram_auth.exceptions import (
    InvalidCredentialsException,
    TokenExpiredException,
    RefreshTokenMissingException,
    InvalidRefreshTokenException
)

COOKIE_SECURE = True
COOKIE_SAMESITE = "none"

def create_access_token(telegram_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_settings.access_token_expire_minutes)
    payload = {
        "sub": str(telegram_id),
        "exp": expire
    }
    return jwt.encode(payload, settings.jwt_settings.secret_key, algorithm=settings.jwt_settings.jwt_algorithm)

def create_refresh_token(telegram_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_settings.refresh_token_expire_days)
    payload = {
        "sub": str(telegram_id),
        "exp": expire
    }
    return jwt.encode(payload, settings.jwt_settings.secret_key, algorithm=settings.jwt_settings.jwt_algorithm)

def verify_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_settings.secret_key, 
            algorithms=[settings.jwt_settings.jwt_algorithm]
        )
        telegram_id_str: str = payload.get("sub")
        
        if telegram_id_str is None:
            raise InvalidCredentialsException()
            
        return int(telegram_id_str)
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise InvalidCredentialsException()

def verify_refresh_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_settings.secret_key, 
            algorithms=[settings.jwt_settings.jwt_algorithm]
        )
        telegram_id_str: str = payload.get("sub")
        
        if telegram_id_str is None:
            raise InvalidCredentialsException()
        return int(telegram_id_str)
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise InvalidCredentialsException()


async def set_tokens(telegram_id: int, response: Response) -> None:
    access_token = create_access_token(telegram_id)
    refresh_token = create_refresh_token(telegram_id)
    
    await set_refresh_token(refresh_token, telegram_id)
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=settings.jwt_settings.access_token_expire_minutes * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=settings.jwt_settings.refresh_token_expire_days * 24 * 60 * 60
    )


async def refresh_access_token(request: Request, response: Response) -> None:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise RefreshTokenMissingException()
        
    telegram_id = verify_refresh_token(refresh_token)
    stored_token = await get_refresh_token(telegram_id)
    
    if not stored_token or stored_token != refresh_token:
        raise InvalidRefreshTokenException()

    await set_tokens(telegram_id, response)


async def delete_tokens(request: Request, response: Response) -> None:
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            telegram_id = verify_refresh_token(refresh_token)
            await delete_refresh_token(telegram_id)
        except HTTPException:
            pass
    
    response.delete_cookie("access_token", secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE)
    response.delete_cookie("refresh_token", secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE)
