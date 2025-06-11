"""
Collection Service Database Configuration
Isolated database session that only knows about collection service models
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..models.collection import Base

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://rag_user:rag_password@localhost:5433/advanced_rag"
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency for Collection Service
    Only knows about collection service models
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create collection service tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop collection service tables (use with caution)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
