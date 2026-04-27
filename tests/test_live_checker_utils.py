from datetime import timedelta

import pytest
from httpx import RequestError, TimeoutException

from src.live_checker import utils


class FakeElapsed:
    def total_seconds(self) -> float:
        return 0.123


class FakeResponse:
    status_code = 204
    elapsed = FakeElapsed()


class FakeAsyncClient:
    def __init__(self, result=None, error: Exception | None = None):
        self.result = result or FakeResponse()
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def get(self, url: str, timeout: int):
        if self.error:
            raise self.error
        return self.result


@pytest.mark.asyncio
async def test_check_link_returns_status_and_response_time(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(utils, "AsyncClient", lambda: FakeAsyncClient())

    result = await utils.check_link("https://example.com")

    assert result == {"status_code": 204, "response_time": 0.123}


@pytest.mark.asyncio
async def test_check_link_returns_408_on_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(utils, "AsyncClient", lambda: FakeAsyncClient(error=TimeoutException("timeout")))

    result = await utils.check_link("https://example.com")

    assert result == {"status_code": 408, "response_time": 10.0}


@pytest.mark.asyncio
async def test_check_link_returns_500_on_request_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(utils, "AsyncClient", lambda: FakeAsyncClient(error=RequestError("connect error")))

    result = await utils.check_link("https://example.com")

    assert result == {"status_code": 500, "response_time": 0.0}
