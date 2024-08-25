from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db import async_session_marker


async def get_db() -> AsyncSession:
    async with async_session_marker() as session:
        yield session