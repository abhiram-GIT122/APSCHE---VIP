from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from app.config.config import settings

# -----------------------------
# Async Engine
# -----------------------------
engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=(settings.ENVIRONMENT == "development"),
)

# -----------------------------
# Session Factory
# -----------------------------
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# -----------------------------
# Dependency
# -----------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()