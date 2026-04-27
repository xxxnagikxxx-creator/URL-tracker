from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from src.config import settings
from src.telegram_auth.token import create_access_token, verify_access_token


def test_verify_access_token_returns_telegram_id() -> None:
    token = create_access_token(telegram_id=123456789)

    assert verify_access_token(token) == 123456789


def test_verify_access_token_rejects_invalid_token() -> None:
    with pytest.raises(HTTPException) as exc_info:
        verify_access_token("not-a-valid-token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"


def test_verify_access_token_rejects_expired_token() -> None:
    token = jwt.encode(
        {
            "sub": "123456789",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_settings.secret_key,
        algorithm=settings.jwt_settings.jwt_algorithm,
    )

    with pytest.raises(HTTPException) as exc_info:
        verify_access_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token expired"
