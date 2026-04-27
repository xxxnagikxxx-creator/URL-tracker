from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

engine = create_async_engine(settings.db_settings.db_url, echo=True)
Session = async_sessionmaker(engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with Session() as session:
        yield session

