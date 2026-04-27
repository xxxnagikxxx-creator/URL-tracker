from hashlib import sha256
import hmac
import time

import pytest

from src.config import settings
from src.telegram_auth.exceptions import InvalidTelegramAuthException
from src.telegram_auth.schemas import TelegramAuthData
from src.telegram_auth.utils import verify_telegram_auth_data


def build_signed_payload(**overrides) -> TelegramAuthData:
    payload = {
        "id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "test_user",
        "photo_url": "https://example.com/photo.jpg",
        "auth_date": int(time.time()),
    }
    payload.update(overrides)

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(payload.items()))
    secret_key = sha256(settings.telegram_settings.telegram_bot_token.encode()).digest()
    payload["hash"] = hmac.new(secret_key, data_check_string.encode(), sha256).hexdigest()

    return TelegramAuthData(**payload)


def test_verify_telegram_auth_data_accepts_valid_payload() -> None:
    auth_data = build_signed_payload()

    user_data = verify_telegram_auth_data(auth_data)

    assert user_data.telegram_id == auth_data.id
    assert user_data.username == auth_data.username
    assert user_data.first_name == auth_data.first_name


def test_verify_telegram_auth_data_rejects_invalid_hash() -> None:
    auth_data = build_signed_payload()
    auth_data.hash = "invalid_hash"

    with pytest.raises(InvalidTelegramAuthException):
        verify_telegram_auth_data(auth_data)


def test_verify_telegram_auth_data_rejects_old_payload() -> None:
    auth_data = build_signed_payload(auth_date=int(time.time()) - 25 * 60 * 60)

    with pytest.raises(InvalidTelegramAuthException):
        verify_telegram_auth_data(auth_data)


def test_verify_telegram_auth_data_rejects_future_payload() -> None:
    auth_data = build_signed_payload(auth_date=int(time.time()) + 120)

    with pytest.raises(InvalidTelegramAuthException):
        verify_telegram_auth_data(auth_data)
