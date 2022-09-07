import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./cryptomonitor.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
DB_HOST = os.environ.get("DB_HOST", "postgres")
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://postgres:password@{DB_HOST}/cryptomonitor"
)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, poolclass=NullPool)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


Base = declarative_base()
