from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


engine = create_async_engine('postgresql+asyncpg://mis_user:password@localhost:54324/fast_api_store',
                             echo=True)
async_session_marker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass
