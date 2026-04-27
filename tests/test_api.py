from hashlib import sha256
import hmac
import time

import pytest
from httpx import AsyncClient

from src.config import settings


def build_telegram_payload(**overrides) -> dict:
    payload = {
        "id": 123456789,
        "first_name": "Api",
        "last_name": "User",
        "username": "api_user",
        "photo_url": "https://example.com/photo.jpg",
        "auth_date": int(time.time()),
    }
    payload.update(overrides)

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(payload.items()))
    secret_key = sha256(settings.telegram_settings.telegram_bot_token.encode()).digest()
    payload["hash"] = hmac.new(secret_key, data_check_string.encode(), sha256).hexdigest()

    return payload


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "live_checker"}


@pytest.mark.asyncio
async def test_protected_endpoint_without_cookies_returns_401(client: AsyncClient) -> None:
    response = await client.get("/auth/get_full_user")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_telegram_login_sets_cookies_and_returns_current_user(client: AsyncClient) -> None:
    login_response = await client.post("/auth/telegram", json=build_telegram_payload())

    assert login_response.status_code == 200
    assert "access_token" in client.cookies
    assert "refresh_token" in client.cookies

    current_user_response = await client.get("/auth/get_full_user")

    assert current_user_response.status_code == 200
    assert current_user_response.json()["telegram_id"] == 123456789


@pytest.mark.asyncio
async def test_create_link_requires_authentication(client: AsyncClient) -> None:
    response = await client.post("/live_checker/create_link", json={"url": "https://example.com"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_user_can_create_and_list_links(client: AsyncClient) -> None:
    await client.post("/auth/telegram", json=build_telegram_payload())

    create_response = await client.post(
        "/live_checker/create_link",
        json={"url": "https://example.com"},
    )
    links_response = await client.get("/live_checker/get_links")

    assert create_response.status_code == 200
    assert create_response.json()["url"] == "https://example.com"
    assert links_response.status_code == 200
    assert links_response.json()["links"] == [{"id": create_response.json()["id"], "url": "https://example.com"}]


@pytest.mark.asyncio
async def test_logout_clears_session(client: AsyncClient) -> None:
    await client.post("/auth/telegram", json=build_telegram_payload())

    logout_response = await client.post("/auth/logout")
    current_user_response = await client.get("/auth/get_full_user")

    assert logout_response.status_code == 200
    assert current_user_response.status_code == 401
