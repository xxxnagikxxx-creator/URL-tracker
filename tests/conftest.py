import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "postgres")
os.environ.setdefault("DB_NAME", "live_checker_test")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_PASSWORD", "redis_pass")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("SECRET_KEY", "test_secret_key")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_bot_token")
os.environ.setdefault("TELEGRAM_BOT_USERNAME", "testivecheckerbot")

from src.database import Base, get_db  # noqa: E402
from src.main import app  # noqa: E402
from src.telegram_auth import token as token_module  # noqa: E402
from src.telegram_auth.models import User  # noqa: E402,F401
from src.live_checker.models import Link, LinkCheck  # noqa: E402,F401


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with TestSession() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield session

    async def fake_set_refresh_token(refresh_token: str, telegram_id: int) -> None:
        return None

    async def fake_delete_refresh_token(telegram_id: int) -> None:
        return None

    monkeypatch.setattr(token_module, "set_refresh_token", fake_set_refresh_token)
    monkeypatch.setattr(token_module, "delete_refresh_token", fake_delete_refresh_token)
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://testserver",
    ) as api_client:
        yield api_client

    app.dependency_overrides.clear()
