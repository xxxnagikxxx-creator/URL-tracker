from hashlib import sha256
import hmac
import time

from src.config import settings
from src.telegram_auth.exceptions import InvalidTelegramAuthException
from src.telegram_auth.schemas import TelegramAuthData, UserCreate


TELEGRAM_AUTH_MAX_AGE_SECONDS = 24 * 60 * 60


def verify_telegram_auth_data(auth_data: TelegramAuthData) -> UserCreate:
    data = auth_data.model_dump(exclude={"hash"}, exclude_none=True)
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
    secret_key = sha256(settings.telegram_settings.telegram_bot_token.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, auth_data.hash):
        raise InvalidTelegramAuthException()

    current_timestamp = int(time.time())
    is_from_future = auth_data.auth_date > current_timestamp + 60
    is_too_old = current_timestamp - auth_data.auth_date > TELEGRAM_AUTH_MAX_AGE_SECONDS

    if is_from_future or is_too_old:
        raise InvalidTelegramAuthException()

    return UserCreate(
        telegram_id=auth_data.id,
        username=auth_data.username,
        first_name=auth_data.first_name,
        last_name=auth_data.last_name,
        photo_url=auth_data.photo_url,
    )
